import json, os, datetime, urllib.request, sys

report_time = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

report = {
    "timestamp": report_time,
    "docker": {"status": "STOPPED", "detail": "Cannot connect to Docker Desktop engine. restart needed."},
    "ram": {"free_mb": 2388, "total_mb": 16263, "status": "OK"},
    "agents": {"hermes_count": 2, "python_count": 18, "node_count": 14, "status": "RUNNING", "total": 34},
    "disk": {"free_gb": 22, "total_gb": 196, "used_percent": 90, "status": "OK", "free_pct": 11.0},
    "git": {"uncommitted_files": 5, "modified_files": 5, "status": "CHANGES_EXIST",
            "changed": ["_cron_health_latest.json", "cron_results_local.json", "site/last-updated.json",
                        "site/static-data/live-db.json", ".gitignore"]},
    "alerts": ["Docker daemon STOPPED"],
    "warnings": ["Git: 5 uncommitted changes"]
}

out_path = "C:/Users/hello/alforaijboard-gh/cron_results_local.json"
os.makedirs(os.path.dirname(out_path), exist_ok=True)
existing = []
if os.path.exists(out_path):
    with open(out_path) as f:
        try:
            existing = json.load(f)
        except Exception:
            existing = []
existing.append(report)
existing = existing[-50:]
with open(out_path, "w") as f:
    json.dump(existing, f, indent=2, default=str)
print("Saved", len(existing), "entries to", out_path)
print("Latest timestamp:", report_time)

# Supabase: try pg8000 with correct parameters and via socket
import pg8000

url = os.environ.get("SUPABASE_URL", "https://bwspcsiazbwrrxpgoldx.supabase.co")
import re
m = re.search(r'https://([^.]+)\.supabase\.co', url)
if m:
    host = m.group(1) + ".supabase.co"
    anon_key = os.environ.get("SUPABASE_ANON_KEY", "")
    
    if anon_key:
        print("Trying pg8000 connection to", host, "...")
        try:
            # pg8000: connection parameters differ from psycopg
            conn = pg8000.dbapi.connect(
                host=host, port=5432, user="postgres",
                password=anon_key, database="postgres",
                ssl=True, timeout=30
            )
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO public.cron_results (created_at, message, status)
                VALUES (%s, %s, %s)
            """, (report_time, "HEALTH CHECK - Docker DOWN, Git dirty (5), Disk 11%%, RAM 2388MB OK, Agents 34", "WARNING"))
            conn.commit()
            print("pg8000 dbapi INSERT SUCCESS!")
            cur.close()
            conn.close()
        except TypeError as e:
            print("pg8000 TypeError:", str(e)[:200])
            # Try different API
            try:
                conn = pg8000.connect(
                    host=host, port=5432, user="postgres",
                    password=anon_key, database="postgres",
                    ssl=True, timeout=30
                )
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO public.cron_results (created_at, message, status)
                    VALUES (%s, %s, %s)
                """, (report_time, "HEALTH CHECK - Docker DOWN, Git dirty (5), Disk 11%%, RAM 2388MB OK, Agents 34", "WARNING"))
                conn.commit()
                print("pg8000 connect() INSERT SUCCESS!")
                cur.close()
                conn.close()
            except Exception as e2:
                print("pg8000 connect() ERROR:", type(e2).__name__, str(e2)[:300])
        except Exception as e:
            print("pg8000 ERROR:", type(e).__name__, str(e)[:300])
    else:
        print("No ANON key")
else:
    print("Cannot parse URL")
