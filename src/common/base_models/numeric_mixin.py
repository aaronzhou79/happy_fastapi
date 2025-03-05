# src/common/base_models/numeric.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Description: 自定义字段类型

from decimal import Decimal
from typing import Any, Callable, TypeVar

import sqlalchemy as sa

from sqlalchemy.types import TypeDecorator
from sqlmodel import Field, SQLModel

from src.common.constants import DEFAULT_NUMERIC_TYPE, DEFAULT_NUMERIC_VALUES, NUMERIC_PRECISION, NumericFieldType

T = TypeVar('T')


class NumericField(TypeDecorator):
    """自定义数值字段类型"""
    impl = sa.Numeric
    cache_ok = True

    def __init__(
        self,
        field_type: NumericFieldType = DEFAULT_NUMERIC_TYPE,
        precision: int | None = None,
        scale: int | None = None,
        **kwargs
    ):
        self.field_type = field_type

        # 如果未指定精度和小数位数，则使用配置中的默认值
        if precision is None:
            precision = NUMERIC_PRECISION[field_type]["precision"]
        if scale is None:
            scale = NUMERIC_PRECISION[field_type]["scale"]

        super().__init__(precision=precision, scale=scale, **kwargs)

    def process_bind_param(self, value: Any, dialect: Any) -> Any:
        """处理绑定参数"""
        if value is None:
            return None

        # 确保值是Decimal类型
        if not isinstance(value, Decimal):
            value = Decimal(str(value))

        # 根据字段类型的小数位数进行四舍五入
        scale = NUMERIC_PRECISION[self.field_type]["scale"]
        return value.quantize(Decimal(f"0.{'0' * scale}"))

    def process_result_value(self, value: Any, dialect: Any) -> Any:
        """处理结果值"""
        if value is None:
            return None

        # 确保值是Decimal类型
        if not isinstance(value, Decimal):
            value = Decimal(str(value))

        # 根据字段类型的小数位数进行四舍五入
        scale = NUMERIC_PRECISION[self.field_type]["scale"]
        return value.quantize(Decimal(f"0.{'0' * scale}"))


# 创建各种数值字段类型的快捷方式
def MoneyField(  # noqa: N802
    default: Decimal | float | int | str | None = None,
    **kwargs
) -> Any:
    """金额字段"""
    if default is None:
        default = DEFAULT_NUMERIC_VALUES[NumericFieldType.MONEY]
    elif not isinstance(default, Decimal):
        default = Decimal(str(default))

    return Field(
        default=default,
        sa_column=sa.Column(
            NumericField(field_type=NumericFieldType.MONEY)
        ),
        **kwargs
    )


def WeightField(  # noqa: N802
    default: Decimal | float | int | str | None = None,
    **kwargs
) -> Any:
    """重量字段"""
    if default is None:
        default = DEFAULT_NUMERIC_VALUES[NumericFieldType.WEIGHT]
    elif not isinstance(default, Decimal):
        default = Decimal(str(default))

    return Field(
        default=default,
        sa_column=sa.Column(
            NumericField(field_type=NumericFieldType.WEIGHT)
        ),
        **kwargs
    )


def AreaField(  # noqa: N802
    default: Decimal | float | int | str | None = None,
    **kwargs
) -> Any:
    """面积字段"""
    if default is None:
        default = DEFAULT_NUMERIC_VALUES[NumericFieldType.AREA]
    elif not isinstance(default, Decimal):
        default = Decimal(str(default))

    return Field(
        default=default,
        sa_column=sa.Column(
            NumericField(field_type=NumericFieldType.AREA)
        ),
        **kwargs
    )


def LengthField(  # noqa: N802
    default: Decimal | float | int | str | None = None,
    **kwargs
) -> Any:
    """长度字段"""
    if default is None:
        default = DEFAULT_NUMERIC_VALUES[NumericFieldType.LENGTH]
    elif not isinstance(default, Decimal):
        default = Decimal(str(default))

    return Field(
        default=default,
        sa_column=sa.Column(
            NumericField(field_type=NumericFieldType.LENGTH)
        ),
        **kwargs
    )


def QuantityField(  # noqa: N802
    default: Decimal | float | int | str | None = None,
    **kwargs
) -> Any:
    """数量字段"""
    if default is None:
        default = DEFAULT_NUMERIC_VALUES[NumericFieldType.QUANTITY]
    elif not isinstance(default, Decimal):
        default = Decimal(str(default))

    return Field(
        default=default,
        sa_column=sa.Column(
            NumericField(field_type=NumericFieldType.QUANTITY)
        ),
        **kwargs
    )


def PercentageField(  # noqa: N802
    default: Decimal | float | int | str | None = None,
    **kwargs
) -> Any:
    """百分比字段"""
    if default is None:
        default = DEFAULT_NUMERIC_VALUES[NumericFieldType.PERCENTAGE]
    elif not isinstance(default, Decimal):
        default = Decimal(str(default))

    return Field(
        default=default,
        sa_column=sa.Column(
            NumericField(field_type=NumericFieldType.PERCENTAGE)
        ),
        **kwargs
    )


def ExchangeRateField(  # noqa: N802
    default: Decimal | float | int | str | None = None,
    **kwargs
) -> Any:
    """汇率字段"""
    if default is None:
        default = DEFAULT_NUMERIC_VALUES[NumericFieldType.EXCHANGE_RATE]
    elif not isinstance(default, Decimal):
        default = Decimal(str(default))

    return Field(
        default=default,
        sa_column=sa.Column(
            NumericField(field_type=NumericFieldType.EXCHANGE_RATE)
        ),
        **kwargs
    )


def PriceField(  # noqa: N802
    default: Decimal | float | int | str | None = None,
    **kwargs
) -> Any:
    """单价字段"""
    if default is None:
        default = DEFAULT_NUMERIC_VALUES[NumericFieldType.PRICE]
    elif not isinstance(default, Decimal):
        default = Decimal(str(default))

    return Field(
        default=default,
        sa_column=sa.Column(
            NumericField(field_type=NumericFieldType.PRICE)
        ),
        **kwargs
    )


def CustomNumericField(  # noqa: N802
    precision: int,
    scale: int,
    default: Decimal | float | int | str | None = None,
    **kwargs
) -> Any:
    """自定义数值字段"""
    if default is None:
        default = Decimal(f"0.{'0' * scale}")
    elif not isinstance(default, Decimal):
        default = Decimal(str(default))

    return Field(
        default=default,
        sa_column=sa.Column(
            NumericField(
                field_type=NumericFieldType.CUSTOM,
                precision=precision,
                scale=scale
            )
        ),
        **kwargs
    )


# 创建数值字段验证器
def create_numeric_validator(field_type: NumericFieldType) -> Callable:
    """创建数值字段验证器"""
    def validate_numeric(cls, value: Any) -> Decimal:
        if value is None:
            return DEFAULT_NUMERIC_VALUES[field_type]

        if not isinstance(value, Decimal):
            try:
                value = Decimal(str(value))
            except (ValueError, TypeError) as err:
                raise ValueError(f"无法将 {value} 转换为 Decimal 类型") from err

        # 根据字段类型的小数位数进行四舍五入
        scale = NUMERIC_PRECISION[field_type]["scale"]
        return value.quantize(Decimal(f"0.{'0' * scale}"))

    return validate_numeric


# 简化的数值字段Mixin
class NumericMixin(SQLModel):
    """数值字段Mixin

    用于在模型中添加数值字段的基类。
    使用方式：

    ```python
    from decimal import Decimal
    from typing import Literal

    from sqlmodel import Field, SQLModel

    from src.common.base_models.database_mixin import DatabaseModel
    from src.common.base_models.datetime_mixin import DateTimeMixin
    from src.common.base_models.numeric_mixin import NumericMixin, MoneyField, QuantityField

    class InvoiceBase(SQLModel):
        invoice_no: str = Field(..., max_length=32, description="发票编号")
        # 使用自定义金额字段
        total_amount: Decimal = MoneyField(description="总金额")
        # 使用自定义数量字段
        quantity: Decimal = QuantityField(description="数量")

    class Invoice(InvoiceBase, NumericMixin, DateTimeMixin, DatabaseModel, table=True):
        __tablename__: Literal["fin_invoice"] = "fin_invoice"
    ```

    在模型中使用字段验证器：

    ```python
    from decimal import Decimal
    from typing import Literal

    from pydantic import field_validator
    from sqlmodel import Field, SQLModel

    from src.common.base_models.database_mixin import DatabaseModel
    from src.common.base_models.datetime_mixin import DateTimeMixin
    from src.common.base_models.numeric_mixin import (
        NumericMixin, MoneyField, QuantityField,
        create_numeric_validator, NumericFieldType
    )

    class InvoiceBase(SQLModel):
        invoice_no: str = Field(..., max_length=32, description="发票编号")
        # 使用自定义金额字段
        total_amount: Decimal = MoneyField(description="总金额")
        # 使用自定义数量字段
        quantity: Decimal = QuantityField(description="数量")

        # 添加字段验证器
        @field_validator("total_amount")
        @classmethod
        def validate_total_amount(cls, value):
            return create_numeric_validator(NumericFieldType.MONEY)(cls, value)

        @field_validator("quantity")
        @classmethod
        def validate_quantity(cls, value):
            return create_numeric_validator(NumericFieldType.QUANTITY)(cls, value)

    class Invoice(InvoiceBase, NumericMixin, DateTimeMixin, DatabaseModel, table=True):
        __tablename__: Literal["fin_invoice"] = "fin_invoice"
    ```
    """
    __abstract__ = True