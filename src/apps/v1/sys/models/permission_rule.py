from datetime import datetime
from typing import Any, List, Literal

from pydantic import BaseModel
from sqlmodel import JSON, Column, Field, SQLModel

from src.common.base_model import DatabaseModel, id_pk


class RuleCondition(BaseModel):
    """规则条件"""
    type: str = Field(..., description="条件类型(time/ip/data等)")
    operator: str = Field(..., description="操作符(eq/gt/lt/in等)")
    value: Any = Field(..., description="条件值")


class Rule(BaseModel):
    """权限规则"""
    name: str = Field(..., description="规则名称")
    conditions: List[RuleCondition] = Field(default_factory=list, description="规则条件列表")
    logic: str = Field(default="and", description="条件组合逻辑(and/or)")
    priority: int = Field(default=0, description="规则优先级")


class PermissionRuleBase(SQLModel):
    """权限规则基础模型"""
    permission_id: int = Field(..., foreign_key="sys_permission.id")
    rule: Rule = Field(..., sa_column=Column(JSON), description="权限规则")
    status: bool = Field(default=True, description="规则状态")
    start_time: datetime | None = Field(default=None, description="生效开始时间")
    end_time: datetime | None = Field(default=None, description="生效结束时间")
    description: str | None = Field(default=None, description="规则描述")


class PermissionRule(PermissionRuleBase, DatabaseModel, table=True):
    """权限规则表"""
    __tablename__: Literal["sys_permission_rule"] = "sys_permission_rule"
    id: id_pk  # type: ignore


class PermissionRuleCreate(PermissionRuleBase):
    """权限规则创建模型"""


class PermissionRuleUpdate(PermissionRuleBase):
    """权限规则更新模型"""
    id: int