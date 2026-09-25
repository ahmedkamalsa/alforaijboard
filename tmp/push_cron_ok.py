import json, urllib.request, urllib.parse, base64, re

url = "https://bwspcsiazbwrrxpgoldx.supabase.co/rest/v1/cron_results"
headers = {
    "apikey": "sb_publishable_c84oHQS94osRqw_SiTIqMg_8icxvatZ",
    "Authorization": "Bearer sb_publishable_c84oHQS94osRqw_SiTIqMg_8icxvatZ",
    "Content-Type": "application/json",
    "Prefer": "return=minimal",
}

with open("C:/Users/hello/AppData/Local/Temp/report_final.json") as f:
    r = json.load(f)

# Map to Supabase schema
status = "success" if r["overall"] == "OK" else "failure"
message_lines = []
for name, check in r["checks"].items():
    s = check["status"]
    d = check["detail"]
    message_lines.append("{}: {} — {}".format(name.upper(), s, d))

payload = {
    "name": "health_check_{}".format(re.sub(r"[^\w]", "_", r["timestamp"].replace(" ", "_").replace(":", ""))),
    "status": status,
    "message": "\n".join(message_lines),
    "records_affected": 5,
}

data = json.dumps(payload).encode("utf-8")
req = urllib.request.Request(url, data=data, headers=headers, method="POST")
try:
    resp = urllib.request.urlopen(req, timeout=10)
    body = resp.read().decode("utf-8")
    print("Supabase INSERT:", resp.status, body[:500])
except Exception as e:
    print("Supabase INSERT error:", str(e))
    print("Payload:", json.dumps(payload, indent=2))
