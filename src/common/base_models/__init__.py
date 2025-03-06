from sqlmodel import SQLModel

from src.common.logger import log


async def create_table() -> None:
    """创建表"""
    try:
        from src.database.db_session import async_engine

        async with async_engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
    except Exception as e:
        log.error("❌ 数据库连接失败: {}", e)
        raise e from e
