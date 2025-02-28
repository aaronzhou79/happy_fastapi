# src/apps/v1/bas/models/mdl_customer_site.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2025/2/8
# @Author  : lei
# @File    : mdl_customer_site.py
# @Software: Cursor
# @Description: 客户工地信息模型

from typing import Literal

import sqlalchemy as sa

from sqlmodel import Field, SQLModel

from src.common.base_models.database_mixin import DatabaseModel


class CustomerSiteBase(SQLModel):
    """客户工地基础模型"""

    customer_id: int | None = Field(default=None, foreign_key="bas_customer.id", ondelete='CASCADE')
    construction_site: str | None = Field(default=None, max_length=128, description="工地名称")
    contact: str | None = Field(default=None, max_length=32, description="联系人")
    phone: str | None = Field(default=None, max_length=32, description="联系电话")
    country: str | None = Field(default=None, max_length=32, description="国家")
    province: str | None = Field(default=None, max_length=32, description="省")
    city: str | None = Field(default=None, max_length=32, description="市")
    area: str | None = Field(default=None, max_length=32, description="区")
    street: str | None = Field(default=None, max_length=128, description="街道")
    address: str | None = Field(default=None, max_length=256, description="地址")
    salesman: str | None = Field(default=None, max_length=32, description="业务员")
    currency: str | None = Field(default=None, max_length=32, description="币别")
    exchange_rate: float | None = Field(default=1, description="汇率")
    pay_mode: str | None = Field(default=None, max_length=32, description="支付方式")
    payment_provision: str | None = Field(default=None, max_length=32, description="付款条款")
    transport: str | None = Field(default=None, max_length=32, description="运输方式")
    pack_mode: str | None = Field(default=None, max_length=32, description="包装方式")
    valid: bool = Field(default=True, description="是否生效")
    notes: str | None = Field(default=None, description="备注")


class CustomerSite(CustomerSiteBase, DatabaseModel, table=True):
    """客户工地表"""
    __tablename__: Literal["bas_customer_site"] = "bas_customer_site"
    __table_args__ = (
        sa.Index('idx_site_customer_id', 'customer_id'),
    )


class CustomerSiteCreate(CustomerSiteBase):
    """客户工地创建模型"""


class CustomerSiteUpdate(CustomerSiteBase):
    """客户工地更新模型"""
    id: int
