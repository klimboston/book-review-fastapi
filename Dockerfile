FROM python:3.14-slim

RUN useradd -m app

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:0.12.7 /uv /uvx /bin/

RUN chown app:app /app

USER app

COPY --chown=app:app pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev --no-install-project

COPY --chown=app:app src/ ./src/
COPY --chown=app:app alembic/ ./alembic/
COPY --chown=app:app alembic.ini ./
COPY --chown=app:app README.md ./

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH=.

CMD ["uvicorn", "src.book_review_project.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

