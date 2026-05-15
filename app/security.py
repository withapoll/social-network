"""Безопасное хранение паролей и генерация токенов авторизации."""
import secrets

import bcrypt


def hash_password(plain: str) -> str:
    """Вернуть bcrypt-хэш пароля.

    bcrypt сам генерирует случайную соль и встраивает её в результат,
    поэтому открытый пароль нигде не сохраняется.
    """
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(plain.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Проверить, что открытый пароль соответствует сохранённому хэшу."""
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except ValueError:
        # На случай повреждённого/некорректного хэша в БД.
        return False


def generate_token() -> str:
    """Сгенерировать криптостойкий токен авторизации."""
    return secrets.token_hex(32)
