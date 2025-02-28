# src/apps/v1/bas/models/mdl_customer.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2025/2/8
# @Author  : lei
# @File    : mdl_customer.py
# @Software: Cursor
# @Description: 客户信息模型

from typing import Any, Literal

import sqlalchemy as sa

from sqlmodel import Field, Relationship, SQLModel

from src.apps.v1.bas.models.mdl_customer_site import CustomerSite, CustomerSiteCreate
from src.common.base_models.database_mixin import DatabaseModel
from src.common.base_models.datetime_mixin import DateTimeMixin


class CustomerBase(SQLModel):
    """客户基础模型"""

    code: str = Field(..., max_length=32, unique=True, index=True, description='客户编码')
    name: str = Field(..., max_length=32, description='客户名称')
    deposit_ratio: float | None = Field(default=None, description='定金比率')
    quota: float | None = Field(default=None, description='额度')
    payment_days: int | None = Field(default=None, description='账期（天）')

    brief_name: str | None = Field(default=None, max_length=32, description='客户简称')
    alias: str | None = Field(default=None, max_length=32, description='客户别名')
    type: str | None = Field(default=None, max_length=32, description='客户类型')
    grade: str | None = Field(default=None, max_length=32, description='客户等级')
    contact: str | None = Field(default=None, max_length=32, description='联系人')
    phone: str | None = Field(default=None, max_length=32, description='联系电话')
    fax: str | None = Field(default=None, max_length=32, description='传真')
    country: str | None = Field(default=None, max_length=32, description='国家')
    province: str | None = Field(default=None, max_length=32, description="省")
    city: str | None = Field(default=None, max_length=32, description="市")
    area: str | None = Field(default=None, max_length=32, description="区")
    street: str | None = Field(default=None, max_length=128, description="街道地址")
    address: str | None = Field(default=None, max_length=128, description='地址')

    salesman: str | None = Field(default=None, max_length=32, description='业务员')
    currency: str | None = Field(default=None, max_length=32, description='币别')
    exchange_rate: float = Field(default=1, description='汇率')
    payment_provision: str | None = Field(default=None, max_length=32, description='付款条款')
    email: str | None = Field(default=None, max_length=128, description='邮箱')
    zip_code: str | None = Field(default=None, max_length=32, description='邮编')
    password: str | None = Field(default=None, max_length=32, description='平台登录密码')
    valid: bool = Field(default=True, description='是否生效')
    notes: str | None = Field(default=None, sa_type=sa.Text, description="备注")


class Customer(CustomerBase, DateTimeMixin, DatabaseModel, table=True):
    """客户表"""

    __tablename__: Literal['bas_customer'] = 'bas_customer'

    # Relationships
    sites: list['CustomerSite'] = Relationship()


class CustomerCreate(CustomerBase):
    """客户创建模型"""
    sites: list[CustomerSiteCreate]


class CustomerUpdate(CustomerBase):
    """客户更新模型"""

    id: int
    sites: list[CustomerSiteCreate]

    def model_dump(self, **kwargs) -> dict[str, Any]:
        """自定义序列化方法，排除字段"""
        exclude = kwargs.get('exclude', set())
        exclude.add('sites')
        kwargs['exclude'] = exclude
        return super().model_dump(**kwargs)
