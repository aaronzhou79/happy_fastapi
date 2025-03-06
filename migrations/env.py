import asyncio
import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlmodel import SQLModel

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


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # 添加以下配置以支持SQLModel
        render_as_batch=True,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        # 添加以下配置以支持SQLModel
        render_as_batch=True,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
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
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
