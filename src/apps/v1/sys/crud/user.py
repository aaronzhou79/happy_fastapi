import sqlalchemy as sa

from fast_captcha import text_captcha

from src.apps.v1.sys.models import Role, User, UserRole
from src.common.base_crud import BaseCRUD
from src.core.exceptions import errors
from src.core.security.jwt import get_hash_password
from src.database.db_session import AuditAsyncSession


class CrudUser(BaseCRUD):
    """
    用户CRUD类
    """
    def __init__(self, model: User) -> None:
        super().__init__(
            model=model,
        )

    async def set_as_user(
        *,
        session: AuditAsyncSession,
        id: int,
        username: str,
        password: str,
        roles: list[int] | None = None,
    ) -> None:
        """
        设置为用户

        :param db:
        :param id:
        :param username:
        :param password:
        :param roles:
        :return:
        """
        current_user = await User.get_by_id(session=session, id=id)
        if current_user is None:
            raise errors.RequestError(msg="员工信息不存在！")
        if current_user.is_user:
            raise errors.RequestError(msg="该员工已设置为系统用户！")
        salt = text_captcha(5)
        current_user.password = get_hash_password(f'{password}{salt}')
        current_user.username = username
        current_user.salt = salt

        # 清空现有roles
        await session.execute(
            sa.delete(UserRole).where(UserRole.user_id == id)
        )

        # 添加新roles
        if roles:
            for role_id in roles:
                role = await Role.get_by_id(session=session, id=role_id)
                if role:
                    await UserRole.create(
                        session=session,
                        user_id=id,
                        role_id=role_id
                    )
        await session.flush()


crud_user = CrudUser