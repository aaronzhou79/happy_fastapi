from typing import Any, TypeVar

from .cache_conf import CacheResult, generate_cache_key, redis_cache

T = TypeVar('T')


class CacheManager:
    """缓存管理类"""
    def __init__(self, prefix: str = "", default_ttl: int = 3600):
        self.prefix = prefix
        self.default_ttl = default_ttl

    def get_key(self, *args, **kwargs) -> str:
        """生成缓存键"""
        return generate_cache_key(self.prefix, *args, **kwargs)

    async def get(self, key: str) -> Any:
        """获取缓存"""
        try:
            data = await redis_cache.get(key)
            return CacheResult(success=True, value=data)
        except Exception as e:
            return CacheResult(success=False, error=str(e))

    async def set(
        self,
        key: str,
        value: Any,
        ttl: int | None = None
    ) -> CacheResult:
        """设置缓存"""
        try:
            await redis_cache.set(
                key,
                value,
                ttl=ttl or self.default_ttl
            )
            return CacheResult(success=True, value=value)
        except Exception as e:
            return CacheResult(success=False, error=str(e))

    async def delete(self, key: str) -> CacheResult:
        """删除缓存"""
        try:
            await redis_cache.delete(key)
            return CacheResult(success=True)
        except Exception as e:
            return CacheResult(success=False, error=str(e))
