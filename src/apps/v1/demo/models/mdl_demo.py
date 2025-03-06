from decimal import Decimal
from typing import Literal

import sqlalchemy as sa

from sqlmodel import Field, Relationship, SQLModel

from src.common.base_models.database_mixin import DatabaseModel
from src.common.base_models.datetime_mixin import DateTimeMixin
from src.common.base_models.numeric_mixin import (
    MoneyField,
    PercentageField,
    PriceField,
    QuantityField,
)
from src.common.base_models.tenant_mixin import TenantMixin


class DemoBase(SQLModel):
    """DEMO基础模型"""

    __table_args__ = (sa.Index("idx_demo_order_no", "order_no"),)

    order_no: str = Field(..., max_length=32, unique=True, description="订单编号")
    customer_name: str = Field(..., max_length=32, description="客户名称")
    total_amount: Decimal = MoneyField(description="总金额")
    tax_amount: Decimal = MoneyField(description="税额")
    discount_amount: Decimal = MoneyField(description="折扣金额")

    # 使用自定义百分比字段
    tax_rate: Decimal = PercentageField(description="税率")
    discount_rate: Decimal = PercentageField(description="折扣率")
    status: str = Field(..., max_length=32, description="状态")


class Demo(DemoBase, TenantMixin, DateTimeMixin, DatabaseModel, table=True):
    """DEMO表"""

    __tablename__: Literal["demo"] = "demo"

    # Relationships
    demo_items: list["DemoItem"] = Relationship(back_populates="demo")


class DemoCreate(DemoBase):
    """DEMO创建模型"""

    demo_items: list["DemoItemCreate"]


class DemoUpdate(DemoCreate):
    """DEMO更新模型"""

    id: int


class DemoItemBase(SQLModel):
    """DEMO明细基础模型"""

    __table_args__ = (
        sa.Index("idx_demo_item_demo_id", "demo_id"),
        sa.UniqueConstraint(
            "product_name", "soft_delete", name="uq_demo_item_product_name_soft_delete"
        ),
        sa.UniqueConstraint(
            "product_code", "soft_delete", name="uq_demo_item_product_code_soft_delete"
        ),
    )

    demo_id: int = Field(
        ..., foreign_key="demo.id", sa_type=sa.BIGINT, description="主表ID"
    )
    product_name: str = Field(..., max_length=32, description="商品名称")
    product_code: str = Field(..., max_length=32, description="商品编码")
    # 使用自定义数量字段
    quantity: Decimal = QuantityField(description="数量")
    # 使用自定义价格字段
    unit_price: Decimal = PriceField(description="单价")
    # 使用自定义金额字段
    total_price: Decimal = MoneyField(description="总价")
    soft_delete: bool = Field(default=False, description="软删除")


class DemoItem(DemoItemBase, DateTimeMixin, DatabaseModel, table=True):
    """DEMO明细表"""

    __tablename__: Literal["demo_item"] = "demo_item"

    # Relationships
    demo: Demo = Relationship(back_populates="demo_items")

    def __repr__(self) -> str:
        attrs = []
        for field in ["id", "product_name", "demo_id"]:
            value = getattr(self, field, None)
            if value is not None:
                attrs.append(f"{field}={value}")

        return f"<{self.__class__.__name__}({', '.join(attrs)})>"


class DemoItemCreate(DemoItemBase):
    """DEMO明细创建模型"""


class DemoItemUpdate(DemoItemCreate):
    """DEMO明细更新模型"""

    id: int
