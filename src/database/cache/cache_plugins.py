from aiocache.plugins import BasePlugin

from src.common.log import log


class CacheLogPlugin(BasePlugin):
    """缓存日志插件"""

    async def pre_get(self, *args, **kwargs) -> None:
        """获取缓存前"""
        key = kwargs.get('key', '')
        log.debug(f"[pre_get] Getting cache for key: {args[1]}")

    async def post_get(self, *args, **kwargs) -> None:
        """获取缓存后"""
        key = kwargs.get('key', '')
        hit = kwargs.get('hit', False)
        log.info(f"[post_get] Cache {'hit' if hit else 'miss'} for key: {args[1]}")

    async def pre_set(self, *args, **kwargs) -> None:
        """设置缓存前"""
        key = kwargs.get('key', '')
        log.debug(f"[pre_set] Setting cache for key: {args[1]}")

    async def post_set(self, *args, **kwargs) -> None:
        """设置缓存后"""
        key = kwargs.get('key', '')
        log.info(f"[post_set] Cache set for key: {args[1]}")