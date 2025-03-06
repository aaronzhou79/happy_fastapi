#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys

from redis.asyncio.client import Redis
from redis.exceptions import AuthenticationError, ConnectionError, TimeoutError

from src.common.logger import log
from src.core.conf import settings


class RedisClient(Redis):
    """Redis 客户端类"""

    def __init__(self):
        """
        初始化 RedisClient 类的实例。

        该方法创建一个 Redis 客户端实例，并配置连接参数，
        如主机地址、端口、密码、数据库编号、连接超时时间和响应解码方式。

        :return: None
        """
        super(RedisClient, self).__init__(
            host=settings.REDIS_HOST,  # Redis 服务器的主机地址
            port=settings.REDIS_PORT,  # Redis 服务器的端口号
            password=settings.REDIS_PASSWORD,  # 连接 Redis 服务器的密码
            db=settings.REDIS_DATABASE,  # 使用的 Redis 数据库编号
            socket_timeout=settings.REDIS_TIMEOUT,  # 连接 Redis 服务器的超时时间
            decode_responses=True,  # 将 Redis 响应解码为 UTF-8 字符串
        )

    async def open(self) -> None:
        """
        触发初始化连接

        :return:
        """
        try:
            await self.ping()
            log.info("🟢 数据库 redis 连接成功")
        except AuthenticationError:
            log.error("❌ 数据库 redis 认证失败")
            log.error("请检查Redis密码配置")
            sys.exit(1)
        except TimeoutError:
            log.error("❌ 数据库 redis 连接超时")
            log.error(
                "请检查Redis服务器地址: {}:{}", settings.REDIS_HOST, settings.REDIS_PORT
            )
            sys.exit(1)
        except ConnectionError as e:
            log.error("❌ 数据库 redis 连接失败: {}", e)
            log.error("请检查:")
            log.error("1. Redis服务是否启动")
            log.error(
                "2. 服务器地址是否正确: {}:{}", settings.REDIS_HOST, settings.REDIS_PORT
            )
            log.error("3. 防火墙是否开放端口")
            log.error("4. 网络连接是否正常")
            sys.exit(1)
        except Exception as e:
            log.error("❌ 数据库 redis 连接异常: {}", e)
            sys.exit(1)

    async def delete_prefix(
        self, prefix: str, exclude: str | list | None = None
    ) -> None:
        """
        删除指定前缀的所有key

        :param prefix:
        :param exclude:
        :return:
        """
        keys = []
        async for key in self.scan_iter(match=f"{prefix}*"):
            if isinstance(exclude, str):
                if key != exclude:
                    keys.append(key)
            elif isinstance(exclude, list):
                if key not in exclude:
                    keys.append(key)
            else:
                keys.append(key)
        if keys:
            await self.delete(*keys)


# 创建 redis 客户端实例
redis_client = RedisClient()
