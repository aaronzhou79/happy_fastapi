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
    # 项目文档地址
    DOCS_URL: str = "/docs"
    # 项目文档地址
    OPENAPI_URL: str = "/openapi.json"
    # 项目文档地址
    REDOC_URL: str = "/redoc"

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
    DB_TYPE: Literal['sqlite', 'mysql', 'postgresql'] = "sqlite"
    DB_NAME: str = "test.db"
    DB_USER: str = "root"
    DB_PASSWORD: str = "root"
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306


@lru_cache
def get_settings() -> Settings:
    """获取全局配置"""
    return Settings()


# 创建配置实例
settings = get_settings()