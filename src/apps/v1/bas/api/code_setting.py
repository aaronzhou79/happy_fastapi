# src/apps/v1/bas/api/code_setting.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2025/02/23
# @Author  : Aaron Zhou
# @File    : code_setting.py
# @Software: Cursor
# @Description: 角色管理API
from src.apps.v1.bas.models.mdl_code_setting import CodeSetting, CodeSettingBase, CodeSettingCreate, CodeSettingUpdate
from src.apps.v1.bas.service.svr_code_setting import svr_code_setting
from src.common.base_api import BaseAPI

code_setting_api = BaseAPI(
    module_name="bas",
    model=CodeSetting,
    service=svr_code_setting,
    create_schema=CodeSettingCreate,
    update_schema=CodeSettingUpdate,
    base_schema=CodeSettingBase,
    prefix="/code_setting",
    gen_delete=True,
    tags=["基础管理/编码生成"],
)
