from enum import Enum
from typing import NamedTuple

from fastapi import Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import (
    DataError,
    IntegrityError,
    SQLAlchemyError,
)

from src.core.conf import settings
from src.core.responses.response_code import ResponseCode, ResponseMessage


class DBErrorType(Enum):
    """数据库错误类型"""
    UNIQUE_VIOLATION = "unique_violation"
    FOREIGN_KEY_VIOLATION = "foreign_key_violation"
    INTEGRITY_CONSTRAINT = "integrity_constraint"
    NUMERIC_ERROR = "numeric_error"
    STRING_ERROR = "string_error"
    DATE_ERROR = "date_error"
    CONNECTION_ERROR = "connection_error"
    TIMEOUT_ERROR = "timeout_error"
    PROGRAMMING_ERROR = "programming_error"
    UNSUPPORTED_ERROR = "unsupported_error"


class DBErrorInfo(NamedTuple):
    """数据库错误信息结构"""
    status_code: int
    code: str
    message: str
    detail: str


class DBErrorHandler:
    """数据库错误处理器"""

    ERROR_PATTERNS = {
        DBErrorType.UNIQUE_VIOLATION: (
            "unique violation",
            DBErrorInfo(
                status.HTTP_400_BAD_REQUEST,
                ResponseCode.PARAMS_ERROR,
                "数据已存在",
                "违反唯一约束"
            )
        ),
        DBErrorType.FOREIGN_KEY_VIOLATION: (
            "foreign key violation",
            DBErrorInfo(
                status.HTTP_400_BAD_REQUEST,
                ResponseCode.PARAMS_ERROR,
                "关联数据不存在",
                "违反外键约束"
            )
        ),
        # ... 其他错误模式映射
    }

    @classmethod
    def get_error_info(cls, exc: SQLAlchemyError) -> DBErrorInfo:
        """根据异常获取错误信息"""
        error_msg = str(exc).lower()

        # 处理IntegrityError
        if isinstance(exc, IntegrityError):
            for error_type, (pattern, error_info) in cls.ERROR_PATTERNS.items():
                if pattern in error_msg:
                    return error_info
            return DBErrorInfo(
                status.HTTP_400_BAD_REQUEST,
                ResponseCode.PARAMS_ERROR,
                "数据违反完整性约束",
                "违反数据库约束"
            )

        # 处理DataError
        if isinstance(exc, DataError):
            if "numeric" in error_msg:
                return DBErrorInfo(
                    status.HTTP_400_BAD_REQUEST,
                    ResponseCode.PARAMS_ERROR,
                    "数值类型错误",
                    "数据格式不符合要求"
                )
            # ... 其他DataError处理

        # 默认错误信息
        return DBErrorInfo(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            ResponseCode.SERVER_ERROR,
            ResponseMessage.zh_CN[ResponseCode.SERVER_ERROR],
            "数据库操作异常"
        )


class DatabaseExceptionHandler:
    """数据库异常处理器"""

    @staticmethod
    async def database_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
        """处理数据库异常"""
        error_info = DBErrorHandler.get_error_info(exc)

        return JSONResponse(
            status_code=error_info.status_code,
            content={
                "code": error_info.code,
                "message": error_info.message,
                "data": {
                    "detail": error_info.detail,
                    "error": str(exc) if settings.APP_DEBUG else None
                }
            }
        )