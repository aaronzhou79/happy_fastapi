
from src.apps.v1.bas.crud.code_setting import crud_code_setting
from src.apps.v1.bas.models.code_setting import CodeSetting, CodeSettingCreate, CodeSettingUpdate
from src.common.base_service import BaseService


class SvrCodeSetting(BaseService[CodeSetting, CodeSettingCreate, CodeSettingUpdate]):
    """
    编码生成设置服务
    """
    def __init__(self):
        self.crud = crud_code_setting


svr_code_setting = SvrCodeSetting()
