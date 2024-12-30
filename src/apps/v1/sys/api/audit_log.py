

from src.common.base_api import BaseAPI
from src.common.data_model.base_model import AuditLog

audit_log_api = BaseAPI(
    model=AuditLog,
    prefix="/audit_log",
    gen_create=False,
    gen_update=False,
    gen_delete=False,
    tags=["审计日志"],
)