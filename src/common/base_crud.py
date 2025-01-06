from typing import Generic

from src.common.base_api import CreateSchemaType, ModelType, UpdateSchemaType


class BaseCRUD(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    基础CRUD类
    """
    def __init__(
        self,
        model: ModelType,
        create_schema: CreateSchemaType,
        update_schema: UpdateSchemaType,
    ):
        self.model = model
        self.create_schema = create_schema
        self.update_schema = update_schema
