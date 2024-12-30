from enum import Enum
from typing import Generic, Type, TypeVar

from fastapi import APIRouter, Query, Request
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
ListSchemaType = TypeVar("ListSchemaType", bound=SchemaBase)


class BaseAPI(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """基础 API 生成器"""

    def __init__(
        self,
        model: Type[ModelType],
        create_schema: Type[CreateSchemaType] | None = None,
        update_schema: Type[UpdateSchemaType] | None = None,
        prefix: str = "",
        tags: list[str | Enum] | None = None,
        gen_delete: bool = True,
    ):
        self.model = model
        self.create_schema = create_schema
        self.update_schema = update_schema
        self.router = APIRouter(prefix=prefix, tags=tags)
        self.gen_delete = gen_delete
        self._register_routes()

    def _register_routes(self):
        """注册所有路由"""

        if self.create_schema:
            @self.router.post("/create")
            async def create(
                request: Request,
                data: self.create_schema  # type: ignore
            ):
                async with async_audit_session(async_session(), request) as session:
                    result = await self.model.create(session=session, **data.model_dump())
                return response_base.success(data=result)

        if self.update_schema:
            @self.router.put("/update/{id}")
            async def update(
                request: Request,
                id: int,
                data: self.update_schema  # type: ignore
            ):
                async with async_audit_session(async_session(), request) as session:
                    result = await self.model.update(session=session, pk=id, **data.model_dump())
                return response_base.success(data=result)

        if self.gen_delete:
            @self.router.delete("/delete/{id}")
            async def delete(
                request: Request,
                id: int
            ):
                async with async_audit_session(async_session(), request) as session:
                    await self.model.delete(session=session, pk=id)
                return response_base.success(data=f"{self.model.__name__}删除成功")

        @self.router.get("/get/{id}")
        async def get(
            id: int,
            max_depth: int = 2
        ):
            item = await self.model.get_by_id(id)
            if not item:
                return response_base.fail(data=f"{self.model.__name__}不存在")
            data = await item.to_api_dict(max_depth=max_depth)
            return response_base.success(data=data)

        @self.router.post("/query")
        async def query(
            options: QueryOptions
        ):
            items, total = await self.model.query_with_count(options=options)
            return response_base.success(data={"total": total, "items": items})

        @self.router.get("/get_all")
        async def get_all(
            include_deleted: Annotated[bool, Query(...)] = False
        ):
            items = await self.model.get_all(include_deleted=include_deleted)
            data = [await item.to_api_dict() for item in items]
            return response_base.success(data=data)
