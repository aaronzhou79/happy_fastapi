
from src.apps.v1.sys.models import OperaLog
from src.common.base_crud import BaseCRUD


class CrudOperaLog(BaseCRUD):
    """操作日志相关CRUD类"""
    pass


crud_opera_log = CrudOperaLog(OperaLog, cached=False)
