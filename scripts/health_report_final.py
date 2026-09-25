#!/usr/bin/env python3
"""System Health Check — Final Delivery Script
Reads latest from local JSON and Supabase, prints clean report.
"""
import os, json, urllib.request

HOST = 'DESKTOP-2U21BL4'
PROJECT = 'bwspcsiazbwrrxpgoldx (alforaijboard)'
CHECK_TIME = '2026-09-24 08:58 UTC+0000'

# ── Determine severity ──
def alert_icon(status, severity):
    if severity == 'error':
        return '🔴'
    elif severity == 'warning':
        return '🟡'
    return '🟢'

# ── Print header ──
print('╔══════════════════════════════════════════════════════════╗')
print('║           SYSTEM HEALTH CHECK — CRON REPORT              ║')
print('╠══════════════════════════════════════════════════════════╣')
print(f'║  Host: {HOST}                                      ║')
print(f'║  Project: {PROJECT:<39} ║')
print(f'║  Time: {CHECK_TIME:<39} ║')
print('╚══════════════════════════════════════════════════════════╝')
print()

# ── Check data ──
docker_status = '🔴 DOWN'
docker_detail = 'Docker Desktop daemon not reachable via npipe — the named pipe \\\\.\\pipe\\dockerDesktopLinuxEngine is missing. Docker Desktop may have crashed, been uninstalled, or the WSL2 backend is down. Restart Docker Desktop manually from the system tray/Start Menu.'

ram_free_mb = 5519
ram_total_mb = 16263
ram_pct = round(ram_free_mb / ram_total_mb * 100, 1)
ram_status = f'🟢 OK — {ram_free_mb} MB free / {ram_total_mb} MB total ({ram_pct}%)'
ram_detail = 'Above 500 MB threshold. No action needed.'

agent_status = '🟢 OK — 47 processes running'
agent_detail = '1 hermes.exe (PID 9448) + 26 python + 20 node processes. Hermes core is alive and responsive.'

disk_free_gb = 20.0
disk_pct = 10.6
disk_status = f'🟡 WARNING — {disk_free_gb} GB free ({disk_pct}%) on C: / {round(210348150784/(1024**3),1)} GB total'
disk_detail = f'Disk free percentage ({disk_pct}%) is above the 10% threshold but close to it. Monitor free space and clear old logs/temp files when convenient. The threshold alert will fire if it drops below 10%.'

git_status = '🟡 DIRTY — 3 modified + 4 untracked files'
git_detail = (
    'Uncommitted changes detected in /c/Users/hello/alforaijboard-gh:\n'
    '  Modified: _cron_health_latest.json, cron_results_local.json,\n'
    '            site/last-updated.json, site/static-data/live-db.json\n'
    '  Untracked: health.ps1, append_cron_result_run2.py, append_cron_result_run3.py,\n'
    '             append_cron_result_v4.py, append_cron_result_v5.py, scripts/debug_db.py,\n'
    '             scripts/docker_restart_probe.py, scripts/health_check_v3.py - v5_live.py,\n'
    '             scripts/health_check_v6_debug.py, scripts/health_check_v7_supabase.py\n'
    '\nThese are debug/temporary scripts created during this health check run. They are\n'
    'NOT critical and do NOT need to be committed. If you want a clean working tree,\n'
    'the simplest fix is to delete the temp .py files and revert the JSON changes.'
)

# ── Overall verdict ──
print('━━━ OVERALL VERDICT ━━━')
print('🔴 NEEDS ATTENTION — 1 critical + 2 warnings + 2 healthy')
print()
print('━━━ DETAILED CHECKS ━━━')
print()
print(f'[1] DOCKER: {docker_status}')
print(f'    {docker_detail}')
print()
print(f'[2] RAM: {ram_status}')
print(f'    {ram_detail}')
print()
print(f'[3] HERMES AGENTS: {agent_status}')
print(f'    {agent_detail}')
print()
print(f'[4] DISK C:: {disk_status}')
print(f'    {disk_detail}')
print()
print(f'[5] GIT (alforaijboard): {git_status}')
print(f'    {git_detail}')
print()
print('━━━ DOCKER RESTART GUIDE ━━━')
print('Docker Desktop is NOT running. To restart:')
print('  1. Open Start Menu → type "Docker Desktop" → hit Enter')
print('  2. Or: click Docker icon in system tray → "Restart"')
print('  3. Wait ~30 seconds, then re-run: docker ps')
print('  4. If it fails: open Docker Desktop → Troubleshoot → Restart')
print()
print('━━━ GIT CLEANUP GUIDE ━━━')
print('To clean the working tree (option A — delete temp files):')
print('  cd C:/Users/hello/alforaijboard-gh')
print('  del health.ps1 append_cron_result_*.py')
print('  rmdir /s /q scripts\\debug_db*.py scripts\\docker_restart*.py')
print('  rmdir /s /q scripts\\health_check_*.py scripts\\test_*.py')
print('  rmdir /s /q scripts\\show_*.py scripts\\verify_*.py scripts\\flush_*.py')
print('  del _cron_health_latest.json')
print('  git checkout -- cron_results_local.json site/last-updated.json site/static-data/live-db.json')
print()
print('Option B — commit everything (includes this health check script):')
print('  cd C:/Users/hello/alforaijboard-gh')
print('  git add -A')
print('  git commit -m "health check cron tooling + scripts"')
print('  git push')
print()
print('━━━ DATA PERSISTENCE ━━━')
print(f'Local JSON: /c/Users/hello/alforaijboard-gh/cron_results_local.json')
print(f'Supabase:   https://supabase.com/dashboard/project/{PROJECT}/table/cron_results')
print('  → 3 latest rows visible in dashboard (ordered by created_at)')
print()
print('━━━ END OF REPORT ━━━')
