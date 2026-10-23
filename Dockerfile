# syntax=docker/dockerfile:1.7

FROM python:3.11-slim AS private-renderer

ARG PRIVATE_RENDERER_COMMIT=73edb4f3181e3da0f7f1990e2d68010e42aa8f4c

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates git \
    && rm -rf /var/lib/apt/lists/*

RUN --mount=type=secret,id=github_token,required=true \
    set -eu; \
    printf '#!/bin/sh\ncase "$1" in *Username*) printf "x-access-token\\n" ;; *) cat /run/secrets/github_token ;; esac\n' > /tmp/github-askpass; \
    chmod 700 /tmp/github-askpass; \
    GIT_ASKPASS=/tmp/github-askpass GIT_TERMINAL_PROMPT=0 \
        git clone --depth 1 --branch renderer \
        https://github.com/Justin-Stombler/Baseball-TV-design-source.git \
        /tmp/private-renderer; \
    test "$(git -C /tmp/private-renderer rev-parse HEAD)" = "$PRIVATE_RENDERER_COMMIT"; \
    rm /tmp/github-askpass

FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
COPY --from=private-renderer /tmp/private-renderer/src/render/ ./src/render/
COPY --from=private-renderer /tmp/private-renderer/data/visuals/ ./data/visuals/

CMD ["python", "-m", "src.main"]