import re

from src.auth_app.constants import LITERAL_PASSWORD, SPECIAL_LITERAL_PASSWORD


def validate_username(username) -> bool:
    regex = r"^[\w]+$"
    p = re.compile(regex)
    if p.match(username):
        return username
    raise ValueError("Username может только содержать буквы латинского алфавита, цифры и _")


def validate_password(psw: str):
    errors = []
    if len(psw) < 8:
        errors.append("Пароль должен состоять минимум из 8 символов")
    for literal in psw:
        if literal not in LITERAL_PASSWORD + SPECIAL_LITERAL_PASSWORD:
            errors.append("Допускаются только буквы латинского алфавита, цифры и символы ! @ # $ % ^ & * ( )")
            break
    if not any([p.islower() for p in psw]):
        errors.append("Должен быть символ в нижнем регистре")
    if not any([p.isupper() for p in psw]):
        errors.append("Должен быть символ в верхнем регистре")
    if not any([p.isdigit() for p in psw]):
        errors.append("Должен содержать цифру")
    if not any([p in SPECIAL_LITERAL_PASSWORD for p in psw]):
        errors.append("Должен содержать хотя бы один спецсимвол ! @ # $ % ^ & * ( )")

    if errors:
        errors_msg: str = " / ".join(errors)
        raise ValueError(errors_msg)
    return psw

