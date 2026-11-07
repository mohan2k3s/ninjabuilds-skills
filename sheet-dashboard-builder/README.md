# Sheet Dashboard Builder — Claude Skill

A reusable skill that turns any Google Sheet of transactions into a live
spending dashboard: a Dashboard tab with formulas and charts, plus an
optional live app that reads the sheet on every open. Built for people who
track household spending in a spreadsheet and want an at-a-glance view they
can share with family, without rebuilding anything by hand each month.

## What it does

- Reads the live structure of a Google Sheet the user provides and confirms
  which tab and columns hold the transactions
- Agrees the views with the user: monthly totals, whole-period totals with
  averages, category breakdown, and split views such as car service versus
  fuel or unplanned household costs
- Defines every split view as a written rule on merchant or category text,
  so the user can correct what counts
- Builds a Dashboard tab from formulas (SUMIFS, FILTER, INDEX with MATCH),
  never pasted values, so it updates when new rows arrive
- Adds a column chart for spending by month and a pie chart for the
  category split, both sourced from the live ranges
- Tracks targets the user names, such as a monthly dining cap or skipping
  one in three orders, with the saving worked out from the real average
- Optionally builds a live app dashboard that reads the sheet on every open,
  so the numbers are current on any device

## What it doesn't do

- It does not invent or assume a sheet layout. It reads the live sheet
  first and asks when the structure is unclear.
- It does not publish the sheet to the web to feed a page. That would make
  the spending data public to anyone with the link.
- The live app dashboard lives in the user's own Muse and cannot be shared
  into another person's Muse. The shared view is the sheet itself.

## Installation

1. Download `SKILL.md` from this repo (or the whole folder if you want the
   structure)
2. In Claude, use the skill upload/install flow, or place the file in your
   skills directory if you're running Claude Code / Claude Desktop with
   custom skills enabled
3. In Muse, share the folder with your Muse and ask it to save it as a
   custom skill
4. The skill will trigger automatically when you ask your assistant to
   build a dashboard from a spreadsheet, or to track a spending category
   separately

## Usage example

> "Here's my spending sheet. Build me a dashboard that shows monthly and
> yearly totals, tracks car service separately from fuel, and tracks
> unplanned household expenses separately."

The skill will read the sheet, agree the split rules with you, build the
Dashboard tab with live formulas and charts, and offer the live app
dashboard if you want to open it anywhere.

## Contributing

If you hit an edge case this skill doesn't handle well (a different sheet
layout, a new split view, a target type), PRs welcome.

## License

MIT — use freely, modify for your own workflow.
