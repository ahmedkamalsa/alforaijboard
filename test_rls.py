#!/usr/bin/env python3
"""Stress-test Supabase RLS on cron_results: push from two connections."""
import os, json, time, urllib.request, urllib.error
PROJECT = "bwspcsiazbwrrxpgoldx"
URL = f"https://{PROJECT}.supabase.co"
HEADERS_TPL = {
    "Content-Type": "application/json",
    "Prefer": "return=minimal",
}

def get_key():
    k = os.environ.get("SUPABASE_ANON_KEY") or ""
    if k:
        return k
    dotenv = "/c/Users/hello/alforaijboard-gh/.env"
    if os.path.exists(dotenv):
        for line in open(dotenv, encoding="utf-8"):
            s = line.strip()
            if s.startswith("SUPABASE_ANON_KEY="):
                return s.split("=",1)[1].strip().strip('"').strip("'")
    return ""

key = get_key()
if not key:
    print("[SKIP] no key"); raise SystemExit(0)

report = {
    "timestamp": "2026-09-22T23:35:00+00:00",
    "status": "TEST",
    "checks": {"docker": {"status": "NOT_RUNNING", "detail": "probe"}, "ram": {"status": "OK", "detail": "probe"}, "agents": {"status": "CRITICAL", "detail": "probe"}, "disk": {"status": "OK", "detail": "probe"}, "git": {"status": "WARNING", "detail": "probe"}},
    "alerts": ["PROBE"],
    "warnings": [],
    "counts": {"docker_containers": 0, "hermes_processes": 0, "node_repls": 0, "python_procs": 0, "git_uncommitted": 0},
    "db_status": "PROBE",
}

def push(tag):
    body = json.dumps({"report": report}).encode("utf-8")
    h = {**HEADERS_TPL, "apikey": key, "Authorization": f"Bearer {key}"}
    req = urllib.request.Request(f"{URL}/rest/v1/cron_results", data=body, headers=h, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, r.read().decode("utf-8", "replace")[:120]
    except urllib.error.HTTPError as e:
        msg = e.read().decode("utf-8","replace")
        return e.code, msg[:200]
    except Exception as e:
        return -1, repr(e)

print("Connection 1:", flush=True)
s1, m1 = push("conn1")
print(f"  -> HTTP {s1}: {m1}", flush=True)
time.sleep(1)

report["timestamp"] = "2026-09-22T23:35:01+00:00"
print("Connection 2 (sequential):", flush=True)
s2, m2 = push("conn2")
print(f"  -> HTTP {s2}: {m2}", flush=True)
print(f"\nResult: conn1={s1}, conn2={s2}", flush=True)
