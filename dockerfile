FROM python:3.12-slim

WORKDIR /app

# Instala o uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copia arquivos de dependência primeiro (cache de camadas do Docker)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Copia o resto do código
COPY . .

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]