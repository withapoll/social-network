"""Слой доступа к данным: чистый параметризованный SQL, без ORM.

ВАЖНО: во всех функциях значения передаются через параметры запроса
(второй аргумент cur.execute), а не конкатенацией строк. Это и есть
защита от SQL-инъекций — драйвер сам экранирует значения.
"""
from app.db import get_cursor


def create_user(
    first_name: str,
    second_name: str,
    birthdate,
    gender: str | None,
    interests: str | None,
    city: str | None,
    password_hash: str,
) -> int:
    """Создать пользователя и вернуть его id."""
    with get_cursor() as cur:
        cur.execute(
            """
            INSERT INTO users
                (first_name, second_name, birthdate, gender, interests, city, password)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            """,
            (first_name, second_name, birthdate, gender, interests, city, password_hash),
        )
        return cur.fetchone()["id"]


def get_user_by_id(user_id: int) -> dict | None:
    """Вернуть анкету пользователя по id (без поля password) или None."""
    with get_cursor() as cur:
        cur.execute(
            """
            SELECT id, first_name, second_name, birthdate, gender, interests, city
            FROM users
            WHERE id = %s
            """,
            (user_id,),
        )
        return cur.fetchone()


def get_password_hash(user_id: int) -> str | None:
    """Вернуть хэш пароля пользователя по id или None."""
    with get_cursor() as cur:
        cur.execute("SELECT password FROM users WHERE id = %s", (user_id,))
        row = cur.fetchone()
        return row["password"] if row else None


def save_token(token: str, user_id: int) -> None:
    """Сохранить выданный токен авторизации."""
    with get_cursor() as cur:
        cur.execute(
            "INSERT INTO auth_tokens (token, user_id) VALUES (%s, %s)",
            (token, user_id),
        )


def get_user_id_by_token(token: str) -> int | None:
    """Вернуть id пользователя по токену авторизации или None."""
    with get_cursor() as cur:
        cur.execute("SELECT user_id FROM auth_tokens WHERE token = %s", (token,))
        row = cur.fetchone()
        return row["user_id"] if row else None
