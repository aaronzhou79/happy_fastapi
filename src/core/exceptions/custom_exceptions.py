from fastapi import status

class CustomException(Exception):
    """自定义异常基类"""
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        code: str | None = None
    ):
        self.message = message
        self.status_code = status_code
        self.code = code or str(status_code) 