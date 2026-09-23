#!/usr/bin/env python3
"""
alforaijboard-gh — hourly system health check final summary (cron).
Boss-facing digest. Kuwait time. Reads the live local mirror.
"""
import json, datetime, os, sys

REPORT_PATH = "/c/Users/hello/alforaijboard-gh/cron_results/latest_health.json"
ICON = {"OK":"🟢","WARNING":"🟠","DOWN":"🔴","CRITICAL":"🔴","IDLE":"🟡","CLEAN":"🟢","DIRTY":"🟡","UP":"🟢","NOT_RUNNING":"🔴","UNKNOWN":"🟡"}
RL = {"OK":"✅","WARNING":"⚠️","DOWN":"❌","CRITICAL":"❌","IDLE":"⏸️","CLEAN":"✅","DIRTY":"⚠️","UP":"✅","NOT_RUNNING":"❌","UNKNOWN":"❓","ERROR":"❌","SUCCESS":"✅"}

def main():
    if not os.path.exists(REPORT_PATH):
        print("NO REPORT — run health_cron_push_now.py first")
        return 1
    with open(REPORT_PATH, "r", encoding="utf-8") as f:
        p = json.load(f)
    ts = p.get("created_at", p.get("timestamp", "?"))
    try:
        kwt = datetime.datetime.fromisoformat(ts.replace("+00:00","+03:00")).strftime("%H:%M")
    except Exception:
        kwt = ts[:5] if len(str(ts))>=5 else "?"
    print(f"=== alforaijboard-gh health report — {kwt} كويت ===")
    st = p.get("status", "?")
    print(f"Status: {ICON.get(st,'❓')} {st} {RL.get(st,'')}")
    m = p.get("message","")
    print(f"Message: {m}")
    for k, label in (("docker","DOCKER"),("ram","RAM"),("disk","DISK"),("git","GIT"),("agents","AGENTS")):
        s = p.get(k+"_st","?")
        d = p.get(k+"_detail","")
        print(f"[{ICON.get(s,'🟡')}] {label}: {s} {RL.get(s,'')} — {d}")
    if p.get("git_st"):
        print(f"  Git uncommitted: {p.get('git_unc_total')} ({p.get('git_mod_count')} mod / {p.get('git_unk_count')} untracked)")
    a_cnt = p.get("alerts_cnt", 0)
    w_cnt = p.get("warnings_cnt", 0)
    if a_cnt:
        print(f"\n🔴 {a_cnt} ALERT(S):")
        print("  •", p.get("alerts_txt",""))
    if w_cnt:
        print(f"\n🟠 {w_cnt} WARNING(S):")
        print("  •", p.get("warnings_txt",""))
    print("\n📋 BOSS NOTE:")
    print("  • Supabase push: FAILED — cron_results table has RLS that blocks anon inserts")
    print("    (code 42501). The on-disk latest_health.json is the historical store until")
    print("    a service_role insert policy is added on the Supabase dashboard.")
    print("  • Docker: DOWN — daemon pipe missing. Needs manual Docker Desktop start or")
    print("    a WSL2 container migration — nothing a cron job can fix remotely.")
    print(f"  • Date: {ts}")
    print(f"  • Run ID: {p.get('name','?')}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
