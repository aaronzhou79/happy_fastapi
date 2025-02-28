from fastapi import APIRouter

from .api.code_setting import code_setting_api
from .api.code_trace import code_trace_api
from .api.cost import cost_api
from .api.currency import currency_api
from .api.customer import customer_api
from .api.demo import router as demo_router
from .api.dict_data import dict_data_api
from .api.dict_type import dict_type_api
from .api.employe import employe_api
from .api.material import material_api
from .api.product import product_api
from .api.workmanship import workmanship_api

router = APIRouter(prefix="/bas")

router.include_router(demo_router)
router.include_router(code_setting_api.router)
router.include_router(code_trace_api.router)
router.include_router(cost_api.router)
router.include_router(material_api.router)
router.include_router(product_api.router)
router.include_router(workmanship_api.router)
router.include_router(customer_api.router)
router.include_router(dict_data_api.router)
router.include_router(dict_type_api.router)
router.include_router(currency_api.router)
router.include_router(employe_api.router)
