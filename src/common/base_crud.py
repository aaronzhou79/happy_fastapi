from typing import Generic

from src.common.base_api import ModelType


class BaseCRUD(Generic[ModelType]):
    """
    基础CRUD类
    """
    def __init__(
        self,
        model: ModelType,
    ):
        self.model = model
