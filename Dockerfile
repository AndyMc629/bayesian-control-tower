FROM python:3.12-slim AS builder

WORKDIR /build

RUN pip install uv

COPY pyproject.toml .
COPY src/ src/

RUN uv sync --no-dev --no-editable


FROM python:3.12-slim AS runtime

WORKDIR /app

RUN useradd -m -u 1001 appuser

COPY --from=builder /build/.venv /app/.venv

COPY src/ src/

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

USER appuser

EXPOSE 8000

CMD ["uvicorn", "bayesian_control_tower.server:app", "--host", "0.0.0.0", "--port", "8000"]
