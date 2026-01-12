from typing import NoReturn

from fastapi import Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_async_db
from src.core.redis.redis import redis_user_ctx
from src.auth_app.services.user import CurrentUser
from src.auth_app.repositories import UserRegisteredRepo
from src.auth_app.schemes.user_schemes import UserWorkSchema
from src.auth_app.services.token import app_token, TypeToken
from src.auth_app.exceptions import UserHTTPException, AuthHTTPException


class Authentication:
    def __init__(self, request: Request, payload: dict, db: AsyncSession):
        self.request = request
        self.payload = payload
        self.db = db
        self.request.state.user = None

    async def _authenticate(self) -> None:
        """
        Устанавливает пользователя в Request.state
        Returns:
            None
        """
        user_map = await UserRegisteredRepo.read_one_user_by_id(self.payload.get("uid"), self.db)
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
    payload = app_token.verify_access_token(header)
    auth: bool = await Authentication(request, payload, db).is_authenticate()

    redis_user_ctx.set(request.state.user.current_user.username)  # username для формирования ключа Redis
    return auth


async def refresh_tokens(
        request: Request, header: str = Depends(TypeToken.REFRESH.value), db: AsyncSession = Depends(get_async_db)
) -> bool:
    """ Предназначено для обновления токенов. В заголовке использовать имя 'RefreshToken' """

    payload = app_token.verify_refresh_token(header)
    request.state.token = header
    return await Authentication(request, payload, db).is_authenticate()


async def available_admin(request: Request) -> NoReturn:
    """ Устанавливает доступ только для администратора """

    user: CurrentUser = request.state.user
    if not isinstance(user, CurrentUser) or not user.current_user.is_superuser:
        AuthHTTPException.raise_http_403()

    return
