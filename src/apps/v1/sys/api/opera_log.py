from src.apps.v1.sys.models.opera_log import OperaLog, OperaLogCreate
from src.apps.v1.sys.service.opera_log import svr_opera_log
from src.common.base_api import BaseAPI

opera_log_api = BaseAPI(
    module_name="sys",
    model=OperaLog,
    service=svr_opera_log,
    create_schema=OperaLogCreate,
    prefix="/opera_log",
    gen_create=False,
    gen_delete=False,
    gen_bulk_create=False,
    tags=["系统管理/操作日志"],
)