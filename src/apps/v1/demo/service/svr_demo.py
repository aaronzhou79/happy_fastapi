from typing import Sequence
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
from src.common.query_fields import FilterCondition, FilterGroup, QueryOptions
from src.database.db_session import AuditAsyncSession


class SvrDemo(BaseService[Demo, DemoCreate, DemoUpdate]):
    """
    DEMO服务
    """
    def __init__(self):
        self.crud = crud_demo

    async def get_by_custom_options(self, session: AuditAsyncSession, code: str, ignore_id: int) -> tuple[int, Sequence[Demo]]:
        """根据自定义选项获取对象列表和总数"""
        options = QueryOptions(
            filters=FilterGroup(
                conditions=[
                    FilterCondition(field="code", op="=", value=code),
                    FilterCondition(field="id", op="!=", value=ignore_id),
                ]
            )
        )
        return await self.crud.get_by_options(session, options)


svr_demo = SvrDemo()


class SvrDemoItem(BaseService[DemoItem, DemoItemCreate, DemoItemUpdate]):
    """
    DEMO明细服务
    """
    def __init__(self):
        self.crud = crud_demo_item


svr_demo_item = SvrDemoItem()
