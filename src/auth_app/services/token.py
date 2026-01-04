from dataclasses import dataclass, asdict
from datetime import datetime, timezone, timedelta
from enum import Enum
from uuid import UUID, uuid4

import jwt
from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.security import APIKeyHeader

from src.auth_app.schemes.user_schemes import UserWorkSchema
from src.core.config import settings


class TypeToken(Enum):
    ACCESS = APIKeyHeader(name="Authorization")
    REFRESH = APIKeyHeader(name="RefreshToken")

    @classmethod
    def all_names(cls) -> list:
        return cls._member_names_


@dataclass
class Payload:
    uid: UUID
    sub: str
    iss: str
    exp: datetime
    jti: UUID
    iat: datetime
    nbf: datetime
    type: str | None = None

    def as_dict(self) -> dict:
        return asdict(self)


class Token:

    @staticmethod
    def __get_payload(user_id: UUID, token_type: str) -> Payload:
        current_time = datetime.now(timezone.utc)

        if token_type == TypeToken.ACCESS.name:
            time_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        elif token_type == TypeToken.REFRESH.name:
            time_delta = timedelta(hours=settings.REFRESH_TOKEN_EXPIRE_HOURS)
        else:
            raise TypeError(f"Token type {token_type} not supported")

        payload = Payload(
            uid=jsonable_encoder(user_id),
            sub=str(user_id),
            iss=settings.APPLICATION,
            exp=current_time + time_delta,
            jti=jsonable_encoder(uuid4()),
            iat=current_time,
            nbf=current_time,
            type=token_type,
        )
        return payload

    def _create_token(self, user: UserWorkSchema, token_type):
        payload: Payload = self.__get_payload(user.id, token_type)
        try:
            encoded = jwt.encode(payload=payload.as_dict(), key=settings.private_key, algorithm=settings.ALGORITHM)
        except jwt.InvalidKeyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="server_error"
            )
        return "JWT " + encoded

    @staticmethod
    def _decode_token(encoded: str):
        if not encoded.startswith("JWT "):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Ошибка аутентификации')

        encoded = encoded.replace("JWT ", "")
        try:
            payload = jwt.decode(encoded, settings.public_key, algorithms=[settings.ALGORITHM])
        except (jwt.ExpiredSignatureError, jwt.DecodeError):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Ошибка аутентификации')
        return payload

    def get_access_token(self, user: UserWorkSchema):
        token_type: str = TypeToken.ACCESS.name
        token: str = self._create_token(user, token_type)
        return token

    def get_refresh_token(self, user: UserWorkSchema):
        token_type: str = TypeToken.REFRESH.name
        token: str = self._create_token(user, token_type)
        return token

    def verify_access_token(self, token: str) -> dict:
        payload = self._decode_token(token)
        if payload.get("type") != TypeToken.ACCESS.name:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Ошибка аутентификации')
        return payload

    def verify_refresh_token(self, token: str) -> dict:
        payload = self._decode_token(token)
        if payload.get("type") != TypeToken.REFRESH.name:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Ошибка аутентификации')
        return payload


app_token = Token()
