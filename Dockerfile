FROM python:3.11
COPY --from=ghcr.io/astral-sh/uv:0.8.8@sha256:67b2bcccdc103d608727d1b577e58008ef810f751ed324715eb60b3f0c040d30 /uv /uvx /bin/

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY README.md pyproject.toml uv.lock ./

RUN uv venv && uv sync --frozen --no-cache --no-install-project --no-dev

COPY robotkirby ./robotkirby

# separate step to allow dependency caching
RUN uv sync --no-dev && uv lock --check

CMD [ "uv", "run", "python", "-m", "robotkirby" ]
