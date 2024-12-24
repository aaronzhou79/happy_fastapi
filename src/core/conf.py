from pydantic import BaseSettings, SettingsConfigDict
from src.core.path_conf import BasePath
from typing import Literal
from functools import lru_cache

class Settings(BaseSettings):
    """Global Settings"""
    model_config = SettingsConfigDict(env_file=f'{BasePath}/.env', env_file_encoding='utf-8', extra='ignore')

    # 项目名称
    PROJECT_NAME: str = model_config.get('PROJECT_NAME', 'FastAPI')
    # 项目版本
    VERSION: str = '1.0.0'
    # 项目描述
    DESCRIPTION: str = 'FastAPI'
    # 项目文档地址
    DOCS_URL: str = '/docs'
    # 项目文档地址
    OPENAPI_URL: str = '/openapi.json'
    # 项目文档地址
    REDOC_URL: str = '/redoc'

    # 运行环境
    APP_ENV: Literal['dev', 'pro'] = model_config.get('APP_ENV', 'dev')
    # 运行端口
    APP_PORT: int = model_config.get('APP_PORT', 8000)
    # 运行地址
    APP_HOST: str = model_config.get('APP_HOST', '0.0.0.0')
    # 调试模式
    APP_DEBUG: bool = model_config.get('APP_DEBUG', False)


@lru_cache
def get_settings() -> Settings:
    """获取全局配置"""
    return Settings()

# 创建配置实例
settings = get_settings()