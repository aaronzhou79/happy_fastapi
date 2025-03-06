# src/apps/v1/sys/api/tenant.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2025/02/27
# @Author  : Aaron Zhou
# @File    : tenant.py
# @Software: Cursor
# @Description: 账套管理API
from src.apps.v1.sys.models.mdl_tenant import (
    Tenant,
    TenantBase,
    TenantCreate,
    TenantUpdate,
)
from src.apps.v1.sys.service.svr_tenant import svr_tenant
from src.common.base_api import BaseAPI

tenant_api = BaseAPI(
    module_name="sys",
    model=Tenant,
    service=svr_tenant,
    create_schema=TenantCreate,
    update_schema=TenantUpdate,
    base_schema=TenantBase,
    prefix="/tenant",
    gen_bulk_create=True,
    gen_bulk_delete=True,
    gen_delete=True,
    tags=["系统管理/账套管理"],
)
