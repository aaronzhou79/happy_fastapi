import asyncio

from enum import Enum
from typing import Any, Callable, Generic, Sequence, Type

from aiocache import RedisCache, cached
from aiocache.serializers import PickleSerializer
from fastapi import APIRouter, Body, Depends, Path, Query, Request
from typing_extensions import Annotated

from src.common.base_crud import CreateModelType, ModelType, UpdateModelType
from src.common.base_service import BaseService
from src.common.query_fields import QueryOptions
from src.core.conf import settings
from src.core.responses.response_schema import ResponseModel, response_base
from src.core.security.auth_security import DependsJwtAuth
from src.core.security.permission import RequestPermission
from src.database.cache.cache_conf import generate_cache_key, get_redis_settings
from src.database.cache.cache_plugins import CacheLogPlugin
from src.database.db_redis import redis_client
from src.database.db_session import CurrentSession, async_audit_session, async_session
from src.database.redis_utils import RedisManager


class BaseAPI(Generic[ModelType, CreateModelType, UpdateModelType]):
    """基础 API 生成器"""

    def __init__(
        self,
        module_name: str,
        model: Type[ModelType],
        service: BaseService[ModelType, CreateModelType, UpdateModelType],
        create_schema: Type[CreateModelType] | None = None,
        update_schema: Type[UpdateModelType] | None = None,
        base_schema: Type[ModelType] | Any = Any,
        with_schema: Type[ModelType] | Any = Any,
        prefix: str = "",
        tags: list[str | Enum] | None = None,
        gen_create: bool = True,
        gen_bulk_create: bool = False,
        gen_update: bool = True,
        gen_delete: bool = True,
        gen_bulk_delete: bool = False,
        gen_query: bool = True,
        cache_ttl: int = 3600 if settings.APP_ENV == "prod" else 60,
        **kwargs: Any,
    ) -> None:
        self.module_name = module_name
        self.model = model
        self.service = service
        self.create_schema = create_schema
        self.update_schema = update_schema
        self.base_schema = base_schema
        self.with_schema = with_schema
        self.prefix = prefix
        self.tags = tags
        self.gen_create = gen_create
        self.gen_bulk_create = gen_bulk_create
        self.gen_update = gen_update
        self.gen_delete = gen_delete
        self.gen_bulk_delete = gen_bulk_delete
        self.gen_query = gen_query
        self.cache_ttl = cache_ttl
        self.cache_prefix = f"{self.module_name}.{self.model.__name__}"
        self.perm_prefix = f"{self.module_name}:{self.model.__name__.lower()}"
        self.redis_manager = RedisManager(prefix=self.cache_prefix)
        self.router = APIRouter(
            prefix=self.prefix,
            tags=self.tags or [],
        )
        self.summary_suffix = f"{str(self.router.tags[0]).split('/')[-1]}"
        self._register_routes()

    def _register_routes(self) -> None:
        """注册所有路由"""
        if self.gen_create:
            self._register_create()
        if self.gen_bulk_create:
            self._register_bulk_create()
        if self.gen_update:
            self._register_update()
        if self.gen_delete:
            self._register_delete()
        if self.gen_bulk_delete:
            self._register_bulk_delete()
        if self.gen_query:
            self._register_query()
        # 基础查询接口总是生成
        self._register_get()

    def _register_create(self) -> None:
        """注册创建接口"""
        @self.router.post(
            "/create",
            summary=f"创建 {self.summary_suffix} {self.perm_prefix}:create",
            dependencies=[
                DependsJwtAuth,
                Depends(RequestPermission(f"{self.perm_prefix}:create"))
            ]
        )
        async def create(
            request: Request,
            obj_in: Annotated[self.create_schema, Body(..., description="创建模型")]  # type: ignore
        ) -> ResponseModel[self.model]:  # type: ignore
            async with async_audit_session(async_session(), request) as session:
                result = await self.service.create(session=session, obj_in=obj_in)
                data = await result.to_api_dict()  # type: ignore
            return response_base.success(data=data)

    def _register_bulk_create(self) -> None:
        """注册批量创建接口"""
        @self.router.post(
            "/bulk_create",
            summary=f"批量创建 {self.summary_suffix} {self.perm_prefix}:bulk_create",
            dependencies=[
                DependsJwtAuth,
                Depends(RequestPermission(f"{self.perm_prefix}:bulk_create"))
            ]
        )
        async def bulk_create(
            request: Request,
            datas: Annotated[Sequence[self.create_schema], Body(..., description="批量创建模型")]  # type: ignore
        ) -> ResponseModel[Sequence[self.base_schema]]:  # type: ignore
            async with async_audit_session(async_session(), request) as session:
                result = await self.service.bulk_create(
                    session=session, objects=datas
                )
            return response_base.success(data=result)

    def _register_update(self) -> None:
        """注册更新接口"""
        @self.router.put(
            "/update",
            summary=f"更新 {self.summary_suffix} {self.perm_prefix}:update",
            dependencies=[
                DependsJwtAuth,
                Depends(RequestPermission(f"{self.perm_prefix}:update"))
            ]
        )
        async def update(
            request: Request,
            obj_in: Annotated[self.update_schema, Body(..., description="更新模型")]  # type: ignore
        ) -> ResponseModel[self.base_schema]:  # type: ignore
            if not hasattr(obj_in, 'id'):
                return response_base.fail(data="请求参数错误，ID不存在！")
            key = generate_cache_key(self.cache_prefix, f"id_{getattr(obj_in, 'id')}")
            await redis_client.delete_prefix(key)

            async with async_audit_session(async_session(), request) as session:
                result = await self.service.update(session=session, obj_in=obj_in)

            # 延迟50ms后再次删除缓存，防止并发删除缓存时出现缓存不一致
            await redis_client.delete_prefix(key)
            await asyncio.sleep(0.05)

            return response_base.success(data=result)

    def _register_delete(self) -> None:
        """注册删除接口"""
        @self.router.delete(
            "/delete/{id}",
            summary=f"删除 {self.summary_suffix} {self.perm_prefix}:delete",
            dependencies=[
                DependsJwtAuth,
                Depends(RequestPermission(f"{self.perm_prefix}:delete"))
            ]
        )
        async def delete(
            request: Request,
            *,
            id: Annotated[int, Path(..., description="要删除的id")]
        ) -> ResponseModel[str]:
            key = generate_cache_key(self.cache_prefix, f"id_{id}")
            await redis_client.delete_prefix(key)

            async with async_audit_session(async_session(), request) as session:
                await self.service.delete(session=session, id=id)

            # 延迟50ms后再次删除缓存，防止并发删除缓存时出现缓存不一致
            await asyncio.sleep(0.05)
            await redis_client.delete_prefix(key)

            return response_base.success(data=f"{self.model.__name__}删除成功")

    def _register_bulk_delete(self) -> None:
        """注册批量删除接口"""
        @self.router.delete(
            "/bulk_delete",
            summary=f"批量删除 {self.summary_suffix} {self.perm_prefix}:bulk_delete",
            dependencies=[
                DependsJwtAuth,
                Depends(RequestPermission(f"{self.perm_prefix}:bulk_delete"))
            ]
        )
        async def bulk_delete(
            request: Request,
            *,
            ids: Annotated[list[int], Query(..., description="要删除的id列表")]
        ) -> ResponseModel[str]:
            for id in ids:
                key = generate_cache_key(self.cache_prefix, f"id_{id}")
                await redis_client.delete_prefix(key)

            async with async_audit_session(async_session(), request) as session:
                unhandled_ids = await self.service.bulk_delete(session=session, ids=ids)
            # 延迟50ms后再次删除缓存
            await asyncio.sleep(0.05)
            for id in ids:
                key = generate_cache_key(self.cache_prefix, f"id_{id}")
                await redis_client.delete_prefix(key)
            if unhandled_ids:
                return response_base.success(data=f"未成功删除的ID: {unhandled_ids}")
            return response_base.success(data="批量删除数据成功")

    def _register_get(self) -> None:
        """注册获取单个接口"""
        @self.router.get(
            "/get",
            summary=f"获取 {self.summary_suffix}",
            dependencies=[
                DependsJwtAuth,
                # Depends(RequestPermission(f"{self.perm_prefix}:get"))
            ]
        )
        @cached(
            ttl=self.cache_ttl,
            cache=RedisCache,
            serializer=PickleSerializer(),
            plugins=[CacheLogPlugin()],
            key_builder=lambda *args, **kwargs: generate_cache_key(
                f"{self.cache_prefix}:{self.model.__name__}",
                f"id_{kwargs.get('id')}",
                f"depth_{kwargs.get('max_depth')}"
            ),
            **get_redis_settings()
        )
        async def get(
            session: CurrentSession,
            *,
            id: int,
            max_depth: Annotated[int, Query(le=3, description="关联数据的最大深度")] = 2
        ) -> ResponseModel:  # type: ignore
            item = await self.service.get_by_id(session=session, id=id)
            if not item:
                return response_base.fail(data=f"{self.model.__name__}不存在")
            data = await item.to_api_dict(max_depth=max_depth)  # type: ignore
            return response_base.success(data=data)

    def _register_query(self) -> None:
        """注册查询接口"""
        @self.router.post(
            "/query",
            summary=f"查询 {self.summary_suffix}",
            dependencies=[
                DependsJwtAuth,
                # Depends(RequestPermission(f"{self.perm_prefix}:query"))
            ]
        )
        async def query(
            session: CurrentSession,
            options: QueryOptions,
        ) -> ResponseModel:  # type: ignore
            total, items = await self.service.get_by_options(session=session, options=options)
            data = [await item.to_api_dict() for item in items]  # type: ignore
            return response_base.success(data={"total": total, "items": data})

    def include_router(self, router: APIRouter) -> None:
        """将路由包含到其他路由器中"""
        router.include_router(self.router)

    def add_api_route(
        self,
        path: str,
        endpoint: Callable,
        **kwargs: Any
    ) -> None:
        """添加自定义路由"""
        self.router.add_api_route(path, endpoint, **kwargs)

    def extend_router(self, router: APIRouter) -> None:
        """扩展现有路由"""
        self.router.include_router(router)