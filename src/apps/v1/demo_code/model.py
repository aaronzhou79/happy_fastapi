from typing import TYPE_CHECKING, Literal

import sqlalchemy as sa

from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.apps.v1.sys.model import User
from src.common.data_model.base_model import DatabaseModel, SoftDeleteMixin, TimestampMixin
from src.common.data_model.schema_generator import generate_schemas


class Comment(TimestampMixin, SoftDeleteMixin, DatabaseModel):
    """评论模型示例"""
    __tablename__: Literal["comments"] = "comments"

    content: Mapped[str] = mapped_column(sa.Text, nullable=False, comment="评论内容")
    article_id: Mapped[int] = mapped_column(sa.ForeignKey("articles.id"), nullable=False, comment="文章ID")
    article: Mapped["Article"] = relationship("Article", back_populates="comments")


class Article(TimestampMixin, SoftDeleteMixin, DatabaseModel):
    """文章模型示例"""
    __tablename__: Literal["articles"] = "articles"

    title: Mapped[str] = mapped_column(sa.String(100), nullable=False, comment="文章标题")
    content: Mapped[str] = mapped_column(sa.Text, nullable=False, comment="文章内容")
    is_published: Mapped[bool] = mapped_column(sa.Boolean, default=False, comment="是否发布")
    author_id: Mapped[int] = mapped_column(sa.ForeignKey("sys_users.id"), nullable=False, comment="作者ID")

    author: Mapped[User] = relationship("User")
    comments: Mapped[list["Comment"]] = relationship("Comment", back_populates="article")


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
