# src/apps/v1/init_data/__init__.py
# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2024/12/29
# @Author  : Aaron Zhou
# @File    : __init__.py
# @Software: Cursor
# @Description: 数据初始化
from src.apps.v1.sys.models import Dept, Role, User
from src.database.db_session import async_session as async_session


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
                {'name': '张三', 'email': 'zhangsan@example.com', 'password': '123456', 'dept_id': depts[0].id},
                {'name': '李四', 'email': 'lisi@example.com', 'password': '123456', 'dept_id': depts[0].id},
                {'name': '王五', 'email': 'wangwu@example.com', 'password': '123456', 'dept_id': depts[1].id},
                {'name': '赵六', 'email': 'zhaoliu@example.com', 'password': '123456', 'dept_id': depts[1].id},
                {'name': '孙七', 'email': 'sunqi@example.com', 'password': '123456', 'dept_id': depts[2].id},
                {'name': '周八', 'email': 'zhouba@example.com', 'password': '123456', 'dept_id': depts[2].id},
                {'name': '吴九', 'email': 'wujiu@example.com', 'password': '123456', 'dept_id': depts[3].id},
                {'name': '郑十', 'email': 'zhengshi@example.com', 'password': '123456', 'dept_id': depts[3].id},
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
