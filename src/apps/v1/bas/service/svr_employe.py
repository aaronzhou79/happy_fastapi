# src/apps/v1/bas/service/svr_employe.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2025-02-12
# @Author  : lei
# @File    : svr_employe.py
# @Software: Cursor
# @Description: 员工档案服务

from src.apps.v1.bas.crud.crud_employe import crud_employe
from src.apps.v1.bas.models.mdl_employe import Employe, EmployeCreate, EmployeUpdate
from src.common.base_crud import HookContext
from src.common.base_service import BaseService
from src.common.enums import HookTypeEnum
from src.core.exceptions import errors


class SvrEmploye(BaseService[Employe, EmployeCreate, EmployeUpdate]):
    """
    员工档案服务
    """
    def __init__(self):
        self.crud = crud_employe

    # Register hook
        self.add_hook(HookTypeEnum.before_create, self._handle_code)
        self.add_hook(HookTypeEnum.before_update, self._handle_code)

    async def _handle_code(self, context: HookContext) -> HookContext:
        """编码赋值"""
        obj_in = context.params['obj_in']
        session = context.session
        obj_id = 0

        if obj_in.employe_no:
            pass  # 如果有编号则保持不变
        else:
            obj_in.employe_no = "自动生成"

        if hasattr(obj_in, "id"):
            obj_id = obj_in.id

        exists = await self.crud.get_employe(session, obj_in.employe_no, obj_id)

        if exists:
            raise errors.RequestError(data=f" [{exists.nick_name}] 已使用工号 {exists.employe_no}")

        return context


svr_employe = SvrEmploye()
