# src/apps/v1/sys/service/svr_user.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2024/12/31
# @Author  : Aaron Zhou
# @File    : svr_user.py
# @Software: Cursor
# @Description: 用户服务
from src.apps.v1.sys.crud.user import crud_user
from src.apps.v1.sys.models.user import User, UserCreate, UserUpdate
from src.common.base_service import BaseService


class SvrUser(BaseService[User, UserCreate, UserUpdate]):
    """
    用户服务
    """


svr_user = SvrUser(crud=crud_user)
