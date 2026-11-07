#!/usr/bin/env python3
"""Categorize parsed statement transactions with a user-owned rules file.

Usage:
  python3 categorize.py --parsed parsed_transactions.json
                        --rules rules.json [--config config.json]
                        [--out-dir .]

rules.json:
  {"rules": [{"keyword": "AMAZON", "category": "Amazon"}, ...],
   "merchant_overrides": [{"match": "AMAZON", "name": "Amazon"}, ...],
   "cities": ["BENTONVILLE", "ROGERS", ...]}

Rules are checked in order; the first keyword found in the description wins.
Keywords are matched case-insensitively as substrings. Anything unmatched
lands in "Other" and is listed at the end so the user can add a rule for it.

config.json (optional):
  {"visit_rule": {"enabled": true, "category": "Dining"}}

The visit rule counts same merchant, same city, same day as ONE visit, so
split charges at one meal do not inflate the visit count. It applies only
to the category named in the config.

Writes categorized_transactions.json and summary.json into --out-dir, then
prints checks: monthly totals, category totals, and any uncategorized rows.
Interest comes from the parsed file's printed totals, never from a hardcoded
figure. The category sums must add up to the parsed purchase total, which
must equal the printed total; a mismatch means the parse step failed.
"""
import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

PHONE_RE = re.compile(r"\s+\d{3}-\d{3}-\d{4}.*$")
PHONE7_RE = re.compile(r"\s+\d{3}-\d{7}.*$")
LONG_NUM_RE = re.compile(r"\s+\d{10,}[-\d]*.*$")
URL_RE = re.compile(r"\s+https?://.*$")
AMZN_RE = re.compile(r"\s+Amzn\.com/billWA.*$")
TRAILING_NUM_RE = re.compile(r"\s+\d{4,}\s*$")
HASH_NUM_RE = re.compile(r"\s+#\d+.*$")
STAR_CODE_RE = re.compile(r"\*[A-Z0-9]{5,}.*$")


def load_rules(path):
    data = json.loads(Path(path).read_text())
    rules = [(r["keyword"].upper(), r["category"]) for r in data.get("rules", [])]
    overrides = [(o["match"].upper(), o["name"])
                 for o in data.get("merchant_overrides", [])]
    cities = [c.upper() for c in data.get("cities", [])]
    suffixes = data.get("strip_suffixes", [])
    return rules, overrides, cities, suffixes


def categorize(desc, rules):
    d = desc.upper()
    for kw, cat in rules:
        if kw in d:
            return cat
    return "Other"


def merchant(desc, overrides, cities, suffixes=None):
    d = re.sub(r"\s+", " ", desc).strip()
    for city in cities:
        d = re.sub(r"\s+" + re.escape(city) + r"\b.*$", "", d, flags=re.IGNORECASE)
    d = PHONE_RE.sub("", d)
    d = PHONE7_RE.sub("", d)
    d = LONG_NUM_RE.sub("", d)
    d = URL_RE.sub("", d)
    d = AMZN_RE.sub("", d)
    d = re.sub(r"\s+WWW\..*$", "", d)
    d = STAR_CODE_RE.sub("", d)
    d = HASH_NUM_RE.sub("", d)
    d = TRAILING_NUM_RE.sub("", d)
    for suffix in (suffixes or []):
        d = re.sub(re.escape(suffix) + r"\s*$", "", d, flags=re.IGNORECASE)
    d = d.replace("SQ *", "").replace("PY *", "").replace("ACT*", "ACT ")
    d = d.replace("TST*", "").replace("TST* ", "")
    u = d.upper()
    for match, name in overrides:
        if match in u:
            return name
    return re.sub(r"\s+", " ", d).strip(" *")


def visit_key(desc, date, cities, suffixes=None):
    m = merchant(desc, [], cities, suffixes)
    base = re.sub(r"\s+#.*$", "", m)
    base = re.sub(r"\s+\d+$", "", base)
    city = ""
    city_re = r"\b(" + "|".join(re.escape(c) for c in cities) + r")\b" if cities else None
    if city_re:
        dm = re.search(city_re, desc.upper())
        if dm:
            city = dm.group(1)
    return (base.upper(), city, date)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--parsed", required=True)
    ap.add_argument("--rules", required=True)
    ap.add_argument("--config", default=None)
    ap.add_argument("--out-dir", default=".")
    args = ap.parse_args()

    rules, overrides, cities, suffixes = load_rules(args.rules)
    config = json.loads(Path(args.config).read_text()) if args.config else {}
    visit_rule = config.get("visit_rule", {})
    visit_category = visit_rule.get("category") if visit_rule.get("enabled") else None

    data = json.load(open(args.parsed))
    txns = [r for r in data["transactions"] if r["section"] == "purchases"]
    credits = [r for r in data["transactions"] if r["section"] != "purchases"]
    printed = data.get("printed_totals", {})

    for r in txns:
        r["category"] = categorize(r["description"], rules)
        r["merchant"] = merchant(r["description"], overrides, cities, suffixes)

    seen = set()
    for r in sorted(txns, key=lambda x: (x["date"], x["description"])):
        if visit_category and r["category"] == visit_category:
            k = visit_key(r["description"], r["date"], cities, suffixes)
            r["visit"] = 0 if k in seen else 1
            seen.add(k)
        else:
            r["visit"] = None

    labels = sorted({r["statement"] for r in txns})
    cats = sorted({r["category"] for r in txns})
    monthly = {m: defaultdict(float) for m in labels}
    monthly_count = {m: defaultdict(int) for m in labels}
    visits = {m: 0 for m in labels}
    for r in txns:
        monthly[r["statement"]][r["category"]] += r["amount"]
        monthly_count[r["statement"]][r["category"]] += 1
        if visit_category and r["category"] == visit_category and r["visit"]:
            visits[r["statement"]] += 1

    interest = {m: printed.get(m, {}).get("interest_charged", 0.0) for m in labels}
    summary = {
        "months": labels,
        "categories": cats,
        "monthly_totals": {m: round(sum(monthly[m].values()), 2) for m in labels},
        "monthly_by_category": {m: {c: round(monthly[m][c], 2) for c in cats}
                                for m in labels},
        "monthly_counts": {m: {c: monthly_count[m][c] for c in cats} for m in labels},
        "dining_visits": visits,
        "dining_charges": {m: monthly_count[m].get(visit_category, 0) for m in labels}
                           if visit_category else {},
        "total": round(sum(r["amount"] for r in txns), 2),
        "total_count": len(txns),
        "category_totals": {c: round(sum(monthly[m][c] for m in labels), 2)
                            for c in cats},
        "category_counts": {c: sum(monthly_count[m][c] for m in labels) for c in cats},
        "interest": interest,
        "returns": [
            {"date": r["date"], "description": r["description"],
             "amount": r["amount"], "statement": r["statement"]}
            for r in credits
            if r["section"] == "credits" and r["amount"] < 0
            and "PAYMENT" not in r["description"]
        ],
        "payments": [
            {"date": r["date"], "description": r["description"],
             "amount": r["amount"], "statement": r["statement"]}
            for r in credits if "PAYMENT" in r["description"]
        ],
    }

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    json.dump(txns, open(out_dir / "categorized_transactions.json", "w"), indent=1)
    json.dump(summary, open(out_dir / "summary.json", "w"), indent=1)

    print("monthly totals:", summary["monthly_totals"])
    print("total:", summary["total"], "count:", summary["total_count"])
    print("category totals:", summary["category_totals"])
    if visit_category:
        print(f"{visit_category} charges:", summary["dining_charges"],
              "visits:", summary["dining_visits"])
    uncategorized = [(r["date"], r["description"], r["amount"])
                     for r in txns if r["category"] == "Other"]
    print(f"Uncategorized (Other): {len(uncategorized)}")
    for row in uncategorized:
        print("  ", row)
    printed_total = round(sum(
        printed.get(m, {}).get("purchases_and_adjustments", 0.0) for m in labels), 2)
    if summary["total"] != printed_total:
        print(f"RECONCILIATION FAILED: categorized total {summary['total']} != "
              f"printed total {printed_total}", file=sys.stderr)
        sys.exit(1)
    print(f"Reconciled to printed totals: {summary['total']} == {printed_total}")


if __name__ == "__main__":
    main()
