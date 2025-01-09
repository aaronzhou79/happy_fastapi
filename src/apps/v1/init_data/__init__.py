# src/apps/v1/init_data/__init__.py
# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2024/12/29
# @Author  : Aaron Zhou
# @File    : __init__.py
# @Software: Cursor
# @Description: 数据初始化
from typing import Sequence

from src.apps.v1.sys.crud.dept import crud_dept
from src.apps.v1.sys.crud.role import crud_role
from src.apps.v1.sys.crud.user import crud_user
from src.apps.v1.sys.crud.user_role import crud_user_role
from src.apps.v1.sys.models.dept import Dept, DeptCreate
from src.apps.v1.sys.models.role import Role, RoleCreate
from src.apps.v1.sys.models.user import User, UserCreate
from src.apps.v1.sys.models.user_role import UserRole, UserRoleCreate
from src.common.enums import RoleStatusType, UserEmpType
from src.database.db_session import async_session as async_session
from src.database.db_session import uuid4_str


async def init_data() -> None:
    """初始化数据"""
    async with async_session() as session:
        # 批量创建部门
        depts = await crud_dept.bulk_create(
            session,
            [
                DeptCreate(
                    name='研发部',
                    code='dev',
                    notes='研发部',
                ),
                DeptCreate(
                    name='测试部',
                    code='test',
                    notes='测试部',
                ),
                DeptCreate(
                    name='运维部',
                    code='ops',
                    notes='运维部',
                ),
                DeptCreate(
                    name='财务部',
                    code='finance',
                    notes='财务部',
                ),
                DeptCreate(
                    name='人事部',
                    code='hr',
                    notes='人事部',
                ),
                DeptCreate(
                    name='市场部',
                    code='market',
                    notes='市场部',
                ),
                DeptCreate(
                    name='法务部',
                    code='law',
                    notes='法务部',
                ),
                DeptCreate(
                    name='行政部',
                    code='admin',
                    notes='行政部',
                ),
                DeptCreate(
                    name='后勤部',
                    code='logistics',
                    notes='后勤部',
                ),
            ]
        )

        roles = await crud_role.bulk_create(
            session,
            [
                RoleCreate(
                    name='总经理',
                    code='admin',
                    status=RoleStatusType.active,
                ),
                RoleCreate(
                    name='部门经理',
                    code='dept_manager',
                    status=RoleStatusType.active,
                ),
                RoleCreate(
                    name='助理',
                    code='assistant',
                    status=RoleStatusType.active,
                ),
                RoleCreate(
                    name='员工',
                    code='staff',
                    status=RoleStatusType.active,
                ),
            ]
        )

        # 批量创建用户
        users = await crud_user.bulk_create(
            session,
            [
                UserCreate(
                    username='admin',
                    name='超级管理员',
                    email='admin@example.com',
                    password='$2b$12$RJXAtJodRw37ZQGxTPlu0OH.aN5lNXG6yvC4Tp9GIQEBmMY/YCc.m',
                    salt='bcNjV',
                    uuid=uuid4_str(),
                    emp_type=UserEmpType.admin,
                    is_user=True,
                ),
                UserCreate(
                    name='张三',
                    email='zhangsan@example.com',
                    dept_id=depts[0].id,
                    uuid=uuid4_str(),
                    emp_type=UserEmpType.staff,
                    is_user=False,
                ),
                UserCreate(
                    name='李四',
                    email='lis@example.com',
                    dept_id=depts[0].id,
                    uuid=uuid4_str(),
                    emp_type=UserEmpType.staff,
                    is_user=False,
                ),
                UserCreate(
                    name='王五',
                    email='wangwu@example.com',
                    dept_id=depts[1].id,
                    uuid=uuid4_str(),
                    emp_type=UserEmpType.staff,
                    is_user=False,
                ),
                UserCreate(
                    name='赵六',
                    email='zhaoliu@example.com',
                    dept_id=depts[1].id,
                    uuid=uuid4_str(),
                    emp_type=UserEmpType.staff,
                    is_user=False,
                ),
                UserCreate(
                    name='孙七',
                    email='sunqi@example.com',
                    dept_id=depts[2].id,
                    uuid=uuid4_str(),
                    emp_type=UserEmpType.staff,
                    is_user=False,
                ),
                UserCreate(
                    name='周八',
                    email='zhouba@example.com',
                    dept_id=depts[2].id,
                    uuid=uuid4_str(),
                    emp_type=UserEmpType.staff,
                    is_user=False,
                ),
                UserCreate(
                    name='吴九',
                    email='wujiu@example.com',
                    dept_id=depts[3].id,
                    uuid=uuid4_str(),
                    emp_type=UserEmpType.staff,
                    is_user=False,
                ),
                UserCreate(
                    name='郑十',
                    email='zhengshi@example.com',
                    dept_id=depts[3].id,
                    uuid=uuid4_str(),
                    emp_type=UserEmpType.staff,
                    is_user=False,
                ),
            ]
        )

        await crud_user_role.bulk_create(
            session,
            [
                UserRoleCreate(user_id=users[0].id, role_id=roles[0].id),
                UserRoleCreate(user_id=users[0].id, role_id=roles[1].id),
            ]
        )

        await session.commit()