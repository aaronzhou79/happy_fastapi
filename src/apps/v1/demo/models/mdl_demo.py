from typing import Literal

import sqlalchemy as sa

from sqlmodel import Field, Relationship, SQLModel

from src.common.base_models.database_mixin import DatabaseModel
from src.common.base_models.datetime_mixin import DateTimeMixin


class DemoBase(SQLModel):
    """DEMO基础模型"""
    __table_args__ = (
        sa.Index('idx_demo_order_no', 'order_no'),
    )

    order_no: str = Field(..., max_length=32, unique=True, description="订单编号")
    customer_name: str = Field(..., max_length=32, description="客户名称")
    total_amount: float = Field(..., description="总金额")
    status: str = Field(..., max_length=32, description="状态")


class Demo(DemoBase, DateTimeMixin, DatabaseModel, table=True):
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
        sa.Index('idx_demo_item_demo_id', 'demo_id'),
    )

    demo_id: int = Field(..., foreign_key="demo.id", sa_type=sa.BIGINT, description="订单ID")
    product_name: str = Field(..., max_length=32, description="商品名称")
    quantity: int = Field(..., description="数量")
    unit_price: float = Field(..., description="单价")
    total_price: float = Field(..., description="总价")


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

