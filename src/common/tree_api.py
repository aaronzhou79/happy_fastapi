from typing import Any, Type

from fastapi import APIRouter, Body, Depends, Path, Query, Request
from typing_extensions import Annotated

from src.common.base_api import BaseAPI
from src.common.base_crud import CreateModelType, ModelType, UpdateModelType
from src.common.tree_service import TreeService
from src.core.responses.response_schema import ResponseModel, response_base
from src.core.security.auth_security import DependsJwtAuth
from src.core.security.permission import RequestPermission
from src.database.db_session import CurrentSession, async_audit_session, async_session


class TreeAPI(BaseAPI[ModelType, CreateModelType, UpdateModelType]):
    """树形结构API基类

    提供树形结构的基本操作,包括:
    - 获取树形结构
    - 移动节点
    - 批量移动节点
    - 复制子树
    - 获取同级节点
    - 获取祖先节点

    Args:
        model: 数据模型类
        service: 树形结构服务类实例
        **kwargs: 其他参数
    """

    def __init__(
        self,
        module_name: str,
        model: Type[ModelType],
        service: TreeService,
        **kwargs: Any
    ) -> None:
        super().__init__(module_name, model, service, **kwargs)
        self.module_name = module_name
        self.tree_router = APIRouter()
        self.service: TreeService = service
        self._register_tree_routes()
        self.router.include_router(self.tree_router)

    def _register_tree_routes(self) -> None:
        """注册树形结构相关路由"""
        self._register_tree_query_routes()
        self._register_tree_mutation_routes()

    def _register_tree_query_routes(self) -> None:
        """注册树形结构查询路由"""
        self._register_get_tree_route()
        self._register_get_siblings_route()
        self._register_get_ancestors_route()

    def _register_tree_mutation_routes(self) -> None:
        """注册树形结构修改路由"""
        self._register_move_node_route()
        self._register_bulk_move_nodes_route()
        self._register_copy_subtree_route()

    def _register_get_tree_route(self) -> None:
        """注册获取树形结构路由"""
        @self.tree_router.get(
            "/tree",
            summary=f"获取{self.model.__name__}树形结构",
            dependencies=[
                DependsJwtAuth,
                # Depends(RequestPermission(f"{self.perm_prefix}:tree"))
            ]
        )
        async def get_tree(
            session: CurrentSession,
            root_id: Annotated[int | None, Query(ge=1, description="根节点ID")] = None,
            max_depth: Annotated[int, Query(ge=-1, le=100, description="最大深度,-1表示不限制")] = -1
        ) -> ResponseModel:
            try:
                items = await self.service.get_tree(
                    session=session,
                    root_id=root_id,
                    max_depth=max_depth
                )
                return response_base.success(data=items)
            except Exception as e:
                return response_base.fail(data=str(e))

    def _register_get_siblings_route(self) -> None:
        """注册获取同级节点路由"""
        @self.tree_router.get(
            "/siblings/{node_id}",
            summary=f"获取{self.model.__name__}同级节点",
            dependencies=[
                DependsJwtAuth,
                # Depends(RequestPermission(f"{self.perm_prefix}:siblings"))
            ]
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

    def _register_get_ancestors_route(self) -> None:
        """注册获取祖先节点路由"""
        @self.tree_router.get(
            "/ancestors/{node_id}",
            summary=f"获取{self.model.__name__}祖先节点",
            dependencies=[
                DependsJwtAuth,
                # Depends(RequestPermission(f"{self.perm_prefix}:ancestors"))
            ]
        )
        async def get_ancestors(
            session: CurrentSession,
            node_id: Annotated[int, Path(..., description="节点ID")],
            include_self: Annotated[bool, Query(description="是否包含自身")] = False
        ) -> ResponseModel:
            items = await self.service.get_ancestors(session=session, node_id=node_id, include_self=include_self)
            return response_base.success(data=items)

    def _register_move_node_route(self) -> None:
        """注册移动节点路由"""
        @self.tree_router.put(
            "/move",
            summary=f"移动{self.model.__name__}节点",
            dependencies=[
                DependsJwtAuth,
                Depends(RequestPermission(f"{self.perm_prefix}:move"))
            ]
        )
        async def move_node(
            request: Request,
            node_id: Annotated[int, Body(ge=1, description="要移动的节点ID")],
            new_parent_id: Annotated[int | None, Body(ge=1, description="新的父节点ID")]
        ) -> ResponseModel:
            async with async_audit_session(async_session(), request) as session:
                result = await self.service.move_node(
                    session=session,
                    node_id=node_id,
                    new_parent_id=new_parent_id
                )
                data = result.model_dump()
            return response_base.success(data=data)

    def _register_bulk_move_nodes_route(self) -> None:
        """注册批量移动节点路由"""
        @self.tree_router.put(
            "/bulk_move",
            summary=f"批量移动{self.model.__name__}节点",
            dependencies=[
                DependsJwtAuth,
                Depends(RequestPermission(f"{self.perm_prefix}:bulk_move"))
            ]
        )
        async def bulk_move_nodes(
            request: Request,
            node_ids: Annotated[list[int], Body(..., min_length=1, max_length=100, description="要移动的节点ID列表")],
            new_parent_id: Annotated[int | None, Body(..., description="新的父节点ID")]
        ) -> ResponseModel:
            # 验证节点ID不重复
            if len(set(node_ids)) != len(node_ids):
                return response_base.fail(data="节点ID不能重复")
            async with async_audit_session(async_session(), request) as session:
                results = await self.service.bulk_move_nodes(
                    session=session,
                    node_ids=node_ids,
                    new_parent_id=new_parent_id
                )
                data = [item.model_dump() for item in results]
            return response_base.success(data=data)

    def _register_copy_subtree_route(self) -> None:
        """注册复制子树路由"""
        @self.tree_router.post(
            "/copy",
            summary=f"复制{self.model.__name__}子树",
            dependencies=[
                DependsJwtAuth,
                Depends(RequestPermission(f"{self.perm_prefix}:copy"))
            ]
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
