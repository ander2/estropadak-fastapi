FROM python:3.13.1-slim
WORKDIR /code
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY ./pyproject.toml /code/
COPY ./uv.lock /code/
COPY ./app /code/app
COPY ./log_conf.yaml /code/
RUN uv sync --frozen --no-cache
CMD ["uv", "run", "uvicorn", "app.main:api", "--host", "0.0.0.0", "--workers", "4", "--proxy-headers", "--port", "80", "--log-config", "log_conf.yaml"]