import json

with open("C:/Users/hello/AppData/Local/Temp/report_final.json") as f:
    r = json.load(f)

# Now push to Supabase
import urllib.request, urllib.parse, base64

url = "https://bwspcsiazbwrrxpgoldx.supabase.co/rest/v1/cron_results"
headers = {
    "apikey": "sb_publishable_c84oHQS94osRqw_SiTIqMg_8icxvatZ",
    "Authorization": "Bearer sb_publishable_c84oHQS94osRqw_SiTIqMg_8icxvatZ",
    "Content-Type": "application/json",
    "Prefer": "return=minimal",
}

data = json.dumps(r).encode("utf-8")
req = urllib.request.Request(url, data=data, headers=headers, method="POST")
try:
    resp = urllib.request.urlopen(req, timeout=10)
    body = resp.read().decode("utf-8")
    print("Supabase response:", resp.status, body[:500])
except Exception as e:
    print("Supabase error:", str(e))
