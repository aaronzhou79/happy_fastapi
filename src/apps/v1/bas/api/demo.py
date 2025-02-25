from fastapi import APIRouter

from src.apps.v1.bas.models.demo import SALOrderCreate, crud_sal_order
from src.common.base_api import BaseAPI
from src.core.responses.response_schema import ResponseModel, response_base
from src.database.db_session import CurrentSession

router = APIRouter(prefix="/demo")

@router.post('/demo', summary='测试')
async def demo(db: CurrentSession, order: SALOrderCreate) -> ResponseModel:
    """测试"""
    db_obj = await crud_sal_order.create(db, obj_in=order)
    data = await db_obj.to_dict()
    return response_base.success(data=data)

