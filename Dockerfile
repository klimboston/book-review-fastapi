FROM python:3.14-slim

WORKDIR /app

RUN pip install uv

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev --no-install-project

COPY src/ ./src/
COPY .env ./
COPY README.md ./

ENV PYTHONPATH=.

CMD ["uv", "run", "fastapi", "run", "src/book_review_project/main.py", "--host", "0.0.0.0", "--port", "8000"]

