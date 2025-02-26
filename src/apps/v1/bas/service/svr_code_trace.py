
from src.apps.v1.bas.crud.crud_code_setting import crud_code_setting
from src.apps.v1.bas.crud.crud_code_trace import crud_code_trace
from src.apps.v1.bas.models.mdl_code_setting import CodeSetting
from src.apps.v1.bas.models.mdl_code_trace import CodeTrace, CodeTraceCreate, CodeTraceUpdate
from src.common.base_service import BaseService
from src.common.enums import DocumentType
from src.core.exceptions import errors
from src.database.db_session import AuditAsyncSession


class SvrCodeTrace(BaseService[CodeTrace, CodeTraceCreate, CodeTraceUpdate]):
    """
    单据编号跟踪服务
    """
    def __init__(self):
        self.crud = crud_code_trace

    async def get_next_code(
        self,
        session: AuditAsyncSession,
        doc_type: DocumentType,
        classify_code: str | None = None
    ) -> str:
        """获取当前编码序列"""
        doc_setting = await crud_code_setting.get_by_fields(session, doc_type=doc_type)
        if not doc_setting or len(doc_setting) != 1:
            raise errors.RequestError(data=f"单据类型[{doc_type.value}]的编码规则设置有误！")

        return await self.crud.get_next_code(
            session,
            doc_type,
            doc_setting[0],
            classify_code
        )


svr_code_trace = SvrCodeTrace()
