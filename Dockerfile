FROM python:3.9-slim

ENV PYTHONUNBUFFERED=1 POETRY_HOME="/opt/poetry" POETRY_VIRTUALENVS_IN_PROJECT=true
RUN apt-get update && apt-get install -y build-essential curl software-properties-common git
RUN rm -rf /var/lib/apt/lists/*
RUN curl -sSL https://install.python-poetry.org | python3 - --version 1.8.3
ENV PATH="${PATH}:${POETRY_HOME}/bin"

WORKDIR /app
COPY pyproject.toml seodpconfig.yaml .env ./

RUN poetry install --only=main --no-interaction --no-ansi

COPY . ./

CMD ["poetry", "run", "python", "src/seodp/main.py"]