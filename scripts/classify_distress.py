#!/usr/bin/env python3
"""Distress Signals Classifier"""
import json, os, sys
from datetime import datetime, timezone
from typing import Dict, List

KEYWORDS = {
    "mild": ["عاجل","سرعة","للبيع فورا","ضاغط","مكثف","quick sale","urgent sale","motivated seller"],
    "moderate": ["أقساط","تعثّر","متأخر","أقساط متأخرة","late payment","arrears","delinquent","collector","دائن","owned","مشكلة مالية"],
    "severe": ["مشاكل مالية","ضائقة","financial difficulty","القاضي","محكمة","دعوى","لجنة","default","enforcement","attorney","lawsuit","summons","legal notice"],
    "auction": ["مزاد","تسييل","auction","sheriff","foreclosure","محل مزاد","بيع بتسييل","تسييل قضائي"]
}

SEVERITY_RULES = [("auction", ["auction"]), ("severe", ["severe","moderate"]), ("moderate", ["moderate"]), ("mild", ["mild"])]

class DistressClassifier:
    def classify(self, listing):
        text = " ".join([listing.get("title",""), listing.get("description",""), listing.get("note",""), listing.get("tags","")]).lower()
        matched = {k: False for k in KEYWORDS}
        matched_kw = []
        for cat, kws in KEYWORDS.items():
            for kw in kws:
                if kw.lower() in text:
                    matched[cat] = True
                    matched_kw.append(kw)
        severity = "clean"
        for sev, rules in SEVERITY_RULES:
            if all(matched.get(r, False) for r in rules):
                severity = sev
                break
        is_distressed = severity != "clean"
        confidence = min(0.5 + len(matched_kw)*0.05 + (4 if is_distressed else 0)*0.1, 0.95)
        return {
            "severity": severity,
            "is_distressed": is_distressed,
            "matched_keywords": matched_kw,
            "matched_categories": [k for k,v in matched.items() if v],
            "confidence": confidence,
            "source": "automated_analysis",
            "notes": f"Detected {len(matched_kw)} keyword matches"
        }
    def batch_classify(self, listings):
        results = []
        for listing in listings:
            result = self.classify(listing)
            result["listing_id"] = listing.get("id") or listing.get("listing_id") or listing.get("data_id")
            result["listing_title"] = listing.get("title","")[:100]
            result["detected_at"] = datetime.now(timezone.utc).isoformat()
            results.append(result)
        return results

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Distress Signals Classifier")
    parser.add_argument("--input","-i", help="Input JSON file")
    parser.add_argument("--output","-o", help="Output directory")
    args = parser.parse_args()
    input_file = args.input or os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "supabase_data", "market_listings.json")
    output_dir = args.output or os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "distress_output")
    os.makedirs(output_dir, exist_ok=True)
    if not os.path.exists(input_file):
        print(f"Input file not found: {input_file}"); sys.exit(1)
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    listings = data if isinstance(data, list) else data.get("data", [])
    if not listings:
        print("No listings found"); sys.exit(1)
    print(f"Analyzing {len(listings)} listings...")
    classifier = DistressClassifier()
    results = classifier.batch_classify(listings)
    severity_counts = {}
    for r in results:
        sev = r["severity"]
        severity_counts[sev] = severity_counts.get(sev, 0) + 1
    distressed = sum(1 for r in results if r["is_distressed"])
    print(f"Results: Total={len(listings)}, Distressed={distressed}")
    print(f"By severity: {severity_counts}")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(output_dir, f"distress_results_{timestamp}.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({"processed_at": datetime.now(timezone.utc).isoformat(), "total_listings": len(listings), "distressed_count": distressed, "by_severity": severity_counts, "results": results}, f, indent=2, ensure_ascii=False)
    print(f"Saved: {output_path}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
