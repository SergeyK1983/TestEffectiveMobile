from abc import ABC, abstractmethod
from typing import Any, TYPE_CHECKING

from sqlalchemy.ext.asyncio import AsyncSession

if TYPE_CHECKING:
    from src.auth_app.schemes.user_schemes import UserUpdateSchema


class UserBase(ABC):
    """ Базовая модель пользователя """

    @abstractmethod
    async def get_user_data(self) -> Any: ...
    """ Дать текущего пользователя """

    @abstractmethod
    async def update_user_data(self, update_data: "UserUpdateSchema") -> Any: ...
    """ Обновить/изменить данные текущего пользователя """

    @abstractmethod
    async def delete_user_data(self) -> Any: ...
    """ Удаление данных пользователя """

    def _check_attr_session_db(self) -> bool:
        """
        Вернет True, если self.db_session: Session sqlalchemy.orm, иначе raise AttributeError
        """
        attr = getattr(self, "db_session", None)
        if not attr or not isinstance(attr, AsyncSession):
            raise AttributeError(
                "Классу {} необходимо установить атрибут 'db_session: AsyncSession'".format(self.__class__.__name__)
            )
        return True
