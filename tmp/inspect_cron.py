import json

with open("C:/Users/hello/alforaijboard-gh/cron_raw.json") as f:
    r = json.load(f)

print("Keys:", list(r.keys()))
print("Type:", type(r))
print("Content:", r)
