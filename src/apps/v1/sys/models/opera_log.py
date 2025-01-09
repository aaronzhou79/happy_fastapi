from datetime import datetime
from typing import Literal

import sqlalchemy as sa

from sqlmodel import Field, SQLModel

from src.common.data_model.base_model import DatabaseModel, id_pk
from src.common.enums import OperaLogStatusType
from src.utils.timezone import TimeZone


class OperaLogBase(SQLModel):
    """操作日志基类"""
    trace_id: str = Field(max_length=64, index=True)
    username: str | None = Field(default=None, max_length=32, index=True)
    method: str = Field(max_length=10)  # GET, POST, PUT, DELETE etc
    title: str = Field(max_length=100)
    path: str = Field(max_length=200)
    ip: str = Field(max_length=64)
    country: str | None = Field(default=None, max_length=64)
    region: str | None = Field(default=None, max_length=64)
    city: str | None = Field(default=None, max_length=64)
    user_agent: str = Field(max_length=500)
    os: str | None = Field(default=None, max_length=64)
    browser: str | None = Field(default=None, max_length=64)
    device: str | None = Field(default=None, max_length=64)
    args: dict | None = Field(default=None, sa_type=sa.JSON)
    status: OperaLogStatusType = Field(default=OperaLogStatusType.success)
    code: str = Field(max_length=20)
    msg: str | None = Field(default=None, max_length=500)
    cost_time: float = Field(ge=0)  # 添加非负数验证
    opera_time: datetime = Field(default_factory=TimeZone.now, index=True)


class OperaLog(OperaLogBase, DatabaseModel, table=True):
    """操作日志表"""
    __tablename__: Literal["sys_opera_log"] = "sys_opera_log"
    id: id_pk  # type: ignore


class OperaLogCreate(OperaLogBase):
    """操作日志创建模型"""


class OperaLogUpdate(OperaLogBase):
    """操作日志更新模型"""
    id: int
