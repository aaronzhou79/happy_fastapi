from typing import Sequence, TypedDict

from sqlmodel import Field, SQLModel, asc, select

from src.database.db_session import AuditAsyncSession


class TreeModel(SQLModel):
    """树形结构基础模型"""
    __abstract__ = True

    parent_id: int | None = Field(
        default=None,
        index=True,
        sa_column_kwargs={"comment": "父节点ID"}
    )
    tree_path: str = Field(
        default="/",
        index=True,
        description="Materialized path",
        sa_column_kwargs={"comment": "节点路径"}
    )
    level: int = Field(
        default=1,
        sa_column_kwargs={"comment": "节点层级"}
    )
    sort_order: int = Field(
        default=0,
        sa_column_kwargs={"comment": "排序号"}
    )

    async def has_children(self, session: AuditAsyncSession) -> bool:
        """是否有子节点"""
        children = await self.get_children(session)
        return len(children) > 0

    async def get_siblings(
        self,
        session: AuditAsyncSession,
        include_self: bool = False
    ) -> Sequence["TreeModel"]:
        """获取同级节点"""
        stmt = select(self.__class__).where(
            self.__class__.parent_id == self.parent_id,  # type: ignore
        ).order_by(asc(self.__class__.sort_order))
        if not include_self:
            stmt = stmt.where(self.__class__.id != self.id)  # type: ignore
        result = await session.execute(stmt)
        return result.scalars().all()

    async def get_children(
        self,
        session: AuditAsyncSession,
        include_self: bool = False
    ) -> Sequence["TreeModel"]:
        """获取子节点"""
        stmt = select(self.__class__).where(
            self.__class__.parent_id == self.id   # type: ignore
        ).order_by(asc(self.__class__.sort_order))
        if not include_self:
            stmt = stmt.where(self.__class__.id != self.id)  # type: ignore
        result = await session.execute(stmt)
        return result.scalars().all()

    async def get_ancestors(
        self,
        session: AuditAsyncSession,
        include_self: bool = False
    ) -> Sequence["TreeModel"]:
        """获取祖先节点"""
        if not self.tree_path or self.tree_path == "/":
            return []

        # 从path中获取所有祖先ID
        ancestor_ids = [
            int(id_) for id_ in self.tree_path.strip("/").split("/") if id_
        ]

        if not ancestor_ids:
            return []

        stmt = select(self.__class__).where(
            self.__class__.id.in_(ancestor_ids)  # type: ignore
        ).order_by(asc(self.__class__.level))
        if not include_self:
            stmt = stmt.where(self.__class__.id != self.id)  # type: ignore
        result = await session.execute(stmt)
        return result.scalars().all()
