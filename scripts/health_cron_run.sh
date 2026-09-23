#!/bin/bash
# System health check - runs via cron every hour
set -e
WORKDIR="/c/Users/hello/alforaijboard-gh"
REPORT_FILE="$WORKDIR/_cron_health_latest.json"

echo "=== Health check running at $(date) ==="

# 1) Docker
DOCKER_STATUS="OK"
DOCKER_MSG="Docker daemon running"
if ! docker ps > /dev/null 2>&1; then
  DOCKER_STATUS="DOWN"
  DOCKER_MSG="Docker daemon DOWN"
fi

# 2) RAM (free > 500MB good)
RAM_FREE_KB=$(awk '/MemFree/ {print $2}' /proc/meminfo)
RAM_FREE_MB=$((RAM_FREE_KB / 1024))
RAM_TOTAL_MB=$(( $(awk '/MemTotal/ {print $2}' /proc/meminfo) / 1024 ))
RAM_PCT=$(echo "scale=1; $RAM_FREE_KB / $(awk '/MemTotal/ {print $2}' /proc/meminfo) * 100" | bc -l 2>/dev/null || echo "0")
if [ "$RAM_FREE_MB" -lt 500 ]; then
  RAM_STATUS="LOW"
  RAM_MSG="RAM low: ${RAM_FREE_MB}MB free"
else
  RAM_STATUS="OK"
  RAM_MSG="RAM OK: ${RAM_FREE_MB}MB free (${RAM_PCT}%) / ${RAM_TOTAL_MB}MB total"
fi

# 3) Agents
AGENT_COUNT=$(ps aux 2>/dev/null | grep -Ei '(hermes|node|python|chrome|agent)' | grep -v grep | wc -l || echo "0")
AGENT_PROCS=$(ps aux 2>/dev/null | grep -Ei '(hermes|node|python|chrome|agent)' | grep -v grep | awk '{printf "PID=%s %s RAM=%sMB\n", $2, $11, int($6/1024)}' | head -20 || echo "none")

# 4) Disk
DISK_INFO=$(df -h /c/Users/hello 2>/dev/null || df -h .)
DISK_AVAIL=$(echo "$DISK_INFO" | awk 'NR==2 {print $4}')
DISK_USE_PCT=$(echo "$DISK_INFO" | awk 'NR==2 {gsub(/%/,""); print $5}')
DISK_TOTAL=$(echo "$DISK_INFO" | awk 'NR==2 {print $2}')

if [ "$DISK_USE_PCT" -lt 90 ]; then
  DISK_STATUS="OK"
  DISK_MSG="Disk OK: ${DISK_AVAIL} free (~${DISK_USE_PCT}% used)"
else
  DISK_STATUS="WARNING"
  DISK_MSG="Disk WARNING: ${DISK_AVAIL} free (${DISK_USE_PCT}% used) - less than 10% free"
fi

# 5) Git status
cd "$WORKDIR"
GIT_DIRTY=$(git status --short 2>/dev/null | wc -l || echo "0")
GIT_CHANGES=$(git status --short 2>/dev/null | head -30 || echo "clean")
GIT_STATUS_TEXT="clean"
GIT_MSG="Git repo clean"
if [ "$GIT_DIRTY" -gt 0 ]; then
  GIT_STATUS_TEXT="DIRTY"
  GIT_MSG="Git repo has $GIT_DIRTY uncommitted change(s)"
fi

# Build report JSON
REPORT=$(cat <<EOF
{
  "timestamp": "$(date +%Y%m%d_%H%M)",
  "checks": {
    "docker": {"status": "$DOCKER_STATUS", "msg": "$DOCKER_MSG"},
    "ram": {"status": "$RAM_STATUS", "msg": "$RAM_MSG", "free_mb": $RAM_FREE_MB},
    "agents": {"status": "OK", "count": $AGENT_COUNT, "procs": "$(echo "$AGENT_PROCS" | tr '\n' ' ')"},
    "disk": {"status": "$DISK_STATUS", "msg": "$DISK_MSG", "free": "$DISK_AVAIL", "use_pct": $DISK_USE_PCT},
    "git": {"status": "$GIT_STATUS_TEXT", "msg": "$GIT_MSG", "dirty_count": $GIT_DIRTY}
  },
  "summary": "$DOCKER_STATUS|$RAM_STATUS|$DISK_STATUS|$GIT_STATUS_TEXT"
}
EOF
)

echo "$REPORT" > "$REPORT_FILE"
echo "$REPORT"
