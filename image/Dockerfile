# Get the digest via `docker buildx imagetools inspect debian:trixie-slim`
# (the FIRST digest shown there - that's the manifest-list digest covering
# all arches, NOT the one from `docker inspect` on a locally pulled image,
# which would only be valid for the build host's architecture and would
# break arm64 builds)
FROM debian:trixie-slim

ARG TARGETARCH

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        syslog-ng cron ca-certificates wget procps python3 \
    && rm -rf /var/lib/apt/lists/* \
    && wget -q "https://github.com/logdyhq/logdy-core/releases/latest/download/logdy_linux_${TARGETARCH}" \
         -O /usr/local/bin/logdy \
    && chmod +x /usr/local/bin/logdy \
    && mkdir -p /var/log/hosts

COPY syslog-ng.conf /etc/syslog-ng/syslog-ng.conf
COPY trim-old.sh /usr/local/bin/trim-old.sh
COPY monitor.py /usr/local/bin/monitor.py
COPY logdy-columns.json /etc/logdy/config.json
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /usr/local/bin/trim-old.sh /usr/local/bin/monitor.py /entrypoint.sh

ENV RETENTION_HOURS=24
ENV MAX_MESSAGE_COUNT=100000
# Monitoring endpoint off by default; set MONITORING=1 or "true" to enable.
# Runs on MONITOR_PORT (default 8081) - NOT 8080, that's Logdy's own web UI.
ENV MONITORING=0
ENV MONITOR_PORT=8081

EXPOSE 514/udp 514/tcp 8080/tcp 8081/tcp

VOLUME ["/var/log/hosts"]

ENTRYPOINT ["/entrypoint.sh"]
