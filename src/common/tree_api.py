from typing import Any, Type

from fastapi import APIRouter, Body, Path, Query, Request
from typing_extensions import Annotated

from src.common.base_api import BaseAPI
from src.common.base_crud import CreateModelType, ModelType, UpdateModelType
from src.common.tree_service import TreeService
from src.core.responses.response_schema import ResponseModel, response_base
from src.database.db_session import CurrentSession, async_audit_session, async_session


class TreeAPI(BaseAPI[ModelType, CreateModelType, UpdateModelType]):
    """树形结构API基类"""

    def __init__(
        self,
        model: Type[ModelType],
        service: TreeService,
        **kwargs: Any
    ) -> None:
        super().__init__(model, service, **kwargs)
        self.tree_router = APIRouter()
        self.service: TreeService = service
        self._register_tree_routes()
        self.router.include_router(self.tree_router)

    def _register_tree_routes(self) -> None:
        """注册树形结构相关路由"""
        @self.tree_router.get(
            "/tree",
            summary=f"获取{self.model.__name__}树形结构"
        )
        async def get_tree(
            session: CurrentSession,
            root_id: Annotated[int | None, Query(description="根节点ID")] = None,
            max_depth: Annotated[int, Query(ge=-1, description="最大深度,-1表示不限制")] = -1
        ) -> ResponseModel:
            items = await self.service.get_tree(
                session=session,
                root_id=root_id,
                max_depth=max_depth
            )
            return response_base.success(data=items)

        @self.tree_router.put(
            "/move",
            summary=f"移动{self.model.__name__}节点"
        )
        async def move_node(
            request: Request,
            node_id: Annotated[int, Body(..., description="要移动的节点ID")],
            new_parent_id: Annotated[int | None, Body(..., description="新的父节点ID")]
        ) -> ResponseModel:
            async with async_audit_session(async_session(), request) as session:
                result = await self.service.move_node(
                    session=session,
                    node_id=node_id,
                    new_parent_id=new_parent_id
                )
                data = result.model_dump()
            return response_base.success(data=data)

        @self.tree_router.put(
            "/bulk_move",
            summary=f"批量移动{self.model.__name__}节点"
        )
        async def bulk_move_nodes(
            request: Request,
            node_ids: Annotated[list[int], Body(..., description="要移动的节点ID列表")],
            new_parent_id: Annotated[int | None, Body(..., description="新的父节点ID")]
        ) -> ResponseModel:
            async with async_audit_session(async_session(), request) as session:
                results = await self.service.bulk_move_nodes(
                    session=session,
                    node_ids=node_ids,
                    new_parent_id=new_parent_id
                )
                data = [item.model_dump() for item in results]
            return response_base.success(data=data)

        @self.tree_router.post(
            "/copy",
            summary=f"复制{self.model.__name__}子树"
        )
        async def copy_subtree(
            request: Request,
            node_id: Annotated[int, Body(..., description="要复制的节点ID")],
            new_parent_id: Annotated[int | None, Body(..., description="新的父节点ID")]
        ) -> ResponseModel:
            async with async_audit_session(async_session(), request) as session:
                result = await self.service.copy_subtree(
                    session=session,
                    node_id=node_id,
                    new_parent_id=new_parent_id
                )
                data = result.model_dump()
            return response_base.success(data=data)

        @self.tree_router.get(
            "/siblings/{node_id}",
            summary=f"获取{self.model.__name__}同级节点"
        )
        async def get_siblings(
            session: CurrentSession,
            node_id: Annotated[int, Path(..., description="节点ID")],
            include_self: Annotated[bool, Query(description="是否包含自身")] = False
        ) -> ResponseModel:
            items = await self.service.get_siblings(
                session=session,
                node_id=node_id,
                include_self=include_self
            )
            return response_base.success(data=items)

        @self.tree_router.get(
            "/ancestors/{node_id}",
            summary=f"获取{self.model.__name__}祖先节点"
        )
        async def get_ancestors(
            session: CurrentSession,
            node_id: Annotated[int, Path(..., description="节点ID")],
            include_self: Annotated[bool, Query(description="是否包含自身")] = False
        ) -> ResponseModel:
            items = await self.service.get_ancestors(session=session, node_id=node_id, include_self=include_self)
            return response_base.success(data=items)
