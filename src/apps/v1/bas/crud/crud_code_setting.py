

from src.apps.v1.bas.models.mdl_code_setting import CodeSetting, CodeSettingCreate, CodeSettingUpdate
from src.common.base_crud import CRUDBase


class CrudCodeSetting(CRUDBase[CodeSetting, CodeSettingCreate, CodeSettingUpdate]):
    """编码生成设置CRUD操作"""
    def __init__(self) -> None:
        super().__init__(
            model=CodeSetting,
            create_model=CodeSettingCreate,
            update_model=CodeSettingUpdate,
        )


crud_code_setting = CrudCodeSetting()
