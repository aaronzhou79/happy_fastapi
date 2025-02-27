# src/apps/v1/bas/api/cost.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2025-02-12
# @Author  : lei
# @File    : cost.py
# @Software: Cursor
# @Description: 附加费信息API

from src.apps.v1.bas.models.mdl_cost import Cost, CostBase, CostCreate, CostUpdate
from src.apps.v1.bas.service.svr_cost import svr_cost
from src.common.base_api import BaseAPI

cost_api = BaseAPI(
    module_name="bas",
    model=Cost,
    service=svr_cost,
    create_schema=CostCreate,
    update_schema=CostUpdate,
    base_schema=CostBase,
    prefix="/cost",
    gen_bulk_create=True,
    gen_bulk_delete=True,
    gen_delete=True,
    tags=["基础管理/附加费信息"],
)
