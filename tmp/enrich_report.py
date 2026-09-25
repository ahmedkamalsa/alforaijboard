import json, urllib.request, urllib.parse

# Read the final report
with open("C:/Users/hello/AppData/Local/Temp/report_final.json") as f:
    r = json.load(f)

# Save enriched version
r["supabase_project"] = "bwspcsiazbwrrxpgoldx"
r["supabase_push_status"] = "failed_401_unauthorized"
r["push_attempted_at"] = r["timestamp"]

with open("C:/Users/hello/AppData/Local/Temp/report_enriched.json", "w") as f:
    json.dump(r, f, indent=2, ensure_ascii=False)

print("Enriched report saved.")
print(json.dumps(r, indent=2, ensure_ascii=False))
