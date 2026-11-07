#!/usr/bin/env python3
"""Parse Bank of America eStatements (PDF) into a transactions JSON.

Supported format: Bank of America eStatement PDFs, the kind downloaded from
online banking ("eStmt_YYYY-MM-DD__N.pdf"). Each statement has a Purchases
and Adjustments section, a Payments and Other Credits section, and printed
period totals. Other banks use different layouts and need their own parser;
see the skill for how to adapt the line pattern and section headers.

Usage:
  python3 parse_statements.py --statements statements.json [--card-last4 3794]
                              [--out parsed_transactions.json]

statements.json is a list of objects:
  [{"file": "eStmt_2026-07-13__1.pdf", "label": "Jun",
    "period_start": "2026-06-14", "period_end": "2026-07-13"}, ...]

The label is any short name for the statement period (Jun, Jul, 2026-01).
The card's last four digits anchor the transaction lines; give --card-last4
when you know it, or leave it off and the parser detects it from the lines
and refuses to continue if the lines disagree.

Writes the output JSON and reconciles every statement: the parsed purchase
total must equal the statement's printed "TOTAL PURCHASES AND ADJUSTMENTS
FOR THIS PERIOD" to the cent. A mismatch exits non-zero. Never silently
accept a mismatch; a wrong total means the layout changed or lines were
missed.
"""
import argparse
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

SECTION_HEADERS = {
    "Payments and Other Credits": "credits",
    "Purchases and Adjustments": "purchases",
    "Fees Charged": "fees",
    "Interest Charged": "interest",
}
TOTAL_RE = re.compile(
    r"TOTAL (PAYMENTS AND OTHER CREDITS|PURCHASES AND ADJUSTMENTS|FEES CHARGED|INTEREST CHARGED) FOR THIS PERIOD\s+(-?\$?[\d,]+\.\d{2})"
)


def line_re(card_last4):
    anchor = card_last4 if card_last4 else r"\d{4}"
    return re.compile(
        r"^(\d{2}/\d{2})\s+(\d{2}/\d{2})\s+(.+?)\s+(\d{4})\s+"
        + anchor
        + r"\s+(-?[\d,]+\.\d{2})\s*$"
    )


def parse_pdf(path, pattern):
    text = subprocess.run(
        ["pdftotext", "-layout", str(path), "-"], capture_output=True, text=True
    ).stdout
    rows = []
    section = None
    printed = {}
    detected_last4 = set()
    for line in text.splitlines():
        for header, name in SECTION_HEADERS.items():
            if header in line:
                section = name
                break
        else:
            m = TOTAL_RE.search(line)
            if m:
                printed[m.group(1).lower().replace(" ", "_")] = float(
                    m.group(2).replace("$", "").replace(",", "")
                )
                continue
            m = pattern.match(line)
            if m and section:
                if pattern.groups == 6:
                    txn_date, post_date, desc, ref, last4, amount = m.groups()
                    detected_last4.add(last4)
                else:
                    txn_date, post_date, desc, ref, amount = m.groups()
                rows.append(
                    {
                        "txn_date": txn_date,
                        "post_date": post_date,
                        "description": re.sub(r"\s+", " ", desc).strip(),
                        "ref": ref,
                        "amount": float(amount.replace(",", "")),
                        "section": section,
                    }
                )
                continue
        # header lines fall through here after the break
    return rows, printed, detected_last4


def iso_date(mmdd, period_start, period_end):
    m, d = int(mmdd[:2]), int(mmdd[3:5])
    ps = date.fromisoformat(period_start)
    pe = date.fromisoformat(period_end)
    for y in (ps.year, pe.year):
        try:
            cand = date(y, m, d)
        except ValueError:
            continue
        if ps <= cand <= pe:
            return cand.isoformat()
    return date(ps.year, m, d).isoformat()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--statements", required=True,
                    help="JSON list of {file, label, period_start, period_end}")
    ap.add_argument("--card-last4", default=None,
                    help="last four digits of the card (optional; auto-detected)")
    ap.add_argument("--out", default="parsed_transactions.json")
    args = ap.parse_args()

    manifest = json.loads(Path(args.statements).read_text())
    pattern = line_re(args.card_last4)
    all_rows = []
    printed_totals = {}
    detected = set()
    for entry in manifest:
        rows, printed, found = parse_pdf(Path(entry["file"]), pattern)
        detected |= found
        for r in rows:
            r["statement"] = entry["label"]
            r["period_start"] = entry["period_start"]
            r["period_end"] = entry["period_end"]
            r["date"] = iso_date(r["txn_date"], entry["period_start"], entry["period_end"])
        all_rows.extend(rows)
        printed_totals[entry["label"]] = printed

    if not args.card_last4:
        if len(detected) != 1:
            print(f"ERROR: could not settle on one card: detected {sorted(detected)}",
                  file=sys.stderr)
            sys.exit(1)
        print(f"Detected card ending {detected.pop()}")

    out = {"transactions": all_rows, "printed_totals": printed_totals}
    Path(args.out).write_text(json.dumps(out, indent=1))

    failed = False
    for entry in manifest:
        label = entry["label"]
        purch = [r for r in all_rows
                 if r["statement"] == label and r["section"] == "purchases"]
        parsed_sum = round(sum(r["amount"] for r in purch), 2)
        printed_sum = printed_totals[label].get("purchases_and_adjustments")
        status = "OK" if printed_sum is not None and parsed_sum == printed_sum else "MISMATCH"
        if status == "MISMATCH":
            failed = True
        print(f"{label}: purchases {len(purch)} sum {parsed_sum} "
              f"printed {printed_sum} [{status}]")
        creds = [r for r in all_rows
                 if r["statement"] == label and r["section"] != "purchases"]
        print(f"  other rows {len(creds)} sum "
              f"{round(sum(r['amount'] for r in creds), 2)} "
              f"printed {printed_totals[label].get('payments_and_other_credits')}")
    total = round(sum(r["amount"] for r in all_rows if r["section"] == "purchases"), 2)
    print(f"TOTAL purchases: {total} count: "
          f"{sum(1 for r in all_rows if r['section'] == 'purchases')}")
    if failed:
        print("RECONCILIATION FAILED: parsed totals do not match the printed "
              "totals. Do not use this output.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
