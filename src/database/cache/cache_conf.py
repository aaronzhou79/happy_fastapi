# core/cache.py


from typing import Any, cast

from aiocache import RedisCache, caches
from pydantic import BaseModel

from src.core.conf import settings


class CacheResult(BaseModel):
    """缓存结果模型"""
    success: bool
    value: Any | None = None
    error: str | None = None


def setup_redis_cache() -> None:
    """初始化Redis缓存配置"""
    cache_config = {
        'default': {
            'cache': "aiocache.RedisCache",
            'endpoint': settings.REDIS_HOST,
            'port': settings.REDIS_PORT,
            'password': settings.REDIS_PASSWORD,
            'db': settings.REDIS_DATABASE,
            'timeout': settings.REDIS_TIMEOUT,
            'serializer': {
                'class': "aiocache.serializers.PickleSerializer"
            },
            'plugins': [
                {'class': "aiocache.plugins.HitMissRatioPlugin"},
                {'class': "aiocache.plugins.TimingPlugin"}
            ]
        }
    }
    caches.set_config(cache_config)


setup_redis_cache()


def generate_cache_key(*args, **kwargs) -> str:
    """生成缓存键的辅助函数"""
    key_parts = [settings.REDIS_CACHE_KEY_PREFIX]
    key_parts.extend(str(arg) for arg in args)
    key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
    return ":".join(filter(None, key_parts))


def get_redis_cache() -> RedisCache:
    """获取Redis缓存实例"""
    if not caches.get_config():
        setup_redis_cache()
    cache = caches.get('default')  # type: ignore
    return cast(RedisCache, cache)


def get_redis_settings() -> dict:
    """获取Redis缓存配置"""
    return {
        'endpoint': settings.REDIS_HOST,
        'port': settings.REDIS_PORT,
        'password': settings.REDIS_PASSWORD,
        'db': settings.REDIS_DATABASE,
        'timeout': settings.REDIS_TIMEOUT
    }


# 创建全局Redis缓存实例
redis_cache: RedisCache = get_redis_cache()
