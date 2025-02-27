
# =========================CRUD 操作=========================
from src.apps.v1.demo.models.mdl_demo import (
    SALOrder,
    SALOrderCreate,
    SALOrderItem,
    SALOrderItemCreate,
    SALOrderItemUpdate,
    SALOrderUpdate,
)
from src.common.base_crud import CRUDBase


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