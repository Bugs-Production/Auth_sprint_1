# Пользовательский Сервис 

Сервис управления пользователями для системы кинотеатра.

## Описание
Этот микросервис предназначен для управления пользователями и их ролями в системе кинотеатра. Сервис предоставляет функционал для:

- Создания и управления учетными записями пользователей.
- Назначения и изменения ролей пользователей.
- Просмотра информации о пользователях и их ролях.

## Стек технологий

- FastAPI: Фреймворк для создания API.
- SQLAlchemy: ORM для работы с базой данных.
- Alembic: Инструмент для миграций базы данных.
- PostgreSQL: СУБД для хранения данных.
- Redis: Кэширование данных
- Docker: Деплой и запуск проекта

## Запуск проекта

Клонировать репозиторий, в корневой папке (на уровне docker-compose) необходимо создать файл **.env** и заполнить переменные окружения 
по примеру файла **.env.example**
```
cp .env.example .env
```

Запустить docker-compose:
```
make build
make start
```

Для остановки контейнеров 
```
make stop
```

Для подготовки миграций 
```
make makemigrations
```

Для применения миграций 
```
make migrate
```

Для форматирования 
```
make format
```

## Документация
Swagger документация находится по ручке `/api/openapi`
