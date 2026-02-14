FROM python:3.11-slim

WORKDIR /app

# Install poetry
RUN pip install --no-cache-dir poetry

# Copy dependency files
COPY pyproject.toml poetry.lock* ./

# Install deps (no dev)
RUN poetry config virtualenvs.create false \
    && poetry install

# Copy proto and generate
COPY proto/ proto/
COPY scripts/generate_proto.py scripts/
RUN python scripts/generate_proto.py

# Copy application code
COPY shared/ shared/
COPY gateway/ gateway/
COPY users/ users/
COPY weather/ weather/
COPY dress_advice/ dress_advice/
COPY workers/ workers/
COPY telegram_bot/ telegram_bot/
COPY mcp_server/ mcp_server/
COPY scripts/ scripts/

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Default command (override in docker-compose)
CMD ["python", "-m", "gateway.main"]
