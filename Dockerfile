FROM python:3.8-slim-buster

ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  POETRY_VERSION=1.1.13 \ 
  NUM_WORKERS=1 \
  NUM_THREADS=1 \
  API_PORT=8001

RUN pip install "poetry==$POETRY_VERSION"

# Copy only requirements to cache them in docker layer
WORKDIR /api
COPY poetry.lock pyproject.toml /api/

RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi

COPY . /api

EXPOSE ${API_PORT}

CMD gunicorn -k uvicorn.workers.UvicornWorker main:fastapi_app --workers="${NUM_WORKERS}" --threads="${NUM_THREADS}" --bind="0.0.0.0:${API_PORT}" --access-logfile - --error-logfile -
