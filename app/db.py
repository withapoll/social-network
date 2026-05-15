"""Работа с пулом соединений PostgreSQL.

ORM сознательно не используется (требование ДЗ). Все запросы пишутся
вручную и обязательно параметризуются — это защищает от SQL-инъекций.
"""
from contextlib import contextmanager

from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from app.config import DSN

# Пул соединений создаётся один раз на всё приложение.
# open=False + явный open() в lifespan, чтобы не открывать пул на этапе импорта.
pool = ConnectionPool(conninfo=DSN, min_size=1, max_size=10, open=False)


def init_pool() -> None:
    """Открыть пул (вызывается при старте приложения)."""
    pool.open()
    pool.wait()


def close_pool() -> None:
    """Закрыть пул (вызывается при остановке приложения)."""
    pool.close()


@contextmanager
def get_cursor():
    """Выдаёт курсор с автоматическим commit/rollback.

    Курсор возвращает строки как словари (dict_row) — удобно отдавать в API.
    """
    with pool.connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            yield cur
        # commit делает контекстный менеджер conn автоматически,
        # при исключении — rollback.
