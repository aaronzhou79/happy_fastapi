from typing import Literal

import sqlalchemy as sa

from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.apps.v1.sys.model import User
from src.common.data_model.base_model import DatabaseModel, SoftDeleteMixin, TimestampMixin
from src.common.data_model.schema_base import generate_schemas


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


ArticleSchema, ArticleCreate, ArticleUpdate = generate_schemas(
    Article,
    exclude_create={"id", "created_at", "updated_at", "deleted_at"},
    exclude_update={"id", "created_at", "updated_at", "deleted_at"},
)

CommentSchema, CommentCreate, CommentUpdate = generate_schemas(
    Comment
)
