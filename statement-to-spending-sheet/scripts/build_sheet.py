#!/usr/bin/env python3
"""Build (or update) a Spending Tracker Google Sheet from categorized data.

Usage:
  python3 build_sheet.py --summary summary.json
                         --categorized categorized_transactions.json
                         [--config config.json] [--title "Spending Tracker"]
                         [--spreadsheet-id ID] [--dry-run]

Without --spreadsheet-id it creates a new spreadsheet. With one it clears
and rewrites the same five tabs in place, so a new month's data updates the
existing tracker instead of making a duplicate. --dry-run prints the rows
that would be written and touches nothing.

config.json (optional):
  {"month_labels": {"Jun": "Jun 14 - Jul 13, 2026"},
   "notes": ["July is an outlier month: ..."],
   "recurring": [{"item": "Internet", "category": "Bills & Utilities",
                  "amount": 50.0, "frequency": "Monthly", "notes": ""}],
   "targets": [{"lever": "Dining cap", "category": "Dining", "cap": 450},
               {"lever": "Amazon skip 1 in 3", "category": "Amazon",
                "skip_fraction": 0.333}]}

Tabs: Dashboard (monthly summary, averages, returns, notes), Transactions
(every purchase with merchant, category, amount, visit flag), Categories
(category by month matrix), Recurring (planned monthly items, TBD allowed),
Targets (each lever with its current average and monthly saving).

Requires the Google Sheets CLI at /opt/hatch/bin/hatch_gws_cli for real
runs. Verify by reading the sheet back after writing it.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

CLI = ["/opt/hatch/bin/hatch_gws_cli", "sheets"]
TABS = ["Dashboard", "Transactions", "Categories", "Recurring", "Targets"]


def run(*args, input_json=None, dry=False):
    if dry:
        return {"dry_run": True}
    cmd = CLI + list(args)
    if input_json is not None:
        cmd += ["--json", json.dumps(input_json)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("FAILED:", " ".join(cmd[:6]), "\n", r.stdout, r.stderr, file=sys.stderr)
        sys.exit(1)
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        print("NON-JSON OUTPUT:", r.stdout, r.stderr, file=sys.stderr)
        sys.exit(1)


def write_range(sid, tab, values, dry):
    run("spreadsheets", "values", "update", "--params",
        json.dumps({"spreadsheetId": sid, "range": f"{tab}!A1",
                    "valueInputOption": "USER_ENTERED"}),
        input_json={"values": values}, dry=dry)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--summary", required=True)
    ap.add_argument("--categorized", required=True)
    ap.add_argument("--config", default=None)
    ap.add_argument("--title", default="Spending Tracker")
    ap.add_argument("--spreadsheet-id", default=None)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    summary = json.load(open(args.summary))
    txns = json.load(open(args.categorized))
    config = json.loads(Path(args.config).read_text()) if args.config else {}
    dry = args.dry_run

    months = summary["months"]
    cats = summary["categories"]
    labels = config.get("month_labels", {})
    label = lambda m: labels.get(m, m)

    payments = {m: 0.0 for m in months}
    for p in summary.get("payments", []):
        payments[p["statement"]] += -p["amount"]

    # ---- Dashboard ----
    dash = [[args.title]]
    dash.append([f"Statements: {', '.join(label(m) for m in months)}. "
                 "Purchases only; payments and returns are listed separately below."])
    dash.append([""])
    dash.append(["Monthly summary (purchases; payments and returns are separate - see below)"])
    hdr = ["Month", "Total"] + cats + ["Payments", "Interest"]
    dash.append(hdr)
    for m in months:
        row = [label(m), summary["monthly_totals"][m]]
        row += [summary["monthly_by_category"][m].get(c, 0) for c in cats]
        row += [round(payments[m], 2), summary["interest"].get(m, 0.0)]
        dash.append(row)
    n = len(months)
    avg = ["Average", round(summary["total"] / n, 2)]
    avg += [round(summary["category_totals"].get(c, 0) / n, 2) for c in cats]
    avg += ["", ""]
    dash.append(avg)
    dash.append(["Total", summary["total"]])
    dash.append([""])
    dash.append(["Returns and credits (not netted against purchases)"])
    dash.append(["Date", "Description", "Amount", "Statement"])
    for ret in summary.get("returns", []):
        dash.append([ret["date"], ret["description"], -ret["amount"], ret["statement"]])
    dash.append([""])
    dash.append(["Notes"])
    for note in config.get("notes", []):
        dash.append([note])

    # ---- Transactions ----
    tx_rows = [["Date", "Merchant", "Category", "Amount", "Statement", "Visit", "Note"]]
    for r in sorted(txns, key=lambda x: x["date"]):
        tx_rows.append([r["date"], r["merchant"], r["category"], r["amount"],
                        r["statement"], r["visit"] if r["visit"] else "", ""])

    # ---- Categories ----
    cat_rows = [["Category"] + months + ["Total", "Average", "Charges"]]
    for c in cats:
        cat_rows.append([c] + [summary["monthly_by_category"][m].get(c, 0) for m in months] +
                        [summary["category_totals"][c],
                         round(summary["category_totals"][c] / n, 2),
                         summary["category_counts"][c]])
    cat_rows.append(["TOTAL"] + [summary["monthly_totals"][m] for m in months] +
                    [summary["total"], round(summary["total"] / n, 2),
                     summary["total_count"]])

    # ---- Recurring ----
    rec = [["Item", "Category", "Amount", "Frequency", "Notes"]]
    for item in config.get("recurring", []):
        rec.append([item.get("item", ""), item.get("category", ""),
                    item.get("amount", "TBD"), item.get("frequency", "Monthly"),
                    item.get("notes", "")])

    # ---- Targets ----
    tgt = [["Lever", "Target", "Current (avg)", "Saves per month", "Notes"]]
    total_saves = 0.0
    for t in config.get("targets", []):
        cat = t.get("category")
        avg_cat = round(summary["category_totals"].get(cat, 0) / n, 2) if cat else 0.0
        saves = 0.0
        if "cap" in t:
            saves = round(avg_cat - t["cap"], 2)
            target = t["cap"]
        elif "skip_fraction" in t:
            saves = round(avg_cat * t["skip_fraction"], 2)
            target = f"skip {t['skip_fraction']:.0%} of orders"
        else:
            target = t.get("target", "-")
        total_saves += saves
        tgt.append([t.get("lever", ""), target, avg_cat, saves, t.get("notes", "")])
    tgt.append(["TOTAL", "", "", round(total_saves, 2), "Sum of the levers above."])

    tabs = {"Dashboard": dash, "Transactions": tx_rows, "Categories": cat_rows,
            "Recurring": rec, "Targets": tgt}

    if dry:
        print(f"DRY RUN: would write {len(tabs)} tabs to '{args.title}'"
              + (f" (spreadsheet {args.spreadsheet_id})" if args.spreadsheet_id
                 else " (new spreadsheet)"))
        for tab, rows in tabs.items():
            print(f"  {tab}: {len(rows)} rows; first row: {rows[0]}")
        return

    if args.spreadsheet_id:
        sid = args.spreadsheet_id
        existing = run("spreadsheets", "get", "--params",
                       json.dumps({"spreadsheetId": sid}))
        have = {s["properties"]["title"] for s in existing.get("sheets", [])}
        missing = [t for t in TABS if t not in have]
        if missing:
            run("spreadsheets", "batchUpdate", "--params",
                json.dumps({"spreadsheetId": sid}),
                input_json={"requests": [
                    {"addSheet": {"properties": {"title": t}}} for t in missing]})
        for tab, rows in tabs.items():
            run("spreadsheets", "values", "clear", "--params",
                json.dumps({"spreadsheetId": sid, "range": f"{tab}!A:Z"}))
            write_range(sid, tab, rows, dry=False)
    else:
        created = run("spreadsheets", "create",
                      input_json={"properties": {"title": args.title}})
        sid = created["spreadsheetId"]
        run("spreadsheets", "batchUpdate", "--params",
            json.dumps({"spreadsheetId": sid}),
            input_json={"requests": [
                {"updateSheetProperties": {"properties": {"sheetId": 0, "title": "Dashboard"},
                                           "fields": "title"}},
                {"addSheet": {"properties": {"title": "Transactions"}}},
                {"addSheet": {"properties": {"title": "Categories"}}},
                {"addSheet": {"properties": {"title": "Recurring"}}},
                {"addSheet": {"properties": {"title": "Targets"}}},
            ]})
        for tab, rows in tabs.items():
            write_range(sid, tab, rows, dry=False)

    chk = run("spreadsheets", "values", "get", "--params",
              json.dumps({"spreadsheetId": sid, "range": "Dashboard!A1:B10"}))
    print("Wrote tabs. Dashboard head:")
    for row in chk.get("values", []):
        print(" ", row)
    print("SHEET URL: https://docs.google.com/spreadsheets/d/" + sid + "/edit")


if __name__ == "__main__":
    main()
