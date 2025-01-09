from src.apps.v1.sys.models.login_log import LoginLog, LoginLogCreate
from src.apps.v1.sys.service.svr_login_log import svr_login_log
from src.common.base_api import BaseAPI

login_log_api = BaseAPI(
    model=LoginLog,
    service=svr_login_log,
    create_schema=LoginLogCreate,
    prefix="/login_log",
    gen_create=False,
    gen_delete=False,
    gen_bulk_create=False,
    tags=["登录日志"],
)