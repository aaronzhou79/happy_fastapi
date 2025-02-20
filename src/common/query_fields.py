# src/common/data_model/query_fields.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2024/12/30
# @Author  : Aaron Zhou
# @File    : query_fields.py
# @Software: Cursor
# @Description: 用于生成查询条件
"""
用于生成查询条件
"""
from enum import Enum
from typing import Any, Literal, Union

import sqlalchemy as sa

from pydantic import BaseModel, Field, ValidationInfo, field_validator
from sqlalchemy.sql.elements import ColumnElement


class FilterOperator(str, Enum):
    """过滤操作符"""
    EQ = "eq"  # 等于
    NE = "ne"  # 不等于
    GT = "gt"  # 大于
    GE = "ge"  # 大于等于
    LT = "lt"  # 小于
    LE = "le"  # 小于等于
    IN = "in"  # 在列表中
    NIN = "nin"  # 不在列表中
    LIKE = "like"  # 模糊匹配
    ILIKE = "ilike"  # 不区分大小写的模糊匹配
    IS_NULL = "is_null"  # 为空
    NOT_NULL = "not_null"  # 不为空


class LogicalOperator(str, Enum):
    """逻辑运算符"""
    AND = "and"
    OR = "or"
    NOT = "not"


class FilterCondition(BaseModel):
    """过滤条件"""
    field: str
    op: FilterOperator | Literal["=", ">", "<", ">=", "<=", "!="]
    value: Any | None = None

    @field_validator('value')
    @classmethod
    def validate_value(cls, v: Any, info: ValidationInfo) -> Any:
        """
        验证 value 的值

        对于 IS_NULL 和 NOT_NULL 操作符,value 应该为 None
        """
        if info.data.get('op') in [FilterOperator.IS_NULL, FilterOperator.NOT_NULL]:
            return None
        return v


class FilterGroup(BaseModel):
    """过滤条件组"""
    couple: LogicalOperator = LogicalOperator.AND
    conditions: list[Union[FilterCondition, 'FilterGroup']] = Field(
        description="过滤条件列表,每个条件可以是 FilterCondition 或 FilterGroup"
    )

    @field_validator('conditions')
    @classmethod
    def validate_conditions(
        cls,
        v: list[Union[FilterCondition, 'FilterGroup']],
    ) -> list[Union[FilterCondition, 'FilterGroup']]:
        """
        验证 conditions 的值

        如果 conditions 为空,则抛出 ValueError
        """
        if not v:
            raise ValueError("conditions 不能为空")
        return v

    def _build_condition(self, field: Any, op: FilterOperator | str, value: Any) -> ColumnElement[bool]:
        """构建单个查询条件"""
        operators = {
            FilterOperator.EQ: lambda: field == value,
            "=": lambda: field == value,
            FilterOperator.NE: lambda: field != value,
            "!=": lambda: field != value,
            FilterOperator.GT: lambda: field > value,
            ">": lambda: field > value,
            FilterOperator.GE: lambda: field >= value,
            ">=": lambda: field >= value,
            FilterOperator.LT: lambda: field < value,
            "<": lambda: field < value,
            FilterOperator.LE: lambda: field <= value,
            "<=": lambda: field <= value,
            FilterOperator.IN: lambda: field.in_(value),
            FilterOperator.NIN: lambda: ~field.in_(value),
            FilterOperator.LIKE: lambda: field.like(f"%{value}%"),
            FilterOperator.ILIKE: lambda: field.ilike(f"%{value}%"),
            FilterOperator.IS_NULL: lambda: field.is_(None),
            FilterOperator.NOT_NULL: lambda: ~field.is_(None),
        }
        return operators[op]()

    def build_query(self, model_class: type) -> ColumnElement[bool]:
        """构建SQLAlchemy查询条件"""
        clauses = []
        for condition in self.conditions:
            if isinstance(condition, FilterGroup):
                clauses.append(condition.build_query(model_class))
            else:
                field = getattr(model_class, condition.field)
                clauses.append(self._build_condition(field, condition.op, condition.value))

        match self.couple:
            case LogicalOperator.AND:
                return sa.and_(*clauses)
            case LogicalOperator.OR:
                return sa.or_(*clauses)
            case LogicalOperator.NOT:
                return sa.not_(clauses[0] if clauses else sa.true())


class SortOrder(str, Enum):
    """排序方向"""
    ASC = "asc"
    DESC = "desc"


class SortField(BaseModel):
    """排序字段"""
    field: str = Field(default="id", description="排序字段")
    order: SortOrder = Field(default=SortOrder.DESC, description="排序方向")


class QueryOptions(BaseModel):
    """查询选项"""
    filters: FilterGroup | None = None
    sort: list[SortField] | None = None
    offset: int = 0
    limit: int = 100