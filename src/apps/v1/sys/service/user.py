# src/apps/v1/sys/service/svr_user.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2024/12/31
# @Author  : Aaron Zhou
# @File    : svr_user.py
# @Software: Cursor
# @Description: 用户服务
from src.apps.v1.sys.crud.role import crud_role
from src.apps.v1.sys.crud.user import crud_user
from src.apps.v1.sys.crud.user_role import crud_user_role
from src.apps.v1.sys.models.user import User, UserCreate, UserCreateWithRoles, UserUpdate
from src.apps.v1.sys.models.user_role import UserRoleCreate
from src.common.base_service import BaseService
from src.common.enums import HookTypeEnum
from src.core.exceptions import errors
from src.database.db_session import AuditAsyncSession
from src.utils.encrypt import generate_salt, hash_password


class SvrUser(BaseService[User, UserCreate, UserUpdate]):
    """
    用户服务
    """
    def __init__(self):
        self.crud = crud_user
        # 注册 after_create 钩子
        self.add_hook(HookTypeEnum.after_create, self._handle_roles)

    async def _handle_roles(self, session: AuditAsyncSession, db_obj: User, obj_in: UserCreateWithRoles) -> None:
        """处理用户角色关联

        Args:
            session: 数据库会话
            db_obj: 创建的用户对象
            obj_in: 输入的创建数据
        """
        if hasattr(obj_in, 'roles') and obj_in.roles:
            # 验证所有role_id是否存在
            invalid_roles = []
            for role_id in obj_in.roles:
                role = await crud_role.get_by_id(session=session, id=role_id)
                if not role:
                    invalid_roles.append(role_id)

            if invalid_roles:
                raise errors.RequestError(data=f"角色ID {invalid_roles} 不存在")

            # 创建用户角色关联
            for role_id in obj_in.roles:
                await crud_user_role.create(
                    session=session,
                    obj_in=UserRoleCreate(
                        user_id=db_obj.id,
                        role_id=role_id
                    )
                )

    async def create(self, session: AuditAsyncSession, obj_in: UserCreateWithRoles) -> User:
        """创建用户"""
        # 生成盐值和密码哈希
        salt = generate_salt()
        if obj_in.password:
            password_hash = hash_password(obj_in.password, salt)
            obj_in.password = password_hash
            obj_in.salt = salt

        return await super().create(session=session, obj_in=obj_in)


svr_user = SvrUser()
