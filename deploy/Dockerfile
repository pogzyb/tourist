FROM ghcr.io/opentofu/opentofu:minimal AS tofu

FROM python:3.13-alpine

ARG CREATED
ARG TOURIST_VERSION
ARG REVISION

LABEL org.opencontainers.image.title="tourist-deploy"
LABEL org.opencontainers.image.description="Use this container to deploy the tourist project."
LABEL org.opencontainers.image.version=$TOURIST_VERSION
LABEL org.opencontainers.image.authors="pogzyb@umich.edu"
LABEL org.opencontainers.image.url="https://github.com/pogzyb/tourist/deploy"
LABEL org.opencontainers.image.source="https://github.com/pogzyb/tourist/deploy"
LABEL org.opencontainers.image.documentation="https://github.com/pogzyb/tourist/deploy"
LABEL org.opencontainers.image.created=$CREATED
LABEL org.opencontainers.image.revision=$REVISION
LABEL org.opencontainers.image.licenses="MIT"

COPY --from=tofu /usr/local/bin/tofu /usr/local/bin/tofu

RUN apk update && \
    apk add --no-cache \
    curl \
    git \
    aws-cli \
    docker \
    openrc && \
    pip install --no-cache-dir azure-cli typer

WORKDIR /tourist
COPY . .

COPY deploy.py /usr/local/bin/deploy.py
RUN chmod u+x /usr/local/bin/deploy.py

ENTRYPOINT ["deploy.py"]