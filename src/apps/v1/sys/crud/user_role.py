
from src.apps.v1.sys.models import UserRole
from src.common.base_crud import BaseCRUD


class CrudUserRole(BaseCRUD):
    """用户角色对应表相关CRUD类"""
    pass


crud_user_role = CrudUserRole(UserRole)