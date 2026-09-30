# docker-syslog-logdy-server

Minimal syslog receiver (UDP/TCP 514) with [Logdy](https://logdy.dev) as a
lightweight web UI for browsing/filtering. Writes one log file per sending
host (`${HOST}` macro in syslog-ng), Logdy tags every line with its origin
file — filtering by hostname works directly in the UI, no database required.

## Environment variables

| Variable | Default | Description |
|---|---|---|
| `RETENTION_HOURS` | `24` | Lines older than N hours are trimmed hourly |
| `MAX_MESSAGE_COUNT` | `100000` | Logdy buffer size |
| `MONITORING` | `0` | Set to `1`/`true` to enable the JSON monitoring endpoint |
| `MONITOR_PORT` | `8081` | Port for the monitoring endpoint, if enabled |

## Ports

| Port | Protocol | Purpose |
|---|---|---|
| 514 | UDP/TCP | Syslog input |
| 8080 | TCP | Logdy web UI |
| 8081 | TCP | Monitoring endpoint (only if `MONITORING=1`) |

## Monitoring endpoint

When enabled, `GET /` or `GET /index.json` on `MONITOR_PORT` returns:

```json
{
  "hostname": "hau-syslog01",
  "uptime_seconds": 1234,
  "retention_hours": 24,
  "services": { "syslog-ng": true, "cron": true, "logdy": true },
  "hosts": { "host_count": 3, "total_bytes": 48213, "newest_message_age_seconds": 12 }
}
```

## Known limitations

- Newly seen hosts only appear in the web UI after a container restart
  (Logdy reads the file list once at startup).
- Empty files (host hasn't sent anything in 24h+) are kept, not deleted —
  intentional, so the container doesn't need to restart for every inactive
  host.
