from typing import Sequence

from sqlalchemy import select, text

from src.common.base_crud import CreateModelType, CRUDBase, UpdateModelType
from src.common.tree_model import TreeModel
from src.core.exceptions import errors
from src.database.db_session import AuditAsyncSession


class TreeCRUD(CRUDBase[TreeModel, CreateModelType, UpdateModelType]):
    """树形结构CRUD基类"""

    async def _update_node_path(
        self,
        session: AuditAsyncSession,
        node: TreeModel,
        parent: TreeModel | None = None
    ) -> None:
        """更新节点路径"""
        if parent is None:
            node.path = f"/{node.id}/"  # type: ignore[attr-defined]
            node.level = 1
        else:
            node.path = f"{parent.path}{node.id}/"  # type: ignore[attr-defined]
            node.level = parent.level + 1

    async def _update_children_path(
        self,
        session: AuditAsyncSession,
        node: TreeModel
    ) -> None:
        """递归更新所有子节点的路径"""
        children = await node.get_children(session)
        for child in children:
            await self._update_node_path(session, child, node)
            session.add(child)
            await self._update_children_path(session, child)

    async def _check_cycle(
        self,
        session: AuditAsyncSession,
        node: TreeModel,
        new_parent_id: int
    ) -> bool:
        """检查是否会形成循环引用"""
        if node.id == new_parent_id:  # type: ignore[attr-defined]
            return True

        new_parent = await self.get_by_id(session, new_parent_id)
        if not new_parent:
            return False

        ancestors = await new_parent.get_ancestors(session)
        return any(a.id == node.id for a in ancestors)  # type: ignore[attr-defined]

    async def create(
        self,
        session: AuditAsyncSession,
        *,
        obj_in: CreateModelType | dict
    ) -> TreeModel:
        """创建节点"""
        if isinstance(obj_in, dict):
            create_data = obj_in
        else:
            create_data = obj_in.model_dump()

        parent_id = create_data.get("parent_id")
        if parent_id:
            parent = await self.get_by_id(session, parent_id)
            if not parent:
                raise errors.RequestError(data={"父节点不存在"})

        db_obj = await super().create(session, obj_in=create_data)

        # 更新路径
        if parent_id:
            await self._update_node_path(session, db_obj, parent)
        else:
            await self._update_node_path(session, db_obj)

        session.add(db_obj)
        await session.flush()

        return db_obj

    async def update(
        self,
        session: AuditAsyncSession,
        *,
        obj_in: UpdateModelType | dict
    ) -> TreeModel:
        """更新节点"""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        db_obj = await self.get_by_id(session, update_data["id"])
        if not db_obj:
            raise errors.RequestError(data={"节点不存在"})

        # 检查是否更新了父节点
        new_parent_id = update_data.get("parent_id")
        if new_parent_id is not None and new_parent_id != db_obj.parent_id:
            # 检查循环引用
            if await self._check_cycle(session, db_obj, new_parent_id):
                raise errors.RequestError(data={"不能将节点移动到其子节点下"})

            # 更新节点路径
            if new_parent_id:
                new_parent = await self.get_by_id(session, new_parent_id)
                if not new_parent:
                    raise errors.RequestError(data={"父节点不存在"})
                await self._update_node_path(session, db_obj, new_parent)
            else:
                await self._update_node_path(session, db_obj)

            # 更新所有子节点的路径
            await self._update_children_path(session, db_obj)

        return await super().update(session, obj_in=update_data)

    async def delete(self, session: AuditAsyncSession, id: int) -> None:
        """删除节点及其所有子节点"""
        node = await self.get_by_id(session, id)
        if not node:
            raise errors.RequestError(data={"节点不存在"})

        # 删除所有子节点
        stmt = select(self.model).where(
            text(f"path LIKE '{node.path}%'")
        )
        result = await session.execute(stmt)
        children = result.scalars().all()

        for child in children:
            await session.delete(child)

        await session.delete(node)
        await session.flush()

    async def get_tree(
        self,
        session: AuditAsyncSession,
        root_id: int | None = None,
        max_depth: int = -1
    ) -> Sequence[TreeModel]:
        """获取树形结构

        Args:
            session: 数据库会话
            root_id: 根节点ID,为None时获取所有根节点
            max_depth: 最大深度,-1表示不限制
        """
        if root_id:
            root = await self.get_by_id(session, root_id)
            if not root:
                return []
            stmt = select(self.model).where(
                text(f"path LIKE '{root.path}%'")
            )
            if max_depth > 0:
                stmt = stmt.where(text(f"level <= {root.level + max_depth}"))
        else:
            stmt = select(self.model).where(text("parent_id IS NULL"))
            if max_depth > 0:
                stmt = stmt.where(text(f"level <= {max_depth}"))

        stmt = stmt.order_by(text("path"), text("sort_order"))
        result = await session.execute(stmt)
        return result.scalars().all()

    async def move_node(
        self,
        session: AuditAsyncSession,
        node_id: int,
        new_parent_id: int | None
    ) -> TreeModel:
        """移动节点"""
        node = await self.get_by_id(session, node_id)
        if not node:
            raise errors.RequestError(data={"节点不存在"})

        if new_parent_id:
            if await self._check_cycle(session, node, new_parent_id):
                raise errors.RequestError(data={"不能将节点移动到其子节点下"})

            new_parent = await self.get_by_id(session, new_parent_id)
            if not new_parent:
                raise errors.RequestError(data={"目标父节点不存在"})

            await self._update_node_path(session, node, new_parent)
        else:
            await self._update_node_path(session, node)

        await self._update_children_path(session, node)

        session.add(node)
        await session.flush()

        return node