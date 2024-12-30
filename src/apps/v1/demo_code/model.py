from typing import Literal

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.common.data_model.base_model import AuditConfig, AuditLogMixin, DatabaseModel, SoftDeleteMixin, TimestampMixin
from src.common.data_model.schema_generator import generate_schemas


class Comment(TimestampMixin, SoftDeleteMixin, AuditLogMixin, DatabaseModel):
    """评论模型示例"""
    __tablename__: Literal["comments"] = "comments"

    content = Column(Text, nullable=False, comment="评论内容")
    article_id = Column(ForeignKey("articles.id"), nullable=False, comment="文章ID")
    article = relationship("Article", back_populates="comments")


class Article(TimestampMixin, SoftDeleteMixin, DatabaseModel):
    """文章模型示例"""
    __tablename__: Literal["articles"] = "articles"

    title = Column(String(100), nullable=False, comment="文章标题")
    content = Column(Text, nullable=False, comment="文章内容")
    is_published = Column(Boolean, default=False, comment="是否发布")
    author_id = Column(ForeignKey("sys_users.id"), nullable=False, comment="作者ID")

    author = relationship("User", back_populates="articles")
    comments = relationship("Comment", back_populates="article")

    async def publish(self) -> None:
        """发布文章"""
        self.is_published = True
        self.touch()  # 使用 TimestampMixin 的 touch 方法更新时间

    async def update_content(self, title: str, content: str) -> None:
        """更新文章内容"""
        self.title = title
        self.content = content
        self.touch()  # 自动更新 updated_at

    @property
    def publish_status(self) -> str:
        """获取发布状态"""
        return "已发布" if bool(self.is_published) else "草稿"

    @property
    def time_info(self) -> dict:
        """获取时间信息"""
        return {
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
            "is_modified": self.updated_at > self.created_at
        }


class Role(SoftDeleteMixin, DatabaseModel):
    """角色模型"""
    __tablename__: Literal["sys_roles"] = "sys_roles"

    name = Column(String(50), nullable=False, comment="角色名称")
    users: Mapped[list["User"]] = relationship("User", secondary="sys_user_roles", back_populates="roles")


class User(SoftDeleteMixin, DatabaseModel):
    """用户模型"""
    __tablename__: Literal["sys_users"] = "sys_users"

    # 启用审计
    audit_config = AuditConfig(
        enabled=True,
        # 只审计这些字段
        fields={'name', 'email', 'role'},
        # 额外忽略这些字段
        exclude_fields={'password'}
    )

    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="用户名")
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False, comment="邮箱")
    password: Mapped[str] = mapped_column(String(128), nullable=False, comment="密码")
    dept_id: Mapped[int] = mapped_column(ForeignKey("departments.id"), nullable=False, comment="部门ID")
    department: Mapped["Department"] = relationship("Department", back_populates="users")

    articles: Mapped[list["Article"]] = relationship("Article", back_populates="author")
    roles: Mapped[list["Role"]] = relationship("Role", secondary="sys_user_roles", back_populates="users")

    @property
    def safe_dict(self):
        """返回安全的用户信息（不包含密码）"""
        return self.to_dict(exclude=["password"])


class UserRole(SoftDeleteMixin, DatabaseModel):
    """用户角色模型"""
    __tablename__: Literal["sys_user_roles"] = "sys_user_roles"

    user_id = Column(ForeignKey("sys_users.id"), nullable=False, comment="用户ID")
    role_id = Column(ForeignKey("sys_roles.id"), nullable=False, comment="角色ID")


class Department(SoftDeleteMixin, DatabaseModel):
    """部门模型"""
    __tablename__: Literal["departments"] = "departments"

    name = Column(String(50), nullable=False, comment="部门名称")
    users: Mapped[list["User"]] = relationship("User", back_populates="department")


comment_schemas = generate_schemas(
    Comment,
    prefix="",
    exclude_create={"id", "created_at", "updated_at"},  # 创建时不需要设置软删除状态
    exclude_update={"id", "created_at", "updated_at"}  # 更新时不允许修改软删除状态
)


article_schemas = generate_schemas(
    Article,
    prefix="",
    exclude_create={"id", "created_at", "updated_at", "is_published"},  # 创建时不需要设置发布状态
    exclude_update={"id", "created_at", "updated_at", "author_id"}  # 更新时不允许修改作者
)
user_schemas = generate_schemas(
    User,
    prefix="",
    exclude_create={"id", "created_at", "updated_at", "deleted_at"},  # 创建时不需要设置软删除状态
    exclude_update={"id", "created_at", "updated_at", "deleted_at"}  # 更新时不允许修改软删除状态
)
dept_schemas = generate_schemas(
    Department,
    prefix="",
    exclude_create={"id", "created_at", "updated_at", "deleted_at"},  # 创建时不需要设置软删除状态
    exclude_update={"id", "created_at", "updated_at", "deleted_at"}  # 更新时不允许修改软删除状态
)
