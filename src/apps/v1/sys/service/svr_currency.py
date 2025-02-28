# src/apps/v1/bas/service/svr_currency.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2025-02-12
# @Author  : lei
# @File    : svr_currency.py
# @Software: Cursor
# @Description: 货币信息服务

from src.apps.v1.bas.crud.crud_currency import crud_currency
from src.apps.v1.bas.models.mdl_currency import Currency, CurrencyCreate, CurrencyUpdate
from src.common.base_crud import HookContext
from src.common.base_service import BaseService
from src.common.enums import HookTypeEnum
from src.core.exceptions import errors


class SvrCurrency(BaseService[Currency, CurrencyCreate, CurrencyUpdate]):
    """
    货币信息服务
    """
    def __init__(self):
        self.crud = crud_currency

    # Register hook
        self.add_hook(HookTypeEnum.before_create, self._handle_code)
        self.add_hook(HookTypeEnum.before_update, self._handle_code)

    async def _handle_code(self, context: HookContext) -> HookContext:
        """编码赋值"""
        obj_in = context.params['obj_in']
        session = context.session
        obj_id = 0

        if obj_in.code:
            pass  # 如果有编号则保持不变
        else:
            obj_in.code = "自动生成"

        if hasattr(obj_in, "id"):
            obj_id = obj_in.id

        exists = await self.crud.get_currency(session, obj_in.code, obj_id)

        if exists:
            raise errors.RequestError(data=f" [{exists.name}] 已使用编码 {exists.code}")

        return context


svr_currency = SvrCurrency()
