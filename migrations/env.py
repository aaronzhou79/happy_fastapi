import asyncio
import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlmodel import SQLModel
from sqlalchemy.engine import Connection

# 将项目根目录添加到sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

# 获取项目根目录路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(f"project_root: {project_root}")
# 加载.env文件
load_dotenv(os.path.join(project_root, ".env"), override=True)

# 添加更多调试信息
print(f"已加载环境变量文件，当前工作目录: {os.getcwd()}")
print(f".env文件路径: {os.path.join(project_root, '.env')}")
print(f"环境变量DB_TYPE: {os.getenv('DB_TYPE')}")
print(f"环境变量DB_NAME: {os.getenv('DB_NAME')}")
print(f"环境变量DB_HOST: {os.getenv('DB_HOST')}")

# 导入项目配置和模型
try:
    from src.core.conf import settings
    from src.database.db_session import SQLALCHEMY_DATABASE_URL

    if settings.DB_TYPE == "sqlite":
        SQLALCHEMY_DATABASE_URL = f"sqlite+aiosqlite:///./{settings.DB_NAME}"
    elif settings.DB_TYPE == "postgresql":
        SQLALCHEMY_DATABASE_URL = f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
    else:
        raise ValueError(f"Invalid database type: {settings.DB_TYPE}")

    # 导入所有模型以确保它们被注册到SQLModel的元数据中
    try:
        from migrations.models_config import *

        print("========== 成功导入模型 ==========")
        print(f"数据库类型：{settings.DB_TYPE}")
        print(f"数据库连接：{SQLALCHEMY_DATABASE_URL}")
    except ImportError as e:
        print(f"导入模型失败: {e}")
except ImportError as e:
    print(f"导入配置失败: {e}")

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# 使用SQLModel的元数据
target_metadata = SQLModel.metadata

# 设置数据库URL
config.set_main_option("sqlalchemy.url", SQLALCHEMY_DATABASE_URL)

# 检查是否启用了checkfirst模式
USE_CHECKFIRST = os.environ.get("ALEMBIC_CHECKFIRST", "0") == "1"

# 自定义钩子函数，用于在执行DDL操作前修改参数
def process_revision_directives(context, revision, directives):
    if USE_CHECKFIRST and directives and hasattr(directives[0], 'ops'):
        for op in directives[0].ops:
            # 为所有操作添加checkfirst=True参数
            if hasattr(op, 'kw') and isinstance(op.kw, dict):
                op.kw['checkfirst'] = True

            # 特殊处理枚举类型创建
            if hasattr(op, 'impl') and op.impl == 'postgresql' and hasattr(op, 'statement') and isinstance(op.statement, str):
                if op.statement.startswith('CREATE TYPE') and 'AS ENUM' in op.statement:
                    # 将CREATE TYPE语句修改为条件创建
                    enum_name = op.statement.split('CREATE TYPE ')[1].split(' AS ENUM')[0].strip()
                    op.statement = f"""
                    DO $$
                    BEGIN
                        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = '{enum_name}') THEN
                            {op.statement};
                        END IF;
                    END
                    $$;
                    """

# 修改PostgreSQL实现，使其在创建枚举类型时检查是否已存在
def patch_postgresql_impl():
    from sqlalchemy.dialects.postgresql.base import PGDDLCompiler
    from sqlalchemy.dialects.postgresql.named_types import CreateEnumType

    # 保存原始的visit_create_enum_type方法
    original_visit_create_enum_type = PGDDLCompiler.visit_create_enum_type

    # 定义新的visit_create_enum_type方法
    def new_visit_create_enum_type(self, create, **kw):
        # 获取枚举类型名称
        enum_name = create.element.name

        # 构建条件创建语句
        if USE_CHECKFIRST:
            return f"""
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = '{enum_name}') THEN
                    CREATE TYPE {enum_name} AS ENUM ({", ".join(f"'{v}'" for v in create.element.enums)});
                END IF;
            END
            $$;
            """
        else:
            return original_visit_create_enum_type(self, create, **kw)

    # 替换原始方法
    PGDDLCompiler.visit_create_enum_type = new_visit_create_enum_type

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    # 修补PostgreSQL实现
    if USE_CHECKFIRST:
        patch_postgresql_impl()

    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # 添加以下配置以支持SQLModel
        render_as_batch=True,
        **{"checkfirst": USE_CHECKFIRST} if USE_CHECKFIRST else {},
        compare_type=True,
        compare_server_default=True,
        # 添加钩子函数
        process_revision_directives=process_revision_directives if USE_CHECKFIRST else None,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        # 添加以下配置以支持SQLModel
        render_as_batch=True,
        **{"checkfirst": USE_CHECKFIRST} if USE_CHECKFIRST else {},
        compare_type=True,
        compare_server_default=True,
        # 添加钩子函数
        process_revision_directives=process_revision_directives if USE_CHECKFIRST else None,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # 修补PostgreSQL实现
    if USE_CHECKFIRST:
        patch_postgresql_impl()

    # 处理异步引擎
    config_section = config.get_section(config.config_ini_section)
    if config_section is None:
        config_section = {}

    connectable = AsyncEngine(
        engine_from_config(
            config_section,
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
            future=True,
        )
    )

    async with connectable.connect() as connection:
        # 如果启用了checkfirst模式，注册钩子函数来处理枚举类型创建
        if USE_CHECKFIRST:
            from sqlalchemy import event
            from sqlalchemy.schema import DDLElement

            # 注册钩子函数来处理DDL语句
            @event.listens_for(connection.sync_connection, "before_execute", retval=True)
            def before_execute(conn, clauseelement, multiparams, params, execution_options):
                # 处理字符串形式的SQL语句
                if isinstance(clauseelement, str) and clauseelement.startswith('CREATE TYPE') and 'AS ENUM' in clauseelement:
                    # 提取枚举类型名称
                    enum_name = clauseelement.split('CREATE TYPE ')[1].split(' AS ENUM')[0].strip()
                    # 修改为条件创建
                    new_statement = f"""
                    DO $$
                    BEGIN
                        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = '{enum_name}') THEN
                            {clauseelement};
                        END IF;
                    END
                    $$;
                    """
                    return new_statement, multiparams, params

                # 处理DDL对象
                if isinstance(clauseelement, DDLElement):
                    # 尝试安全地获取SQL字符串
                    try:
                        sql_str = str(clauseelement)
                        if sql_str.startswith('CREATE TYPE') and 'AS ENUM' in sql_str:
                            # 提取枚举类型名称
                            enum_name = sql_str.split('CREATE TYPE ')[1].split(' AS ENUM')[0].strip()
                            # 修改为条件创建
                            new_statement = f"""
                            DO $$
                            BEGIN
                                IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = '{enum_name}') THEN
                                    {sql_str};
                                END IF;
                            END
                            $$;
                            """
                            # 返回修改后的SQL语句
                            return new_statement, multiparams, params
                    except Exception:
                        # 如果无法转换为字符串，则忽略
                        pass

                # 对于其他类型的语句，保持不变
                return clauseelement, multiparams, params

        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
