# src/apps/v1/sys/models/factory.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2025-02-12
# @Author  : lei
# @File    : factory.py
# @Software: Cursor
# @Description: 工厂信息API

from src.apps.v1.sys.models.mdl_factory import (
    Factory,
    FactoryBase,
    FactoryCreate,
    FactoryUpdate,
)
from src.apps.v1.sys.service.svr_factory import svr_factory
from src.common.base_api import BaseAPI

factory_api = BaseAPI(
    module_name="sys",
    model=Factory,
    service=svr_factory,
    create_schema=FactoryCreate,
    update_schema=FactoryUpdate,
    base_schema=FactoryBase,
    prefix="/factory",
    gen_bulk_create=True,
    gen_bulk_delete=True,
    gen_delete=True,
    tags=["系统管理/工厂信息"],
)
