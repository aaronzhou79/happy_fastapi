from pydantic_settings import BaseSettings, SettingsConfigDict
from src.core.path_conf import BasePath
from typing import Literal
from functools import lru_cache

class Settings(BaseSettings):
    """Global Settings"""
    model_config = SettingsConfigDict(env_file=f'{BasePath}/.env', env_file_encoding='utf-8', extra='ignore')

    # 项目名称
    PROJECT_NAME: str = model_config.get('PROJECT_NAME', 'FastAPI')
    # 项目版本
    VERSION: str = model_config.get('VERSION', '1.0.0')
    # 项目描述
    DESCRIPTION: str = model_config.get('DESCRIPTION', 'FastAPI')
    # 项目文档地址
    DOCS_URL: str = model_config.get('DOCS_URL', '/docs')
    # 项目文档地址
    OPENAPI_URL: str = model_config.get('OPENAPI_URL', '/openapi.json')
    # 项目文档地址
    REDOC_URL: str = model_config.get('REDOC_URL', '/redoc')

    # 运行环境
    APP_ENV: Literal['dev', 'pro'] = model_config.get('APP_ENV', 'dev')
    # 运行端口
    APP_PORT: int = model_config.get('APP_PORT', 8081)
    # 运行地址
    APP_HOST: str = model_config.get('APP_HOST', '0.0.0.0')
    # 调试模式
    APP_DEBUG: bool = model_config.get('APP_DEBUG', False)

    # JWT配置
    JWT_SECRET_KEY: str = model_config.get('JWT_SECRET_KEY', 'your-secret-key')  # 建议在.env中配置
    JWT_ALGORITHM: str = model_config.get('JWT_ALGORITHM', 'HS256')
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = model_config.get('JWT_ACCESS_TOKEN_EXPIRE_MINUTES', 30)


@lru_cache
def get_settings() -> Settings:
    """获取全局配置"""
    return Settings()

# 创建配置实例
settings = get_settings()