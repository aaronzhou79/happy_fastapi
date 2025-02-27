# src/apps/v1/bas/api/dict_data.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2025-02-19
# @Author  : lei
# @File    : dict_data.py
# @Software: Cursor
# @Description: 字典数据API

from fastapi import BackgroundTasks, Body, Depends, Request, Response

from src.apps.v1.bas.models.mdl_dict_data import DictData, DictDataBase, DictDataCreate, DictDataUpdate
from src.apps.v1.bas.service.svr_dict_data import svr_dict_data
from src.common.base_api import BaseAPI
from src.core.responses.response_schema import ResponseModel, response_base
from src.core.security.auth_security import DependsJwtAuth
from src.core.security.permission import RequestPermission
from src.database.db_session import CurrentSession

dict_data_api = BaseAPI(
    module_name="bas",
    model=DictData,
    service=svr_dict_data,
    create_schema=DictDataCreate,
    update_schema=DictDataUpdate,
    base_schema=DictDataBase,
    prefix="/dict_data",
    gen_bulk_create=True,
    gen_bulk_delete=True,
    gen_delete=True,
    tags=["基础管理/字典数据"],
)

@dict_data_api.router.get("/get_dict_datas",
    description="获取字典数据",
    dependencies=[
        DependsJwtAuth,
    ])
async def get_dict_datas(request: Request, session: CurrentSession, dict_code: str) -> ResponseModel:
    """获取字典数据"""
    data = await svr_dict_data.get_dict_datas(session=session, dict_code=dict_code)
    return response_base.success(data=data)
