
# =========================服务=========================


from src.apps.v1.demo.crud.crud_demo import crud_sal_order, crud_sal_order_item
from src.apps.v1.demo.models.mdl_demo import (
    SALOrder,
    SALOrderCreate,
    SALOrderItem,
    SALOrderItemCreate,
    SALOrderItemUpdate,
    SALOrderUpdate,
)
from src.common.base_service import BaseService


class SvrSALOrder(BaseService[SALOrder, SALOrderCreate, SALOrderUpdate]):
    """
    销售订单服务
    """
    def __init__(self):
        self.crud = crud_sal_order


svr_sal_order = SvrSALOrder()


class SvrSALOrderItem(BaseService[SALOrderItem, SALOrderItemCreate, SALOrderItemUpdate]):
    """
    销售订单服务
    """
    def __init__(self):
        self.crud = crud_sal_order_item


svr_sal_order_item = SvrSALOrderItem()
