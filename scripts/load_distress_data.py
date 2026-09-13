#!/usr/bin/env python3
"""Load distress data for dashboard"""
import json, os, sys, urllib.request, ssl
from datetime import datetime, timezone

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
SITE_DIR = os.path.join(PROJECT_ROOT, "site", "static-data")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "distress_output")
SUPABASE_URL = "https://bwspcsiazbwrrxpgoldx.supabase.co"
ANON_KEY = os.environ.get("SUPABASE_ANON_KEY", "")

class Loader:
    def __init__(self):
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        self.ctx = ctx
    def load_from_supabase(self):
        BASE = SUPABASE_URL + "/rest/v1"
        try:
            req = urllib.request.Request(BASE + "/v_distress_summary")
            req.add_header("apikey", ANON_KEY)
            req.add_header("Authorization", "Bearer " + ANON_KEY)
            with urllib.request.urlopen(req, context=self.ctx, timeout=20) as resp:
                return json.loads(resp.read())
        except: return []
    def load_local(self, path=None):
        if not path:
            files = sorted([f for f in os.listdir(OUTPUT_DIR) if f.startswith("distress_results_") and f.endswith(".json")], reverse=True)
            if files: path = os.path.join(OUTPUT_DIR, files[0])
        if path and os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f: return json.load(f)
        return None
    def save_js(self, data, path=None):
        if not path: path = os.path.join(SITE_DIR, "distress_data.js")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        js = "// Auto-generated distress data
// Generated: " + datetime.now(timezone.utc).isoformat() + "

const DISTRESS_DATA = " + json.dumps(data, ensure_ascii=False, indent=2) + ";

export default DISTRESS_DATA;
"
        with open(path, "w", encoding="utf-8") as f: f.write(js)
        return path

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", choices=["supabase","local","fallback"], default="local")
    parser.add_argument("--input","-i")
    parser.add_argument("--output","-o")
    args = parser.parse_args()
    loader = Loader()
    if args.source == "supabase":
        data = {"source":"supabase","data":loader.load_from_supabase(),"loaded_at":datetime.now(timezone.utc).isoformat()}
    elif args.source == "local":
        data = {"source":"local","data":loader.load_local(args.input),"loaded_at":datetime.now(timezone.utc).isoformat()}
    else:
        data = {"source":"fallback","data":{"results":[],"by_severity":{}},"loaded_at":datetime.now(timezone.utc).isoformat()}
    if data["data"]:
        path = loader.save_js(data, args.output)
        print("Saved: " + path)
    else:
        print("No data to save")
        sys.exit(1)

if __name__ == "__main__":
    main()
