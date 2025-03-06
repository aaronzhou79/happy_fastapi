# =========================CRUD 操作=========================
from src.apps.v1.demo.models.mdl_demo import (
    Demo,
    DemoCreate,
    DemoItem,
    DemoItemCreate,
    DemoItemUpdate,
    DemoUpdate,
)
from src.common.base_crud import CRUDBase


class CrudDemo(CRUDBase[Demo, DemoCreate, DemoUpdate]):
    """DEMO CRUD操作"""

    def __init__(self) -> None:
        super().__init__(
            model=Demo,
            create_model=DemoCreate,
            update_model=DemoUpdate,
        )


crud_demo = CrudDemo()


class CrudDemoItem(CRUDBase[DemoItem, DemoItemCreate, DemoItemUpdate]):
    """DEMO明细CRUD操作"""

    def __init__(self) -> None:
        super().__init__(
            model=DemoItem,
            create_model=DemoItemCreate,
            update_model=DemoItemUpdate,
        )


crud_demo_item = CrudDemoItem()
