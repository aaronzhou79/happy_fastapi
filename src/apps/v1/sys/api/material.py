# src/apps/v1/bas/api/material.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2025-02-12
# @Author  : lei
# @File    : material.py
# @Software: Cursor
# @Description: 原片信息API

from src.apps.v1.bas.models.mdl_material import Material, MaterialBase, MaterialCreate, MaterialUpdate
from src.apps.v1.bas.service.svr_material import svr_material
from src.common.base_api import BaseAPI

material_api = BaseAPI(
    module_name="bas",
    model=Material,
    service=svr_material,
    create_schema=MaterialCreate,
    update_schema=MaterialUpdate,
    base_schema=MaterialBase,
    prefix="/material",
    gen_bulk_create=True,
    gen_bulk_delete=True,
    gen_delete=True,
    tags=["基础管理/物料信息"],
)
