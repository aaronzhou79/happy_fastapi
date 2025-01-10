from typing import Sequence

from src.common.base_service import BaseService
from src.common.enums import HookTypeEnum
from src.common.tree_crud import TreeCRUD
from src.common.tree_model import TreeModel
from src.core.exceptions import errors
from src.database.db_session import AuditAsyncSession


class TreeService(BaseService, TreeCRUD):
    """树形结构Service基类"""

    def __init__(self, crud: TreeCRUD, **kwargs):
        super().__init__(crud, **kwargs)
        self.tree_crud: TreeCRUD = crud
        self.add_hook(HookTypeEnum.before_delete, self.before_delete)

    async def before_delete(self, session: AuditAsyncSession, db_obj: TreeModel) -> None:
        """删除节点前钩子"""
        if await db_obj.has_children(session):
            raise errors.RequestError(data={"节点存在子节点，无法删除"})

    async def get_tree(
        self,
        session: AuditAsyncSession,
        root_id: int | None = None,
        max_depth: int = -1
    ) -> Sequence[dict]:
        """获取树形结构"""
        return await self.tree_crud.get_tree(
            session,
            root_id=root_id,
            max_depth=max_depth
        )

    async def move_node(
        self,
        session: AuditAsyncSession,
        node_id: int,
        new_parent_id: int | None
    ) -> TreeModel:
        """移动节点"""
        return await self.tree_crud.move_node(
            session,
            node_id=node_id,
            new_parent_id=new_parent_id
        )

    async def bulk_move_nodes(
        self,
        session: AuditAsyncSession,
        node_ids: Sequence[int],
        new_parent_id: int | None
    ) -> Sequence[TreeModel]:
        """批量移动节点"""
        return await self.tree_crud.bulk_move_nodes(
            session,
            node_ids=node_ids,
            new_parent_id=new_parent_id
        )

    async def copy_subtree(
        self,
        session: AuditAsyncSession,
        node_id: int,
        new_parent_id: int | None
    ) -> TreeModel:
        """复制子树"""
        return await self.tree_crud.copy_subtree(
            session,
            node_id=node_id,
            new_parent_id=new_parent_id
        )

    async def get_siblings(
        self,
        session: AuditAsyncSession,
        node_id: int,
        include_self: bool = False
    ) -> Sequence[TreeModel]:
        """获取同级节点"""
        return await self.tree_crud.get_siblings(
            session,
            node_id=node_id,
            include_self=include_self
        )

    async def get_ancestors(
        self,
        session: AuditAsyncSession,
        node_id: int,
        include_self: bool = False
    ) -> Sequence[dict]:
        """获取祖先节点"""
        return await self.tree_crud.get_ancestors(
            session,
            node_id=node_id,
            include_self=include_self
        )
