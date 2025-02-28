# src/apps/v1/bas/models/mdl_employe.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2025-02-12
# @Author  : lei
# @File    : mdl_employe.py
# @Software: Cursor
# @Description: 员工档案模型

from typing import Literal
from datetime import datetime

from sqlmodel import Field, SQLModel

from src.common.base_models.database_mixin import DatabaseModel


class EmployeBase(SQLModel):
    """员工档案模型"""

    employe_no: str | None = Field(default=None, min_length=1, max_length=32, unique=True, description='工号')
    nick_name: str | None = Field(default=None, min_length=1, max_length=128, description='姓名')
    dept_id: int | None = Field(default=None, description='所属部门')
    dept_name: str | None = Field(default=None, max_length=128, description='所属部门名称')
    post_id: int | None = Field(default=None, description='岗位')
    post_name: str | None = Field(default=None, max_length=128, description='岗位名称')
    employment_type: str | None = Field(default=None, max_length=32, description='用工类型 全职、兼职')
    state: int | None = Field(default=None, description='人员状态： 1.待入职 2.试用期 3.转正 4.离职')
    phone_number: str | None = Field(default=None, max_length=32, description='联系电话')
    birthdate: datetime | None = Field(default=None, description='生日')
    sex: str | None = Field(default=None, max_length=1, description='员工性别(0男 1女 2未知)')
    qualification: str | None = Field(default=None, max_length=128, description='学历')
    mailbox: str | None = Field(default=None, max_length=128, description='邮箱')
    entry_date: datetime | None = Field(default=None, description='入职日期')
    worker_date: datetime | None = Field(default=None, description='转正日期')
    term_date: datetime | None = Field(default=None, description='离职日期')
    probation: int | None = Field(default=None, description='试用期(月)')
    contract_date_start: datetime | None = Field(default=None, description='劳动合同起始日期')
    contract_date_end: datetime | None = Field(default=None, description='劳动合同终止日期')
    native_place: str | None = Field(default=None, max_length=128, description='籍贯')
    id_card_no: str | None = Field(default=None, max_length=32, description='身份证')
    bank: str | None = Field(default=None, max_length=32, description='所属银行')
    bank_card_no: str | None = Field(default=None, max_length=32, description='银行卡号')
    current_address: str | None = Field(default=None, max_length=128, description='通讯地址')
    remark: str | None = Field(default=None, description='备注')
    age: int | None = Field(default=None, description='年龄')
    nation: str | None = Field(default=None, max_length=32, description='民族')
    marital_status: str | None = Field(default=None, max_length=32, description='婚姻状况')
    account_address: str | None = Field(default=None, max_length=128, description='户口地址')
    graduate_school: str | None = Field(default=None, max_length=128, description='毕业院校')
    major: str | None = Field(default=None, max_length=50, description='专业')
    emergency_contact_name: str | None = Field(default=None, max_length=32, description='紧急联系人')
    emergency_contact_phone: str | None = Field(default=None, max_length=20, description='紧急联系人电话')
    relationship: str | None = Field(default=None, max_length=50, description='与其关系')
    nationality: str | None = Field(default=None, max_length=50, description='国籍')
    id_expiring_date: str | None = Field(default=None, max_length=50, description='身份证有效期限')


class Employe(EmployeBase, DatabaseModel, table=True):
    """员工档案表"""

    __tablename__: Literal['bas_employe'] = 'bas_employe'

    # Relationships


class EmployeCreate(EmployeBase):
    """员工档案创建模型"""


class EmployeUpdate(EmployeBase):
    """员工档案更新模型"""

    id: int
