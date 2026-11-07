---
name: statement-to-spending-sheet
description: Turn Bank of America eStatement PDFs into a categorized Spending Tracker Google Sheet, with every total reconciled to the printed statement totals to the cent. Use this whenever the user shares credit card statements and wants the spending parsed, categorized, and built into a tracker sheet, or when a new month of statements arrives and the tracker needs updating.
---

# Statement to Spending Sheet

## Parse the statements

- Ask the user for the statement PDFs, one per statement period, and the last four digits of the card if they know them.

- List the PDFs in a statements file with a short label and the period start and end dates for each one.

- Run `scripts/parse_statements.py` with the statements file and the card digits, and read the reconciliation it prints for every statement.

- Refuse to continue when a parsed purchase total does not equal the printed total to the cent. A mismatch means the layout changed or lines were missed, so find the cause before you use the output.

- Remember that the parser supports Bank of America eStatements only. For another bank, adapt the line pattern and the section headers in the script first and verify the reconciliation before you trust it.

## Categorize with the user's rules

- Ask the user for their category rules as a rules file, or build one from the example in `scripts/rules.example.json` and fill it in with them.

- Put one keyword per rule in order, since the first keyword found in a description wins, and keep the keywords as plain substrings, never as patterns.

- Add merchant display overrides and the home cities to the same file, plus any trailing suffixes the cleaner should strip.

- Run `scripts/categorize.py` with the parsed file, the rules file, and the config file, and read the uncategorized list it prints.

- Add a rule for every uncategorized charge the user can identify, and leave a charge in Other only when nobody knows what it was.

- Take interest from the parsed printed totals, never from a hardcoded figure.

## Build or update the sheet

- Run `scripts/build_sheet.py` with `--dry-run` first and check the tab row counts it prints.

- Run it again without `--dry-run` to create a new tracker sheet, or pass `--spreadsheet-id` to clear and rewrite the same five tabs in an existing tracker.

- Read the sheet back after writing it and check the Dashboard totals against the summary before you call it done.

- Keep the sheet as the single source of truth for the numbers. The dashboard views live in the sheet-dashboard-builder skill, which builds on top of this one.

## Monthly update

- When a new month of statements arrives, add them to the statements file and rerun the parse and categorize steps on the full set.

- Update the existing sheet with `--spreadsheet-id` instead of creating a new one, so the history stays in one place.

- Send the user a short note on what went up, what went down, and where to cut, using the Targets tab for the saving math.
