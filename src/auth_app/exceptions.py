from typing import NoReturn

from fastapi import HTTPException, status


class AuthBaseException(Exception):
    pass


class AuthHTTPException(AuthBaseException):

    @classmethod
    def raise_http_403(cls, detail: str | None = None) -> NoReturn:
        if detail is None:
            detail = "Доступ запрещён"
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)

    @classmethod
    def raise_http_401(cls, detail: str | None = None) -> NoReturn:
        if detail is None:
            detail = "Неверно указаны пользователь, почта или пароль"
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)

    @classmethod
    def raise_http_400(cls, detail: str | None = None) -> NoReturn:
        if detail is None:
            detail = "Введенные пароли не совпадают"
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class UserHTTPException(AuthBaseException):

    @classmethod
    def raise_http_500(cls, detail: str | None = None) -> NoReturn:
        if detail is None:
            detail = "Server error"
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)

    @classmethod
    def raise_http_404(cls, detail: str | None = None) -> NoReturn:
        if detail is None:
            detail = "User not found"
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

    @classmethod
    def raise_http_409(cls, detail: str | None = None) -> NoReturn:
        if detail is None:
            detail = "Пользователь с таким username или email уже существует"
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)
