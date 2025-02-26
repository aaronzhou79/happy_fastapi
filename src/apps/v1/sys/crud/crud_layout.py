# src/apps/v1/sys/models/layout.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2025-02-14
# @Author  : lei
# @File    : layout.py
# @Software: Cursor
# @Description: 页面布局CRUD类

from sqlmodel import select

from src.apps.v1.sys.models.mdl_layout import Layout, LayoutCreate, LayoutUpdate
from src.common.base_crud import CRUDBase
from src.database.db_session import AuditAsyncSession


class CrudLayout(CRUDBase):
    """页面布局CRUD类"""
    def __init__(self):
        super().__init__(
            model=Layout,
            create_model=LayoutCreate,
            update_model=LayoutUpdate,
        )


crud_layout = CrudLayout()
