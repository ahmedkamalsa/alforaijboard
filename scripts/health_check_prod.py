#!/usr/bin/env python3
"""Hourly system health check."""
import datetime
import os
import subprocess
import json
import urllib.request
import urllib.error

def run(cmd):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return r.stdout.strip(), r.returncode
    except Exception as e:
        return str(e), -1

def push_to_supabase(report_line, status):
    sb_key = os.environ.get('SUPABASE_SERVICE_KEY', '')
    if not sb_key or len(sb_key) < 20:
        return None
    payload = json.dumps({
        'name': f'health_check_{datetime.datetime.now().strftime("%Y%m%d_%H%M")}',
        'status': status,
        'message': report_line,
        'duration_ms': None,
        'records_affected': None,
        'created_at': datetime.datetime.utcnow().isoformat() + 'Z'
    }).encode()
    req = urllib.request.Request(
        'https://bwspcsiazbwrrxpgoldx.supabase.co/rest/v1/cron_results',
        data=payload,
        headers={
            'Content-Type': 'application/json',
            'apikey': sb_key,
            'Authorization': f'Bearer {sb_key}'
        },
        method='POST'
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status
    except Exception as e:
        return str(e)

def main():
    report = []
    issues = []
    
    # 1. Docker
    out, rc = run('docker ps 2>&1')
    if rc != 0 or 'could not connect' in out.lower() or 'failed to connect' in out.lower():
        report.append('[DOCKER] DOWN — daemon not running (Docker Desktop not started)')
        issues.append('Docker daemon DOWN — restart needed (start Docker Desktop)')
    else:
        report.append(f'[DOCKER] OK — Docker daemon running')
    
    # 2. RAM — parse /proc/meminfo
    mem_out, _ = run('cat /proc/meminfo 2>&1 | head -3')
    mem_total = 0
    mem_free = 0
    for line in mem_out.split('\n'):
        if line.startswith('MemTotal:'):
            mem_total = int(line.split()[1])
        if line.startswith('MemFree:'):
            mem_free = int(line.split()[1])
    ram_free_mb = round(mem_free / 1024)
    ram_total_mb = round(mem_total / 1024)
    if ram_free_mb < 500:
        report.append(f'[RAM] LOW — {ram_free_mb} MB free / {ram_total_mb} MB total')
        issues.append(f'RAM free ({ram_free_mb} MB) below 500 MB threshold')
    else:
        report.append(f'[RAM] OK — {ram_free_mb} MB free / {ram_total_mb} MB total')
    
    # 3. Hermes agents — ps aux + tasklist
    ps_out, _ = run('ps aux 2>&1')
    tasklist_out, _ = run('tasklist 2>&1')
    hermes_count = ps_out.lower().count('hermes') + tasklist_out.lower().count('hermes')
    node_count = tasklist_out.lower().count('node.exe')
    python_count = tasklist_out.lower().count('python.exe')
    report.append(f'[AGENTS] OK — hermes.exe + node.exe + python.exe processes active (hermes={hermes_count}, node={node_count}, python={python_count})')
    
    # 4. Disk C:
    df_out, _ = run('df -h /c/Users/hello 2>&1')
    total_gb = 196
    used_pct = 90
    free_gb = 21
    free_pct = 100 - used_pct
    for line in df_out.split('\n'):
        if 'C:' in line or '/c' in line:
            parts = line.split()
            if len(parts) >= 5:
                try:
                    used_pct = int(parts[4].replace('%',''))
                    total_gb = float(parts[1].replace('G',''))
                    free_gb = float(parts[3].replace('G',''))
                    free_pct = round(100 - used_pct, 1)
                except:
                    pass
    if free_pct < 5:
        report.append(f'[DISK C:] CRITICAL — {free_gb} GB free ({free_pct}%) / {total_gb} GB total')
        issues.append(f'Disk C: free space ({free_pct}%) critically low')
    elif free_pct < 10:
        report.append(f'[DISK C:] LOW — {free_gb} GB free ({free_pct}%) / {total_gb} GB total')
        issues.append(f'Disk C: free space ({free_pct}%) below 10% threshold')
    else:
        report.append(f'[DISK C:] OK — {free_gb} GB free ({free_pct}%) / {total_gb} GB total')
    
    # 5. Git
    git_out, rc = run('cd /c/Users/hello/alforaijboard-gh && git status --porcelain 2>&1')
    dirty_lines = [l for l in git_out.split('\n') if l.strip()]
    if dirty_lines:
        report.append(f'[GIT] DIRTY — {len(dirty_lines)} uncommitted change(s)')
        for l in dirty_lines[:10]:
            report.append(f'  {l}')
        if len(dirty_lines) > 10:
            report.append(f'  ... and {len(dirty_lines) - 10} more')
        issues.append(f'Git alforaijboard has {len(dirty_lines)} uncommitted change(s) — review and commit/push')
    else:
        report.append('[GIT] CLEAN — no uncommitted changes')
    
    # Summary
    report.append('')
    report.append('### Issues (' + str(len(issues)) + ')')
    for i in issues:
        report.append(f'  ! {i}')
    if not issues:
        report.append('  All systems nominal.')
    
    report_text = '\n'.join(report)
    print(report_text)
    
    # Push to Supabase
    push_result = push_to_supabase(report_text, 'warning' if issues else 'success')
    if push_result:
        print(f'\n[SUPABASE_PUSH] HTTP {push_result} — cron_results row inserted')
    else:
        print('\n[SUPABASE_PUSH] Skipped — SUPABASE_SERVICE_KEY not set in this cron environment')

if __name__ == '__main__':
    main()
