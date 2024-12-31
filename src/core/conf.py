from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

from src.core.path_conf import BasePath


class Settings(BaseSettings):
    """Global Settings"""
    model_config = SettingsConfigDict(
        env_file=f'{BasePath}/.env',
        env_file_encoding='utf-8',
        extra='ignore'
    )

    # 项目名称
    PROJECT_NAME: str = "FastAPI"
    # 项目版本
    VERSION: str = "1.0.0"
    # 项目描述
    DESCRIPTION: str = "FastAPI"
    # 项目API版本
    API_V1_PATH: str = "/api/v1"
    # 项目文档地址
    DOCS_URL: str = f"{API_V1_PATH}/docs"
    # 项目文档地址
    OPENAPI_URL: str = f"{API_V1_PATH}/openapi.json"
    # 项目文档地址
    REDOC_URL: str = f"{API_V1_PATH}/redoc"

    # 运行环境
    APP_ENV: Literal['dev', 'pro'] = "dev"
    # 运行端口
    APP_PORT: int = 8081
    # 运行地址
    APP_HOST: str = "0.0.0.0"
    # 调试模式
    APP_DEBUG: bool = False

    # JWT配置
    JWT_SECRET_KEY: str = "your-secret-key"  # 建议在.env中配置
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # 数据库配置
    DB_TYPE: Literal['sqlite', 'mysql', 'postgresql', 'dm', 'kingbase', 'oscar', 'gbase'] = "sqlite"
    DB_NAME: str = "test.db"
    DB_USER: str = "root"
    DB_PASSWORD: str = "root"
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306

    # 日期时间格式
    DATETIME_TIMEZONE: str = 'Asia/Shanghai'
    DATETIME_FORMAT: str = "%Y-%m-%d %H:%M:%S"

    # 数据库特性配置
    DB_FEATURES: dict[str, dict[str, bool]] = {
        'sqlite': {
            'supports_window_functions': False,
            'supports_cte': True,
            'supports_ilike': False
        },
        'mysql': {
            'supports_window_functions': True,
            'supports_cte': True,
            'supports_ilike': False
        },
        'postgresql': {
            'supports_window_functions': True,
            'supports_cte': True,
            'supports_ilike': True
        },
        'dm': {
            'supports_window_functions': True,
            'supports_cte': True,
            'supports_ilike': False
        },
        'kingbase': {
            'supports_window_functions': True,
            'supports_cte': True,
            'supports_ilike': True
        },
        'oscar': {
            'supports_window_functions': False,
            'supports_cte': True,
            'supports_ilike': False
        },
        'gbase': {
            'supports_window_functions': False,
            'supports_cte': False,
            'supports_ilike': False
        }
    }

    # Log
    LOG_ROOT_LEVEL: str = 'NOTSET'
    LOG_STD_FORMAT: str = (
        '<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</> | <lvl>{level: <8}</> | '
        '<cyan> {correlation_id} </> | <lvl>{message}</>'
    )
    LOG_LOGURU_FORMAT: str = (
        '<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</> | <lvl>{level: <8}</> | '
        '<cyan> {correlation_id} </> | <lvl>{message}</>'
    )
    LOG_CID_DEFAULT_VALUE: str = '-'
    LOG_CID_UUID_LENGTH: int = 32  # must <= 32
    LOG_STDOUT_LEVEL: str = 'INFO'
    LOG_STDERR_LEVEL: str = 'ERROR'
    LOG_STDOUT_FILENAME: str = 'fba_access.log'
    LOG_STDERR_FILENAME: str = 'fba_error.log'

    # Opera log
    OPERA_LOG_PATH_EXCLUDE: list[str] = [
        '/favicon.ico',
        str(DOCS_URL),
        str(REDOC_URL),
        str(OPENAPI_URL),
        f'{API_V1_PATH}/auth/login/swagger',
        f'{API_V1_PATH}/oauth2/github/callback',
        f'{API_V1_PATH}/oauth2/linux-do/callback',
    ]
    OPERA_LOG_ENCRYPT_TYPE: int = 1  # 0: AES (性能损耗); 1: md5; 2: ItsDangerous; 3: 不加密, others: 替换为 ******  # noqa: E501
    OPERA_LOG_ENCRYPT_KEY_INCLUDE: list[str] = [  # 将加密接口入参参数对应的值
        'password',
        'old_password',
        'new_password',
        'confirm_password',
    ]

    # Trace ID
    TRACE_ID_REQUEST_HEADER_KEY: str = 'X-Request-ID'


@lru_cache
def get_settings() -> Settings:
    """获取全局配置"""
    return Settings()


# 创建配置实例
settings = get_settings()