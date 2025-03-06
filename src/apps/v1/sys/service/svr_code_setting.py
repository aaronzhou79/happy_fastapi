from src.apps.v1.sys.crud.crud_code_setting import crud_code_setting
from src.apps.v1.sys.models.mdl_code_setting import (
    CodeSetting,
    CodeSettingCreate,
    CodeSettingUpdate,
)
from src.common.base_service import BaseService


class SvrCodeSetting(BaseService[CodeSetting, CodeSettingCreate, CodeSettingUpdate]):
    """
    编码生成设置服务
    """

    def __init__(self):
        self.crud = crud_code_setting


svr_code_setting = SvrCodeSetting()
