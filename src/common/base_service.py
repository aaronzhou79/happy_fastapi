from typing import Annotated, Any, Callable, Dict, Generic, Sequence

from sqlmodel import Field

from src.common.base_crud import CreateModelType, CRUDBase, ModelType, UpdateModelType
from src.common.enums import HookTypeEnum
from src.common.query_fields import QueryOptions
from src.database.db_session import AuditAsyncSession


class BaseService(Generic[ModelType, CreateModelType, UpdateModelType]):
    """
    基础服务类
    """
    def __init__(
        self,
        crud: CRUDBase[ModelType, CreateModelType, UpdateModelType],
        hooks: Dict[str, list[Callable[..., Any]]] | None = None
    ):
        self.crud = crud
        # 注册钩子
        if hooks:
            for hook_type, hook_funcs in hooks.items():
                for hook_func in hook_funcs:
                    self.crud.add_hook(HookTypeEnum(hook_type), hook_func)

    def add_hook(self, hook_type: HookTypeEnum, hook_func: Callable[..., Any]) -> None:
        """添加钩子函数

        Args:
            hook_type: 钩子类型,如 'before_create', 'after_update' 等
            hook_func: 钩子函数
        """
        self.crud.add_hook(hook_type, hook_func)

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
