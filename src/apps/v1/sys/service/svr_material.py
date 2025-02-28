# src/apps/v1/bas/service/svr_material.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2025-02-12
# @Author  : lei
# @File    : svr_material.py
# @Software: Cursor
# @Description: 物料信息服务

from src.apps.v1.bas.crud.crud_material import crud_material
from src.apps.v1.bas.models.mdl_material import Material, MaterialCreate, MaterialUpdate
from src.common.base_crud import HookContext
from src.common.base_service import BaseService
from src.common.enums import HookTypeEnum
from src.core.exceptions import errors


class SvrMaterial(BaseService[Material, MaterialCreate, MaterialUpdate]):
    """
    物料信息服务
    """
    def __init__(self):
        self.crud = crud_material

        # Register hook
        self.crud.hook_manager.add_hook(
            hook_type=HookTypeEnum.before_create,
            func=self._handle_code,
            priority=1
        )

        self.crud.hook_manager.add_hook(
            hook_type=HookTypeEnum.before_update,
            func=self._handle_code,
            priority=1
        )

    async def _handle_code(self, context: HookContext) -> HookContext:
        """编码赋值"""
        obj_in = context.params['obj_in']
        session = context.session
        material_id = 0

        if obj_in.code:
            pass  # 如果有编号则保持不变
        else:
            obj_in.code = "自动生成"

        if hasattr(obj_in, "id"):
            material_id = obj_in.id

        rm = await crud_material.get_material(session, obj_in.code, material_id)

        if rm:
            raise errors.RequestError(data=f"物料 [{rm.name}] 已使用编码 {rm.code}")

        return context


svr_material = SvrMaterial()
