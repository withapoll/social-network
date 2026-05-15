-- Схема базы данных для социальной сети (ДЗ «Заготовка для социальной сети»)
-- СУБД: PostgreSQL. ORM не используется — только чистый SQL.

CREATE TABLE IF NOT EXISTS users (
    id          BIGSERIAL PRIMARY KEY,
    first_name  VARCHAR(100)  NOT NULL,           -- Имя
    second_name VARCHAR(100)  NOT NULL,           -- Фамилия
    birthdate   DATE          NOT NULL,           -- Дата рождения
    gender      VARCHAR(20),                      -- Пол
    interests   TEXT,                             -- Интересы
    city        VARCHAR(120),                     -- Город
    password    VARCHAR(255)  NOT NULL,           -- Хэш пароля (bcrypt)
    created_at  TIMESTAMPTZ   NOT NULL DEFAULT now()
);

-- Таблица для простейшей токен-авторизации.
-- Токен выдаётся при /login и проверяется при защищённых запросах.
CREATE TABLE IF NOT EXISTS auth_tokens (
    token      VARCHAR(64) PRIMARY KEY,
    user_id    BIGINT      NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
