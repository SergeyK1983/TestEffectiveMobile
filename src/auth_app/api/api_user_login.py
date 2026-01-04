from fastapi import Depends, status, Response
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_async_db
from src.auth_app.api import router
from src.auth_app.schemes.auth_schemes import AuthSchema
from src.auth_app.services.user_actions import AuthUserActions


@router.post(path="/login", status_code=status.HTTP_200_OK)
async def login_user(response: Response, user: AuthSchema, db: AsyncSession = Depends(get_async_db)):
    """
    Аутентификация. Устанавливает заголовки "access_token" и "refresh_token" в ответе. Если пользователь не пройдет
    проверку будет вызвано исключение: HTTPException, status.HTTP_401_UNAUTHORIZED.
    Args:
        response: Response
        user: schema AuthUser (from post body)
        db: session
    Returns:
        sets the headers "access_token" and "refresh_token"
    """
    access_token, refresh_token = await AuthUserActions().login_user(user_input=user, db=db)
    del user

    response.headers["access_token"]: str = access_token
    response.headers["refresh_token"]: str = refresh_token
    return True
