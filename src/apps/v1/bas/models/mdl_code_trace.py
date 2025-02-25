# src/apps/v1/bas/models/mdl_code_trace.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2025/02/24
# @Author  : Aaron Zhou
# @File    : mdl_code_trace.py
# @Software: Cursor
# @Description: 单据编号跟踪模型

from typing import Literal

from sqlmodel import Field, SQLModel

from src.common.base_models.database_mixin import DatabaseModel
from src.common.enums import DocumentType


class CodeTraceBase(SQLModel):
    """单据编号跟踪基础模型"""
    doc_type: DocumentType = Field(..., description="单据类型")
    year: int = Field(..., description="年份")
    month: int = Field(..., description="月份")
    day: int = Field(..., description="日期")
    current_sequence: int = Field(..., description="单据序号")
    classify_code: str | None = Field(default=None, description="分类代码")


class CodeTrace(DatabaseModel, CodeTraceBase, table=True):
    """单据编号跟踪模型"""
    __tablename__: Literal["code_trace"] = "code_trace"


class CodeTraceCreate(CodeTraceBase):
    """单据编号跟踪创建模型"""


class CodeTraceUpdate(CodeTraceBase):
    """单据编号跟踪更新模型"""
    id: int = Field(..., description="主键")