# src/apps/v1/sys/models/factory_user.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2025-02-12
# @Author  : lei
# @File    : factory_user.py
# @Software: Cursor
# @Description: 工厂信息服务

from typing import Sequence

from src.apps.v1.sys.crud.crud_factory_user import crud_factory_user
from src.apps.v1.sys.crud.crud_user import crud_user
from src.apps.v1.sys.models.mdl_factory_user import FactoryUser, FactoryUserCreate, FactoryUserUpdate
from src.apps.v1.sys.models.mdl_user import User
from src.common.base_service import BaseService
from src.database.db_session import AuditAsyncSession, CurrentSession


class SvrFactoryUser(BaseService[FactoryUser, FactoryUserCreate, FactoryUserUpdate]):
    """
    工厂信息服务
    """
    def __init__(self):
        self.crud = crud_factory_user

    async def clear_factory_users(self, session: AuditAsyncSession, factory_id: int, user_ids: list[int]) -> None:
        """
        清除工厂用户

        :param factory_id: 工厂id
        :param user_ids: 用户id数组
        """
        await self.crud.clear_factory_users(session, factory_id, user_ids)

    async def get_by_factory_id(self, session: CurrentSession, factory_id: int,
                                is_factory_user: bool) -> Sequence[User]:
        """
        获取工厂用户

        :param factory_id: 工厂id
        :param is_factory_user: 是否当前工厂用户
        """
        factory_users = await self.crud.get_by_factory_id(session, factory_id)
        factory_user_ids = [FactoryUser.user_id for FactoryUser in factory_users]
        users = await crud_user.get_multi(session=session, limit=10000)
        factory_users.clear()

        if is_factory_user:  # 查询当前工厂已分配用户
            for user in users:
                if user.id in factory_user_ids:
                    factory_users.append(user)
        else:  # 查询当前工厂未分配用户
            for user in users:
                if user.id not in factory_user_ids:
                    factory_users.append(user)

        return factory_users

    async def get_by_user_id(self, session: CurrentSession, user_id: int) -> Sequence[FactoryUser]:
        """
        获取用户工厂

        :param user_id: 用户id
        """
        return await self.crud.get_by_user_id(session, user_id)


svr_factory_user = SvrFactoryUser()
