FROM python:3.10-slim

# Add curl to the container (allow installation of poetry)
RUN apt update -y && apt install -y curl && rm -rf /var/lib/apt/lists/*

# Install poetry
# Note: Don't install poetry using pip. If you do, the chance will arise that poetry's
# dependencies will conflict with pip's or your own, resulting in the following error:
# https://github.com/python-poetry/poetry/issues/6288
ENV POETRY_HOME=/etc/poetry
RUN curl -sSL https://install.python-poetry.org | python -
ENV PATH "$POETRY_HOME/bin:$PATH"
RUN poetry config virtualenvs.create false

WORKDIR /workspaces/aerosense-dashboard

# Install python dependencies. Note that poetry installs any root packages by default, but this is not available at this
# stage of caching dependencies. So we do a dependency-only install here to cache the dependencies, then a full poetry
# install post-create to install the root package, which will change more rapidly than dependencies.
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-ansi --no-interaction --no-root

COPY . .
RUN poetry install --no-ansi --no-interaction

EXPOSE $PORT

ARG GUNICORN_WORKERS=1
ENV GUNICORN_WORKERS=$GUNICORN_WORKERS

ARG GUNICORN_THREADS=8
ENV GUNICORN_THREADS=$GUNICORN_THREADS

# Timeout is set to 0 to disable the timeouts of the workers to allow Cloud Run to handle instance scaling.
CMD exec gunicorn --bind :$PORT --workers $GUNICORN_WORKERS --threads $GUNICORN_THREADS --timeout 0 app:app
