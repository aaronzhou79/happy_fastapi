
from src.core.exceptions.custom_exceptions import CustomException
from src.core.middleware.jwt import JWTBearer
from src.core.responses.response_code import ResponseCode, ResponseMessage
from src.core.responses.response_schema import ResponseSchema
from src.core.conf import settings
from fastapi import Depends
from fastapi import status
from typing import Union
from fastapi import APIRouter

from src.core.security.jwt import create_access_token
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