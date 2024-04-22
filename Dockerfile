# syntax=docker/dockerfile:1.5-labs
FROM docker.io/node:20 AS build

# This doesn't work because sr.ht is not github LOL
# ADD --keep-git-dir=false https://git.sr.ht/~emersion/gamja /gamja
ADD https://git.sr.ht/~emersion/gamja/archive/master.tar.gz /gamja.tar.gz
RUN tar -xzf /gamja.tar.gz && mv /gamja-master /gamja && cd /gamja && npm install --production

FROM docker.io/caddy:2.7 AS gamja

COPY --from=build /gamja /gamja
COPY gamja/Caddyfile /etc/caddy/Caddyfile
COPY gamja/config.json /gamja/config.json
