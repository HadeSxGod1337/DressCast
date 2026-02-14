.PHONY: install install-dev proto lint format security test all clean run-gateway run-weather run-users run-dress-advice run-scheduler run-bot run-mcp docker-up docker-build docker-build-no-cache create-admin pre-commit

# Poetry
POETRY = poetry

# Install deps (creates venv via Poetry if needed)
install:
	$(POETRY) install

# Install with dev group (default)
install-dev:
	$(POETRY) install --with dev

# Install pre-commit hooks
pre-commit:
	$(POETRY) run pre-commit install
	$(POETRY) run pre-commit run --all-files

# Generate gRPC code from proto
proto:
	$(POETRY) run python scripts/generate_proto.py

# Lint (ruff)
lint:
	$(POETRY) run ruff check .

# Format (ruff)
format:
	$(POETRY) run ruff format .
	$(POETRY) run ruff check --fix .

# Security (bandit)
security:
	$(POETRY) run bandit -c pyproject.toml -r . -x proto_gen,venv,.venv

# Run tests
test:
	$(POETRY) run pytest tests/

# Lint + format + security + test
all: lint format security test

# Clean generated and cache
clean:
	rm -rf proto_gen/*.py proto_gen/__pycache__ 2>/dev/null || true
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true

# Run services (examples; require env vars)
run-gateway:
	$(POETRY) run uvicorn gateway.main:app --host 0.0.0.0 --port 8000

run-weather:
	$(POETRY) run python -m weather.main

run-users:
	$(POETRY) run python -m users.main

run-dress-advice:
	$(POETRY) run python -m dress_advice.main

run-scheduler:
	$(POETRY) run python -m workers.scheduler.main

run-bot:
	$(POETRY) run python -m telegram_bot.main

run-mcp:
	$(POETRY) run python -m mcp_server.main

docker-up:
	docker compose up -d

docker-build:
	docker compose up --build -d

docker-build-no-cache:
	docker compose build --no-cache && docker compose up -d

# Create admin user locally: make create-admin USERNAME=admin
create-admin:
	$(POETRY) run python scripts/create_admin.py --username $(USERNAME)

# Create admin in Docker (after docker-up): make create-admin-docker USERNAME=admin
create-admin-docker:
	docker compose exec users-service python scripts/create_admin.py --username $(USERNAME)
