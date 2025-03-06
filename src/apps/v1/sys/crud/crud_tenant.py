# src/apps/v1/sys/crud/crud_tenant.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2024/12/31
# @Author  : Aaron Zhou
# @File    : crud_tenant.py
# @Software: Cursor
# @Description: 账套相关CRUD类


from src.apps.v1.sys.models.mdl_tenant import Tenant, TenantCreate, TenantUpdate
from src.common.base_crud import CRUDBase


class CrudTenant(CRUDBase):
    """账套相关CRUD类"""

    def __init__(self):
        super().__init__(
            model=Tenant,
            create_model=TenantCreate,
            update_model=TenantUpdate,
        )


crud_tenant = CrudTenant()
