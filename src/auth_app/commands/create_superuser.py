from src.core.database import AsyncSessionLocal
from src.auth_app.repositories.superuser_repository import SuperuserRepo
from src.auth_app.services.password import password


async def create_superuser(username: str, email: str, pwd: str) -> str:
    """
    Создает суперпользователя.
    Args:
        username: name of the user
        email: email of the user
        pwd: <PASSWORD>
    Return:
        Massage: str
    """
    pwd_hash = password.hashing_password(pwd)

    async with AsyncSessionLocal() as session:
        try:
            exists = await SuperuserRepo.is_unique_user(
                username=username,
                email=email,
                db=session
            )
            if not exists:
                result: bool = await SuperuserRepo.create_superuser(
                    username=username,
                    email=email,
                    password=pwd_hash,
                    db=session
                )
        finally:
            await session.close()

    if exists:
        return f"Суперпользователь c {username}, {email} уже существует!"

    if not result:
        return f"Суперпользователя {username}, {email} создать не удалось"

    return f"Суперпользователь {username}, {email} создан!"
