from datetime import datetime
from typing import Literal

import sqlalchemy as sa

from sqlmodel import Field, SQLModel

from src.common.base_model import DatabaseModel, id_pk
from src.utils.timezone import TimeZone


class LoginLogBase(SQLModel):
    """登录日志表"""

    trace_id: str = Field(max_length=64, description='跟踪ID')
    user_uuid: str = Field(max_length=64, description='用户UUID')
    username: str = Field(max_length=64, description='用户名')
    status: int = Field(description='登录状态(0失败 1成功)')
    ip: str = Field(max_length=64, description='登录IP地址')
    country: str | None = Field(default=None, description='国家')
    region: str | None = Field(default=None, description='地区')
    city: str | None = Field(default=None, description='城市')
    user_agent: str = Field(description='请求头')
    os: str | None = Field(default=None, description='操作系统')
    browser: str | None = Field(default=None, description='浏览器')
    device: str | None = Field(default=None, description='设备')
    msg: str = Field(default=None, description='提示消息', sa_type=sa.Text)
    login_time: datetime = Field(default_factory=TimeZone.now, description='登录时间')


class LoginLog(LoginLogBase, DatabaseModel, table=True):
    """登录日志表"""
    __tablename__: Literal["sys_login_log"] = "sys_login_log"
    __table_args__ = (
        sa.Index('idx_login_log_user_uuid', 'user_uuid'),
    )
    id: id_pk  # type: ignore


class LoginLogCreate(LoginLogBase):
    """登录日志创建模型"""


class LoginLogUpdate(LoginLogBase):
    """登录日志更新模型"""
    id: int
