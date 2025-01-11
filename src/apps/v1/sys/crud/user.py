# src/apps/v1/sys/crud/user.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2024/12/31
# @Author  : Aaron Zhou
# @File    : user.py
# @Software: Cursor
# @Description: 用户相关CRUD类
from fast_captcha import text_captcha

from src.apps.v1.sys.crud.role import crud_role
from src.apps.v1.sys.crud.user_role import crud_user_role
from src.apps.v1.sys.models.user import User, UserCreate, UserUpdate
from src.common.base_crud import CRUDBase
from src.core.exceptions import errors
from src.core.security.auth_security import get_hash_password
from src.database.db_session import AuditAsyncSession


class CrudUser(CRUDBase[User, UserCreate, UserUpdate]):
    """
    用户CRUD类
    """
    def __init__(self) -> None:
        super().__init__(
            model=User,
            create_model=UserCreate,
            update_model=UserUpdate,
        )

    async def set_as_user(
        self,
        *,
        session: AuditAsyncSession,
        id: int,
        username: str,
        password: str,
        roles: list[int] | None = None,
    ) -> User:
        """
        设置为用户

        :param db:
        :param id:
        :param username:
        :param password:
        :param roles:
        :return:
        """
        current_user = await self.get_by_id(session=session, id=id)
        if current_user is None:
            raise errors.RequestError(data="员工信息不存在！")
        if current_user.is_user:
            raise errors.RequestError(data="该员工已设置为系统用户！")
        salt = text_captcha(5)
        # current_user.password = get_hash_password(f'{password}{salt}')
        # current_user.username = username
        # current_user.salt = salt

        await self.update(
            session=session,
            obj_in={
                "id": current_user.id,
                "salt": salt,
                "password": get_hash_password(f'{password}{salt}'),
                "username": username,
                "is_user": True,
            }
        )

        # 清空现有roles
        await crud_user_role.delete_by_fields(session, user_id=id)

        # 添加新roles
        if roles:
            for role_id in roles:
                role = await crud_role.get_by_id(session=session, id=role_id)
                if role:
                    await crud_user_role.create(
                        session=session,
                        obj_in={
                            "user_id": id,
                            "role_id": role_id
                        }
                    )
        await session.flush()
        return current_user


crud_user = CrudUser()