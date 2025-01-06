from src.apps.v1.sys.models import LoginLog, LoginLogSchemaCreate
from src.common.base_api import BaseAPI

login_log_api = BaseAPI(
    model=LoginLog,
    create_schema=LoginLogSchemaCreate,
    prefix="/login_log",
    gen_create=False,
    gen_delete=False,
    gen_bulk_create=False,
    tags=["登录日志"],
)