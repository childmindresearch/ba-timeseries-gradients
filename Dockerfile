FROM python:3.11-slim-buster

WORKDIR /app

COPY src ./pyproject.toml ./poetry.lock ./

ENV PYTHONPATH "${PYTHONPATH}:/app"

# Workaround for the python environment installation to not install vtk.
# VTK builds have issues on Apple Silicon.
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir poetry && \
    poetry export --only main --without-hashes --without-urls | grep -vE "^vtk" > requirements.txt && \
    pip install --no-cache-dir --no-deps -r requirements.txt && \
    rm requirements.txt poetry.lock pyproject.toml

ENTRYPOINT [ "python", "/app/ba_timeseries_gradients/cli.py" ]
CMD [ "python", "/app/ba_timeseries_gradients/cli.py", "-h" ]
