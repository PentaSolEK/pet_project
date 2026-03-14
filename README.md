Это бэкенд-часть (RESTful API) для сервиса по продаже билетов на мероприятия. API позволяет клиентским приложениям (веб-сайтам, мобильным приложениям) получать информацию о концертах, группах, концертных залах.

Ключевые функции и технологии:

- Язык и фреймворк: Python (FastAPI).
- База данных: MySQL (для хранения структурированных данных о событиях, заказах, пользователях).
- Аутентификация: JWT.
- Основные endpoints: Концерты (`/api/v1/concerts`), Музыкальные группы (`/api/v1/groups`), Залы (`/api/v1/halls`), Типы билетов (`/api/v1/tickettypes`), Продажи (`/api/v1/sales`).

## Структура проекта

Основной код приложения находится в каталоге **`src/ticketshop/`**:

- `api/` — маршруты и зависимости FastAPI (v1)
- `core/` — конфигурация, безопасность, логирование, брокер
- `db/` — сессия БД и миграции
- `domain/` — доменная логика по сущностям (concerts, halls, sales, tickets, users и т.д.)
- `messaging/` — издатели/подписчики сообщений
- `main.py` — точка входа приложения

## Запуск проекта

1. Установите зависимости (из корня проекта):

   ```bash
   poetry install
   ```

2. Создайте файл `.env` в корне проекта с переменными (как в `src.ticketshop.core.config`), например:

   ```
   database_url=mysql+asyncmy://USER:PASSWORD@HOST/DB_NAME
   secret_key=your-secret-key
   algorithm=HS256
   rabbitmq_url=amqp://guest:guest@localhost/
   ```

3. Запустите API (из корня проекта):

   **Вариант 1 — через скрипт (рекомендуется):**
   ```bash
   poetry run python run.py
   ```
   Скрипт `run.py` добавляет корень проекта в `PYTHONPATH`, поэтому модуль `src.ticketshop` находится без ошибки.

   **Вариант 2 — через uvicorn с явным PYTHONPATH (Windows PowerShell):**
   ```bash
   $env:PYTHONPATH = "."; poetry run uvicorn src.ticketshop.main:app --reload --host 0.0.0.0 --port 8000
   ```
   В CMD: `set PYTHONPATH=. && poetry run uvicorn src.ticketshop.main:app --reload --host 0.0.0.0 --port 8000`

   Документация API будет доступна по адресам:
   - Swagger UI: http://127.0.0.1:8000/docs
   - ReDoc: http://127.0.0.1:8000/redoc

## Устаревшие файлы (вне `src/`)

После перехода на структуру в `src/ticketshop/` следующие каталоги и файлы в корне проекта считаются устаревшими и не используются приложением:

- **`data/`** — старый `init_db.py` (сессия БД теперь в `src/ticketshop/db/session.py`)
- **`models/`** — старые `db_models.py`, `other_models.py` (модели перенесены в `src/ticketshop/domain/*/models.py`)
- **`service/`** — старые `auth.py`, `fs_broker.py`, `fs_subs/`, `common_params.py`, `log.py` (логика в `src/ticketshop/core/`, `api/`, `messaging/`)
- **`web/`** — старый `user_functions.py`
- **`front.html`** — статическая страница

Их можно удалить после проверки, что всё работает из `src/`. Тесты переведены на новую структуру (`src.ticketshop.domain.*`).

