# src/apps/v1/sys/models/layout.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2025-02-14
# @Author  : lei
# @File    : layout.py
# @Software: Cursor
# @Description: 页面布局API

from src.apps.v1.sys.models.mdl_layout import Layout, LayoutBase, LayoutCreate, LayoutUpdate
from src.apps.v1.sys.service.svr_layout import svr_layout
from src.common.base_api import BaseAPI

layout_api = BaseAPI(
    module_name="sys",
    model=Layout,
    service=svr_layout,
    create_schema=LayoutCreate,
    update_schema=LayoutUpdate,
    base_schema=LayoutBase,
    prefix="/layout",
    gen_bulk_create=True,
    gen_bulk_delete=True,
    gen_delete=True,
    tags=[" 系统管理/页面布局"],
)
