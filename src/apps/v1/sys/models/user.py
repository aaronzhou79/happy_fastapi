from datetime import datetime
from typing import TYPE_CHECKING, Any, Literal

from sqlmodel import Field, Relationship, SQLModel

from src.apps.v1.sys.models.user_role import UserRole
from src.common.data_model.base_model import DatabaseModel, id_pk
from src.common.enums import UserEmpType, UserStatus
from src.core.conf import settings
from src.database.db_session import uuid4_str

if TYPE_CHECKING:
    from src.apps.v1.sys.models.dept import Dept
    from src.apps.v1.sys.models.role import Role


class UserBase(SQLModel):
    """用户基础模型"""
    __tablename__: Literal["sys_user"] = "sys_user"

    dept_id: int | None = Field(
        default=None, foreign_key="sys_dept.id", description="部门ID")
    name: str = Field(
        ..., max_length=32, description="真实姓名")
    username: str | None = Field(
        default=None, max_length=32, unique=True, index=True, description="用户名")
    password: str | None = Field(
        default=None, max_length=128, description="密码")
    salt: str | None = Field(
        default=None, max_length=16, description="盐")
    avatar: str | None = Field(
        default=None, max_length=256, description="头像")
    status: UserStatus = Field(
        default=UserStatus.ACTIVE, description="用户状态")
    emp_type: UserEmpType = Field(
        default=UserEmpType.staff, description="员工类型")
    email: str | None = Field(
        default=None, max_length=128, description="邮箱")
    phone: str | None = Field(
        default=None, max_length=16, description="手机号")
    is_user: bool = Field(
        default=False, description="是否用户")
    is_superuser: bool = Field(
        default=False, description="是否超级用户")
    is_multi_login: bool = Field(
        default=False, description="是否多端登录")
    last_login: datetime | None = Field(
        default=None, description="最后登录时间")
    uuid: str = Field(
        default_factory=uuid4_str, description="UUID")


class User(UserBase, DatabaseModel, table=True):
    """用户表"""
    __tablename__: Literal["sys_user"] = "sys_user"
    id: id_pk  # type: ignore

    # Relationships
    dept: "Dept" = Relationship(back_populates="users")
    roles: list["Role"] = Relationship(back_populates="users", link_model=UserRole)


class UserCreate(UserBase):
    """用户创建模型"""


class UserUpdate(UserBase):
    """用户更新模型"""
    id: int


class AuthBase(SQLModel):
    """认证基础模型"""
    username: str
    password: str | None


class AuthLoginParam(AuthBase):
    """认证登录参数"""
    if settings.CAPTCHA_NEED:
        captcha: str


class GetSwaggerToken(SQLModel):
    """
    获取 Swagger Token
    """
    access_token: str
    token_type: str = 'Bearer'
    user: UserBase  # type: ignore


class AccessTokenBase(SQLModel):
    """
    访问令牌基础类
    """
    access_token: str
    access_token_type: str = 'Bearer'
    access_token_expire_time: datetime


class GetNewToken(AccessTokenBase):
    """
    获取新令牌
    """


class GetLoginToken(AccessTokenBase):
    """
    获取登录令牌
    """
    user: dict[str, Any]
