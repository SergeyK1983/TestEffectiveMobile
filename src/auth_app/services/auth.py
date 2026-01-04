from fastapi import Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_async_db
from src.auth_app.services.user import CurrentUser
from src.auth_app.repositories import UserRegisteredRepo
from src.auth_app.schemes.user_schemes import UserWorkSchema
from src.auth_app.services.token import app_token, TypeToken
from src.auth_app.exceptions import UserHTTPException


class Authentication:
    def __init__(self, request: Request, token: str, db: AsyncSession):
        self.request = request
        self.token = token
        self.db = db
        self.request.state.user = None

    async def _authenticate(self) -> None:
        """
        Устанавливает пользователя в Request.state или вызывает ошибку: HTTP_403_FORBIDDEN
        Returns:
            None
        """
        payload = app_token.verify_access_token(self.token)
        user_map = await UserRegisteredRepo.read_one_user_by_id(payload.get("uid"), self.db)

        user = UserWorkSchema(**user_map) if user_map else UserHTTPException.raise_http_404()

        self.request.state.user = CurrentUser(db_session=self.db, current_user=user)
        return None

    async def is_authenticate(self) -> bool:
        """
        Вернет True или вызовет HTTP ошибку.
        """
        await self._authenticate()
        return True


async def authenticate(
        request: Request, header: str = Depends(TypeToken.ACCESS.value), db: AsyncSession = Depends(get_async_db)
) -> bool:
    """
    Использовать для апи, в которых нужна аутентификация. Вернет True или вызовет ошибку аутентификации.
    Args:
        request: Request
        header: token in the header (Authorization)
        db: Session
    Returns:
        True if token is valid else raises exception
    """
    return await Authentication(request, header, db).is_authenticate()


async def refresh_tokens(
        request: Request, header: str = Depends(TypeToken.REFRESH.value), db: AsyncSession = Depends(get_async_db)
) -> bool:
    """ Предназначено для обновления токенов. В заголовке использовать имя 'RefreshToken' """

    return await Authentication(request, header, db).is_authenticate()
