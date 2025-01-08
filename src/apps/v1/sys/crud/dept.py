
from src.apps.v1.sys.models import Dept
from src.common.base_crud import BaseCRUD


class CrudDept(BaseCRUD):
    """部门相关CRUD类"""
    pass


crud_dept = CrudDept(Dept)
