from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import (
    DataError,
    IntegrityError,
    NotSupportedError,
    OperationalError,
    ProgrammingError,
    SQLAlchemyError,
    TimeoutError,
)

from ..responses.response_code import StandardResponseCode


class DBExceptionHandler:
    """
    数据库异常处理
    """
    @staticmethod
    async def database_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
        """统一处理数据库异常"""
        error_response = {
            "code": StandardResponseCode.HTTP_500,
            "msg": "数据库操作失败",
            "data": {
                "error_type": exc.__class__.__name__,
                "detail": str(exc)
            }
        }

        if isinstance(exc, IntegrityError):
            if hasattr(exc, 'orig') and exc.orig:
                error_response.update({
                    "code": 400,
                    "msg": "数据完整性错误",
                    "data": {
                        "error_code": exc.orig.args[0] if exc.orig.args else None,
                        "error_msg": exc.orig.args[1] if len(exc.orig.args) > 1 else None,
                        "statement": str(exc.statement) if exc.statement else None,
                        "params": str(exc.params) if exc.params else None
                    }
                })

        elif isinstance(exc, DataError):
            error_response.update({
                "code": 400,
                "msg": "数据格式错误",
            })

        elif isinstance(exc, OperationalError):
            error_response.update({
                "code": 503,
                "msg": "数据库连接错误",
            })

        elif isinstance(exc, TimeoutError):
            error_response.update({
                "code": 504,
                "msg": "数据库操作超时",
            })

        elif isinstance(exc, ProgrammingError):
            error_response.update({
                "code": 400,
                "msg": "SQL语法错误",
            })

        elif isinstance(exc, NotSupportedError):
            error_response.update({
                "code": 400,
                "msg": "不支持的数据库操作",
            })

        return JSONResponse(
            status_code=error_response["code"],
            content=error_response
        )
