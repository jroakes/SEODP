FROM python:3.9-slim

WORKDIR /app

COPY pyproject.toml .
COPY .env .
COPY seodpconfig.yaml .

RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev

COPY . .

CMD ["python", "src/seodp/main.py"]