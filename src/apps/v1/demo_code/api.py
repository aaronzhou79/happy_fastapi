

from fastapi import APIRouter, Depends

from src.core.exceptions.custom_exceptions import CustomException
from src.core.middleware.jwt import JWTBearer
from src.core.responses.response import response_base
from src.core.responses.response_code import ResponseCode, ResponseMessage
from src.core.responses.response_schema import ResponseSchema
from src.database.db_session import CurrentSession

from .model import Article, Comment, Department, User, article_schemas, comment_schemas, dept_schemas, user_schemas

router = APIRouter()


@router.get("/protected", dependencies=[Depends(JWTBearer())])
def protected_route():
    return response_base.success(data={"message": "这是一个受保护的接口"})

@router.post("/create_dept")
async def create_dept(
    session: CurrentSession,
    dept: dept_schemas["Create"]
):
    dept = Department(**dept.model_dump())
    session.add(dept)
    await session.flush()

    data = await dept.to_dict()

    return response_base.success(data=data)


@router.get("/get_dept")
async def get_dept(
    dept_id: int
):
    dept = await Department.get_by_id(dept_id)
    if not dept:
        raise CustomException(message="部门不存在")
    data = await dept.to_dict(max_depth=3)
    return response_base.success(data=data)


@router.post("/create_user")
async def create_user(
    session: CurrentSession,
    user: user_schemas["Create"]
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
        raise CustomException(message="用户不存在")
    return response_base.success(data=await user.to_dict())

@router.post("/create_article")
async def create_article(
    session: CurrentSession,
    article: article_schemas["Create"]
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
        raise CustomException(message="文章不存在")
    return response_base.success(data=article_schemas["WithRelations"](**await article.to_dict()))

@router.post("/create_comment")
async def create_comment(
    session: CurrentSession,
    comment: comment_schemas["Create"]
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
        raise CustomException(message="评论不存在")
    return response_base.success(data=await comment.to_dict())
