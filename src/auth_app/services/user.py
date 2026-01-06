from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import RowMapping

from src.auth_app.exceptions import UserHTTPException
from src.auth_app.repositories import UserRegisteredRepo
from src.auth_app.services.base import UserBase

if TYPE_CHECKING:
    from src.auth_app.schemes.user_schemes import UserUpdateSchema, UserWorkSchema


class CurrentUser(UserBase):
    """
    Пользователь. Вы можете установить следующие атрибуты при создании экземпляра класса:
        - current_user: UserWorkSchema,
        - db_session: Session of sqlalchemy.orm
    """
    def __init__(
            self,
            db_session: AsyncSession,
            current_user: "UserWorkSchema",

    ):
        self.db_session: AsyncSession = db_session
        self.current_user: "UserWorkSchema" = current_user

    def _check_attr_user_id(self) -> bool:
        """
        Вернет True, если self.current_user.id: UUID, иначе raise AttributeError
        """
        attr = getattr(self.current_user, "id", None)
        if not attr or not isinstance(attr, UUID):
            raise AttributeError(
                "Классу {} необходимо установить атрибут 'current_user.id: UUID'".format(self.__class__.__name__)
            )
        return True

    async def get_user_data(self) -> RowMapping | None:
        """ Предоставляет данные пользователя """

        self._check_attr_session_db()
        self._check_attr_user_id()

        user_data: RowMapping | None = await UserRegisteredRepo.read_one_user_by_id(
            user_id=self.current_user.id, db=self.db_session
        )
        if user_data is None:
            return None

        return user_data

    async def update_user_data(self, update_data: "UserUpdateSchema") -> RowMapping | None:
        """
        Изменение данных пользователя по update_data. Вернет HTTP_409 если пользователь с таким username или email
        уже существует.
        """
        self._check_attr_session_db()
        self._check_attr_user_id()

        if update_data.username is not None or update_data.email is not None:
            is_exists: bool = await UserRegisteredRepo.is_unique_user(
                username=update_data.username,
                email=update_data.email,
                db=self.db_session
            )
            if is_exists:
                UserHTTPException.raise_http_409()

        data_dict: dict = update_data.model_dump(exclude_none=True)
        user_dict: RowMapping = await UserRegisteredRepo.update_one_user_by_id(
            self.current_user.id, data_dict, self.db_session
        )

        return user_dict

    async def delete_user_data(self) -> RowMapping | None:
        """ Удаление данных пользователя """

        self._check_attr_session_db()
        self._check_attr_user_id()

        user_dict: RowMapping = await UserRegisteredRepo.delete_user(self.current_user, self.db_session)
        return user_dict
