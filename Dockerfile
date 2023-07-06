FROM python:3.11-alpine

WORKDIR /app

COPY ./pyproject.toml ./poetry.lock ./

RUN pip install --no-chace-dir --upgrade pip && \
    pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev --no-interaction --no-ansi

CMD ["python", "main.py"]

