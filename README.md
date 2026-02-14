# DressCast

Микросервисная система: погода и рекомендации по одежде. Пользователи привязывают города, получают прогноз и советы «что надеть» по выбранному городу.

**Демо:** [видео на YouTube](https://youtu.be/G59iIhcJgXE)

**О проекте.** Реализация собрана в **монорепе чисто для наглядности** — один репозиторий и общие proto/тесты упрощают изучение. В реальных проектах микросервисы обычно выносят в **отдельные репозитории**: у каждого свой контур тестов, свои proto-контракты (или общий пакет контрактов как зависимость), отдельный CI/CD. Цель этой системы — **показать, как микросервисы общаются по gRPC и как это сочетается с REST API**: единая точка входа (Gateway) принимает REST и gRPC, внутри оркестрирует вызовы к сервисам Users, Weather и Dress Advice по gRPC.

---

## Содержание

- [Запуск проекта](#запуск-проекта)
- [Микросервисы](#микросервисы)
- [Кеширование](#кеширование)
- [Дополнительно](#дополнительно) (тесты, линтеры, CI/CD, конфигурация)

---

## Запуск проекта

### Требования

- Python 3.10+
- [Poetry](https://python-poetry.org/docs/#installation) (управление зависимостями)
- Redis и PostgreSQL (локально или в Docker)

### Установка зависимостей

```bash
poetry install
```

Создаётся виртуальное окружение и устанавливаются все зависимости (включая dev-группу).

### Генерация gRPC-кода из proto

Перед первым запуском сервисов необходимо сгенерировать код из `.proto`:

```bash
make proto
# или: poetry run python scripts/generate_proto.py
```

### Переменные окружения

Скопируйте пример конфигурации и при необходимости отредактируйте:

```bash
cp .env.example .env
```

Обязательно задайте в `.env` (для локального запуска):

- `USERS_DATABASE_URL` — строка подключения к PostgreSQL (если не используете значения по умолчанию из `.env.example`)
- Для бота: `TELEGRAM_BOT_TOKEN`
- Для Dress Advice: `OPENAI_API_KEY`

### Запуск инфраструктуры (Redis и PostgreSQL)

Если Redis и PostgreSQL ещё не запущены, поднимите их, например:

```bash
# Redis
docker run -d -p 6379:6379 redis:7-alpine

# PostgreSQL
docker run -d -p 5432:5432 -e POSTGRES_USER=dresscast -e POSTGRES_PASSWORD=dresscast -e POSTGRES_DB=dresscast postgres:16-alpine
```

Либо используйте уже установленные экземпляры и укажите в `.env` свои URL (например `USERS_DATABASE_URL`, `WEATHER_REDIS_URL`, `DRESS_ADVICE_REDIS_URL`).

### Локальный запуск сервисов (в отдельных терминалах)

Из корня проекта, с активированным окружением (`poetry shell` или `poetry run`):

| Порядок | Команда | Порт / назначение |
|--------|---------|--------------------|
| 1 | `python -m users.main` | gRPC 50053 |
| 2 | `python -m weather.main` | gRPC 50051 |
| 3 | `python -m dress_advice.main` | gRPC 50052 |
| 4 | `uvicorn gateway.main:app --host 0.0.0.0 --port 8000` или `python -m gateway.main` | HTTP 8000, gRPC 50050 |
| 5 (опционально) | `python -m workers.scheduler.main` | Периодическое обновление кэша прогнозов |
| 6 (опционально) | `python -m telegram_bot.main` | Telegram-бот (нужен `TELEGRAM_BOT_TOKEN`, `GATEWAY_GRPC_ADDR=localhost:50050`) |
| 7 (опционально) | `python -m mcp_server.main` | MCP-сервер (stdio; для интеграции с AI-средами) |

После запуска:

- **REST API:** http://localhost:8000  
- **gRPC Gateway:** localhost:50050  

### Запуск через Docker Compose

Все сервисы (кроме MCP) можно поднять одной командой:

```bash
cp .env.example .env
# В .env при необходимости задайте: OPENAI_API_KEY, TELEGRAM_BOT_TOKEN
docker compose up -d
```

- **REST API:** http://localhost:8000  
- **gRPC Gateway:** localhost:50050  
- Telegram-бот стартует, если в окружении задан `TELEGRAM_BOT_TOKEN`.

**Отказоустойчивость:** можно тестировать систему без Telegram и без OpenAI. Если не задать `TELEGRAM_BOT_TOKEN`, контейнер бота остаётся в работе (режим «отключён»), остальные сервисы работают. Если не задать `OPENAI_API_KEY`, сервис Dress Advice стартует; при запросе совета по одежде вернётся ошибка `ADVICE_PROVIDER_NOT_CONFIGURED` (gRPC `FAILED_PRECONDITION`), без падения сервиса.

Пересборка образов:

```bash
docker compose up --build -d
```

### Создание пользователя-администратора

- **При первом запуске:** в `.env` можно задать `USERS_CREATE_ADMIN_USERNAME=admin` (или в Docker `CREATE_ADMIN_USERNAME=admin`) — пользователь `admin` будет создан при старте сервиса Users.
- **После запуска (локально):** `make create-admin USERNAME=admin`
- **В Docker:** `make create-admin-docker USERNAME=admin`

---

## Микросервисы

Система построена по принципам: один сервис — одна зона ответственности, слои api → application → domain → infrastructure, единые коды ошибок и при необходимости i18n.

| Сервис | Порт (gRPC) | Назначение |
|--------|-------------|------------|
| **Gateway** | 50050 | Единая точка входа: REST (FastAPI) и gRPC. Авторизация JWT для REST. Оркестрация вызовов к Users, Weather и Dress Advice. Не содержит бизнес-логики доменов. |
| **Users** | 50053 | Учётные записи (username, password_hash, telegram_id, is_admin, locale), города пользователя (user_id, name, lat, lon). PostgreSQL. Proto: `users.proto`, сервис `UsersService`. |
| **Weather** | 50051 | Текущая погода и прогноз по координатам (lat, lon, date, параметры). Кэш в Redis. Внешний API: Open-Meteo. |
| **Dress Advice** | 50052 | Текстовые рекомендации «что надеть» по погодным данным. Кэш в Redis. LLM: OpenAI API. |
| **Scheduler** | — | Фоновый воркер: периодически вызывает Users.ListAllCoordinates и Weather.RefreshForecasts для подогрева кэша прогнозов. |
| **Telegram Bot** | — | Обработка команд пользователя (`/start`, `/weather`, `/dress`, `/cities`, `/add_city`, выбор языка). Вызов Gateway по gRPC. Локализованные ответы (i18n: ru/en). |
| **MCP Server** | — | Опциональный MCP-сервер (stdio) для интеграции с AI-средами; обращается к Gateway по gRPC. |

### Scheduler

Фоновый воркер, который периодически подогревает кэш прогнозов погоды. В цикле с заданным интервалом (по умолчанию 15 минут, `SCHEDULER_INTERVAL_SECONDS`) он запрашивает у сервиса **Users** список всех координат городов пользователей (`ListAllCoordinates`), затем передаёт их в сервис **Weather** методом `RefreshForecasts`. Weather для каждой пары (широта, долгота) запрашивает текущую погоду у Open-Meteo и сохраняет результат в Redis. В результате при запросе прогноза по городу пользователя данные чаще оказываются уже в кэше. При временных сбоях (сервисы недоступны, сеть) воркер повторяет попытку с экспоненциальной задержкой (`SCHEDULER_MAX_RETRIES`, `SCHEDULER_RETRY_BACKOFF_SECONDS`); после старта может выждать задержку перед первым запуском (`startup_delay`), чтобы дождаться подъёма Users и Weather.

**Стек:** Python 3.10+, FastAPI, gRPC, Redis, PostgreSQL, OpenAI API, Telegram Bot API.

**Точки входа для клиентов:**

- **REST API** (Gateway) — для веб- и мобильных клиентов, авторизация JWT.
- **gRPC** (Gateway) — для Telegram-бота и MCP-сервера.
- **Telegram-бот** — основной пользовательский интерфейс с командами и выбором языка.

---

## Кеширование

Кеш снижает нагрузку на внешние API (Open-Meteo, OpenAI), ускоряет ответы и уменьшает риск лимитов. Используется паттерн **Cache-Aside**: приложение сначала читает из кэша; при промахе запрашивает данные у провайдера, записывает в кэш и возвращает результат. Хранилище — **Redis** (один инстанс для Weather и Dress Advice, разные ключи). Если Redis недоступен, сервисы стартуют без кэша (каждый запрос идёт во внешний API).

### Что кешируется

| Сервис        | Данные | Ключ | TTL (по умолчанию) |
|---------------|--------|------|---------------------|
| **Weather**   | Текущая погода по координатам | `current:{lat}:{lon}` | 1 час (3600 с) |
| **Weather**   | Прогноз по координатам и времени | `forecast:{lat}:{lon}:{date}:{time}` | 1 час |
| **Dress Advice** | Текст рекомендации по погоде и языку | `advice:{temp}:{humidity}:{wind}:{precip}:{locale}` | 1 час |

В кэше Weather хранятся агрегированные погодные данные (температура, влажность, ветер, осадки, время). В кэше Dress Advice — готовый текст совета «что надеть» для комбинации параметров погоды и локали (ru/en).

### Как устроено

- **Weather:** use case (например `GetForecastUseCase`) перед вызовом Open-Meteo проверяет Redis по ключу; при попадании возвращает сохранённый `WeatherData`; при промахе вызывает провайдера, сериализует ответ в JSON, пишет в Redis с TTL и возвращает данные.
- **Dress Advice:** use case `GetAdviceUseCase` по ключу из параметров погоды и `locale` ищет в Redis текст совета; при промахе вызывает OpenAI, сохраняет ответ в кэш с TTL и возвращает текст.
- Оба сервиса при старте подключаются к Redis по `WEATHER_REDIS_URL` / `DRESS_ADVICE_REDIS_URL`. При ошибке подключения кэш не используется (логируется предупреждение), работа продолжается без кэша.

### Подогрев кэша (Scheduler)

Воркер **Scheduler** периодически (интервал задаётся `SCHEDULER_INTERVAL_SECONDS`, по умолчанию 900 с) запрашивает у Users список всех координат городов (`ListAllCoordinates`) и передаёт их в Weather (`RefreshForecasts`). Weather для каждой пары (lat, lon) запрашивает текущую погоду у Open-Meteo и кладёт результат в кэш. Так при первом запросе прогноза по городу пользователя данные уже могут быть в кэше.

---

## Дополнительно

### Тесты

```bash
poetry run pytest tests/
# или: make test
```

### Линтеры, форматирование и безопасность

- **Ruff** — линтинг и форматирование (настройки в `pyproject.toml`)
- **Bandit** — проверка безопасности
- **pre-commit** — хуки при коммите (ruff, bandit, trailing whitespace и др.)

```bash
poetry run pre-commit install
poetry run pre-commit run --all-files
```

Через Makefile (в среде с `make`, например Git Bash или WSL):

```bash
make install      # poetry install
make pre-commit   # установка хуков и прогон по всем файлам
make lint         # ruff check
make format       # ruff format и fix
make security     # bandit
make test         # pytest
make all          # lint + format + security + test
```

### CI/CD (GitHub Actions)

- **CI** (`.github/workflows/ci.yml`) — при каждом push и pull request в `main`/`master`: установка зависимостей (Poetry), генерация proto, линтинг (Ruff), проверка форматирования, проверка безопасности (Bandit), тесты (pytest). Запускается для Python 3.10 и 3.11.
- **CD** (`.github/workflows/cd.yml`) — при push в `main`/`master`: сборка Docker-образа и публикация в **GitHub Container Registry** (ghcr.io). Образ помечается тегами `latest` и `sha-<short>`. Запустить вручную можно через **Actions → CD → Run workflow**.

Для публикации в GHCR достаточно стандартного `GITHUB_TOKEN` (права `packages: write` заданы в workflow). Готовый образ можно подтянуть как `docker pull ghcr.io/<owner>/<repo>:latest`.

### Конфигурация сервисов

У каждого сервиса свой префикс переменных окружения: `GATEWAY_`, `USERS_`, `WEATHER_`, `DRESS_ADVICE_`, `SCHEDULER_`, `TELEGRAM_BOT_`. Порты и адреса задаются в конфиге; в Docker Compose они переопределяются для общения между контейнерами. Секреты (JWT, OpenAI API key, пароли БД) задаются через окружение и не хранятся в репозитории.
