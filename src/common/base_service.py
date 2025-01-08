from typing import Generic

from src.common.base_api import CreateSchemaType, ModelType, UpdateSchemaType
from src.common.base_crud import BaseCRUD


class BaseService(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    基础服务类
    """
    def __init__(self, crud: BaseCRUD[ModelType, CreateSchemaType, UpdateSchemaType]):
        # 初始化时接收一个BaseCRUD实例，用于执行具体的数据库操作
        self.crud = crud