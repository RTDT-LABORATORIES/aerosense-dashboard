FROM python:3.10-slim

WORKDIR /workspaces/aerosense-dashboard

# Install poetry
RUN pip install poetry
RUN poetry config virtualenvs.create false

# Install python dependencies. Note that poetry installs any root packages by default, but this is not available at this
# stage of caching dependencies. So we do a dependency-only install here to cache the dependencies, then a full poetry
# install post-create to install any root packages.
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-interaction --no-root

COPY . .
RUN poetry install

EXPOSE $PORT

ARG GUNICORN_WORKERS=1
ENV GUNICORN_WORKERS=$GUNICORN_WORKERS

ARG GUNICORN_THREADS=8
ENV GUNICORN_THREADS=$GUNICORN_THREADS

# Timeout is set to 0 to disable the timeouts of the workers to allow Cloud Run to handle instance scaling.
CMD exec gunicorn --bind :$PORT --workers $GUNICORN_WORKERS --threads $GUNICORN_THREADS --timeout 0 app:app
