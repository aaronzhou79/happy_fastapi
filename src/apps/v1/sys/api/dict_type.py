# src/apps/v1/bas/api/dict_type.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2025-02-19
# @Author  : lei
# @File    : dict_type.py
# @Software: Cursor
# @Description: 字典类型API

from src.apps.v1.bas.models.mdl_dict_type import DictType, DictTypeBase, DictTypeCreate, DictTypeUpdate
from src.apps.v1.bas.service.svr_dict_type import svr_dict_type
from src.common.base_api import BaseAPI

dict_type_api = BaseAPI(
    module_name="bas",
    model=DictType,
    service=svr_dict_type,
    create_schema=DictTypeCreate,
    update_schema=DictTypeUpdate,
    base_schema=DictTypeBase,
    prefix="/dict_type",
    gen_bulk_create=True,
    gen_bulk_delete=True,
    gen_delete=True,
    tags=["基础管理/字典类型"],
)
