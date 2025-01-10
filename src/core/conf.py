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
    API_PATH: str = "/api"
    # 项目文档地址
    DOCS_URL: str = f"{API_PATH}/docs"
    # 项目文档地址
    OPENAPI_URL: str = f"{API_PATH}/openapi.json"
    # 项目文档地址
    REDOC_URL: str = f"{API_PATH}/redoc"

    # 运行环境
    APP_ENV: Literal['dev', 'pro'] = "dev"
    # 运行端口
    APP_PORT: int = 8081
    # 运行地址
    APP_HOST: str = "0.0.0.0"  # noqa: S104
    # 调试模式
    APP_DEBUG: bool = False

    # JWT配置
    JWT_SECRET_KEY: str = "your-secret-key"  # 建议在.env中配置
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # 日期时间格式
    DATETIME_TIMEZONE: str = 'Asia/Shanghai'
    DATETIME_FORMAT: str = "%Y-%m-%d %H:%M:%S"

    # 数据库配置
    DB_TYPE: Literal['sqlite', 'mysql', 'postgresql', 'dm', 'kingbase', 'oscar', 'gbase'] = "sqlite"
    DB_NAME: str = "test.db"
    DB_USER: str = "root"
    DB_PASSWORD: str = "root"
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306

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

    # Redis 配置
    REDIS_HOST: str = ""
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""
    REDIS_DATABASE: int = 0
    REDIS_TIMEOUT: int = 5
    REDIS_PREFIX: str = "HC"
    REDIS_CACHE_KEY_PREFIX: str = f'{REDIS_PREFIX}:cache'
    CACHE_EXPIRE_IN_SECONDS: int = 60 * 60 * 24 * 7  # 7天
    CACHE_TREE_EXPIRE_IN_SECONDS: int = 60 * 60 * 24 * 30  # 30天
    MAX_TREE_DEPTH: int = 10  # 树的最大深度

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
        f'{API_PATH}/auth/login/swagger',
        f'{API_PATH}/oauth2/github/callback',
        f'{API_PATH}/oauth2/linux-do/callback',
    ]
    OPERA_LOG_ENCRYPT_TYPE: int = 1  # 0: AES (性能损耗); 1: md5; 2: ItsDangerous; 3: 不加密, others: 替换为 ******  # noqa: E501
    OPERA_LOG_ENCRYPT_KEY_INCLUDE: list[str] = [  # 将加密接口入参参数对应的值
        'password',
        'old_password',
        'new_password',
        'confirm_password',
    ]

    # 加密密钥
    # Env Opera Log # 密钥 os.urandom(32), 需使用 bytes.hex(os.urandom(32)) 方法转换为 str
    OPERA_LOG_ENCRYPT_SECRET_KEY: str = 'your-secret-key'

    # Request limiter
    REQUEST_LIMITER_REDIS_PREFIX: str | None = f'{REDIS_PREFIX}:limiter'

    # Trace ID
    TRACE_ID_REQUEST_HEADER_KEY: str = 'X-Request-ID'

    # Middleware
    MIDDLEWARE_CORS: bool = True
    MIDDLEWARE_ACCESS: bool = True

    # CORS
    CORS_ALLOWED_ORIGINS: list[str] = [
        'http://localhost:5173',  # 前端地址，末尾不要带 '/'
        '*',
    ]
    CORS_EXPOSE_HEADERS: list[str] = [
        TRACE_ID_REQUEST_HEADER_KEY,
    ]

    # Token
    TOKEN_SECRET_KEY: str = 'FqmttF4sQzTT9_gNJuzStpnMPRYw01vorr0grhhpR7I'
    TOKEN_ALGORITHM: str = 'HS256'  # 算法
    TOKEN_EXPIRE_SECONDS: int = 60 * 60 * 24 * 1  # 过期时间，单位：秒
    TOKEN_REFRESH_EXPIRE_SECONDS: int = 60 * 60 * 24 * 7  # refresh token 过期时间，单位：秒
    TOKEN_REDIS_PREFIX: str = f'{REDIS_PREFIX}:token'
    TOKEN_REFRESH_REDIS_PREFIX: str = f'{REDIS_PREFIX}:refresh_token'
    TOKEN_REQUEST_PATH_EXCLUDE: list[str] = [  # JWT / RBAC 白名单
        f'{API_PATH}/auth/login',
        f'{API_PATH}/auth/refresh',
        f'{API_PATH}/auth/logout',
    ]

    # JWT
    JWT_USER_REDIS_PREFIX: str = f'{REDIS_PREFIX}:user'
    JWT_USER_REDIS_EXPIRE_SECONDS: int = 60 * 60 * 24 * 7

    # 验证码
    CAPTCHA_NEED: bool = False

    # Captcha
    CAPTCHA_LOGIN: bool = True
    CAPTCHA_LOGIN_REDIS_PREFIX: str = f'{REDIS_PREFIX}:captcha'
    CAPTCHA_LOGIN_EXPIRE_SECONDS: int = 60 * 5  # 过期时间，单位：秒

    # Cookies
    COOKIE_REFRESH_TOKEN_KEY: str = f'{REDIS_PREFIX}:refresh_token'
    COOKIE_REFRESH_TOKEN_EXPIRE_SECONDS: int = TOKEN_REFRESH_EXPIRE_SECONDS

    # Profiling
    SLOW_REQUEST_THRESHOLD: float = 0.1  # 慢请求阈值(秒)
    MEMORY_WARNING_THRESHOLD: int = 100 * 1024 * 1024  # 内存警告阈值(字节)

    # Ip location
    IP_LOCATION_PARSE: Literal['online', 'offline', 'false'] = 'offline'
    IP_LOCATION_REDIS_PREFIX: str | None = f'{REDIS_PREFIX}:ip:location'
    IP_LOCATION_EXPIRE_SECONDS: int | None = 60 * 60 * 24 * 1  # 过期时间，单位：秒

@lru_cache
def get_settings() -> Settings:
    """获取全局配置"""
    return Settings()


# 创建配置实例
settings = get_settings()