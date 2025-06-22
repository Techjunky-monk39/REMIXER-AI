# syntax=docker/dockerfile:1

FROM python:3.8.10-slim AS base

# Update system packages for security
RUN apt-get update && apt-get upgrade -y && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

FROM base AS builder

COPY --link flask_app/requirements.txt ./
ENV PIP_CACHE_DIR=/root/.cache/pip

RUN --mount=type=cache,target=$PIP_CACHE_DIR \
    python -m venv .venv && \
    .venv/bin/pip install --upgrade pip && \
    .venv/bin/pip install -r requirements.txt

# Explicitly copy flask_app directory and all code
COPY --link flask_app ./flask_app

FROM base AS final

RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/ /app/

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH=/app

RUN mkdir -p /app/uploads && chown -R appuser:appgroup /app/uploads

USER appuser

EXPOSE 8080

CMD ["gunicorn", "-b", "0.0.0.0:8080", "flask_app.app:app"]
