from datetime import datetime, timedelta
from typing import Any, Awaitable, Dict

from src.core.conf import settings
from src.database.db_redis import redis_client


class RedisManager:
    """Redis 管理类"""
    def __init__(self, prefix: str = ""):
        self.prefix = f"{settings.REDIS_CACHE_KEY_PREFIX}:{prefix}"
        self.client = redis_client.client

    def get_key(self, key: str) -> str:
        """生成完整的键名"""
        return f"{self.prefix}:{key}" if self.prefix else key

    # 字符串操作
    async def get_str(self, key: str) -> str:
        """获取字符串值"""
        return await self.client.get(self.get_key(key))

    async def set_str(
        self,
        key: str,
        value: str,
        expire: int | None = None
    ) -> bool:
        """设置字符串值"""
        key = self.get_key(key)
        if expire:
            if isinstance(expire, timedelta):
                expire = int(expire.total_seconds())
            return await self.client.setex(key, expire, value)
        return await self.client.set(key, value)

    # Hash操作
    async def hget(self, key: str, field: str) -> str | Any | None:
        """获取Hash字段值"""
        return self.client.hget(self.get_key(key), field)

    async def hset(self, key: str, field: str, value: str) -> (Awaitable[int] | int):
        """设置Hash字段值"""
        return self.client.hset(self.get_key(key), field, value)

    async def hmset(self, key: str, mapping: Dict[str, Any]) -> (Awaitable[str] | str):
        """批量设置Hash字段"""
        return self.client.hmset(self.get_key(key), mapping)

    # 计数器
    async def incr(self, key: str, amount: int = 1) -> int:
        """增加计数"""
        return await self.client.incrby(self.get_key(key), amount)

    async def decr(self, key: str, amount: int = 1) -> int:
        """减少计数"""
        return await self.client.decrby(self.get_key(key), amount)

    # 分布式锁
    async def acquire_lock(
        self,
        lock_name: str,
        expire_seconds: int = 10
    ) -> bool:
        """获取分布式锁"""
        key = self.get_key(f"lock:{lock_name}")
        return await self.client.set(
            key,
            str(datetime.now()),
            nx=True,
            ex=expire_seconds
        )

    async def release_lock(self, lock_name: str) -> bool:
        """释放分布式锁"""
        return await self.client.delete(self.get_key(f"lock:{lock_name}"))

    # 限流器
    async def check_rate_limit(
        self,
        key: str,
        max_requests: int,
        period: int
    ) -> bool:
        """检查是否超出限流"""
        redis_key = self.get_key(f"ratelimit:{key}")
        requests = await self.client.get(redis_key)

        if not requests:
            await self.client.setex(redis_key, period, 1)
            return True

        requests = int(requests)
        if requests >= max_requests:
            return False

        await self.client.incr(redis_key)
        return True

    # 会话管理
    async def set_session(
        self,
        session_id: str,
        data: dict,
        expire: int | None = None
    ) -> None:
        """设置会话数据"""
        key = self.get_key(f"session:{session_id}")
        self.client.hmset(key, data)
        if expire:
            if isinstance(expire, timedelta):
                expire = int(expire.total_seconds())
            await self.client.expire(key, expire)

    async def get_session(self, session_id: str) -> (Awaitable[dict[Any, Any]] | dict[Any, Any]):
        """获取会话数据"""
        return self.client.hgetall(
            self.get_key(f"session:{session_id}")
        )

    async def delete_session(self, session_id: str) -> (Awaitable[int] | int):
        """删除会话数据"""
        return await self.client.delete(self.get_key(f"session:{session_id}"))
