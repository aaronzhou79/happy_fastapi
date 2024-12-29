from enum import Enum
from typing import Any, Literal, Union

import sqlalchemy as sa

from pydantic import BaseModel, Field, field_validator
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
    def validate_value(cls, v, info):
        # 对于 IS_NULL 和 NOT_NULL 操作符,value 应该为 None
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
    def validate_conditions(cls, v):
        if not v:
            raise ValueError("conditions 不能为空")
        return v

    def build_query(self, model_class) -> ColumnElement[bool]:
        """构建SQLAlchemy查询条件"""
        clauses = []
        for condition in self.conditions:
            if isinstance(condition, FilterGroup):
                clauses.append(condition.build_query(model_class))
            else:
                field = getattr(model_class, condition.field)
                value = condition.value

                match condition.op:
                    case FilterOperator.EQ | "=":
                        clause = field == value
                    case FilterOperator.NE | "!=":
                        clause = field != value
                    case FilterOperator.GT | ">":
                        clause = field > value
                    case FilterOperator.GE | ">=":
                        clause = field >= value
                    case FilterOperator.LT | "<":
                        clause = field < value
                    case FilterOperator.LE | "<=":
                        clause = field <= value
                    case FilterOperator.IN:
                        clause = field.in_(value)
                    case FilterOperator.NIN:
                        clause = ~field.in_(value)
                    case FilterOperator.LIKE:
                        clause = field.like(f"%{value}%")
                    case FilterOperator.ILIKE:
                        clause = field.ilike(f"%{value}%")
                    case FilterOperator.IS_NULL:
                        clause = field.is_(None)
                    case FilterOperator.NOT_NULL:
                        clause = ~field.is_(None)
                clauses.append(clause)

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
    field: str
    order: SortOrder = SortOrder.ASC


class QueryOptions(BaseModel):
    """查询选项"""
    filters: FilterGroup | None = None
    sort: list[SortField] | None = None
    offset: int = 0
    limit: int = 100