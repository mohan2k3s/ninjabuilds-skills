---
name: sheet-dashboard-builder
description: Build a live spending dashboard from any Google Sheet the user provides, as a Dashboard tab with formulas and charts and optionally a live app that reads the sheet on every open. Use this whenever the user wants a dashboard for their spending, wants to track a category separately such as car service versus fuel or unplanned household costs, or wants a sheet dashboard they can share with someone else.
---

# Sheet Dashboard Builder

## Collect the sheet

- Ask the user for the spreadsheet link or ID and read its live structure with the Google Sheets CLI before you plan anything.

- Confirm which tab holds the transactions and which columns hold the date, merchant, category and amount.

- Confirm the currency and the date range the sheet covers.

- Never invent a sheet, a tab, a column or a row. If the structure is unclear, ask the user to point at the right tab.

## Agree the views

- Ask the user which views they want, such as monthly totals, whole period totals with averages, a category breakdown, and any split views.

- Define every split view as a rule on merchant or category text, and write the rule down in the dashboard so the user can correct it.

- Agree any targets the user wants tracked, such as a monthly cap or a skip rate, and compute the saving from the actual average, never from a guessed number.

- Confirm whether the user also wants a live app dashboard they can open anywhere, or only the sheet dashboard.

## Build the sheet dashboard

- Add or rebuild a Dashboard tab with formulas that point at the transaction and category tabs, never pasted values, so the dashboard updates when new rows arrive.

- Use SUMIFS for category and merchant totals, FILTER for live transaction lists, and INDEX with MATCH for biggest month and similar lookups.

- Leave blank spill rows under every FILTER so a growing list does not overwrite the next section.

- Add a column chart for spending by month and a pie chart for the category split, both sourced from the live ranges.

- Format money cells as currency and bold the section headers.

- Read the dashboard back after writing it and check every computed value against the source tabs before you call it done.

## Build the live app dashboard

- When the user wants a dashboard they can open on any device, build a fullstack web artifact that reads the sheet live on every open through the Google Sheets connector.

- Declare only the read method the app needs and name the spreadsheet in the build brief so the builder reads the right sheet.

- Tell the user plainly that the app lives in their Muse and cannot be shared into another person's Muse.

- Never publish the sheet to the web to feed a page. That makes the spending data public to anyone with the link.

- Keep the sheet as the single source of truth and let the app read from it, so one update feeds both views.

## Share the skill

- The skill is a folder with SKILL.md and skill.yaml and it carries no data, no sheet IDs and no names.

- Share the folder or its files with anyone, and their Muse saves it under their own custom skills and follows the same steps with their own sheet.

- Do not promise a one tap store download. No public skill store is verified, so file sharing is the route that works today.
