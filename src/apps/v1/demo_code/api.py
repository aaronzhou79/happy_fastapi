
from datetime import datetime
from typing import Union

from fastapi import APIRouter, Depends, status

from src.apps.v1.demo_code.model import User
from src.core.conf import settings
from src.core.exceptions.custom_exceptions import CustomException
from src.core.middleware.jwt import JWTBearer
from src.core.responses.response_code import ResponseCode, ResponseMessage
from src.core.responses.response_schema import ResponseSchema
from src.core.security.jwt import create_access_token

from .model import article_schemas, user_schemas

router = APIRouter()

@router.get("/", response_model=ResponseSchema[dict])
def read_root():
    return ResponseSchema(
        code=ResponseCode.SUCCESS,
        message=ResponseMessage.zh_CN[ResponseCode.SUCCESS],
        data={"Hello": settings.JWT_SECRET_KEY}
    )

@router.get("/items/{item_id}", response_model=ResponseSchema[dict])
def read_item(item_id: int, q: Union[str, None] = None):
    return ResponseSchema(
        code=ResponseCode.SUCCESS,
        message=ResponseMessage.zh_CN[ResponseCode.SUCCESS],
        data={"item_id": item_id, "q": q}
    )

@router.get("/protected", dependencies=[Depends(JWTBearer())], response_model=ResponseSchema[dict])
def protected_route():
    return ResponseSchema(
        code=ResponseCode.SUCCESS,
        message=ResponseMessage.zh_CN[ResponseCode.SUCCESS],
        data={"message": "这是一个受保护的接口"}
    )

@router.post("/login", response_model=ResponseSchema[dict])
def login(username: str, password: str):
    token = create_access_token(username)
    return ResponseSchema(
        code=ResponseCode.SUCCESS,
        message=ResponseMessage.zh_CN[ResponseCode.SUCCESS],
        data={"access_token": token, "token_type": "bearer"}
    )

@router.get("/error-demo")
def error_demo():
    # 抛出自义异常示例
    raise CustomException(
        message="这是一个自定义错误",
        status_code=status.HTTP_400_BAD_REQUEST,
        code="400001"  # 可以自定义错误码
    )

@router.get("/error-demo2")
def error_demo2():
    # 抛出系统异常示例
    1/0  # 这会触发全局异常处理器


@router.get("/demo_user")
def demo_user(
    create_user: user_schemas["Create"],
    update_user: user_schemas["Update"],
    base_user: user_schemas["Base"],
    with_relations_user: user_schemas["WithRelations"],
    list_user: user_schemas["List"],
):
    user_data = {
        "id": 1,
        "username": "test_user",
        "email": "test@example.com",
        "password": "rtfgkj23rhks",
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "deleted_at": datetime.now()
    }
    user = user_schemas["Base"](**user_data)
    return ResponseSchema(
        code=ResponseCode.SUCCESS,
        message=ResponseMessage.zh_CN[ResponseCode.SUCCESS],
        data=user.model_dump()
    )

@router.get("/demo_article")
def demo_article(
    create_article: article_schemas["Create"],
    update_article: article_schemas["Update"],
    base_article: article_schemas["Base"],
    with_relations_article: article_schemas["WithRelations"],
    list_article: article_schemas["List"],
):
    article_data = {
        "id": 1,
        "title": "test_article",
        "content": "test_content",
    }
    article = article_schemas["Base"](**article_data)
    return ResponseSchema(
        code=ResponseCode.SUCCESS,
        message=ResponseMessage.zh_CN[ResponseCode.SUCCESS],
        data=article.model_dump()
    )