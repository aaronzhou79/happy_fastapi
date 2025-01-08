
from src.apps.v1.sys.models import Role
from src.common.base_crud import BaseCRUD


class CrudRole(BaseCRUD):
    """角色相关CRUD类"""
    pass


crud_role = CrudRole(Role)