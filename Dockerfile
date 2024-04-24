# syntax=docker/dockerfile:1.5-labs
FROM docker.io/node:20-alpine AS build

# This doesn't work because sr.ht is not github LOL
# ADD --keep-git-dir=false https://git.sr.ht/~emersion/gamja /gamja
RUN apk add bash git
RUN git clone https://git.sr.ht/~emersion/gamja /gamja
WORKDIR /gamja

# Apply patches
RUN mkdir /gamja-patches
COPY gamja/patches/*.patch /gamja-patches
ENV GIT_COMMITTER_NAME="ocfbot" GIT_COMMITTER_EMAIL="ocfbot@ocf.berkeley.edu"
RUN bash -c "git am < /gamja-patches/*.patch"

RUN npm install --production

FROM docker.io/caddy:2.7 AS gamja

COPY --from=build /gamja /gamja
COPY gamja/Caddyfile /etc/caddy/Caddyfile
COPY gamja/config.json /gamja/config.json

FROM docker.io/python:3.11 AS sopel

RUN adduser --disabled-password --gecos "" --home /home/sopel --uid 1000 sopel
RUN apt-get update && apt-get install -y --no-install-recommends libcrack2-dev && rm -rf /var/lib/apt/lists/*
USER sopel
ENV PATH="${PATH}:/home/sopel/.local/bin"
RUN python -m pip install pipx && pipx install git+https://github.com/sopel-irc/sopel.git#ab32aca08f7bf67d1ba754fdfc22a10ee5a442d0 && pipx inject sopel ocflib celery kombu redis
CMD [ "sopel", "start" ]
