# src/apps/v1/bas/api/currency.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2025-02-12
# @Author  : lei
# @File    : currency.py
# @Software: Cursor
# @Description: 货币信息API

from src.apps.v1.bas.models.mdl_currency import Currency, CurrencyBase, CurrencyCreate, CurrencyUpdate
from src.apps.v1.bas.service.svr_currency import svr_currency
from src.common.base_api import BaseAPI

currency_api = BaseAPI(
    module_name="bas",
    model=Currency,
    service=svr_currency,
    create_schema=CurrencyCreate,
    update_schema=CurrencyUpdate,
    base_schema=CurrencyBase,
    prefix="/currency",
    gen_bulk_create=True,
    gen_bulk_delete=True,
    gen_delete=True,
    tags=["基础管理/货币信息"],
)
