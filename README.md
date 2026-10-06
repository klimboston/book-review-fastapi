# Book Review API 📚

Асинхронный бэкенд-сервис для отзывов и обзоров на книги. Проект разработан на базе **FastAPI** и **SQLModel** с контейнеризацией и автоматическим тестированием.

## 🚀 Стек

**Python**: 3.14+
**Web framework**: FastAPI
**ORM / database toolkit**: SQLModel, SQLAlchemy
**Database**: PostgreSQL 17
**Async driver**: asyncpg
**Migrations**: Alembic
**Validation / configuration**: Pydantic, Pydantic Settings
**Authentication**: JWT / OAuth2 Bearer
**Password hashing**: bcrypt
**Package manager**: uv
**Testing**: pytest, pytest-asyncio, HTTPX, aiosqlite
**Containerization**: Docker, Docker Compose
**CI**: GitHub Actions

---

## 🏗️ Архитектурные особенности проекта

API предоставляет следующие основные возможности:

* регистрация пользователей;
* авторизация пользователей с выдачей JWT access token;
* получение пользователей;
* создание, получение и изменение книг;
* создание и получение отзывов;
* проверка прав доступа через JWT;
* валидация входных данных;
* обработка конфликтов, например регистрации с уже существующим email;
* каскадное удаление отзывов при удалении книги.
---

## 🛠️ Быстрый запуск через Docker Compose 🐳

Приложение и база данных PostgreSQL запускаются одной кнопкой в изолированной сети.

1. **Создайте файл конфигурации окружения** в корне проекта с именем `.env` (вы можете взять за основу структуру ниже):
   ```text
   SECRET_KEY=your_super_long_secret_key_here_for_jwt_security_32_bytes
   ALGORITHM=HS256
   DB_USER=postgres
   DB_PASSWORD=qwe12345
   DB_NAME=book_review_database
   DB_HOST=db
   DB_PORT=5432
   DB_HOST_ALEMBIC=localhost
   DB_PORT_ALEMBIC=5433
   ```
   DB_HOST_ALEMBIC и DB_PORT_ALEMBIC используются для локального запуска Alembic. При запуске в Docker Compose они автоматически переопределяются для подключения к сервису PostgreSQL.

2. **Запустите сборку и старт контейнеров:**
   ```bash
   docker compose up --build
   ```

3. **Откройте интерактивную документацию API:**
   Перейдите в браузере по адресу: `http://127.0.0.1:8000/docs`

4. **Остановка проекта:** Для завершения работы контейнеров нажмите `Ctrl + C` в терминале.

---
## 🗄️ Миграции базы данных
Для управления схемой PostgreSQL используется Alembic.

Создание новой миграции после изменения моделей:

uv run alembic revision --autogenerate -m "описание изменения"

Применение миграций:

uv run alembic upgrade head

В Docker миграции применяются автоматически при запуске проекта.

---
## 🧪 Запуск автоматических тестов (`pytest`)

Тесты полностью изолированы. При запуске `uv run pytest` приложение автоматически подменяет боевую базу данных PostgreSQL на асинхронную SQLite, разворачивает чистые таблицы, симулирует действия пользователя через `AsyncClient` и стирает данные после проверок.

Для запуска тестов локально (из среды WSL/Linux):

1. Установите зависимости разработки:
   ```bash
   uv sync
   ```
2. Запустите тестовую сессию:
   ```bash
   uv run pytest -v
   ```
Тесты проверяют регистрацию и авторизацию пользователей, JWT-аутентификацию, работу с книгами и отзывами, валидацию входных данных и обработку ошибок.

---
## 🔄 Continuous Integration (CI)
Для автоматической проверки проекта используется GitHub Actions.
CI запускается при push в main и при создании Pull Request в main.
Pipeline:
Checkout
   ↓
Python 3.14
   ↓
uv
   ↓
uv sync --locked
   ↓
pytest
   ↓
✅ / ❌
---

## 📂 Структура проекта

```text
src/
└── book_review_project/
    ├── core/
    │   ├── config.py           # Настройки приложения и переменные окружения
    │   ├── database.py         # AsyncEngine и фабрика асинхронных сессий
    │   ├── dependencies.py     # FastAPI dependencies, БД и JWT
    │   └── security.py         # JWT и хеширование паролей
    │
    ├── repositories/
    │   ├── user.py             # Запросы к таблице User
    │   ├── book.py             # Запросы к таблице Book
    │   └── review.py           # Запросы к таблице Review
    │
    ├── services/
    │   └── review_service.py   # Логика работы с отзывами
    │
    ├── routers/
    │   ├── users.py            # User endpoints
    │   ├── books.py            # Book endpoints
    │   └── reviews.py          # Review endpoints
    │
    ├── models.py               # SQLModel-модели таблиц БД
    ├── schemas.py              # Pydantic-схемы запросов и ответов
    └── main.py                 # Создание FastAPI-приложения

tests/
├── conftest.py
├── test_users.py
├── test_books.py
└── test_reviews.py

alembic/
├── env.py
└── versions/
    └── 2274c41a60df_initial_migration.py


```
