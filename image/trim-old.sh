#!/bin/bash
# Removes lines older than $RETENTION_HOURS from every /var/log/hosts/*.log
# Runs via cron (see entrypoint.sh), interval/duration configurable via ENV.

RETENTION_HOURS="${RETENTION_HOURS:-24}"
CUTOFF="$(date -u -d "-${RETENTION_HOURS} hours" '+%Y-%m-%dT%H:%M:%S')"

for f in /var/log/hosts/*.log; do
    [ -f "$f" ] || continue
    tmp="${f}.tmp"
    # Keep lines whose ISODATE prefix is >= cutoff (lexical comparison
    # works because ISO8601 is sortable by time)
    awk -v cutoff="$CUTOFF" '{ if (substr($1,1,19) >= cutoff) print }' "$f" > "$tmp" \
        && mv "$tmp" "$f"
done
