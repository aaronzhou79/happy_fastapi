# src/apps/v1/bas/api/employe.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2025-02-12
# @Author  : lei
# @File    : employe.py
# @Software: Cursor
# @Description: 员工档案API

from src.apps.v1.bas.models.mdl_employe import Employe, EmployeBase, EmployeCreate, EmployeUpdate
from src.apps.v1.bas.service.svr_employe import svr_employe
from src.common.base_api import BaseAPI

employe_api = BaseAPI(
    module_name="bas",
    model=Employe,
    service=svr_employe,
    create_schema=EmployeCreate,
    update_schema=EmployeUpdate,
    base_schema=EmployeBase,
    prefix="/employe",
    gen_bulk_create=True,
    gen_bulk_delete=True,
    gen_delete=True,
    tags=["基础管理/员工档案"],
)
