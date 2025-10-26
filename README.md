# МАИ таблетки
Сервис для связи пациентов и мед-друзей, и управления синхранизацией таблеток и историей приемов лекарств.

## Содержание

- [Требования](#требования)
- [Запуск](#запуск)

## Требования

(Я работаю по wsl2 и устанавливал Docker Desktop на Windows 11 и настроил интеграцию в wsl2)

- Docker
- Docker Compose

## Запуск

Для запуска приложения в режиме разработки с автоматической перезагрузкой:

```bash
docker-compose up --build
```

Приложение будет доступно по адресу `http://localhost:8000`. Панель интерактивной документации: `http://localhost:8000/docs`.

Для запуска в фоновом режиме:

```bash
docker-compose up --build -d
```

Для остановки и удаления контейнеров (без удаления данных БД):

```bash
docker-compose down
```

Для полного сброса (с удалением данных БД):

```bash
docker-compose down -v
```

## Дерево проекта
```
meds-reminder-backend
├── .env
├── .git
├── .gitignore
├── .venv
├── Dockerfile
├── README.md
├── app
│   ├── __pycache__
│   ├── auth
│   │   ├── ERADME.md
│   │   ├── api
│   │   │   ├── __pycache__
│   │   │   ├── auth.py
│   │   │   └── friend.py
│   │   ├── crud
│   │   │   ├── __pycache__
│   │   │   ├── friend.py
│   │   │   └── user.py
│   │   ├── models
│   │   │   ├── __pycache__
│   │   │   └── user.py
│   │   ├── schemas
│   │   │   ├── __pycache__
│   │   │   ├── auth.py
│   │   │   └── friend.py
│   │   └── utils
│   │       ├── __pycache__
│   │       └── password.py
│   ├── core
│   │   ├── __pycache__
│   │   ├── config.py
│   │   └── security.py
│   ├── db
│   │   ├── __pycache__
│   │   ├── base.py
│   │   └── session.py
│   ├── main.py
│   └── medicines
│       └── README.md
├── docker-compose.yml
├── init.sql
├── poetry.lock
└── pyproject.toml
```