import sqlalchemy as sa

from fast_captcha import text_captcha

from src.apps.v1.sys.crud.role import crud_role
from src.apps.v1.sys.crud.user_role import crud_user_role
from src.apps.v1.sys.models import User, UserSchemaCreate, UserSchemaUpdate
from src.common.base_crud import BaseCRUD
from src.core.exceptions import errors
from src.core.security.jwt import get_hash_password
from src.database.db_session import AuditAsyncSession


class CrudUser(BaseCRUD[User, UserSchemaCreate, UserSchemaUpdate]):
    """
    用户CRUD类
    """
    def __init__(self) -> None:
        super().__init__(
            model=User,
        )

    async def set_as_user(
        self,
        *,
        session: AuditAsyncSession,
        id: int,
        username: str,
        password: str,
        roles: list[int] | None = None,
    ) -> User:
        """
        设置为用户

        :param db:
        :param id:
        :param username:
        :param password:
        :param roles:
        :return:
        """
        current_user = await self.get_by_id(session=session, id=id)
        if current_user is None:
            raise errors.RequestError(msg="员工信息不存在！")
        if current_user.is_user:
            raise errors.RequestError(msg="该员工已设置为系统用户！")
        salt = text_captcha(5)
        # current_user.password = get_hash_password(f'{password}{salt}')
        # current_user.username = username
        # current_user.salt = salt

        await self.update(
            session=session,
            db_obj=current_user,
            obj_in={
                "salt": salt,
                "password": get_hash_password(f'{password}{salt}'),
                "username": username,
                "is_user": True,
            }
        )

        # 清空现有roles
        await crud_user_role.delete_by_fields(session, user_id=id)

        # 添加新roles
        if roles:
            for role_id in roles:
                role = await crud_role.get_by_id(session=session, id=role_id)
                if role:
                    await crud_user_role.create(
                        session=session,
                        obj_in={
                            "user_id": id,
                            "role_id": role_id
                        }
                    )
        await session.flush()
        return current_user


crud_user = CrudUser()