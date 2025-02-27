# src/apps/v1/bas/api/customer.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2025/2/8
# @Author  : lei
# @File    : customer.py
# @Software: Cursor
# @Description: 客户管理API
from src.apps.v1.bas.models.mdl_customer import Customer, CustomerBase, CustomerCreate, CustomerUpdate
from src.apps.v1.bas.service.svr_customer import svr_customer
from src.common.base_api import BaseAPI

customer_api = BaseAPI(
    module_name="bas",
    model=Customer,
    service=svr_customer,
    create_schema=CustomerCreate,
    update_schema=CustomerUpdate,
    base_schema=CustomerBase,
    prefix="/customer",
    gen_bulk_create=True,
    gen_bulk_delete=True,
    gen_delete=True,
    tags=["基础管理/客户管理"],
)
