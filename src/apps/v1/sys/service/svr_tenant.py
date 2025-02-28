# src/apps/v1/sys/service/svr_tenant.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2025/02/27
# @Author  : Aaron Zhou
# @File    : svr_tenant.py
# @Software: Cursor
# @Description: 账套服务
from src.apps.v1.sys.crud.crud_tenant import crud_tenant
from src.apps.v1.sys.models.mdl_tenant import Tenant, TenantCreate, TenantUpdate
from src.common.base_service import BaseService


class SvrTenant(BaseService[Tenant, TenantCreate, TenantUpdate]):
    """
    账套服务
    """
    def __init__(self):
        self.crud = crud_tenant


svr_tenant = SvrTenant()
