# src/apps/v1/sys/models/factory.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2025-02-12
# @Author  : lei
# @File    : factory.py
# @Software: Cursor
# @Description: 工厂信息服务

from src.apps.v1.sys.crud.crud_factory import crud_factory
from src.apps.v1.sys.models.mdl_factory import Factory, FactoryCreate, FactoryUpdate
from src.common.base_crud import HookContext
from src.common.base_service import BaseService
from src.common.enums import HookTypeEnum
from src.core.exceptions import errors


class SvrFactory(BaseService[Factory, FactoryCreate, FactoryUpdate]):
    """
    工厂信息服务
    """

    def __init__(self):
        self.crud = crud_factory


svr_factory = SvrFactory()
