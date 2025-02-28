# src/apps/v1/bas/api/workmanship.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2025-02-12
# @Author  : lei
# @File    : workmanship.py
# @Software: Cursor
# @Description: 工艺信息API

from src.apps.v1.bas.models.mdl_workmanship import Workmanship, WorkmanshipBase, WorkmanshipCreate, WorkmanshipUpdate
from src.apps.v1.bas.service.svr_workmanship import svr_workmanship
from src.common.base_api import BaseAPI

workmanship_api = BaseAPI(
    module_name="bas",
    model=Workmanship,
    service=svr_workmanship,
    create_schema=WorkmanshipCreate,
    update_schema=WorkmanshipUpdate,
    base_schema=WorkmanshipBase,
    prefix="/workmanship",
    gen_bulk_create=True,
    gen_bulk_delete=True,
    gen_delete=True,
    tags=["基础管理/工艺信息"],
)
