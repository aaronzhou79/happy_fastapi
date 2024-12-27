
from pydantic import BaseModel, ConfigDict


class DatabaseSchema(BaseModel):
    """基础Schema模型"""
    model_config = ConfigDict(use_enum_values=True, from_attributes=True)