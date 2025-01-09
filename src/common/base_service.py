from typing import Annotated, Dict, Generic, Sequence

from sqlmodel import Field

from src.common.base_crud import CreateModelType, CRUDBase, ModelType, UpdateModelType
from src.common.query_fields import QueryOptions
from src.database.db_session import AuditAsyncSession


class BaseService(Generic[ModelType, CreateModelType, UpdateModelType]):
    """
    基础服务类
    """
    def __init__(self, crud: CRUDBase[ModelType, CreateModelType, UpdateModelType]):
        # 初始化时接收一个CRUDBase实例，用于执行具体的数据库操作
        self.crud = crud

    async def get_by_id(self, session: AuditAsyncSession, id: int) -> ModelType | None:
        """获取单个数据"""
        return await self.crud.get_by_id(session=session, id=id)

    async def get_by_fields(self, session: AuditAsyncSession, **kwargs) -> Sequence[ModelType]:
        """根据字段获取对象"""
        return await self.crud.get_by_fields(session=session, **kwargs)

    async def create(
        self,
        session: AuditAsyncSession,
        obj_in: Annotated[CreateModelType, Field(..., description="创建模型")]
    ) -> ModelType:
        """创建对象"""
        return await self.crud.create(session=session, obj_in=obj_in)

    async def bulk_create(
        self,
        session: AuditAsyncSession,
        objects: Sequence[Dict | CreateModelType],
        *,
        batch_size: int = 1000
    ) -> Sequence[ModelType]:
        """批量创建对象"""
        return await self.crud.bulk_create(session=session, objects=objects, batch_size=batch_size)

    async def update(self, session: AuditAsyncSession, obj_in: UpdateModelType) -> ModelType:
        """更新对象"""
        return await self.crud.update(session=session, obj_in=obj_in)

    async def delete(self, session: AuditAsyncSession, id: int) -> None:
        """删除对象"""
        return await self.crud.delete(session=session, id=id)

    async def bulk_delete(self, session: AuditAsyncSession, ids: Sequence[int]) -> list[int]:
        """批量删除对象"""
        return await self.crud.bulk_delete(session=session, ids=ids)

    async def get_by_options(self, session: AuditAsyncSession, options: QueryOptions) -> tuple[int, Sequence[ModelType]]:
        """根据查询选项获取对象列表和总数"""
        return await self.crud.get_by_options(session=session, options=options)
