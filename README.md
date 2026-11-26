# Лабораторная работа №4. Реализация пользовательского интерфейса

## Описание проекта

**Concerts Afisha** - веб-приложение для работы с афишей концертов.

Проект состоит из трёх основных компонентов:

- **Frontend** - пользовательский интерфейс приложения.
- **Backend** - REST API на FastAPI.
- **Database** - PostgreSQL для хранения данных.

## Технологии

- Python 3.12
- FastAPI
- SQLAlchemy
- Alembic
- PostgreSQL 16
- Pydantic
- Argon2id
- JWT
- Docker Compose

## Требования

Для запуска проекта необходимы:

- Docker
- Docker Compose

## Установка и запуск

1. Клонируйте репозиторий:

   ```bash
   git clone https://github.com/mapat221/concerts_afisha
   cd concerts_afisha
   ```

2. Создайте файл `.env` на основе `.env.example` и настройте необходимые переменные окружения.

3. Запустите приложение вместе со всеми зависимостями:

   ```bash
   docker compose up --build -d
   ```

4. Примените миграции базы данных:

   ```bash
   docker compose exec backend uv run alembic upgrade head
   ```

5. Проверьте состояние контейнеров:

   ```bash
   docker compose ps
   ```

Для просмотра логов:

```bash
docker compose logs -f
```

## Использование

После успешного запуска приложение будет доступно по следующим адресам:

| Компонент | Адрес |
|---|---|
| Frontend | http://localhost:5174 |
| Backend API | http://localhost:8001 |
| Swagger UI | http://localhost:8001/docs |
| ReDoc | http://localhost:8001/redoc |

### Swagger UI

Для просмотра и тестирования доступных API-методов используется Swagger UI.

Он позволяет:
- Просматривать доступные HTTP-эндпоинты.
- Изучать схемы запросов и ответов.
- Выполнять API-запросы непосредственно из браузера.
- Проверять работу авторизации.

Документация доступна по адресу:

http://localhost:8001/docs

## Конфигурация

Настройки приложения передаются через переменные окружения.

Основные параметры:

| Переменная | Назначение |
|---|---|
| `APP_ENV` | Окружение приложения |
| `DATABASE_URL` | Строка подключения к PostgreSQL |
| `HASH_SCHEME` | Алгоритм хеширования паролей |
| `ARGON2_TIME_COST` | Параметр вычислительной сложности Argon2 |
| `ARGON2_MEMORY_COST` | Объём памяти для Argon2 |
| `ARGON2_PARALLELISM` | Степень параллелизма Argon2 |
| `PORT` | Порт backend |
| `SECRET_KEY` | Секретный ключ для JWT |
| `ADMIN_LOGIN` | Логин начального администратора |
| `ADMIN_PASSWORD` | Пароль начального администратора |

<!-- Этот README почти не вайбкод! --> 
