# Theme & Sub-Theme Ticker Universe

`Input_Ticker_List_by_Theme.csv` — Every ticker is assigned to one or more of a
structured set of themes and sub-themes, which the rotation model then weights by
sub-theme market capitalization.

## At a glance

| Metric | Count |
|---|---|
| Unique tickers | **1,394** |
| Themes | **34** |
| Sub-themes | **175** |
| Total assignments (rows) | 1,935 |
| — Primary assignments | 1,397 (one per ticker) |
| — Secondary assignments | 538 |

Each company has exactly one **Primary** sub-theme (its core business) and may
carry one or more **Secondary** sub-themes where it has meaningful second-order
exposure. Because a ticker can appear in several sub-themes, per-sub-theme ticker
counts sum to more than the 1,397 unique names; a theme-level total counts each
company once even when it holds multiple sub-themes within that theme.

## Index coverage

The universe now spans the full large- and mid-cap core of the U.S. market:

- **S&P 500 — 100% represented.** All 500 index constituents are included. The
  only S&P 500 symbols not listed separately are the redundant share-class
  siblings (`GOOG`, `FOX`, `NWS`), which are folded into their primary listings
  (`GOOGL`, `FOXA`, `NWSA`).
- **S&P MidCap 400 — 100% represented.** All 400 index constituents are included.
- **~498 additional names** beyond the S&P 500 / 400 provide thematic depth
  (smaller-cap pure-plays, ADRs, and specialist "picks-and-shovels" businesses)
  so that emerging rotations are visible before they show up in the large-cap
  indices.

Membership reflects the S&P 500 and S&P MidCap 400 rosters as constituted through
the 2026 index rebalances.

## Structure

The CSV has five columns:

| Column | Description |
|---|---|
| `Ticker` | Exchange symbol |
| `Company Name` | Issuer name |
| `Theme` | One of 34 top-level themes |
| `Sub Theme` | One of 175 sub-themes nested under a theme |
| `Assignment` | `Primary` or `Secondary` |

## Companion files

- `SubThemes_by_Theme_Counts.pdf` — the full theme → sub-theme tree with the
  unique-ticker count for each sub-theme.
- `Weekly_Theme_Updater_v01.py` — Python Program that take the Input Ticker List
  an assigns Market Cap and Price Change History to each line.
- `Tickers_Themes_SubThemes.csv` — The output of the Python Program that is
  feed into Claude as a Context file.
- `Claude_rotatation_instructions` — The Claude instruction file to produce the
  weekly report.


## Notes


