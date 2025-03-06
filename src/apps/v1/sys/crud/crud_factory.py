# src/apps/v1/sys/models/factory.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2025-02-12
# @Author  : lei
# @File    : factory.py
# @Software: Cursor
# @Description: 工厂信息CRUD类

from sqlmodel import select

from src.apps.v1.sys.models.mdl_factory import Factory, FactoryCreate, FactoryUpdate
from src.common.base_crud import CRUDBase
from src.database.db_session import AuditAsyncSession


class CrudFactory(CRUDBase):
    """工厂信息CRUD类"""

    def __init__(self):
        super().__init__(
            model=Factory,
            create_model=FactoryCreate,
            update_model=FactoryUpdate,
        )


crud_factory = CrudFactory()
