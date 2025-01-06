# src/apps/v1/init_data/__init__.py
# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2024/12/29
# @Author  : Aaron Zhou
# @File    : __init__.py
# @Software: Cursor
# @Description: 数据初始化
from src.apps.v1.sys.models import Dept, Role, User
from src.common.enums import UserEmpType
from src.database.db_session import async_session as async_session
from src.database.db_session import uuid4_str


async def init_data() -> None:
    """初始化数据"""
    async with async_session() as session:
        # 批量创建部门
        depts = await Dept.bulk_create(
            session,
            [
                {'name': '研发部'},
                {'name': '测试部'},
                {'name': '运维部'},
                {'name': '人事部'},
                {'name': '财务部'},
                {'name': '市场部'},
                {'name': '行政部'},
                {'name': '法务部'},
            ]
        )
        if depts is None:
            return

        # 批量创建用户
        await User.bulk_create(
            session,
            [
                {
                    'username': 'admin',
                    'name': '超级管理员',
                    'email': 'admin@example.com',
                    'password': '$2b$12$RJXAtJodRw37ZQGxTPlu0OH.aN5lNXG6yvC4Tp9GIQEBmMY/YCc.m',
                    'salt': 'bcNjV',
                    'uuid': uuid4_str(),
                    'emp_type': UserEmpType.admin,
                    'is_user': True,
                },
                {
                    'name': '张三',
                    'email': 'zhangsan@example.com',
                    'dept_id': depts[0].id,
                    'uuid': uuid4_str(),
                    'emp_type': UserEmpType.staff,
                    'is_user': False,
                },
                {
                    'name': '李四',
                    'email': 'lis@example.com',
                    'dept_id': depts[0].id,
                    'uuid': uuid4_str(),
                    'emp_type': UserEmpType.staff,
                    'is_user': False,
                },
                {
                    'name': '王五',
                    'email': 'wangwu@example.com',
                    'dept_id': depts[1].id,
                    'uuid': uuid4_str(),
                    'emp_type': UserEmpType.staff,
                    'is_user': False,
                },
                {
                    'name': '赵六',
                    'email': 'zhaoliu@example.com',
                    'dept_id': depts[1].id,
                    'uuid': uuid4_str(),
                    'emp_type': UserEmpType.staff,
                    'is_user': False,
                },
                {
                    'name': '孙七',
                    'email': 'sunqi@example.com',
                    'dept_id': depts[2].id,
                    'uuid': uuid4_str(),
                    'emp_type': UserEmpType.staff,
                    'is_user': False,
                },
                {
                    'name': '周八',
                    'email': 'zhouba@example.com',
                    'dept_id': depts[2].id,
                    'uuid': uuid4_str(),
                    'emp_type': UserEmpType.staff,
                    'is_user': False,
                },
                {
                    'name': '吴九',
                    'email': 'wujiu@example.com',
                    'dept_id': depts[3].id,
                    'uuid': uuid4_str(),
                    'emp_type': UserEmpType.staff,
                    'is_user': False,
                },
                {
                    'name': '郑十',
                    'email': 'zhengshi@example.com',
                    'dept_id': depts[3].id,
                    'uuid': uuid4_str(),
                    'emp_type': UserEmpType.staff,
                    'is_user': False,
                },
            ]
        )

        await Role.bulk_create(
            session,
            [
                {'name': '总经理'},
                {'name': '部门经理'},
                {'name': '助理'},
                {'name': '员工'},
            ]
        )

        await session.commit()
