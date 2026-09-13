#!/usr/bin/env python3
"""Batch Processor for Distress Classification"""
import json, os, sys
from datetime import datetime, timezone
from classify_distress import DistressClassifier

class BatchProcessor:
    def __init__(self, batch_size=100):
        self.classifier = DistressClassifier()
        self.batch_size = batch_size
        self.results = []
    def process_file(self, input_path, output_dir):
        with open(input_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        listings = data if isinstance(data, list) else data.get("data", [])
        if not listings: return {"error": "No listings"}
        return self.process_listings(listings, output_dir, data)
    def process_listings(self, listings, output_dir, metadata=None):
        total = len(listings)
        os.makedirs(output_dir, exist_ok=True)
        for i in range(0, total, self.batch_size):
            batch = listings[i:i+self.batch_size]
            batch_num = i // self.batch_size + 1
            print(f"Batch {batch_num}: {len(batch)} listings")
            self.results.extend(self.classifier.batch_classify(batch))
        return self.generate_report(output_dir, metadata)
    def generate_report(self, output_dir, metadata=None):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        severity_counts = {}
        for r in self.results:
            sev = r.get("severity", "unknown")
            severity_counts[sev] = severity_counts.get(sev, 0) + 1
        os.makedirs(os.path.join(output_dir, "reports"), exist_ok=True)
        json_path = os.path.join(output_dir, f"distress_results_{timestamp}.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump({"processed_at": datetime.now(timezone.utc).isoformat(), "total": len(self.results), "by_severity": severity_counts, "results": self.results, "metadata": metadata or {}}, f, indent=2, ensure_ascii=False)
        html = self.generate_html(severity_counts, timestamp)
        html_path = os.path.join(output_dir, f"distress_report_{timestamp}.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html)
        return {"json_file": json_path, "html_file": html_path, "timestamp": timestamp, "severity_counts": severity_counts}
    def generate_html(self, severity_counts, timestamp):
        total = max(1, len(self.results))
        distressed = sum(1 for r in self.results if r.get("is_distressed"))
        clean = total - distressed
        rows = ""
        colors = {"auction":"#8b5cf6","severe":"#ef4444","moderate":"#f97316","mild":"#f59e0b","clean":"#10b981"}
        for sev in ["auction","severe","moderate","mild","clean"]:
            cnt = severity_counts.get(sev, 0)
            pct = (cnt / total) * 100
            rows += "<tr><td style=color:white;background:" + colors[sev] + ";padding:8px;border-radius:4px>" + sev.upper() + "</td><td style=padding:8px>" + str(cnt) + "</td><td style=padding:8px>" + str(round(pct, 1)) + "%</td></tr>"
        return "<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8"><title>Distress Report " + timestamp + "</title>
<style>
body{font-family:system-ui;margin:0;padding:20px;background:#f9fafb}.container{max-width:800px;margin:0 auto;background:white;padding:24px;border-radius:8px}.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin:20px 0}.stat{padding:16px;border-radius:8px;text-align:center;color:white}table{width:100%;border-collapse:collapse}th,td{padding:12px;text-align:right}th{background:#f3f4f6}
</style></head>
<body><div class="container">
<h1>Distress Report - " + timestamp + "</h1>
<p>" + datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S") + " UTC</p>
<div class="stats">
<div class="stat" style="background:#10b981"><h3>" + str(len(self.results)) + "</h3><p>Total</p></div>
<div class="stat" style="background:#ef4444"><h3>" + str(distressed) + "</h3><p>Distressed</p></div>
<div class="stat" style="background:#10b981"><h3>" + str(clean) + "</h3><p>Clean</p></div>
</div>
<h2>By Severity</h2>
<table><thead><tr><th>Category</th><th>Count</th><th>%</th></tr></thead><tbody>" + rows + "</tbody></table>
</div></body></html>"

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Batch Distress Processor")
    parser.add_argument("--input","-i", required=True)
    parser.add_argument("--output-dir","-o", default="distress_output")
    parser.add_argument("--batch-size","-b", type=int, default=100)
    args = parser.parse_args()
    processor = BatchProcessor(batch_size=args.batch_size)
    result = processor.process_file(args.input, args.output_dir)
    print(f"Done: {result["total"]} listings, {result["severity_counts"]}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
