#!/bin/bash
set -e

mkdir -p /var/log/hosts
# Placeholder so the *.log glob below doesn't get passed as a literal string
# to logdy on the very first start (no host file exists yet)
touch /var/log/hosts/.placeholder.log

# Set up the cron job for retention (Debian: /etc/cron.d, with user field)
cat > /etc/cron.d/trim-old <<CRON
0 * * * * root RETENTION_HOURS=${RETENTION_HOURS} /usr/local/bin/trim-old.sh >> /var/log/trim.log 2>&1
CRON
chmod 0644 /etc/cron.d/trim-old
cron

# Start syslog-ng in foreground-friendly mode, backgrounded
syslog-ng -F --no-caps &

# Optional monitoring endpoint (JSON on MONITOR_PORT, default 8081)
case "${MONITORING:-0}" in
    1|true|TRUE|True)
        python3 /usr/local/bin/monitor.py &
        ;;
esac

# Short pause so syslog-ng can create the first files before logdy tries
# to open them (cosmetic, not a hard requirement)
sleep 2

# Logdy in the foreground - keeps the container alive.
# Newly appearing host files are only picked up after a restart; with
# 24h retention and occasional restarts (e.g. weekly via Ansible/Watchtower)
# that's acceptable for a homelab.
exec logdy follow --full-read \
    --max-message-count "${MAX_MESSAGE_COUNT:-100000}" \
    --ui-ip 0.0.0.0 --port 8080 \
    --no-updates --no-analytics \
    /var/log/hosts/*.log
