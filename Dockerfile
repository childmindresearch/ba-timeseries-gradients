FROM python:3.11-slim-buster

WORKDIR /app

COPY src ./pyproject.toml ./poetry.lock ./

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false && \
    poetry install --only main --no-interaction --no-ansi

ENTRYPOINT [ "poetry run grag_brainspace" ]
CMD [ "poetry run grag_brainspace --help" ]
