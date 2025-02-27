
from src.apps.v1.demo.models.mdl_demo import Demo, DemoBase, DemoCreate, DemoUpdate
from src.apps.v1.demo.service.svr_demo import svr_demo
from src.common.base_api import BaseAPI

demo_api = BaseAPI(
    module_name="demo",
    model=Demo,
    service=svr_demo,
    create_schema=DemoCreate,
    update_schema=DemoUpdate,
    base_schema=DemoBase,
    prefix="/demo",
    gen_bulk_create=True,
    gen_bulk_delete=True,
    gen_delete=True,
    tags=["功能调试"],
)