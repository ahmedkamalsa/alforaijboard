import json, urllib.request, urllib.parse, base64

# First check what columns exist by doing a GET
url = "https://bwspcsiazbwrrxpgoldx.supabase.co/rest/v1/cron_results?select=*&limit=1"
headers = {
    "apikey": "sb_publishable_c84oHQS94osRqw_SiTIqMg_8icxvatZ",
    "Authorization": "Bearer sb_publishable_c84oHQS94osRqw_SiTIqMg_8icxvatZ",
    "Content-Type": "application/json",
}

req = urllib.request.Request(url, headers=headers, method="GET")
try:
    resp = urllib.request.urlopen(req, timeout=10)
    body = resp.read().decode("utf-8")
    print("GET response:", resp.status)
    print(body[:2000])
except Exception as e:
    print("GET error:", str(e))
