#!/bin/bash
# Master health check executor — with verbose intermediate debug

set -e

cd /c/Users/hello/alforaijboard-gh

# --- Timestamp ---
RUN_AT=$(date -u +'%Y-%m-%dT%H:%M:%SZ')
echo "TIMESTAMP: $RUN_AT"

# --- Docker ---
echo "--- DOCKER ---"
DOCKER_OUT=$(docker ps 2>&1 | head -5)
echo "DOCKER_OUT=$DOCKER_OUT"
if echo "$DOCKER_OUT" | grep -qi "CONTAINER"; then
    DOCKER_RUNNING="true"
    DOCKER_ERROR=""
    echo "DOCKER_RESULT: RUNNING"
else
    DOCKER_RUNNING="false"
    DOCKER_ERROR=$(echo "$DOCKER_OUT" | head -1 | tr -d '\r')
    echo "DOCKER_RESULT: DOWN — $DOCKER_ERROR"
fi
export DOCKER_RUNNING
export DOCKER_ERROR

# --- RAM ---
echo "--- RAM ---"
FREE_KB=$(wmic OS get FreePhysicalMemory /Value 2>/dev/null | grep "FreePhysicalMemory" | cut -d= -f2 | tr -d '\r')
TOTAL_KB=$(wmic OS get TotalVisibleMemorySize /Value 2>/dev/null | grep "TotalVisibleMemorySize" | cut -d= -f2 | tr -d '\r')
echo "FREE_KB=$FREE_KB TOTAL_KB=$TOTAL_KB"
export FREE_MEM_KB="${FREE_KB:-0}"
export TOTAL_MEM_KB="${TOTAL_KB:-0}"

FREE_MB=$((FREE_KB / 1024))
TOTAL_MB=$((TOTAL_KB / 1024))
echo "FREE_MB=$FREE_MB TOTAL_MB=$TOTAL_MB"

if [ "$FREE_MB" -lt 500 ]; then
    RAM_STATUS="CRITICAL"
elif [ "$FREE_MB" -lt 1024 ]; then
    RAM_STATUS="WARNING"
else
    RAM_STATUS="OK"
fi
export RAM_STATUS
echo "RAM_STATUS=$RAM_STATUS"

# --- Disk ---
echo "--- DISK ---"
DISK_LINE=$(df -h /c 2>/dev/null | tail -1)
echo "DISK_LINE=$DISK_LINE"
DISK_TOTAL=$(echo "$DISK_LINE" | awk '{print $2}')
DISK_FREE=$(echo "$DISK_LINE" | awk '{print $4}')
echo "DISK_TOTAL=$DISK_TOTAL DISK_FREE=$DISK_FREE"

parse_gb() {
    local s="$1"
    local num=$(echo "$s" | sed 's/[^0-9.]//g')
    local unit=$(echo "$s" | sed 's/[0-9.]//g' | tr '[:lower:]' '[:upper:]')
    if [ -z "$num" ]; then echo "0"; return; fi
    case "$unit" in
        G) echo "$num" ;;
        M) echo "$num" | awk '{printf "%.2f", $1/1024}' ;;
        *) echo "$num" ;;
    esac
}

DISK_FREE_GB=$(parse_gb "$DISK_FREE")
DISK_TOTAL_GB=$(parse_gb "$DISK_TOTAL")
echo "DISK_FREE_GB=$DISK_FREE_GB DISK_TOTAL_GB=$DISK_TOTAL_GB"
export DISK_FREE_GB
export DISK_TOTAL_GB

FREE_GB_NUM=$(echo "$DISK_FREE_GB" | awk '{print $1+0}')
echo "FREE_GB_NUM=$FREE_GB_NUM"
if [ "$FREE_GB_NUM" -gt 20 ] 2>/dev/null; then
    DISK_STATUS="OK"
elif [ "$FREE_GB_NUM" -gt 10 ] 2>/dev/null; then
    DISK_STATUS="WARNING"
else
    DISK_STATUS="CRITICAL"
fi
export DISK_STATUS
echo "DISK_STATUS=$DISK_STATUS"

# --- Git ---
echo "--- GIT ---"
GIT_OUT=$(git status --short 2>&1)
echo "GIT_OUT=$GIT_OUT"
CHANGED=$(echo "$GIT_OUT" | grep -c "^[MARC]" || true)
UNTRACKED=$(echo "$GIT_OUT" | grep -c "^??" || true)
echo "CHANGED=$CHANGED UNTRACKED=$UNTRACKED"
export GIT_CHANGED="${CHANGED:-0}"
export GIT_UNTRACKED="${UNTRACKED:-0}"
if [ "$CHANGED" -eq 0 ] && [ "$UNTRACKED" -eq 0 ]; then
    GIT_STATUS="OK"
else
    GIT_STATUS="CHANGES"
fi
export GIT_STATUS
echo "GIT_STATUS=$GIT_STATUS"

# --- Agents ---
echo "--- AGENTS ---"
AGENTS_LINES=$(ps aux 2>/dev/null | grep -v grep | grep -iE "hermes|node|python|git" || true)
echo "AGENTS_LINES=$AGENTS_LINES"
AGENTS_COUNT=$(echo "$AGENTS_LINES" | grep -c . || true)
export AGENTS_STATUS="${AGENTS_COUNT} processes"
echo "AGENTS_STATUS=$AGENTS_STATUS"

# --- Final summary ---
echo ""
echo "=== HEALTH CHECK $RUN_AT ==="
echo "Docker:  $([ "$DOCKER_RUNNING" = "true" ] && echo RUNNING || echo DOWN)"
echo "RAM:     ${FREE_MB}MB free / ${TOTAL_MB}MB (${RAM_STATUS})"
echo "Disk C:  ${DISK_FREE_GB}GB free / ${DISK_TOTAL_GB}GB (${DISK_STATUS})"
echo "Git:     ${GIT_CHANGED} changed, ${GIT_UNTRACKED} untracked (${GIT_STATUS})"
echo "Agents:  ${AGENTS_STATUS}"
echo "-----------------------------"

# --- Push ---
python scripts/quick_health_push.py
echo "--- local persist ---"
python scripts/local_health_persist.py
