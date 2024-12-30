

import asyncio

from fastapi import APIRouter, Depends, Request

from src.core.middleware.jwt import JWTBearer
from src.core.responses.response import response_base
from src.database.db_session import CurrentSession, async_audit_session, async_session

from .model import (
    Article,
    ArticleCreate,
    ArticleList,
    ArticleUpdate,
    Comment,
    CommentCreate,
    CommentList,
    CommentUpdate,
)

router = APIRouter()


@router.get("/protected", dependencies=[Depends(JWTBearer())])
def protected_route():
    return response_base.success(data={"message": "这是一个受保护的接口"})

@router.post("/create_article")
async def create_article(
    session: CurrentSession,
    article: ArticleCreate  # type: ignore
):
    article = Article(**article.model_dump())
    session.add(article)
    await session.flush()

    return response_base.success(data=await article.to_dict())

@router.get("/get_article")
async def get_article(
    article_id: int
):
    article = await Article.get_by_id(article_id)
    if not article:
        return response_base.fail(data="文章不存在")
    return response_base.success(data=ArticleList(items=[article]))

@router.post("/create_comment")
async def create_comment(
    session: CurrentSession,
    comment: CommentCreate  # type: ignore
):
    comment = Comment(**comment.model_dump())
    session.add(comment)
    await session.flush()

    return response_base.success(data=await comment.to_dict())

@router.get("/get_comment")
async def get_comment(
    comment_id: int
):
    comment = await Comment.get_by_id(comment_id)
    if not comment:
        return response_base.fail(data="评论不存在")
    return response_base.success(data=CommentList(items=[comment]))
