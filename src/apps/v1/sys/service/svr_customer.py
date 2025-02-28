# src/apps/v1/bas/service/svr_customer.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2025/2/8
# @Author  : lei
# @File    : svr_customer.py
# @Software: Cursor
# @Description: 客户信息服务

from src.apps.v1.bas.crud.crud_customer import crud_customer
from src.apps.v1.bas.crud.crud_customer_site import crud_customer_site
from src.apps.v1.bas.models.mdl_customer import Customer, CustomerCreate, CustomerUpdate
from src.common.base_crud import HookContext
from src.common.base_service import BaseService
from src.common.enums import HookTypeEnum
from src.core.exceptions import errors


class SvrCustomer(BaseService[Customer, CustomerCreate, CustomerUpdate]):
    """
    客户信息服务
    """
    def __init__(self):
        self.crud = crud_customer

        # Register hook
        self.crud.hook_manager.add_hook(
            hook_type=HookTypeEnum.before_create,  # 创建之前
            func=self._handle_code,
            priority=1
        )

        self.crud.hook_manager.add_hook(
            hook_type=HookTypeEnum.before_update,  # 修改之前
            func=self._handle_code,
            priority=1
        )

        self.crud.hook_manager.add_hook(
            hook_type=HookTypeEnum.after_update,  # 修改之后
            func=self._sync_customer_sites,
            priority=1
        )

    async def _handle_code(self, context: HookContext) -> HookContext:
        """编码赋值"""
        obj_in = context.params['obj_in']
        session = context.session
        customer_id = 0

        if obj_in.code:
            pass  # 如果有编号则保持不变
        else:
            obj_in.code = "自动生成"

        if hasattr(obj_in, "id"):
            customer_id = obj_in.id

        customer_name = await self.crud.get_customer(session, obj_in.code, customer_id)

        if customer_name:
            raise errors.RequestError(data=f"客户[{customer_name}] 已使用编码 {obj_in.code}")

        return context

    async def _sync_customer_sites(self, context: HookContext) -> HookContext:
        """同步客户工地"""
        obj_in = context.params['obj_in']
        session = context.session
        sites = []

        if hasattr(obj_in, "sites"):
            if obj_in.sites:
                for site in obj_in.sites:
                    site.customer_id = obj_in.id
                    sites.append(site)

        await crud_customer_site.sync_customer_sites(session, obj_in.id, sites)

    def set_customer(self, customer: Customer) -> Customer:
        """设置数据"""
        if customer.sites:
            for site in customer.sites:
                site.customer_id = customer.id

        return customer


svr_customer = SvrCustomer()
