from typing import Sequence

from src.common.base_service import BaseService
from src.common.tree_crud import TreeCRUD
from src.common.tree_model import TreeModel
from src.database.db_session import AuditAsyncSession


class TreeService(BaseService):
    """树形结构Service基类"""

    def __init__(self, crud: TreeCRUD, **kwargs):
        super().__init__(crud, **kwargs)
        self.tree_crud = crud

    async def get_tree(
        self,
        session: AuditAsyncSession,
        root_id: int | None = None,
        max_depth: int = -1
    ) -> Sequence[TreeModel]:
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