# src/apps/v1/init_data/__init__.py
# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2024/12/29
# @Author  : Aaron Zhou
# @File    : __init__.py
# @Software: Cursor
# @Description: 数据初始化

from src.apps.v1.demo_code.model import Article, Comment, Department, User
from src.database.db_session import async_session


async def init_data():
    async with async_session() as session:
        # 设置查询会话
        Department.query_session = session
        User.query_session = session
        Article.query_session = session
        Comment.query_session = session

        # 批量创建部门
        depts = await Department.bulk_create([
            {'name': '研发部'},
            {'name': '测试部'},
            {'name': '运维部'},
            {'name': '人事部'},
            {'name': '财务部'},
            {'name': '市场部'},
            {'name': '行政部'},
            {'name': '法务部'},
        ])

        # 批量创建用户
        users = await User.bulk_create([
            {'name': '张三', 'email': 'zhangsan@example.com', 'password': '123456', 'dept_id': depts[0].id},
            {'name': '李四', 'email': 'lisi@example.com', 'password': '123456', 'dept_id': depts[0].id},
            {'name': '王五', 'email': 'wangwu@example.com', 'password': '123456', 'dept_id': depts[1].id},
            {'name': '赵六', 'email': 'zhaoliu@example.com', 'password': '123456', 'dept_id': depts[1].id},
            {'name': '孙七', 'email': 'sunqi@example.com', 'password': '123456', 'dept_id': depts[2].id},
            {'name': '周八', 'email': 'zhouba@example.com', 'password': '123456', 'dept_id': depts[2].id},
            {'name': '吴九', 'email': 'wujiu@example.com', 'password': '123456', 'dept_id': depts[3].id},
            {'name': '郑十', 'email': 'zhengshi@example.com', 'password': '123456', 'dept_id': depts[3].id},
        ])

        # 批量创建文章
        articles = await Article.bulk_create([
            {'title': '文章1', 'content': '文章内容1', 'author_id': users[0].id},
            {'title': '文章2', 'content': '文章内容2', 'author_id': users[1].id},
            {'title': '文章1_1', 'content': '文章内容1_1', 'author_id': users[0].id},
            {'title': '文章2_1', 'content': '文章内容2_1', 'author_id': users[1].id}
        ])

        # 批量创建评论
        await Comment.bulk_create([
            {'content': '评论内容1', 'article_id': articles[0].id},
            {'content': '评论内容2', 'article_id': articles[1].id},
            {'content': '评论内容1_1', 'article_id': articles[2].id},
            {'content': '评论内容2_1', 'article_id': articles[3].id}
        ])

        await session.commit()
