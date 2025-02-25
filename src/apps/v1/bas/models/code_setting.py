
from typing import Literal

from sqlmodel import Field, SQLModel

from src.common.base_models.database_mixin import DatabaseModel
from src.common.enums import CodeGenerationRule, CodeResetFrequency, DocumentType


class CodeSettingBase(SQLModel):
    """单据编号设置基础模型"""
    document_type: DocumentType = Field(..., description="单据类型")
    date_rule: CodeGenerationRule = Field(..., description="日期生成规则")
    reset_frequency: CodeResetFrequency = Field(..., description="序号重置频率")
    prefix: str = Field(..., description="前缀代码")
    suffix_length: int = Field(default=3, ge=3, le=8, description="后缀序列号长度(3-8位)")
    placeholder: bool = Field(default=False, description="占位符")


class CodeSetting(CodeSettingBase, DatabaseModel, table=True):
    """单据编号设置"""
    __tablename__: Literal["bas_code_setting"] = "bas_code_setting"


class CodeSettingCreate(CodeSettingBase):
    """单据编号设置创建"""


class CodeSettingUpdate(CodeSettingBase):
    """单据编号设置更新"""
    id: int = Field(..., description="主键ID")
