from typing import TYPE_CHECKING, Literal

import sqlalchemy as sa

from sqlmodel import Field, Relationship, SQLModel

from src.common.base_crud import CRUDBase
from src.common.base_model import DatabaseModel, DateTimeMixin


class SALOrderBase(SQLModel):
    """销售订单基础模型"""
    __table_args__ = (
        sa.Index('idx_sal_order_order_no', 'order_no'),
    )

    order_no: str = Field(..., max_length=32, unique=True, description="订单编号")
    customer_name: str = Field(..., max_length=32, description="客户名称")
    total_amount: float = Field(..., description="总金额")
    status: str = Field(..., max_length=32, description="状态")


class SALOrder(SALOrderBase, DateTimeMixin, DatabaseModel, table=True):
    """销售订单表"""
    __tablename__: Literal["sal_order"] = "sal_order"

    # Relationships
    order_items: list["SALOrderItem"] = Relationship(back_populates="order")


class SALOrderCreate(SALOrderBase):
    """销售订单创建模型"""
    order_items: list["SALOrderItemCreate"]


class SALOrderUpdate(SALOrderCreate):
    """销售订单更新模型"""
    id: int


class SALOrderItemBase(SQLModel):
    """销售订单明细基础模型"""
    __table_args__ = (
        sa.Index('idx_sal_order_item_order_id', 'order_id'),
    )

    order_id: int = Field(..., foreign_key="sal_order.id", description="订单ID")
    product_name: str = Field(..., max_length=32, description="商品名称")
    quantity: int = Field(..., description="数量")
    unit_price: float = Field(..., description="单价")
    total_price: float = Field(..., description="总价")


class SALOrderItem(SALOrderItemBase, DateTimeMixin, DatabaseModel, table=True):
    """销售订单明细表"""
    __tablename__: Literal["sal_order_item"] = "sal_order_item"

    # Relationships
    order: SALOrder = Relationship(back_populates="order_items")


class SALOrderItemCreate(SALOrderItemBase):
    """销售订单明细创建模型"""


class SALOrderItemUpdate(SALOrderItemCreate):
    """销售订单明细更新模型"""
    id: int


# =========================CRUD 操作=========================
class CrudSALOrder(CRUDBase[SALOrder, SALOrderCreate, SALOrderUpdate]):
    """销售订单CRUD操作"""
    def __init__(self) -> None:
        super().__init__(
            model=SALOrder,
            create_model=SALOrderCreate,
            update_model=SALOrderUpdate,
        )


crud_sal_order = CrudSALOrder()


class CrudSALOrderItem(CRUDBase[SALOrderItem, SALOrderItemCreate, SALOrderItemUpdate]):
    """销售订单明细CRUD操作"""
    def __init__(self) -> None:
        super().__init__(
            model=SALOrderItem,
            create_model=SALOrderItemCreate,
            update_model=SALOrderItemUpdate,
        )


crud_sal_order_item = CrudSALOrderItem()
