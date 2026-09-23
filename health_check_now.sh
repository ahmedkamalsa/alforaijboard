#!/bin/sh
# Hourly health check — collect results into JSON

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Docker
DOCKER_STATUS="UNKNOWN"
if docker ps > /dev/null 2>&1; then
    DOCKER_STATUS="OK"
else
    DOCKER_STATUS="STOPPED"
fi

# RAM: extract from /proc/meminfo
RAM_TOTAL=$(grep MemTotal /proc/meminfo | awk '{print $2}')
RAM_FREE=$(grep MemFree /proc/meminfo | awk '{print $2}')
RAM_FREE_MB=$((RAM_FREE / 1024))
RAM_TOTAL_MB=$((RAM_TOTAL / 1024))
RAM_OK="yes"
if [ "$RAM_FREE_MB" -lt 500 ]; then
    RAM_OK="NO"
fi

# Disk
DISK_FREE=$(df -BG /c/Users/hello 2>/dev/null | tail -1 | awk '{print $4}' | tr -d 'G')
DISK_TOTAL=$(df -BG /c/Users/hello 2>/dev/null | tail -1 | awk '{print $2}' | tr -d 'G')
DISK_USED_PCT=$(df -BG /c/Users/hello 2>/dev/null | tail -1 | awk '{print $5}' | tr -d '%')
DISK_WARN="no"
if [ "$DISK_USED_PCT" -ge 90 ]; then
    DISK_WARN="yes"
fi

# Git status
cd /c/Users/hello/alforaijboard-gh
GIT_CHANGED=$(git status --short 2>/dev/null | grep -c "^M")
GIT_UNTRACKED=$(git status --short 2>/dev/null | grep -c "^\?\?")
GIT_ISSUE="none"
if [ "$GIT_CHANGED" -gt 0 ] || [ "$GIT_UNTRACKED" -gt 0 ]; then
    GIT_ISSUE="unclean"
fi

# Build JSON report
cat > _cron_health_latest.json << EOF
{
  "timestamp": "$TIMESTAMP",
  "checks": {
    "docker": "$DOCKER_STATUS",
    "ram_total_mb": $RAM_TOTAL_MB,
    "ram_free_mb": $RAM_FREE_MB,
    "ram_ok": "$RAM_OK",
    "disk_total_gb": $DISK_TOTAL,
    "disk_free_gb": $DISK_FREE,
    "disk_used_pct": $DISK_USED_PCT,
    "disk_warn": "$DISK_WARN",
    "hermes_agents": "None detected (cron job runs inside Hermes environment)",
    "git_uncommitted": $GIT_ISSUE,
    "git_modified_count": $GIT_CHANGED,
    "git_untracked_count": $GIT_UNTRACKED
  }
}
EOF

echo "Health report written to _cron_health_latest.json"
cat _cron_health_latest.json
