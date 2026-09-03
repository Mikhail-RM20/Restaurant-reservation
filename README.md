# Сервис бронирования столиков в ресторане

Бэкенд сервиса бронирования столиков, реализованный на Python 3.13 с использованием FastAPI,
SQLAlchemy (async), PostgreSQL и Docker.
Проект предоставляет REST API для создания бронирований, просмотра списка броней,
получения брони по ID и отмены брони. Валидация входных данных включает проверку даты,
времени (дискретные слоты с 12:00 до 22:00), телефона и количества гостей.

---

## ПРЕДВАРИТЕЛЬНЫЕ ТРЕБОВАНИЯ ДЛЯ ЗАПУСКА ПРОЕКТА:

1. Установленные Docker и Docker Compose.
2. Python 3.12+ (для локального запуска без Docker).

---

В проекте используется Ruff — быстрый линтер и форматер, заменяющий flake8, black и isort.
Настройки находятся в pyproject.toml.

1. Проверка кода на ошибки и стиль: ruff check .
2. Автоматическое исправление ошибок:  ruff check --fix .
3. Сортировка импортов (замена isort):  ruff check --fix --select I .
4. Форматирование кода (замена black):  ruff format .
5. Полный цикл (исправление + форматирование): ruff check --fix . && ruff format .

ПРИМЕЧАНИЕ:
    Некоторые длинные строки (особенно сообщения логов и f-строки) Ruff не может исправить автоматически
    – они требуют ручной правки. Проверка длины строк отключена в конфигурации (E501, W505 игнорируются).

---

## ИНСТРУКЦИЯ К ЗАПУСКУ:

### ВНИМАНИЕ: .env файл

!!! Файл `.env` **не хранится в репозитории**, так как содержит персональные данные (пароли) !!!

1. Создайте файл `.env` в корне проекта со следующим содержимым:

```env
POSTGRES_USER=your_login          (Замените на свой логин)
POSTGRES_PASSWORD=your_password   (Замените на свой пароль)
POSTGRES_DB=restaurant_db
```

2. Запустите контейнеры:

```bash
docker compose up -d --build
```

После успешного запуска приложение будет доступно:
- **API:** http://localhost
- **Swagger:** http://localhost/docs — подробное описание работы эндпоинтов.

3. Остановка контейнера производится командой:

```bash
docker compose down
```

---

## Функциональные возможности
    
    | № | Описание | Метод и URL |
    |---|----------|-------------|
    | 1 | Создание нового бронирования | `POST /bookings` |
    | 2 | Получение списка всех бронирований (с фильтром по дате) | `GET /bookings` |
    | 3 | Получение бронирования по ID | `GET /bookings/{id}` |
    | 4 | Отмена бронирования по ID | `DELETE /bookings/{id}` |
    | 5 | Автоматическая документация Swagger | `GET /docs` |

---

## Технологический стек
    
    | № | Компонент | Технология |
    |---|-----------|------------|
    | 1 | Язык | Python 3.13 |
    | 2 | Веб-фреймворк | FastAPI |
    | 3 | ORM | SQLAlchemy (асинхронный) |
    | 4 | База данных | PostgreSQL 15 |
    | 5 | Контейнеризация | Docker, Docker Compose |
    | 6 | Веб-сервер | Uvicorn (внутри контейнера) |
    | 7 | Валидация | Pydantic v2 |
    | 8 | Тестирование | pytest, pytest-asyncio, httpx, aiosqlite |
    | 9 | Логирование | Python logging + dictConfig |

---

## Структура проекта

```
├── core/                          # Конфигурации и настройки (логирование и т.п.)
│   └── dict_config.py             # dictConfig для логгеров
├── database/                      # Модели SQLAlchemy, ассоциативные таблицы, сессии
│   ├── __init__.py
│   ├── base.py                    # Асинхронный движок, Base, get_db
│   └── models.py                  # Модели Person, Booking, BookingStatus
├── routes/                        # Роутеры FastAPI (эндпоинты)
│   ├── __init__.py
│   ├── route_new_booking.py       # POST /bookings
│   ├── get_list_bookings.py       # GET /bookings
│   ├── get_booking_by_id.py       # GET /bookings/{id}
│   └── delete_bookings_by_id.py   # DELETE /bookings/{id}
├── services/                      # Бизнес-логика (CRUD-операции)
│   ├── function_add_new_booking.py
│   ├── function_get_bookings.py
│   ├── function_get_booking_by_id.py
│   └── function_delete_booking_by_id.py
├── schemas/                       # Pydantic-схемы (валидация входных/выходных данных)
│   ├── __init__.py
│   └── pydantic_shemas.py         # BookingCreateIn, BookingCreateOut
├── tests/                         # Интеграционные и unit-тесты (pytest)
│   ├── conftest.py                # Фикстуры (БД, клиент, фабрики)
    ├── test_database.py           # Тесты БД
    ├── test_routes.py             # Тесты роутов
│   └── test_services.py           # Тесты логики
├── docker-compose.yml             # Настройка контейнеров (FastAPI + PostgreSQL)
├── pyproject.toml                 # Настройка Ruff
├── Dockerfile                     # Сборка образа FastAPI
├── requirements.txt               # Зависимости Python
├── .env                           # Переменные окружения (создаётся пользователем)
└── README.md
```

---

## Зависимости проекта

```
aiohappyeyeballs==2.6.1
aiohttp==3.12.15
aiosignal==1.4.0
aiosqlite==0.22.1
annotated-doc==0.0.5
annotated-types==0.8.0
anthropic==0.124.0
anyio==4.14.2
argon2-cffi==25.1.0
argon2-cffi-bindings==25.1.0
arrow==1.4.0
asttokens==3.0.1
async-lru==2.1.0
asyncpg==0.31.0
attrs==25.3.0
babel==2.18.0
beautifulsoup4==4.14.3
black==26.5.1
bleach==6.3.0
blinker==1.9.0
certifi==2026.7.22
cffi==2.0.0
cfgv==3.5.0
charset-normalizer==3.4.3
click==8.4.2
colorama==0.4.6
comm==0.2.3
debugpy==1.8.20
decorator==5.2.1
defusedxml==0.7.1
distlib==0.4.3
distro==1.9.0
docker==7.1.0
docstring_parser==0.18.0
dotenv==0.9.9
executing==2.2.1
fastapi==0.141.1
fastjsonschema==2.21.2
filelock==3.32.3
flake8==7.3.0
Flask==3.1.2
fqdn==1.5.1
frozenlist==1.7.0
greenlet==3.5.5
gunicorn==25.3.0
h11==0.16.0
httpcore==1.0.9
httpx==0.28.1
identify==2.6.19
idna==3.19
iniconfig==2.1.0
ipykernel==7.2.0
ipython==9.10.0
ipython_pygments_lexers==1.1.1
isoduration==20.11.0
isort==8.0.1
itsdangerous==2.2.0
jedi==0.19.2
Jinja2==3.1.6
jiter==0.16.0
json5==0.13.0
jsonpointer==3.0.0
jsonschema==4.26.0
jsonschema-specifications==2025.9.1
jupyter-events==0.12.0
jupyter-lsp==2.3.0
jupyter_client==8.8.0
jupyter_core==5.9.1
jupyter_server==2.17.0
jupyter_server_terminals==0.5.4
jupyterlab==4.5.4
jupyterlab_pygments==0.3.0
jupyterlab_server==2.28.0
lark==1.3.1
MarkupSafe==3.0.2
matplotlib-inline==0.2.1
mccabe==0.7.0
mistune==3.2.0
multidict==6.6.4
mypy_extensions==1.1.0
nbclient==0.10.4
nbconvert==7.17.0
nbformat==5.10.4
nest-asyncio==1.6.0
nodeenv==1.10.0
notebook==7.5.3
notebook_shim==0.2.4
packaging==25.0
pandocfilters==1.5.1
parso==0.8.6
pathspec==1.1.1
platformdirs==4.9.1
pluggy==1.6.0
postgres==4.0
pre_commit==4.6.2
prometheus_client==0.24.1
prompt_toolkit==3.0.52
propcache==0.3.2
psutil==7.2.2
psycopg2-binary==2.9.12
psycopg2-pool==1.2
pure_eval==0.2.3
pycodestyle==2.14.0
pycparser==3.0
pydantic==2.13.4
pydantic_core==2.46.4
pyflakes==3.4.0
Pygments==2.19.2
PyPDF2==3.0.1
pyTelegramBotAPI==4.29.0
pytest==8.4.1
pytest-asyncio==1.4.0
python-dateutil==2.9.0.post0
python-discovery==1.5.2
python-dotenv==1.1.1
python-json-logger==4.0.0
python-multipart==0.0.32
pytokens==0.4.1
PyYAML==6.0.3
pyzmq==27.1.0
referencing==0.37.0
requests==2.32.5
rfc3339-validator==0.1.4
rfc3986-validator==0.1.1
rfc3987-syntax==1.1.0
rpds-py==0.30.0
Send2Trash==2.1.0
setuptools==82.0.0
six==1.17.0
sniffio==1.3.1
soupsieve==2.8.3
SQLAlchemy==2.0.52
stack-data==0.6.3
starlette==1.6.0
tabulate==0.10.0
terminado==0.18.1
tinycss2==1.4.0
tornado==6.5.4
traitlets==5.14.3
typing-inspection==0.4.4
typing_extensions==4.16.0
tzdata==2025.3
uri-template==1.3.0
urllib3==2.5.0
uvicorn==0.52.4
virtualenv==21.7.4
wcwidth==0.6.0
webcolors==25.10.0
webencodings==0.5.1
websocket-client==1.9.0
Werkzeug==3.1.3
wheel==0.45.1
yarl==1.20.1

```

---

## Тестирование

Проект покрыт интеграционными и unit-тестами (pytest). Для тестов используется
SQLite in-memory (файловая), что позволяет запускать тесты без поднятия PostgreSQL.

```bash
# Установка зависимостей для тестов
pip install pytest pytest-asyncio httpx aiosqlite

# Запуск тестов
pytest tests/ -v
```

### Что тестируется:

- **База данных** — создание Person/Booking, каскадное удаление, Enum-статусы, NOT NULL-ограничения.
- **Сервисы** — `add_new_booking`, `get_information_about_bookings`, `get_booking_by_id`, `delete_booking`.
  Проверяются позитивные сценарии, конфликты (409), 404, откат транзакций.
- **Роуты** — end-to-end тесты через `httpx.AsyncClient`:
  - `POST /bookings` — 201, 409, 422
  - `GET /bookings` — 200 (пустой список, фильтр по дате, все записи), 422
  - `GET /bookings/{id}` — 200, 404, 422
  - `DELETE /bookings/{id}` — 200, 404, 422, идемпотентность

---

## API Endpoint'ы

### 1. POST /bookings

**Что делает:** Создаёт новое бронирование. Валидирует входные данные.
Проверяет отсутствие дублирующей брони на ту же дату и время.

**HTTP Params:**
- `information_booking` (body, JSON) — данные для создания брони

**Входные данные (JSON):**
```json
{
  "name": "Иван Петров",
  "phone": "+79161234567",
  "booking_date": "2026-09-10",
  "booking_time": "19:00",
  "guests": 4
}
```

**Валидация:**
- `name` — минимум 2 символа, только буквы, пробелы и дефисы.
- `phone` — формат `+7XXXXXXXXXX` или `8XXXXXXXXXX` (11 цифр).
- `booking_date` — сегодня или позже, не более чем на 90 дней вперёд.
- `booking_time` — только целые часы с 12:00 до 22:00.
- `guests` — от 1 до 12.
- На сегодняшний день нельзя бронировать время в прошлом.

**Ответ (201 Created):**
```json
{
  "id": 1,
  "name": "Иван Петров",
  "booking_date": "2026-09-10",
  "booking_time": "19:00",
  "guests": 4,
  "status": "Создана/Confirmed"
}
```

**Возможные ошибки:**
- `422` — Невалидные входные данные (неверная дата, время, телефон и т.д.)
- `409` — На эту дату и время уже есть бронь.
- `500` — Ошибка базы данных.

---

### 2. GET /bookings

**Что делает:** Возвращает список всех бронирований.
Опционально фильтрует по дате через query-параметр `date`.

**HTTP Params:**
- `date` (query, опционально) — дата в формате `YYYY-MM-DD`

**Пример запроса:**
```bash
GET /bookings?date=2026-09-10
```

**Ответ (200 OK):**
```json
[
  {
    "id": 1,
    "name": "Иван Петров",
    "booking_date": "2026-09-10",
    "booking_time": "19:00",
    "guests": 4,
    "status": "Создана/Confirmed"
  }
]
```

**Особенности:**
- Если бронирований нет — возвращается пустой список `[]`.
- Если передана невалидная дата — `422`.

---

### 3. GET /bookings/{id}

**Что делает:** Возвращает данные конкретного бронирования по его ID.

**HTTP Params:**
- `id` (URL) — ID бронирования

**Ответ (200 OK):**
```json
{
  "id": 1,
  "name": "Иван Петров",
  "booking_date": "2026-09-10",
  "booking_time": "19:00",
  "guests": 4,
  "status": "Создана/Confirmed"
}
```

**Возможные ошибки:**
- `404` — Бронь с таким ID не найдена.
- `422` — Некорректный формат ID (строка вместо числа).
- `500` — Ошибка базы данных.

---

### 4. DELETE /bookings/{id}

**Что делает:** Отменяет бронирование по ID. Статус меняется на `Отменена/Cancelled`.
Запись не удаляется физически — сохраняется в истории.

**HTTP Params:**
- `id` (URL) — ID бронирования для отмены

**Ответ (200 OK):**
```json
{
  "id": 1,
  "name": "Иван Петров",
  "booking_date": "2026-09-10",
  "booking_time": "19:00",
  "guests": 4,
  "status": "Отменена/Cancelled"
}
```

**Возможные ошибки:**
- `404` — Бронь с таким ID не найдена.
- `422` — Некорректный формат ID.
- `500` — Ошибка базы данных.

**Примечание:** Повторная отмена уже отменённой брони возвращает `200` (идемпотентность).

---

## Модели данных

### Person

    | Поле | Тип | Описание |
    |------|-----|----------|
    | `id` | Integer, PK | Уникальный идентификатор |
    | `name` | String, NOT NULL | Имя клиента |
    | `phone` | String, NOT NULL | Номер телефона |
    | `bookings` | Relationship | Список броней клиента (каскадное удаление) |

### Booking

    | Поле | Тип | Описание |
    |------|-----|----------|
    | `id` | Integer, PK | Уникальный идентификатор брони |
    | `person_id` | Integer, FK → Person.id | Связь с клиентом |
    | `booking_date` | Date, NOT NULL | Дата бронирования |
    | `booking_time` | Time, NOT NULL | Время бронирования |
    | `guests` | Integer, NOT NULL | Количество гостей |
    | `status` | Enum | `Ожидает/Pending`, `Создана/Confirmed`, `Отменена/Cancelled` |

---

## Логирование

Проект использует стандартный модуль `logging` с `dictConfig`.
Логи разделены по уровням:
- **route_logger** — логи роутов (входящие запросы, ответы, ошибки)
- **services_logger** — логи бизнес-логики (CRUD-операции, валидация)

---

## Примечания

- При первом запуске через Docker таблицы создаются автоматически (`Base.metadata.create_all`).
- Для локальной разработки без Docker убедитесь, что PostgreSQL запущен и `.env` настроен корректно.
- Все даты и время в API передаются в формате ISO 8601 (`YYYY-MM-DD`, `HH:MM`).
