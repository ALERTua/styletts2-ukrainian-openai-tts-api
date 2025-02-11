FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS production

LABEL maintainer="ALERT <alexey.rubasheff@gmail.com>"

ENV DATA_DIR=/data
ENV GRADIO_WEB=1
ENV GRADIO_ENDPOINT=web
ENV PORT=8000

EXPOSE $PORT

VOLUME ["$DATA_DIR"]

ENV \
    # uv
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_FROZEN=1 \
    UV_NO_PROGRESS=true \
    UV_CACHE_DIR=.uv_cache \
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
    SOURCE_DIR_NAME=styletts2-ukrainian-openai-tts-api


WORKDIR $APP_DIR

RUN apt-get update && apt-get install -y git ffmpeg \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN --mount=type=cache,target=$UV_CACHE_DIR \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --all-packages --no-dev

COPY . .

RUN cd $APP_DIR/styletts2-ukrainian/voices \
    && rm -rf ./voices \
    && ln -s . voices \
    && cd $APP_DIR

HEALTHCHECK --interval=10s --timeout=5s --start-period=10s --retries=5 \
        CMD curl localhost:${PORT}/health || exit 1

ENTRYPOINT []

CMD uv run uvicorn $SOURCE_DIR_NAME.__main__:app --host 0.0.0.0 --port ${PORT-8000}
