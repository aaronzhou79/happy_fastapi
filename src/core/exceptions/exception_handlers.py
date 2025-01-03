from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from src.core.conf import settings
from src.core.exceptions.custom_exceptions import CustomException
from src.core.exceptions.database_exceptions import DatabaseExceptionHandler
from src.core.responses.response_code import ResponseCode, ResponseMessage


class GlobalExceptionHandler:
    """全局异常处理器"""

    @staticmethod
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """处理请求参数验证异常"""
        # 格式化验证错误信息
        error_messages = []
        for error in exc.errors():
            field = error["loc"][-1]  # 获取字段名
            msg = error["msg"]  # 获取错误信息
            error_messages.append(f"字段 '{field}': {msg}")

        formatted_message = "; ".join(error_messages)

        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "code": ResponseCode.PARAMS_ERROR.code,
                "msg": formatted_message,
                "data": None  # 改为 None，因为详细错误信息已经包含在 message 中
            }
        )

    @staticmethod
    async def custom_exception_handler(request: Request, exc: CustomException):
        """处理自定义异常"""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "code": exc.code,
                "msg": exc.message,
                "data": None
            }
        )

    @staticmethod
    async def http_exception_handler(request: Request, exc):
        """处理HTTP异常"""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "code": str(exc.status_code),
                "msg": exc.detail,
                "data": None
            }
        )

    @staticmethod
    async def global_exception_handler(request: Request, exc: Exception):
        """处理未捕获的异常"""
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "code": ResponseCode.SERVER_ERROR.code,
                "msg": ResponseMessage.zh_CN[ResponseCode.SERVER_ERROR],
                "data": str(exc) if settings.APP_DEBUG else None
            }
        )


def register_exception(app: FastAPI) -> None:
    """注册异常处理器"""

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        return await GlobalExceptionHandler.validation_exception_handler(request, exc)

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        return await GlobalExceptionHandler.http_exception_handler(request, exc)

    @app.exception_handler(CustomException)
    async def custom_exception_handler(request: Request, exc: CustomException) -> JSONResponse:
        return await GlobalExceptionHandler.custom_exception_handler(request, exc)

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "code": ResponseCode.PARAMS_ERROR.code,
                "msg": str(exc) or ResponseMessage.zh_CN[ResponseCode.PARAMS_ERROR],
                "data": None
            }
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        return await GlobalExceptionHandler.global_exception_handler(request, exc)

    @app.exception_handler(SQLAlchemyError)
    async def database_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
        return await DatabaseExceptionHandler.database_exception_handler(request, exc)

    @app.exception_handler(ResponseValidationError)
    async def response_validation_exception_handler(request: Request, exc: ResponseValidationError) -> JSONResponse:
        """处理响应验证异常"""
        error_messages = []
        for error in exc.errors():
            field = error["loc"][-1]  # 获取字段名
            msg = error["msg"]  # 获取错误信息
            error_messages.append(f"字段 '{field}': {msg}")

        formatted_message = "; ".join(error_messages)

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "code": ResponseCode.SERVER_ERROR.code,
                "msg": f"响应格式错误: {formatted_message}",
                "data": None
            }
        )
