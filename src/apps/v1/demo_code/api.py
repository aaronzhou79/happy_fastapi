# src/apps/v1/demo_code/api.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2024/12/27 17:20
# @Author  : Aaron Zhou
# @File    : api.py
# @Software: Cursor
# @Description: 演示CRUD API代码

from src.common.base_api import BaseAPI

from .model import Article, ArticleCreate, ArticleUpdate, Comment, CommentCreate, CommentUpdate

# 创建API实例
article_api = BaseAPI(
    model=Article,
    create_schema=ArticleCreate,
    update_schema=ArticleUpdate,
    prefix="/article",
    gen_delete=True,
    tags=["文章管理"],
)

comment_api = BaseAPI(
    model=Comment,
    create_schema=CommentCreate,
    update_schema=CommentUpdate,
    prefix="/comment",
    gen_delete=True,
    tags=["评论管理"],
)
