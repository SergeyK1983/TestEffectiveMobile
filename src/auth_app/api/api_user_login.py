from fastapi import Depends, status, Response, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_async_db
from src.auth_app.api import router
from src.auth_app.services.auth import refresh_tokens, authenticate
from src.auth_app.schemes.auth_schemes import AuthSchema
from src.auth_app.services.user_actions import AuthUserActions


@router.post(path="/login", status_code=status.HTTP_200_OK)
async def login_user(request: Request, response: Response, user: AuthSchema, db: AsyncSession = Depends(get_async_db)):
    """
    Аутентификация. Устанавливает заголовки "access_token" и "refresh_token" в ответе. Если пользователь не пройдет
    проверку будет вызвано исключение: HTTPException, status.HTTP_401_UNAUTHORIZED.
    Args:
        request: Request
        response: Response
        user: schema AuthUser (from post body)
        db: session
    Returns:
        sets the headers "access_token" and "refresh_token"
    """
    access_token, refresh_token = await AuthUserActions().login_user(request=request, user_input=user, db=db)
    del user

    response.headers["access_token"]: str = access_token
    response.headers["refresh_token"]: str = refresh_token
    return True


@router.get(
    path="/logout",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(authenticate)]
)
async def logout_user(request: Request, response: Response) -> dict:
    """
    Выход пользователя из системы
    """
    await AuthUserActions().logout_user(request)
    response.headers["access_token"]: str = ""
    response.headers["refresh_token"]: str = ""
    return {"msg": "Пользователь вышел из системы"}


@router.post(
    path="/refresh-tokens",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(refresh_tokens)]
)
async def refresh_tokens(request: Request, response: Response) -> bool:
    """
    Обновление токенов.
    Args:
        request: Request
        response: Response
    Returns:
        sets the headers "access_token" and "refresh_token"
    """
    access_token, refresh_token = await AuthUserActions().refresh_login(request=request)
    response.headers["access_token"]: str = access_token
    response.headers["refresh_token"]: str = refresh_token
    return True
