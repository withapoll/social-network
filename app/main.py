"""Точка входа: монолитное FastAPI-приложение «Заготовка для социальной сети».

Эндпоинты соответствуют спецификации OtusTeam/highload:
    POST /login            — простейшая авторизация, выдаёт токен
    POST /user/register    — регистрация пользователя
    GET  /user/get/{id}    — получение анкеты по id

Дополнительно отдаётся статический фронтенд из каталога static/.
"""
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app import repository
from app.config import APP_HOST, APP_PORT
from app.db import close_pool, init_pool
from app.models import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
    UserResponse,
)
from app.security import generate_token, hash_password, verify_password

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Открываем пул соединений при старте, закрываем при остановке.
    init_pool()
    yield
    close_pool()


app = FastAPI(
    title="Социальная сеть — заготовка",
    description="Базовый скелет соцсети: регистрация, авторизация, просмотр анкет.",
    version="1.0.0",
    lifespan=lifespan,
)


# --------------------------------------------------------------------------
# Зависимость авторизации: проверяет токен из заголовка Authorization.
# --------------------------------------------------------------------------
def require_auth(authorization: str = Header(default="")) -> int:
    """Достаёт токен из заголовка `Authorization: Bearer <token>`
    и возвращает id текущего пользователя. Иначе — 401."""
    prefix = "Bearer "
    if not authorization.startswith(prefix):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Требуется заголовок Authorization: Bearer <token>",
        )
    token = authorization[len(prefix):].strip()
    user_id = repository.get_user_id_by_token(token)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный токен",
        )
    return user_id


# --------------------------------------------------------------------------
# API
# --------------------------------------------------------------------------
@app.post("/user/register", response_model=RegisterResponse, tags=["user"])
def register(body: RegisterRequest):
    """Регистрация нового пользователя. Пароль хранится в виде bcrypt-хэша."""
    user_id = repository.create_user(
        first_name=body.first_name,
        second_name=body.second_name,
        birthdate=body.birthdate,
        gender=body.gender,
        interests=body.interests,
        city=body.city,
        password_hash=hash_password(body.password),
    )
    return RegisterResponse(user_id=user_id)


@app.post("/login", response_model=LoginResponse, tags=["auth"])
def login(body: LoginRequest):
    """Простейшая авторизация: проверка пароля и выдача токена."""
    password_hash = repository.get_password_hash(body.id)
    # Одинаковый ответ и для несуществующего пользователя, и для неверного
    # пароля — чтобы не подсказывать, какие id существуют.
    if password_hash is None or not verify_password(body.password, password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный идентификатор или пароль",
        )
    token = generate_token()
    repository.save_token(token, body.id)
    return LoginResponse(token=token)


@app.get("/user/get/{user_id}", response_model=UserResponse, tags=["user"])
def get_user(user_id: int, _current_user: int = Depends(require_auth)):
    """Получение анкеты пользователя по id. Требует авторизации."""
    user = repository.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )
    return UserResponse(**user)


@app.get("/health", tags=["service"])
def health():
    """Проверка живости сервиса."""
    return {"status": "ok"}


# --------------------------------------------------------------------------
# Статический фронтенд
# --------------------------------------------------------------------------
@app.get("/", include_in_schema=False)
def index():
    return FileResponse(STATIC_DIR / "index.html")


# Остальные статические файлы (css, js, страницы) — из каталога static/.
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host=APP_HOST, port=APP_PORT, reload=True)
