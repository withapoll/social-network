"""Загрузка конфигурации из переменных окружения / .env."""
import os
from pathlib import Path

from dotenv import load_dotenv

# .env лежит в корне проекта (на уровень выше пакета app).
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def _db_password() -> str:
    # Пароль можно положить в отдельный файл (DB_PASSWORD_FILE) — удобно,
    # чтобы не хранить секрет в .env. Если файл не задан — берём DB_PASSWORD.
    path = os.getenv("DB_PASSWORD_FILE", "").strip()
    if path:
        return Path(path).read_text(encoding="utf-8").strip()
    return os.getenv("DB_PASSWORD", "")


DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "dbname": os.getenv("DB_NAME", "social_network"),
    "user": os.getenv("DB_USER", "social"),
    "password": _db_password(),
}

APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT = int(os.getenv("APP_PORT", "8000"))

# Строка подключения для psycopg.
DSN = (
    f"host={DB_CONFIG['host']} port={DB_CONFIG['port']} "
    f"dbname={DB_CONFIG['dbname']} user={DB_CONFIG['user']} "
    f"password={DB_CONFIG['password']}"
)
