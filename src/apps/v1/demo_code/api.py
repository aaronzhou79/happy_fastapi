# src/apps/v1/demo_code/api.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2024/12/27 17:20
# @Author  : Aaron Zhou
# @File    : api.py
# @Software: Cursor
# @Description: 演示CRUD API代码

from fastapi import Depends

from src.common.base_api import BaseAPI
from src.core.middleware.jwt import JWTBearer

from .model import Article, ArticleCreate, ArticleUpdate, Comment, CommentCreate, CommentUpdate

# 创建API实例
article_api = BaseAPI(
    model=Article,
    create_schema=ArticleCreate,
    update_schema=ArticleUpdate,
    prefix="/article",
    tags=["文章管理"],
    dependencies=[Depends(JWTBearer())],  # 添加JWT认证
    gen_delete=True,  # 启用删除接口
    cache_ttl=300,  # 缓存5分钟
)

comment_api = BaseAPI(
    model=Comment,
    create_schema=CommentCreate,
    update_schema=CommentUpdate,
    prefix="/comment",
    gen_delete=True,
    tags=["评论管理"],
)

# 添加自定义路由
@article_api.router.get("/custom", summary="自定义接口")
async def custom_route():
    return {"message": "这是一个自定义接口"}

# 获取路由
router = article_api.router
