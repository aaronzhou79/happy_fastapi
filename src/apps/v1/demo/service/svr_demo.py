from src.apps.v1.demo.crud.crud_demo import crud_demo, crud_demo_item
from src.apps.v1.demo.models.mdl_demo import (
    Demo,
    DemoCreate,
    DemoItem,
    DemoItemCreate,
    DemoItemUpdate,
    DemoUpdate,
)
from src.common.base_service import BaseService


class SvrDemo(BaseService[Demo, DemoCreate, DemoUpdate]):
    """
    DEMO服务
    """
    def __init__(self):
        self.crud = crud_demo


svr_demo = SvrDemo()


class SvrDemoItem(BaseService[DemoItem, DemoItemCreate, DemoItemUpdate]):
    """
    DEMO明细服务
    """
    def __init__(self):
        self.crud = crud_demo_item


svr_demo_item = SvrDemoItem()
