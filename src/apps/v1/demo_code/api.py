

import asyncio

from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request

from src.common.data_model.query_fields import QueryOptions
from src.core.middleware.jwt import JWTBearer
from src.core.responses.response import response_base
from src.database.db_session import CurrentSession, async_audit_session, async_session

from .model import Article, Comment, Department, User, article_schemas, comment_schemas, dept_schemas, user_schemas

router = APIRouter()


@router.get("/protected", dependencies=[Depends(JWTBearer())])
def protected_route():
    return response_base.success(data={"message": "这是一个受保护的接口"})

@router.post("/lock_test")
async def lock_test(
    request: Request,
    dept_id: int,
    name: str
):
    model = await Department.get_by_id(dept_id)
    if not model:
        return response_base.fail(data="部门不存在")

    async def do_something():
        await asyncio.sleep(30)
        return "done"
    # 使用 with_lock 执行自定义操作
    await model.with_lock(lambda: do_something())

    # update 和 delete 方法已经内置了锁保护
    async with async_audit_session(async_session(), request) as session:
        data = await model.update(session=session, pk=model.id, name=name)
    return response_base.success(data=data)


@router.post("/create_dept")
async def create_dept(
    request: Request,
    dept: dept_schemas["Create"]  # type: ignore
):
    async with async_audit_session(async_session(), request) as session:
        data = await Department.create(session=session, **dept.model_dump())

    return response_base.success(data=data)


@router.put("/update_dept")
async def update_dept(
    request: Request,
    dept_id: int,
    dept_update: dept_schemas["Update"]  # type: ignore
):
    async with async_audit_session(async_session(), request) as session:
        data = await Department.update(session=session, pk=dept_id, **dept_update.model_dump())

    return response_base.success(data=data)

@router.delete("/delete_dept")
async def delete_dept(
    request: Request,
    dept_id: int
):
    async with async_audit_session(async_session(), request) as session:
        await Department.delete(session=session, pk=dept_id)
    return response_base.success(data="部门删除成功")

@router.get("/get_dept")
async def get_dept(
    request: Request,
    dept_id: int,
    max_depth: int = 2
):
    dept = await Department.get_by_id(dept_id)
    if not dept:
        return response_base.fail(data="部门不存在")
    data = await dept.to_api_dict(max_depth=max_depth)
    return response_base.success(data=data)

@router.post("/query_dept")
async def query_dept(
    options: QueryOptions
):
    items, total = await Department.query_with_count(options=options)
    return response_base.success(data={"total": total, "items": items})

@router.get("/get_dept_list")
async def get_dept_list(
    include_deleted: Annotated[bool, Query(...)] = False
):
    depts: list[Department] = await Department.get_all(include_deleted=include_deleted)
    data = [await dept.to_dict() for dept in depts]
    return response_base.success(data=data)



@router.post("/create_user")
async def create_user(
    session: CurrentSession,
    user: user_schemas["Create"]  # type: ignore
):
    user = User(**user.model_dump())
    session.add(user)
    await session.flush()

    return response_base.success(data=await user.to_dict())

@router.get("/get_user")
async def get_user(
    user_id: int
):
    user = await User.get_by_id(user_id)
    if not user:
        return response_base.fail(data="用户不存在")
    return response_base.success(data=await user.to_dict())

@router.post("/create_article")
async def create_article(
    session: CurrentSession,
    article: article_schemas["Create"]  # type: ignore
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
    return response_base.success(data=article_schemas["WithRelations"](**await article.to_dict()))

@router.post("/create_comment")
async def create_comment(
    session: CurrentSession,
    comment: comment_schemas["Create"]  # type: ignore
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
    return response_base.success(data=await comment.to_dict())
