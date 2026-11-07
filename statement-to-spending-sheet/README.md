# Statement to Spending Sheet — Claude Skill

A reusable skill that turns Bank of America eStatement PDFs into a
categorized Spending Tracker Google Sheet — parsed, categorized, and
reconciled to the printed statement totals to the cent. Built for people
who want to see where their money actually goes without tracking anything
by hand: share the statements once a month, get a tracker that stays
current.

## What it does

- Parses BofA eStatement PDFs with `pdftotext` and a line pattern, and
  reconciles every statement: the parsed purchase total must equal the
  printed total to the cent, or it refuses to continue
- Categorizes every purchase from a rules file the user owns, first
  keyword match wins, with merchant display overrides and a home-city
  list for clean merchant names
- Counts same merchant, same city, same day as one dining visit, so
  split charges at one meal do not inflate the visit count
- Lists uncategorized charges at the end so the user can add a rule for
  each one, and keeps payments and returns separate from purchases
- Builds a five-tab Google Sheet (Dashboard, Transactions, Categories,
  Recurring, Targets) or updates the existing tracker in place when a
  new month arrives, with a `--dry-run` mode that touches nothing
- Takes interest from the printed totals, never from a hardcoded figure

## What it doesn't do

- It supports Bank of America eStatements only. Other banks use
  different layouts and need their own line pattern and section headers
  before the parser can be trusted.
- It does not guess categories. Anything unmatched lands in Other and is
  listed for the user to rule on.
- It does not connect to a bank or pull statements itself. The user
  shares the PDFs, and the skill works from those files.

## Installation

1. Download this folder from the repo
2. In Claude, use the skill upload/install flow, or place the folder in
   your skills directory if you're running Claude Code / Claude Desktop
   with custom skills enabled
3. In Muse, share the folder with your Muse and ask it to save it as a
   custom skill
4. The skill will trigger automatically when you share credit card
   statements and ask for a spending tracker, or when a new month of
   statements arrives

## Usage example

> "Here are my last four BofA statements. Build me a spending tracker
> that shows monthly totals by category and flags what I can cut."

The skill will ask for the card's last four digits and your category
rules (or build them with you from the example), parse and reconcile
every statement, categorize the purchases, and build the tracker sheet.
Next month, share the new statement and it updates the same sheet.

## Files

- `SKILL.md` — the workflow
- `skill.yaml` — the skill descriptor
- `scripts/parse_statements.py` — PDF to transactions JSON, with
  reconciliation
- `scripts/categorize.py` — rules-based categorizing and summaries
- `scripts/build_sheet.py` — tracker sheet create or update, with
  `--dry-run`
- `scripts/rules.example.json` — example category rules
- `scripts/config.example.json` — example recurring items and targets
- `scripts/statements.example.json` — example statement manifest

## Contributing

If you adapt the parser for another bank, or add a rule pattern that
helps, PRs welcome.

## License

MIT — use freely, modify for your own workflow.
