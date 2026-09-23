#!/usr/bin/env python3
"""Health report summary builder."""
import json, datetime, os

LF = '/c/Users/hello/alforaijboard-gh/_cron_health_latest.json'
with open(LF) as f:
    r = json.load(f)

raw_ts = r.get('timestamp_utc', '?')
host = r.get('host', 'unknown')

lines = []
lines.append("=" * 50)
lines.append(f"⏱ {raw_ts}  |  {host}")
lines.append("=" * 50)

if r.get('docker_running'):
    lines.append("✅ Docker: RUNNING")
else:
    lines.append(f"❌ Docker: {r.get('docker_status','STOPPED')}")

lines.append("")
ram = r.get('ram_free_mb', 0)
ram_total = r.get('ram_total_mb', 0)
lines.append(f"💾 RAM: {ram:.0f} MB free / {ram_total:.0f} MB total — {r.get('ram_status','?')}")
lines.append(f"💽 Disk C:/Users/hello: {r.get('disk_free_pct','?')}% free — {r.get('disk_status','?')}")
lines.append("")
if r.get('git_dirty'):
    lines.append(f"📦 Git (alforaijboard): ⚠️  UNCLEAN — {r.get('git_status','uncommitted changes')}")
else:
    lines.append(f"📦 Git (alforaijboard): ✅ clean")
lines.append("")
agents = r.get('hermes_agents_running', 0)
lines.append(f"🤖 Hermes agents: {r.get('hermes_agents_status','?')} (detected: {agents})")
lines.append("")
lines.append("=" * 50)
lines.append("Local save: _cron_health_latest.json, cron_results_local.json")
lines.append("(Supabase push requires MCP credentials — not executed this run)")

print("\n".join(lines))

out = '/c/Users/hello/health_report_now.txt'
with open(out,'w') as f:
    f.write("\n".join(lines) + "\n")
print(f"\nSaved to {out}")
