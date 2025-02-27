# src/apps/v1/sys/models/layout.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2025-02-14
# @Author  : lei
# @File    : layout.py
# @Software: Cursor
# @Description: 页面布局服务

from src.apps.v1.sys.crud.crud_layout import crud_layout
from src.apps.v1.sys.models.mdl_layout import Layout, LayoutCreate, LayoutUpdate
from src.common.base_crud import HookContext
from src.common.base_service import BaseService
from src.common.enums import HookTypeEnum
from src.core.exceptions import errors


class SvrLayout(BaseService[Layout, LayoutCreate, LayoutUpdate]):
    """
    页面布局服务
    """
    def __init__(self):
        self.crud = crud_layout


svr_layout = SvrLayout()
