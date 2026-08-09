FROM ghcr.io/astral-sh/uv:python3.14-trixie-slim AS production

ARG PUID=1000
ARG PGID=1000

LABEL maintainer="ALERT <alexey.rubasheff@gmail.com>"

ENV \
    GRADIO_URL="http://gradio:7860" \
    UVICORN_PORT=8000 \
    UVICORN_HOST=0.0.0.0

EXPOSE $UVICORN_PORT

ENV \
    # uv
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_FROZEN=1 \
    UV_NO_PROGRESS=true \
    UV_NO_DEV=true \
    # writable for any PUID at runtime; used as a cache mount during build
    UV_CACHE_DIR=/tmp/uv-cache \
    # Python
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONIOENCODING=utf-8 \
    LANG=en_US.UTF-8 \
    LANGUAGE=en_US.UTF-8 \
    # pip
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    # app
    APP_DIR=/app \
    SOURCE_DIR_NAME=app


WORKDIR $APP_DIR

RUN groupadd --gid ${PGID} appuser \
    && useradd --uid ${PUID} --gid ${PGID} --no-log-init --create-home appuser

RUN --mount=type=cache,target=$UV_CACHE_DIR \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --all-packages --no-dev

COPY . .

HEALTHCHECK --interval=10s --timeout=5s --start-period=10s --retries=5 \
        CMD python -c "import urllib.request as u; u.urlopen('http://127.0.0.1:${UVICORN_PORT}/health', timeout=1)"

ENV HOME=/tmp

USER ${PUID}:${PGID}

ENTRYPOINT []

CMD ["sh", "-c", "exec uv run --no-sync uvicorn ${SOURCE_DIR_NAME}.__main__:app --host ${UVICORN_HOST} --port ${UVICORN_PORT}"]
