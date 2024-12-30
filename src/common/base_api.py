from enum import Enum
from typing import Any, Callable, Generic, Type, TypeVar

from fastapi import APIRouter, Query, Request
from fastapi.params import Depends
from typing_extensions import Annotated

from src.common.data_model.base_model import DatabaseModel
from src.common.data_model.query_fields import QueryOptions
from src.common.data_model.schema_base import SchemaBase
from src.core.responses.response import response_base
from src.database.db_session import async_audit_session, async_session

# 泛型类型变量
ModelType = TypeVar("ModelType", bound=DatabaseModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=SchemaBase)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=SchemaBase)


class BaseAPI(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """基础 API 生成器"""

    def __init__(
        self,
        model: Type[ModelType],
        create_schema: Type[CreateSchemaType] | None = None,
        update_schema: Type[UpdateSchemaType] | None = None,
        prefix: str = "",
        tags: list[str | Enum] | None = None,
        dependencies: list[Depends] | None = None,
        gen_create: bool = True,
        gen_update: bool = True,
        gen_delete: bool = True,
        gen_query: bool = True,
        cache_ttl: int | None = None,
        **kwargs: Any
    ):
        self.model = model
        self.create_schema = create_schema
        self.update_schema = update_schema
        self.prefix = prefix
        self.tags = tags
        self.dependencies = dependencies or []
        self.gen_create = gen_create
        self.gen_update = gen_update
        self.gen_delete = gen_delete
        self.gen_query = gen_query
        self.cache_ttl = cache_ttl

        self.router = APIRouter(
            prefix=self.prefix,
            tags=self.tags or [],
            dependencies=self.dependencies or []
        )
        self._register_routes()

    def _register_routes(self):
        """注册所有路由"""
        if self.gen_create:
            self._register_create()
        if self.gen_update:
            self._register_update()
        if self.gen_delete:
            self._register_delete()
        if self.gen_query:
            self._register_query()
        # 基础查询接口总是生成
        self._register_get()
        self._register_get_all()

    def _register_create(self):
        """注册创建接口"""
        @self.router.post(
            "/create",
            summary=f"创建{self.model.__name__}"
        )
        async def create(
            request: Request,
            data: self.create_schema  # type: ignore
        ):
            async with async_audit_session(async_session(), request) as session:
                result = await self.model.create(session=session, **data.model_dump())
            return response_base.success(data=result)

    def _register_update(self):
        """注册更新接口"""
        @self.router.put(
            "/update/{id}",
            summary=f"更新{self.model.__name__}"
        )
        async def update(
            request: Request,
            id: int,
            data: self.update_schema  # type: ignore
        ):
            async with async_audit_session(async_session(), request) as session:
                result = await self.model.update(session=session, pk=id, **data.model_dump())
            return response_base.success(data=result)

    def _register_delete(self):
        """注册删除接口"""
        @self.router.delete(
            "/delete/{id}",
            summary=f"删除{self.model.__name__}"
        )
        async def delete(
            request: Request,
            id: int
        ):
            async with async_audit_session(async_session(), request) as session:
                await self.model.delete(session=session, pk=id)
            return response_base.success(data=f"{self.model.__name__}删除成功")

    def _register_get(self):
        """注册获取单个接口"""
        @self.router.get(
            "/get/{id}",
            summary=f"获取{self.model.__name__}"
        )
        async def get(
            id: int,
            max_depth: Annotated[int, Query(description="关联数据的最大深度")] = 2
        ):
            item = await self.model.get_by_id(id)
            if not item:
                return response_base.fail(data=f"{self.model.__name__}不存在")
            data = await item.to_api_dict(max_depth=max_depth)
            return response_base.success(data=data)

    def _register_query(self):
        """注册查询接口"""
        @self.router.post(
            "/query",
            summary=f"查询{self.model.__name__}"
        )
        async def query(
            options: QueryOptions
        ):
            items, total = await self.model.query_with_count(options=options)
            return response_base.success(data={"total": total, "items": items})

    def _register_get_all(self):
        """注册获取所有接口"""
        @self.router.get(
            "/get_all",
            summary=f"获取所有{self.model.__name__}"
        )
        async def get_all(
            include_deleted: Annotated[bool, Query(description="是否包含已删除数据")] = False
        ):
            items = await self.model.get_all(include_deleted=include_deleted)
            return response_base.success(data={"items": items})

    def include_router(self, router: APIRouter):
        """将路由包含到其他路由器中"""
        router.include_router(self.router)

    def add_api_route(
        self,
        path: str,
        endpoint: Callable,
        **kwargs: Any
    ):
        """添加自定义路由"""
        self.router.add_api_route(path, endpoint, **kwargs)

    def extend_router(self, router: APIRouter):
        """扩展现有路由"""
        self.router.include_router(router)