# src/apps/v1/init_data/init_base.py
# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2025/01/10
# @Author  : Aaron Zhou
# @File    : init_base.py
# @Software: Cursor
# @Description: 数据初始化
from src.apps.v1.sys.crud.dept import crud_dept
from src.apps.v1.sys.crud.role import crud_role
from src.apps.v1.sys.crud.user import crud_user
from src.apps.v1.sys.crud.user_role import crud_user_role
from src.apps.v1.sys.models.dept import DeptCreate
from src.apps.v1.sys.models.role import RoleCreate
from src.apps.v1.sys.models.user import UserCreate
from src.apps.v1.sys.models.user_role import UserRoleCreate
from src.common.enums import RoleStatus, UserEmpType
from src.database.db_session import AuditAsyncSession, uuid4_str


async def init_base(session: AuditAsyncSession) -> None:
    """初始化数据"""
    # 批量创建部门
    depts = []
    depts_in = [
        {
            'name': '研发部',
            'code': 'dev',
            'notes': '研发部',
            'parent_id': None,
            'children': [
                {
                    'name': '研发一部',
                    'code': 'dev_one',
                    'notes': '研发一部',
                    'parent_id': None,
                    'children': [
                        {
                            'name': '研发一部-前端',
                            'code': 'dev_one_frontend',
                            'notes': '研发一部-前端',
                            'parent_id': None,
                        },
                        {
                            'name': '研发一部-后端',
                            'code': 'dev_one_backend',
                            'notes': '研发一部-后端',
                            'parent_id': None,
                        },
                    ],
                },
                {
                    'name': '研发二部',
                    'code': 'dev_two',
                    'notes': '研发二部',
                    'parent_id': None,
                },
            ],
        },
        {
            'name': '测试部',
            'code': 'test',
            'notes': '测试部',
            'parent_id': None,
            'children': [
                {
                    'name': '测试一部',
                    'code': 'test_one',
                    'notes': '测试一部',
                    'parent_id': None,
                },
                {
                    'name': '测试二部',
                    'code': 'test_two',
                    'notes': '测试二部',
                    'parent_id': None,
                },
            ],
        },
        {
            'name': '运维部',
            'code': 'ops',
            'notes': '运维部',
            'parent_id': None,
            'children': [
                {
                    'name': '运维一部',
                    'code': 'ops_one',
                    'notes': '运维一部',
                    'parent_id': None,
                },
            ],
        },
        {
            'name': '财务部',
            'code': 'finance',
            'notes': '财务部',
            'parent_id': None,
        },
        {
            'name': '人事部',
            'code': 'hr',
            'notes': '人事部',
            'parent_id': None,
        },
    ]

    async def create_dept(dept_in: dict):
        dept = await crud_dept.create(session, obj_in=dept_in)
        if dept_in.get('children'):
            for child in dept_in['children']:
                child['parent_id'] = dept.id
                await create_dept(child)
        depts.append(dept)

    for dept_in in depts_in:
        await create_dept(dept_in)

    roles = await crud_role.bulk_create(
        session,
        [
            RoleCreate(
                name='总经理',
                code='admin',
                status=RoleStatus.ACTIVE,
            ),
            RoleCreate(
                name='部门经理',
                code='dept_manager',
                status=RoleStatus.ACTIVE,
            ),
            RoleCreate(
                name='助理',
                code='assistant',
                status=RoleStatus.ACTIVE,
            ),
            RoleCreate(
                name='员工',
                code='staff',
                status=RoleStatus.ACTIVE,
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
                password='$2b$12$RJXAtJodRw37ZQGxTPlu0OH.aN5lNXG6yvC4Tp9GIQEBmMY/YCc.m',  # noqa: S106
                salt='bcNjV',
                uuid=uuid4_str(),
                emp_type=UserEmpType.ADMIN,
                is_user=True,
                is_superuser=True,
            ),
            UserCreate(
                username='user',
                name='普通用户',
                email='user@example.com',
                password='$2b$12$RJXAtJodRw37ZQGxTPlu0OH.aN5lNXG6yvC4Tp9GIQEBmMY/YCc.m',  # noqa: S106
                salt='bcNjV',
                uuid=uuid4_str(),
                emp_type=UserEmpType.STAFF,
                is_user=True,
                is_superuser=False,
            ),
            UserCreate(
                name='张三',
                email='zhangsan@example.com',
                dept_id=depts[0].id,
                uuid=uuid4_str(),
                emp_type=UserEmpType.STAFF,
                is_user=False,
            ),
            UserCreate(
                name='李四',
                email='lis@example.com',
                dept_id=depts[0].id,
                uuid=uuid4_str(),
                emp_type=UserEmpType.STAFF,
                is_user=False,
            ),
            UserCreate(
                name='王五',
                email='wangwu@example.com',
                dept_id=depts[1].id,
                uuid=uuid4_str(),
                emp_type=UserEmpType.STAFF,
                is_user=False,
            ),
            UserCreate(
                name='赵六',
                email='zhaoliu@example.com',
                dept_id=depts[1].id,
                uuid=uuid4_str(),
                emp_type=UserEmpType.STAFF,
                is_user=False,
            ),
            UserCreate(
                name='孙七',
                email='sunqi@example.com',
                dept_id=depts[2].id,
                uuid=uuid4_str(),
                emp_type=UserEmpType.STAFF,
                is_user=False,
            ),
            UserCreate(
                name='周八',
                email='zhouba@example.com',
                dept_id=depts[2].id,
                uuid=uuid4_str(),
                emp_type=UserEmpType.STAFF,
                is_user=False,
            ),
            UserCreate(
                name='吴九',
                email='wujiu@example.com',
                dept_id=depts[3].id,
                uuid=uuid4_str(),
                emp_type=UserEmpType.STAFF,
                is_user=False,
            ),
            UserCreate(
                name='郑十',
                email='zhengshi@example.com',
                dept_id=depts[3].id,
                uuid=uuid4_str(),
                emp_type=UserEmpType.STAFF,
                is_user=False,
            ),
        ]
    )

    await crud_user_role.bulk_create(
        session,
        [
            UserRoleCreate(user_id=users[1].id, role_id=roles[0].id),
            UserRoleCreate(user_id=users[1].id, role_id=roles[1].id),
        ]
    )