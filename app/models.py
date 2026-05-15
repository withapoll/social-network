"""Pydantic-схемы запросов и ответов API."""
from datetime import date

from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    """Тело запроса POST /user/register."""
    first_name: str = Field(..., min_length=1, max_length=100, description="Имя")
    second_name: str = Field(..., min_length=1, max_length=100, description="Фамилия")
    birthdate: date = Field(..., description="Дата рождения, формат YYYY-MM-DD")
    gender: str | None = Field(None, max_length=20, description="Пол")
    interests: str | None = Field(None, description="Интересы")
    city: str | None = Field(None, max_length=120, description="Город")
    password: str = Field(..., min_length=6, max_length=128, description="Пароль")


class RegisterResponse(BaseModel):
    user_id: int


class LoginRequest(BaseModel):
    """Тело запроса POST /login."""
    id: int = Field(..., description="Идентификатор пользователя")
    password: str = Field(..., min_length=1, max_length=128)


class LoginResponse(BaseModel):
    token: str


class UserResponse(BaseModel):
    """Анкета пользователя (ответ GET /user/get/{id})."""
    id: int
    first_name: str
    second_name: str
    birthdate: date
    gender: str | None = None
    interests: str | None = None
    city: str | None = None
