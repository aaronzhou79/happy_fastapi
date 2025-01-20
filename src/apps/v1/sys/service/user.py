# src/apps/v1/sys/service/svr_user.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2024/12/31
# @Author  : Aaron Zhou
# @File    : svr_user.py
# @Software: Cursor
# @Description: 用户服务
from typing import Sequence

from src.apps.v1.sys.crud.permission import crud_permission
from src.apps.v1.sys.crud.role import crud_role
from src.apps.v1.sys.crud.user import crud_user
from src.apps.v1.sys.crud.user_role import crud_user_role
from src.apps.v1.sys.models.permission import Permission
from src.apps.v1.sys.models.user import User, UserCreate, UserUpdate
from src.apps.v1.sys.models.user_role import UserRoleCreate
from src.common.base_crud import HookContext
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
        # Register hook
        self.crud.hook_manager.add_hook(
            hook_type=HookTypeEnum.before_create,
            func=self._create_password,
            priority=1
        )

        self.crud.hook_manager.add_hook(
            hook_type=HookTypeEnum.after_create,
            func=self._handle_roles,
            priority=1
        )

    async def _handle_roles(self, context: HookContext) -> None:
        """处理用户角色关联"""
        db_obj = context.params['db_obj']
        obj_in = context.params['obj_in']
        session = context.session

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

    async def _create_password(self, context: HookContext) -> HookContext:
        """创建用户"""
        # 生成盐值和密码哈希
        salt = generate_salt()
        obj_in = context.params['obj_in']
        if obj_in.password:
            password_hash = hash_password(obj_in.password, salt)
            obj_in.password = password_hash
            obj_in.salt = salt
        else:
            raise errors.RequestError(data="密码不能为空")

        context.results['modified_data'] = obj_in

        return context

    async def get_permissions(self, session: AuditAsyncSession, user_id: int, is_superuser: bool) -> Sequence[Permission]:
        """获取用户权限"""
        return await crud_permission.get_permissions_by_user(session=session, user_id=user_id, is_superuser=is_superuser)


svr_user = SvrUser()
