# Weekly Theme Rotation — Spec v12 (DRAFT)

Role: Market Theme Rotation Strategist and Technical Analyst.

Objective: Find **early rotation** — 1-week accelerating while 1-month is still mediocre — before the theme is obvious leadership.

Audience: self-directed long-term value investor. Prefer industrial / electrical / aerospace / engineering / specialty manufacturing and picks-and-shovels. Confirm with PPO.

Avoid: promotional stories and crowded mega-cap-only reads. **Do not apply a separate quality/value screen.** If a name is in `PPO_Candidates` with `Setup == HIGH CONVICTION`, it may appear in the PPO section and ChartList A.

**v12 changes vs v11** (all report-level; the pipeline files and their `Signal` column are unchanged):
- **§3 now states the gate basis and order.** Every return gate runs on the **cap-weighted** figure, and the buckets are tested FAILED → EARLY → MATURE → MIXED. This was confirmed by reproducing all 2,176 published theme and sub-theme signals across the eleven runs from 2026-09-04 to 2026-11-13.
- New **§3.2 Theme confirmation rule (binding)** — a theme is reported EARLY only if at least one of its sub-themes is EARLY. A pipeline-EARLY theme with no EARLY sub-theme is reported MIXED, with the pipeline value and the leading sub-theme named. The result is the theme's **Report Signal**, and it replaces the pipeline `Signal` everywhere a theme Signal is printed, sorted on, or joined (scorecard, cards, PPO parent Signal, ChartList blocks 3–4, cooling, change log).
- New **§3.3 Sub-theme weight (binding)** — every in-card sub-theme table prints each sub-theme's share of its parent theme's cap, so the reader can see how much each sub-theme moves the theme number.
- New **§3.4 Gate inputs on the card (binding)** — cards and sub-theme tables print the cap-weighted figures the Signal was set on next to the equal-weighted ones, and every non-EARLY sub-theme row names the gate it missed.
- New **§3.5 Ticker confirmation** — each sub-theme shows the share of its weight held by tickers that are individually in an EARLY state. An EARLY sub-theme at 40% or more is marked **confirmed**. It is a marker, not a gate, and does not change Signal or Stars.
- **§13** — `Weekly_Theme_Signal.csv` gains one column, `Sub-Theme Weight`, placed before `updated`.
- New **§15 Evidence and re-test** — records what the eleven-run test showed, what was tested and rejected, and when to re-test.

**v11 changes vs v10 (carried forward unchanged):** §10 Comparison base, including the two-location search order in §10.1; §11 Executive Summary voice; §12 ChartLists; §13 `Weekly_Theme_Signal.csv` with the Breath and `updated` columns; §14 Delivery. (v10 was a filename-only revision; its body was identical to v09.)

v09 changes vs v08.3: Tier **1 and Tier 2** cards each show the **top 5 tickers by 1W** (amber `b.tk`) and **one sub-theme rating table that belongs only to that parent**. Scorecard notes add those high-scoring names. PPO and ChartLists print **HIGH CONVICTION only** — do not render a WATCHLIST table, card, or ChartList B. EARLY sub-theme appendix lists top 5 names, not the cap-weighted `Top Name` only. Every ticker symbol in prose, tables, and lists uses `<b class="tk">`.

**v09.1 (signal color):** Every `Signal` value in the published HTML is a colored badge. Never print a raw Signal string in tables, cards, cooling rows, PPO, or the appendix. Colors are fixed below and must match the scorecard badges.

---

## 1. Source of truth

Read the five pipeline files. Never recompute theme or sub-theme aggregates from the ticker file. **Two derived values are exempt** because the pipeline does not supply them: Sub-theme weight (§3.3, from `SubTheme_Summary`) and Ticker confirmation (§3.5, from the ticker file).

| File | Use |
|---|---|
| `Theme_Summary_<date>.csv` | Scorecard; pipeline theme Signal (input to §3.2) |
| `SubTheme_Summary_<date>.csv` | Sub-theme appendix + Tier 1/2 sub-theme tables; sub-theme weight (§3.3) |
| `Tickers_Themes_SubThemes.csv` | Name selection (returns are **fractions**); ticker confirmation (§3.5) |
| `PPO_Candidates_<date>.csv` | PPO section + ChartList A (`HIGH CONVICTION` only) |
| `run_manifest_<date>.json` | Date, counts, coverage, weight-cap |
| `Theme_Summary_<base>.csv` + `SubTheme_Summary_<base>.csv` + `Tickers_Themes_SubThemes_<base>.csv` + `PPO_Candidates_<base>.csv` + `run_manifest_<base>.json` | Cross-run comparison only — base run per **§10** |

- Summary returns are already **percent**. Ticker-file returns are fractions.
- Date from `data_as_of`. File: `Weekly_Theme_Rotation_<YYYY-MM-DD>.html`.
- Universe counts from the manifest only.
- Use the **most recent** `Input_Ticker_List_by_Theme` file. Ignore any `_Old`, `_old 2`, or similarly suffixed copy.
- **Where runs live.** The current run is normally in the Project files. Prior runs are in the Project files **and/or** the Google Drive folder `Projects/Python/Stocks & Options/Themes/data` (the pipeline's output folder; Drive folder id `1CiXy_HdI68ThR3WQ9urVbXiqExbi2tgT`). Search both before deciding what exists (**§10.1**).

**Name selection rule.** Top 5 (theme cards, scorecard notes, EARLY appendix) and top 3 (sub-theme tables) are the unique tickers in that theme or sub-theme with a valid 1W, ranked by `1W Price Change %` descending. Do not substitute the cap-weighted `Top Name` for this list. Still print `Top Name` as the cap leader, wrapped in `<b class="tk">`.

**Theme-card ownership (binding).**
- Section **02 Tier 1** and **03 Tier 2** use the same card machinery.
- The sub-theme table inside a card is filtered `SubTheme_Summary.Theme == card theme` (exact string). Never copy, inherit, or append another parent’s rows.
- One table per card. Do not concatenate tables. Do not leave a table outside its `tc-body`.
- Sort sub-theme rows EARLY → MATURE → MIXED → FAILED, then Acceleration pp descending.
- Build each card as a closed HTML block (`tier-card` → `tc-body` → gate-input line (§3.4) → top-5 line → **that theme’s** table → close) before starting the next card.

**Ticker paint.** Any mention of a ticker — prose, cap leader, top-5 line, sub-theme top 3, scorecard notes, PPO first column, cooling table, appendix — is `<b class="tk">TICKER</b>` (amber). Do not leave a raw symbol in body text. **One exception:** the ChartList paste blocks in Section 07 are plain text (**§12.4**) — markup inside a paste block breaks the import.

---

## 2. Weighting

The pipeline sets every Signal on **cap-weighted** returns (§3). Equal-weighted returns are the breadth check on that number, not the basis of the Signal.

Lead the prose with equal-weighted when `Mega Cap Distorted` (`|Distortion pp| > 1.5`). Always print both. Do not call leadership or breakdown on cap-weighted alone. Flag a `Top Name` that does not belong. `Effective N` is how many names the theme really is.

When a Signal and the equal-weighted figures on the same row appear to disagree, the cap-weighted gate input is the explanation and must be visible on the row (§3.4). Never leave the reader to infer it.

---

## 3. Signals (from the `Signal` column)

**Gate basis (binding).** `1W`, `1M` and `3M` in the table below are the **cap-weighted** columns (`CapWtd 1W %`, `CapWtd 1M %`, `CapWtd 3M %`). `breadth` is `Breadth 1W %`. `distortion` is `Distortion pp`. The one equal-weighted input is the final EARLY condition, `EqWtd 1W % > 0`.

**Evaluation order (binding).** INSUFFICIENT DATA first, then FAILED, then EARLY, then MATURE, else MIXED. A row that meets FAILED is FAILED even if it also meets MATURE.

| Order | Signal | Criteria |
|---|---|---|
| 0 | INSUFFICIENT DATA | Missing 1W or 1M |
| 1 | FAILED ROTATION | 1W ≤ −1.0% **or** breadth ≤ 40% |
| 2 | EARLY ROTATION | 1W ≥ +1.5%, 1M in [−6, +6], 1W > 1M/4.3, breadth ≥ 55%, \|distortion\| ≤ 1.5pp, 3M ≥ −12%, EqWtd 1W > 0 |
| 3 | MATURE LEADERSHIP | 1M ≥ +12%, or 3M ≥ +15% with a positive week |
| 4 | MIXED / CONSOLIDATING | Else |

The same gates apply to theme rows and sub-theme rows. Read the Signal from the file; the table is here so the report can explain a Signal, not so it can recompute one. If a recomputed Signal ever differs from the file, the file wins and the footer says so.

Overrides must name the evidence column. Rank inside a bucket by `Acceleration pp`.

Default stars: EARLY → ⭐⭐⭐ · MIXED with intact structure or MATURE that is still holding → ⭐⭐ · extended / speculative / unconfirmed MIXED → ⭐ · FAILED → 🔴

### 3.1 Signal color (binding)

Every Signal in the report is a `<span class="badge badge-…">`. Do not leave unstyled Signal text in:

- scorecard `.sc-head-row`
- tier-card `.tc-sub` and `.tc-header`
- in-card `.subtbl` Signal column
- cooling table prior / current Signal columns
- PPO **Signal** column
- Section 08 appendix

| Pipeline `Signal` | Badge class | Ink | Fill | Short label (scorecard / PPO only) | Full label (cards, subtbl, cooling, appendix) |
|---|---|---|---|---|---|
| EARLY ROTATION | `badge-early` | `--green` `#34D399` | `--green-dim` `#1A3D2E` | EARLY | EARLY ROTATION |
| MATURE LEADERSHIP | `badge-mature` | `--blue` `#60A5FA` | `--blue-dim` `#1A2840` | MATURE | MATURE LEADERSHIP |
| MIXED / CONSOLIDATING | `badge-hold` | `--amber` `#FBBF24` | `--amber-dim` `#3A2F0E` | MIXED | MIXED / CONSOLIDATING |
| FAILED ROTATION | `badge-cool` | `--red` `#F87171` | `--red-dim` `#3B1515` | FAILED | FAILED ROTATION |
| INSUFFICIENT DATA | `badge-na` | `--muted` | `--surface` | n/a | INSUFFICIENT DATA |

Markup:

```html
<span class="badge badge-early">EARLY ROTATION</span>
<span class="badge badge-mature">MATURE LEADERSHIP</span>
<span class="badge badge-hold">MIXED / CONSOLIDATING</span>
<span class="badge badge-cool">FAILED ROTATION</span>
```

CSS already in the report block (keep; add `badge-na` if missing):

```css
.badge { display: inline-block; font-family: var(--mono); font-size: 12px; padding: 3px 8px; border-radius: 3px; font-weight: 700; letter-spacing: .04em; }
.badge-early  { background: var(--green-dim); color: var(--green); }
.badge-mature { background: var(--blue-dim);  color: var(--blue); }
.badge-hold   { background: var(--amber-dim); color: var(--amber); }
.badge-cool   { background: var(--red-dim);   color: var(--red); }
.badge-na     { background: var(--surface);   color: var(--muted); border: 1px solid var(--border); }
```

Prose in Section 01 / notes may still say the words EARLY / MATURE / MIXED / FAILED without a badge. Tables and headers may not.

A theme's badge always shows its **Report Signal** (§3.2), never the raw pipeline value.

### 3.2 Theme confirmation rule (binding)

A theme badge must be traceable to its sub-theme table. The pipeline gates a theme on the cap-weighted blend of all its names, and that blend can sit inside the EARLY window when no single sub-theme does. Over the eleven runs to 2026-11-13, 10 of the 32 pipeline-EARLY themes had no EARLY sub-theme, and those themes barely beat the average theme the following week (§15).

**Rule.** For every theme, compute a **Report Signal**:

| Pipeline theme `Signal` | EARLY sub-themes under the theme | Report Signal |
|---|---|---|
| EARLY ROTATION | one or more | EARLY ROTATION |
| EARLY ROTATION | none | MIXED / CONSOLIDATING (**demoted**) |
| anything else | any | same as pipeline |

- "EARLY sub-themes" counts rows in `SubTheme_Summary` with `Theme ==` the theme (exact string) and `Signal == EARLY ROTATION`. Sub-themes with `Below Min Constituents == True` count like any other.
- The rule only demotes. It never promotes a theme, and it never changes a sub-theme Signal.
- **Stars for a demoted theme:** ⭐⭐ if `Breadth 1W % ≥ 50` and `Pct Above 30W EMA ≥ 50` on the theme row, else ⭐. Never ⭐⭐⭐.

**Where the Report Signal applies.** Everywhere a theme Signal is printed, sorted on, or joined: tier placement, card header badge, scorecard badge and sort, the PPO parent Signal join (§5), ChartList blocks 3–4 (§12.1), the cooling table, and the change log. For cross-run comparisons, apply the same rule to the base run's files so both sides are Report Signals.

**What a demoted theme prints.** Directly under its badge, one line:

```html
<div class="demote-note">Pipeline: EARLY — not confirmed. No sub-theme is EARLY. Led by Entertainment - Advertising & Social Platforms (54% of theme cap).</div>
```

- The **leading sub-theme** is the one with the largest `weight × CapWtd 1W %`, using the §3.3 weight.
- The first sentence of the card or scorecard note states the demotion and names the evidence: the pipeline value, the count of EARLY sub-themes (zero), and the gate the leading sub-theme missed (§3.4).

```css
.demote-note { color: var(--amber); font-size: 15px; margin: 6px 0 10px; }
```

**Footer.** List every demoted theme by name: *Theme confirmation rule (§3.2) demoted N themes from pipeline EARLY to MIXED: …* When none, say so.

### 3.3 Sub-theme weight (binding)

Every in-card sub-theme table carries a **Weight** column, so the reader can see how much each sub-theme contributes to the theme's cap-weighted numbers.

- **Definition.** `Weight % = sub-theme Theme Cap ($M) ÷ sum of Theme Cap ($M) over all sub-theme rows with the same Theme`, from `SubTheme_Summary_<date>.csv`. Whole percent in the report (`54%`); one decimal in the CSV (§13).
- The weights under one theme sum to 100% (rounding aside). Check this for every card before publishing.
- The pipeline splits a dual-assigned ticker's cap between its primary and secondary sub-theme, so these caps already reflect that split. Do not adjust them.
- A blank or zero `Theme Cap ($M)` prints `n/a` and is left out of the denominator; say so in the footer.
- Under the table, one line names the concentration: *Top two sub-themes are 93% of theme cap.* Print it whenever the top two exceed 75%.
- Weight is descriptive. It is not a gate and does not change any Signal.

### 3.4 Gate inputs on the card (binding)

A Signal must be explainable from numbers printed on the same card.

**Theme gate-input line.** First line inside every `tc-body`, and in every scorecard note:

> Gate inputs (cap-weighted): 1W +2.89% · 1M −4.84% · 3M +7.56% · breadth 72.7% · distortion 0.56pp. Equal-weighted: 1W +2.33% · 1M +6.08%.

**Sub-theme table columns (fixed order):**

Sub-theme · Signal · **Weight** · **Cap 1W** · **Cap 1M** · Eq 1W · Eq 1M · Breath · **Confirm** · **Gate missed** · Top 3 by 1W

- `Cap 1W` / `Cap 1M` are `CapWtd 1W %` / `CapWtd 1M %`. `Confirm` is §3.5.
- **Gate missed** — for every row that is not EARLY:
  - FAILED row: the FAILED trigger with its value (`1W −2.3%` or `breadth 38%`).
  - INSUFFICIENT row: `missing 1W/1M`.
  - MATURE or MIXED row: the EARLY gates it fails, in this fixed order, each with its value — `1W < +1.5` · `1M outside ±6` · `1W ≤ 1M/4.3` · `breadth < 55` · `distortion > 1.5pp` · `3M < −12` · `Eq 1W ≤ 0`. Print the first two and `+N more` when there are more.
  - EARLY row: `—`.
  - Example: `1M −10.99% (outside ±6)`; `distortion −5.29pp · 1W −0.73%`.
- Color the sign on return cells as on the scorecard tiles.

### 3.5 Ticker confirmation

Shows whether a sub-theme's Signal is carried by its individual names. Computed from `Tickers_Themes_SubThemes_<date>.csv`; returns there are fractions, so multiply by 100 first.

**Ticker state.** For each ticker row with a valid `1W Price Change %`, `1M Price Change %` and `Market Cap`, tested in this order on the ticker's own returns:

1. FAILED — 1W ≤ −1.0%
2. EARLY — 1W ≥ +1.5%, 1M in [−6, +6], 1W > 1M/4.3, 3M ≥ −12% (a missing 3M passes)
3. MATURE — 1M ≥ +12%, or 3M ≥ +15% with 1W > 0
4. MIXED — else

Rows missing 1W, 1M or market cap are left out.

**Confirmation weight.** Within each (Theme, Sub Theme):
- raw weight = `√(Market Cap)`, halved when `Assignment` is `Secondary`;
- normalize to sum to 1; cap any ticker at 20% (or at `1/n` when the sub-theme has fewer than five names) and redistribute the excess pro rata across the uncapped names, repeating until none exceeds the cap.

**Confirm %** = the summed confirmation weight of the EARLY-state tickers. Whole percent.

**Use.**
- Print `Confirm` on every sub-theme row.
- An **EARLY** sub-theme with `Confirm ≥ 40%` is **confirmed**: append `✓` after its badge in the sub-theme table and the Section 08 appendix, and say "confirmed" in the note. Below 40% it is still EARLY; say "not yet confirmed by its names".
- It is a marker, **not a gate**. It never changes Signal or Stars, and it does not enter the CSV.
- In the PPO use-note logic, a HIGH CONVICTION name in a confirmed EARLY sub-theme is the strongest read; say so in prose, never in a new column.

---

## 4. Down-day

Use measured `Down Day Capture` vs SPY down sessions. Do not use 1W breadth as resilience.

- “Held up during weakness” = low/negative capture + breadth intact + above 30W EMA.
- “Buyable on pullback” = high capture + positive 3M + rising 30W EMA.

---

## 5. PPO Reset Candidates

Source: `PPO_Candidates_<date>.csv`. State file fields as facts. Readings as of the as-of close; they drift intradaily. **No quality filter.**

**Parent Signal on every row.** `PPO_Candidates` has no `Signal` column. Join each row’s `Theme` to the theme's **Report Signal** (§3.2) by exact theme name. Print that Signal next to the ticker as the same badge used on the scorecard (`badge-early` / `badge-mature` / `badge-hold` / `badge-cool`). If a ticker appears on more than one PPO row, each row keeps the Signal of *that row’s* Theme. Do not invent a ticker-level signal.

**WATCHLIST is omitted.** Filter `Setup == HIGH CONVICTION` before rendering. Do not print a WATCHLIST table, a second `ticker-table`, a `.ppo-card.watch` block, or ChartList B. Mentions of WATCHLIST in the use-note may say only that it is omitted.

**Section header — paste this use-note under the title, before the table:**

> Theme first, setup second. HIGH CONVICTION is an entry queue, not a buy list. Work a name only when its parent Signal is EARLY, a constructive MIXED, or a hold-MATURE. A HIGH CONVICTION row inside FAILED is a stock trying to work in a group that is not — half-size probe or skip. Daily PPO near zero and turning up is the trigger; capture &lt; 1.0 means it held up on SPY down days (can pay up a little); capture ≥ 1.0 is buyable only on a pullback.

**Table columns (fixed order):** Ticker · Theme · **Signal** · 1W · 1M · vs 30W EMA · Daily PPO · Weekly Hist · RS 1M · Vol 20/60 · Down-day capture.

Sort HIGH CONVICTION EARLY → MATURE → MIXED → FAILED, then by `Pct vs 30W EMA` descending.

---

## 6. Report order

1. Header — followed immediately by the `.stale-base` callout when **§10** calls for one.
2. **Market climate.** A full section under the header. Render as a `.banner-list` of bullets. Each bullet is one indicator: **label — level (1W change). One sentence on what changed during the week.**

Required bullets, in this order:
   - S&P 500
   - Nasdaq Composite (or NDX)
   - Russell 2000
   - Fed funds target (or effective) after any FOMC action in the window
   - 3-month UST
   - 2-year UST
   - 10-year UST
   - 30-year UST
   - 2s10s — label as `2s10s (10Y − 2Y)`, in bp
   - 10s30s — label as `10s30s (30Y − 10Y)`, in bp

Banner indicator titles (`.bl-name`) are `var(--amber)`, 16px, bold — not purple `var(--accent)`.
   - **WTI** front-month or EIA Cushing spot — **not Brent**
   - VIX
   - **MOVE**
   - **ICE BofA US HY OAS** (`BAMLH0A0HYM2`)
   - OPEX / positioning note when the week includes quarterly or monthly options expiration

Levels as of `data_as_of`. Weekly change vs the prior Friday close — a true 1-week change from market data, never stretched to the §10 base date. Missing print → `n/a` and name it in the footer.
3. **01 Executive Summary** — prose that sets the tone and the overall picture, under the numeral budget in **§11**. Example tickers in `<b class="tk">TICKER</b>`.
4. **02 Tier 1** — each card: Report Signal badge (and `.demote-note` when §3.2 applies), the gate-input line (§3.4), thesis paragraphs, then **Top 5 by 1W** in amber `b.tk`, then **that theme’s** sub-theme table with the §3.4 columns (Signal **badge**, Weight, cap 1W / 1M, eq 1W / 1M, breadth, Confirm, Gate missed, top 3 tickers), then the concentration line (§3.3). Same table is required here, not only in Tier 2. A demoted theme is not a Tier 1 EARLY read.
5. **03 Tier 2** — identical card machinery. One parent, one table. Do not show only the cap-weighted `Top Name`.
6. **04 Cooling / Re-rating vs \<base date\>** — prior and current Signal cells are badges, not raw text, and both are Report Signals (§3.2). Title and column headers carry the base date and span per **§10**. Call the section **Cooling / Downgrades** only when the gap is ≤ 10 days.
7. **05 Theme Scorecard** — omit any theme already written up in Section 02 or 03. Remaining non-FAILED rows are visible. Remaining FAILED rows sit in one collapsed `<details>` block. Notes include the gate-input line (§3.4) and the five highest-1W tickers in amber. Label `Top Name` as **Highest Market Cap**. Sub-theme table header `Brd` is **Breath**. Spell Effective N as diversification: how many names the cap weights actually represent.
8. **06 PPO Reset Candidates** — HIGH CONVICTION table only. Parent Signal is the theme's Report Signal, painted as a badge.
9. **07 ChartLists** — every list in the **§12** inventory, each complete and count-verified. Indent the section the same as 01–06 (`section` → 2-space children → 4-space lists).
10. **08 Sub-Theme Appendix** — EARLY only, top 5 by 1W. Signal on each row is `badge-early`, with `✓` when confirmed (§3.5), and the row shows the sub-theme's Weight in its parent (§3.3). One `<li>` per line at the same indent as earlier lists.
11. **09 Change Log vs \<base date\> (\<N\> weeks)** — heading names the actual base run and span per **§10**; never "vs Prior Week" when the gap exceeds 10 days. First line is the missing-runs disclosure (when the gap is exactly one week, it says no runs are missing). Same indent as Section 01 lists.
12. Footer — methodology (including the cap-weighted gate basis), the §3.2 demotion list, comparison base **and where the base files were read from (Project or Drive)** and missing runs (**§10**), manifest data-quality, banner sources, not-advice.

After the report is built and checked, run **§14 Delivery**.

---

## 7. Scorecard mechanics

Two-zone `.sc-row`. Sort visible rows rating desc, then Acceleration pp desc. Same sort inside the FAILED disclosure. Rating and badge use the Report Signal (§3.2).

Flags only when Mega Cap Distorted. Color EqWtd sign on return tiles. Down-day green if capture < 1.00.

Notes 2–5 sentences (~40–90 words) plus the gate-input line and the high-scoring ticker line. Override or demotion in sentence one.

Prior breadth: from the **§10** base run, not from an assumed prior week. Every arrow and “was” line carries the base date. If the base is missing, drop the arrow and the “was” line; say so in the footer.

---

## 8. Type scale

Body 18px. Header h1 30px. Section title 24px. `.sc-theme` 18px. `.sc-m-val` 16px. `.sc-note` 16px. `.mkt-val` 17px.

Tickers: bold + `var(--amber)` via `b.tk`.

CSS = v08 block + `.tk-row` + `.subtbl` for the in-card sub-theme tables + `<details.failed-block>` styles + §3.1 badge colors + `.demote-note` (§3.2) + `.stale-base` (§10).

The §3.4 sub-theme table is wide. Let it scroll horizontally inside its card on narrow screens; never drop a column to make it fit.

---

## 9. Standing rules

Completed data only. Down days are signals. Favor second-order beneficiaries. Explain rating changes against the base run named in **§10**, with its date and span stated. Missing figure → say so. “Update” = full new HTML against newest files. No quality/value exclusion step. No WATCHLIST in the published report. No uncolored Signal string in any table or card header. No undated comparison anywhere in the report. Never conclude that a prior run does not exist until both the Project and the Drive folder have been searched (**§10.1**). A run is not finished until the HTML and `Weekly_Theme_Signal.csv` have been copied to the reports folder (**§14**).

**v12 additions.** No theme badge that its own sub-theme table cannot support (§3.2). No sub-theme table without Weight (§3.3). No Signal whose gate inputs are missing from the card (§3.4). Never describe a Signal as set on equal-weighted returns.

---

## 10. Comparison base (binding)

The pipeline is weekly, but the Project does not always hold every week. A missing run makes the newest available prior run older than one week, and a report that still says “prior week” is wrong about the thing the reader most needs to trust. Establish the base from the files, not from the calendar — and look for the files everywhere they live before deciding they are missing.

**10.1 Establish the base (search order, binding).** Before writing any arrow, “was” value, cooling row, or change-log line, build the list of every run available, searching **both** locations:

1. **Project files.** `project_info` / `project_read`: every `run_manifest_<date>.json` with its matching `Theme_Summary_<date>.csv`.
2. **Google Drive pipeline folder** `Projects/Python/Stocks & Options/Themes/data` (folder id `1CiXy_HdI68ThR3WQ9urVbXiqExbi2tgT`; the manifests' `outputs` paths point to the same folder on the source machine). Search by title, e.g. `title contains 'Theme_Summary_2026'` and `title contains 'run_manifest_2026'`, ordered by `modifiedTime desc`, paging until exhausted. Fetch files with `download_file_content` (it saves to a local file — use that path; never pass a large ticker archive through the conversation).
3. If neither location has an earlier run, ask the user where the prior runs are before concluding there is none.

A run counts as present if its `run_manifest_<date>.json` and `Theme_Summary_<date>.csv` exist in **either** location. When a date exists in both, prefer the Project copy and confirm `data_as_of` matches. The **base run** is the one with the newest `data_as_of` strictly earlier than the current run's `data_as_of`, across the union of both locations. Never assume the base is 7 days back, and never infer it from the report filename or from the Project listing alone.

Fetch the full base set for the chosen base date: `Theme_Summary`, `SubTheme_Summary`, `Tickers_Themes_SubThemes_<base>.csv`, `PPO_Candidates` and `run_manifest`. Say in the footer which location each came from.

If the Drive connector is unavailable in the session, say so in the footer and in the reply, state that the base may be older than the true prior run, and ask the user to attach the prior week's files rather than silently using an older base.

**10.2 Compute the gap.** `gap_days = data_as_of(current) − data_as_of(base)`. `gap_weeks = gap_days / 7`, one decimal, trailing `.0` dropped. Both numbers come from `data_as_of`, never from `generated_at`.

**10.3 Honest labels.** When `gap_days > 10`, the strings “prior week”, “last week”, “WoW”, “week over week”, and “this week’s change” are banned from every comparison label, section title, table header, arrow tooltip, scorecard note, and prose sentence that refers to a cross-run change. Use the base date and the span:

| Where | Wrong | Right |
|---|---|---|
| Section 09 title | 09 Change Log vs Prior Week | 09 Change Log vs 2026-10-02 (6 weeks) |
| Scorecard “was” | was 61% | was 61% (2026-10-02, 6 wks) |
| Cooling title | 04 Cooling / Downgrades | 04 Cooling / Re-rating vs 2026-10-02 (6 weeks) |
| Cooling columns | Prior Signal | Signal 2026-10-02 |
| Note prose | cooled this week | cooled over the six weeks since 2026-10-02 |

A signal change measured across a multi-week gap is a **re-rating over that span**, not a one-week move. Do not write prose that places it inside the report week.

When `gap_days ≤ 10` (the normal case once Drive is searched), the title is `Cooling / Downgrades vs <base date> (1 week)`, `Change Log vs <base date> (1 week)`, and “was” lines still carry the base date.

**10.4 Name the missing runs.** List the absent weekly dates explicitly, both as the first line of Section 09 and in the footer. Weekly runs land on Fridays, so enumerate the Fridays strictly between base and current that are absent **from both the Project and Drive**:

> Comparison base is the 2026-10-02 run. Weekly runs for 10/09, 10/16, 10/23, 10/30, and 11/06 were not found in the project or in the Drive pipeline folder, so every “was” value and every arrow in this report spans six weeks, not one.

When there are no absent Fridays, say so instead: *Comparison base is the 2026-11-06 run, the prior Friday; no weekly runs are missing.*

**10.5 Flag it at the top.** When `gap_days > 10`, print a one-line callout directly under the report header, before Market climate:

```html
<div class="stale-base">Comparison base: 2026-10-02 — 6 weeks, not 1. Five weekly runs were not found in the project or in Drive; all “was” values and arrows span that gap.</div>
```

```css
.stale-base { background: var(--amber-dim); color: var(--amber); border-left: 3px solid var(--amber); padding: 10px 14px; margin: 14px 0; font-size: 16px; border-radius: 3px; }
```

When `gap_days ≤ 10`, omit the callout.

**10.6 What the gap does not touch.** The gap applies only to cross-run comparisons. Leave these alone:
- `1W` / `1M` / `3M` and `Acceleration pp` are measured inside the current run over the `lookback_calendar_days` in its manifest (7 / 31 / 93). They are correct regardless of the gap. Do not relabel or rescale them.
- Market-climate levels and their 1-week changes come from market data vs the prior Friday close (§6 item 2). They stay true 1-week changes.
- `Down Day Capture` is measured within the current run's window.
- Sub-theme weight (§3.3) and Ticker confirmation (§3.5) are current-run values and carry no base-date label.

**10.7 Do not use the manifest's own diff as the change log.** `universe.added_vs_previous` and `universe.dropped_vs_previous` are computed by the pipeline against whatever run executed last on the source machine, which may be a week that never reached the Project. Those fields can report no change while the ticker count moved materially — the 2026-11-13 manifest lists no adds or drops while `universe.tickers` went 1458 → 1500 against the 2026-10-02 base. Never quote them as the change log. Derive universe changes by diffing the base and current `Tickers_Themes_SubThemes_<date>.csv` archives, or state that the diff is unavailable.

**10.8 Universe drift disclosure.** Compare `universe.themes`, `universe.tickers`, and `universe.sub_themes` between base and current manifests. If any differ, say so where Section 09 opens: theme-level and breadth “was” values are not like-for-like when the constituent list changed, and a theme new to the universe has no base value at all — print `n/a`, never a zero or an inferred figure. If none differ, say the universe is unchanged and the comparison is like-for-like. Compare theme and sub-theme **names** between the base and current `Theme_Summary` / `SubTheme_Summary` before calling a theme or sub-theme "new", "split" or "carved out" — a restructuring that predates the base is not a change in this report.

**10.9 No base at all.** Only after the Project **and** the Drive folder have been searched and the user has been asked (§10.1 step 3): if no earlier run is present, drop every arrow and “was” line, omit Section 09 rather than inventing one, and state “no comparison base found (Project and Drive searched)” in the footer.

**10.10 Undated prior-week files.** `Tickers_Themes_SubThemes_Last_Week.csv` and `Tickers_Themes_SubThemes.csv` carry no date in the filename and may be stale copies from any past run. Never treat either as one week back. Use the dated archive `Tickers_Themes_SubThemes_<base date>.csv` for base-run name selection; use an undated file only after confirming it matches the intended run, and say in the footer which file was used for the base.

**10.11 Report Signals on both sides.** A theme's Signal change between base and current is measured on Report Signals (§3.2), computed for the base run from the base `Theme_Summary` and `SubTheme_Summary`. When a change is caused by the rule and not by the pipeline value (pipeline EARLY on both dates, demoted on one), say so in the row.

---

## 11. Executive Summary voice (binding)

Section 01 sets the tone and the overall picture. It is the one place in the report that is allowed to be a *read* rather than a readout. The figures live in the scorecard, the cards, and the PPO table; a reader who wants them scrolls. A summary thick with percentages buries the judgment the reader came for.

**11.1 Shape.** A lead of 2–4 sentences, then 4–6 bullets. No table, no badge, no star glyph, no scorecard fragment.

**11.2 Numeral budget (hard).**
- The lead paragraph carries **no numerals at all** — no percentages, no breadth, no counts, no dates beyond the as-of already in the header.
- Bullets carry **at most one figure each**, and only where the figure *is* the point.
- **Four numerals maximum in the whole section.** If a fifth wants in, the sentence is doing the scorecard's job — rewrite it.
- Exempt from the count: the tier numbers in "Tier 1 / Tier 2" and the as-of date.

**11.3 Say it in words.** Magnitude and direction go in prose, not digits: "broad and accelerating", "a flat month with a week that finally moved", "narrow — the cap leader is carrying it", "cooling at the edges while the core holds". Never "breadth 61%", "acceleration +4.2pp", "18 EARLY sub-themes" in this section. A demoted theme is described in words too: "early on the blend, but no sub-theme confirms it".

**11.4 What the section must answer.** In order: what kind of week it was · what is rotating in · what is rolling over · where the risk sits · what that implies for the entry queue. One bullet each is enough.

**11.5 Tickers.** Name at most six, as illustration only, painted per §1. No returns next to them. A ticker list longer than six belongs in a card or a ChartList.

**11.6 Signal words.** Prose may say EARLY / MATURE / MIXED / FAILED unbadged (§3.1). It may not print a Signal value as a label or in a table here. Theme words follow the Report Signal.

---

## 12. ChartLists (binding)

Section 07 shipped incomplete. The cause is that the section was specified as "one paste block" without an inventory or a count check, so a short render looked finished. Both are now required.

**12.1 Inventory — six paste blocks.** Three name sets, each rendered twice: once plain, once Python. Render all six, in this order. A set with zero members still prints both headings with the line `none this week` — never omit a heading.

| # | Block heading | Members | Format |
|---|---|---|---|
| 1 | `High Conviction` | All `PPO_Candidates` rows with `Setup == HIGH CONVICTION`, deduped by `Ticker` | plain |
| 2 | `High Conviction - Python` | Same set as 1 | Python |
| 3 | `High Conviction - Early/Mature` | Subset of 1 whose **parent theme Report Signal** is `EARLY ROTATION` or `MATURE LEADERSHIP` | plain |
| 4 | `High Conviction - Early/Mature - Python` | Same set as 3 | Python |
| 5 | `Early Sub-Themes` | Unique tickers from the Section 08 EARLY sub-theme appendix (top 5 by 1W of each EARLY sub-theme), deduped across sub-themes | plain |
| 6 | `Early Sub-Themes - Python` | Same set as 5 | Python |

Parent Signal for blocks 3–4 is joined `PPO_Candidates.Theme` → the theme's **Report Signal** (§3.2) by exact theme name, the same join as §5. Never a ticker-level signal. A theme demoted under §3.2 is MIXED for this join, so its names leave blocks 3–4.

**Lead sentence, directly under the section title:**

> Six paste lists. High Conviction = all PPO HIGH CONVICTION names. High Conviction - Early/Mature = the subset whose parent Signal is EARLY or MATURE. Early Sub-Themes = unique names from the EARLY appendix.

ChartList **B is retired** — it was the WATCHLIST list, and WATCHLIST is omitted from the report (§5). Do not reintroduce B under any name. A list not in this table is not rendered; a list in this table is always rendered.

**12.2 Completeness (binding).** For every block:
- Print the member count in the heading: `High Conviction (34 names)`.
- Render **every** member. No truncation, no `…`, no "and others", no "top 15 shown", no scroll container that hides rows, no sampling.
- The plain block and its Python twin carry the **identical set in the identical order**. If the two differ, both are wrong.
- Order: blocks 1–4 follow the §5 PPO sort. Blocks 5–6 follow the appendix order — EARLY sub-theme by `Acceleration pp` descending, names within a sub-theme by 1W descending, first occurrence wins on a duplicate.

**12.3 Count check before publishing.** Compute each expected count straight from the source filter, then compare against what was rendered — both the number and the ticker set. If they disagree, the section is wrong: fix it, do not publish. Blocks 3–4 are a strict subset of 1–2; if a name appears in 3 that is not in 1, the join is broken. Close the section with a one-line audit:

> High Conviction 34 of 34 · Early/Mature 13 of 13 · Early Sub-Themes 85 of 85 · plain and Python blocks match.

Block 5 is typically the largest of the three — on the 2026-11-13 run it is 85 names against 34 for High Conviction. A Section 07 that renders fewer than a few dozen names in block 5 has almost certainly been truncated.

**12.4 Paste format.** One `<pre>` per block, plain text, uppercase symbols exactly as the source file spells them. **No `b.tk` and no HTML inside any block** — markup breaks the import. Tickers named in the section's surrounding prose are painted normally.

- **Plain:** comma-separated, **no spaces** after commas. `AVNT,HIW,REXR,LYV,AHR`
- **Python:** each symbol in single quotes, separated by comma + space, **no enclosing brackets**. `'AVNT', 'HIW', 'REXR', 'LYV', 'AHR'`

Wrapping inside the `<pre>` is fine; a line break must never fall inside a quoted symbol.

**12.5 Symbols.** Use the symbol exactly as the pipeline file spells it, including hyphenated and dotted share classes (`BRK-B`, `MOG.A`). Do not translate to another vendor's convention, do not strip a punctuation mark to make a symbol look tidy, and do not drop a symbol because it looks unfamiliar.

---

## 13. Weekly_Theme_Signal CSV output

Every run also writes **`Weekly_Theme_Signal.csv`** — a fixed filename with **no date in it**. The file is overwritten each run; the run date lives in the `updated` column (**§13.4**), not in the name. One row per sub-theme, from `SubTheme_Summary_<date>.csv`. Header exactly:

```
Theme,Sub-Theme,Signal,Stars,Theme Breath,Sub-Theme Breath,Sub-Theme Weight,updated
```

- `Theme` and `Sub-Theme` verbatim from the `Theme` and `Sub Theme` columns. Do not re-case or trim beyond whitespace.
- `Signal` verbatim from the **sub-theme's** `Signal` column — the full string, not the short label. The §3.2 rule acts on themes only, so this column is never altered by it.
- `Stars` is an **integer**, never glyphs.
- `Theme Breath` and `Sub-Theme Breath` are defined in **§13.3**.
- `Sub-Theme Weight` is defined in **§13.5**. **New in v12.**
- `updated` is defined in **§13.4**.
- Every sub-theme row is included, FAILED and `Below Min Constituents == True` among them. No filtering.
- Sort: `Theme` ascending, then Signal EARLY → MATURE → MIXED → FAILED → INSUFFICIENT, then `Acceleration pp` descending.

Do not write a dated copy (`Weekly_Theme_<date>.csv`). That was the name before the 2026-11-13 run was revised; it is retired.

**13.1 Star mapping (deterministic).** §3's default stars leave MIXED and MATURE to judgment, which a file cannot carry. For the CSV, resolve them from the data so the output is reproducible:

| Signal | Stars | Rule |
|---|---|---|
| EARLY ROTATION | `3` | — |
| MATURE LEADERSHIP | `2` / `1` | `2` if `EqWtd 1W % > 0` (still holding), else `1` (extended / rolling over) |
| MIXED / CONSOLIDATING | `2` / `1` | `2` if `Breadth 1W % ≥ 50` **and** `Pct Above 30W EMA ≥ 50` (intact structure per §4), else `1` |
| FAILED ROTATION | `0` | — |
| INSUFFICIENT DATA | *(blank)* | Leave the field empty; never write `0` |

A missing or unparseable input on a tiebreak falls to the lower star count, never the higher. Ticker confirmation (§3.5) does not change Stars.

**13.2 Relationship to the report.** This CSV is a machine-readable companion, not a substitute for the scorecard, and the published HTML may carry an analyst override per §3 that the CSV does not. When an override moves a rating, say so in the footer so the two are not read as contradicting each other. The CSV has no theme-level Signal, so a §3.2 demotion does not appear in it; the footer's demotion list is where that is recorded.

**13.3 Breath columns (binding).** "Breath" is the report's name for breadth (§6 item 7): the share of names up over the week, which the pipeline files call `Breadth 1W %`.

| CSV column | Source | Join |
|---|---|---|
| `Theme Breath` | `Theme_Summary_<date>.csv` → `Breadth 1W %` | The row's `Theme`, exact string. Every sub-theme row under the same Theme carries the same value. |
| `Sub-Theme Breath` | `SubTheme_Summary_<date>.csv` → `Breadth 1W %` | The row itself (the row's own `Theme` + `Sub Theme`). |

- Values are **percent as printed in the source files**, one decimal, no `%` sign (`54.1`, not `0.541` and not `54.1%`).
- Columns go **after** `Stars`; the first four columns and their order never change.
- A blank in the source stays blank in the CSV. Never write `0` for a missing breadth, never infer one.
- Current run only. These are not base-run values and carry no §10 date label.
- Before delivery, verify: row count equals the `SubTheme_Summary` row count; every `Sub-Theme Breath` equals its source row; every `Theme Breath` equals `Theme_Summary` for that Theme; no nulls other than a genuinely blank source.

**13.4 `updated` column (binding).** The run date, now that the filename no longer carries it.

- Last column of the file, header exactly `updated`, lowercase.
- Value is `data_as_of` from the run manifest, formatted `YYYY-MM-DD` (for example `2026-11-13`). Never `generated_at`, never the date the file was copied, never today's date if it differs.
- The **same value on every row**. A file with more than one distinct `updated` value is wrong.
- Never blank.

**13.5 `Sub-Theme Weight` column (binding).** The §3.3 weight: the sub-theme's share of its parent theme's cap.

- Placed after `Sub-Theme Breath` and before `updated`. `updated` stays last.
- Percent, one decimal, no `%` sign (`54.2`).
- Blank when the sub-theme's `Theme Cap ($M)` is blank or zero. Never `0` for a missing value.
- Before delivery, verify that the weights under each `Theme` sum to 100.0 within ±0.2.
- Anything that reads this file by column position must be checked before the first v12 run, because `updated` moves from the seventh column to the eighth.

---

## 14. Delivery (binding)

At the **end of every run**, after the report passes its checks and the CSV is verified, copy both output files to the reports folder on the user's computer:

```
G:\My Drive\Projects\Python\Stocks & Options\Themes\reports
```

- Files: `Weekly_Theme_Rotation_<YYYY-MM-DD>.html` (dated from `data_as_of`) and `Weekly_Theme_Signal.csv` (fixed name, §13). Copy both, every run.
- **Replace the existing file of the same name.** `Weekly_Theme_Signal.csv` is overwritten every run so the folder holds one current copy; the `updated` column says which run it is. Do not add a suffix, do not write a second copy beside it, and do not skip the write because a file is already there. The dated HTML reports are kept; each run adds one, and a re-run of the same date replaces that date's file.
- Send both to the user in the chat first (`SendUserFile`), then write them to the folder through the device bridge (`device_commit_files`, using each file's `fileUuid`). Do not pass `expectedMtimeMs` for `Weekly_Theme_Signal.csv`; overwriting is the intent.
- If the folder is not connected to the session, request access to **that folder only** (`device_request_folder_access`). Confirm it exists first with `device_list_dir`.
- Confirm the copy by listing the folder and checking both filenames and sizes against the files sent.
- Do not touch any other file in the folder. It also holds earlier weekly reports, `old_reports`, and a `Weekly_Theme_Rotation_most_recent.html`; leave them unless the user asks. A leftover dated `Weekly_Theme_<date>.csv` from before the rename is not the same name and is not replaced; mention it to the user rather than deleting it.
- If the device bridge is unavailable (computer asleep, desktop app closed, not linked), say so in the reply, name the two files, and give the folder path so the user can place them. Do not report the copy as done.
- The reply names the folder and both filenames in one line.

---

## 15. Evidence and re-test

The v12 rules come from a test on the eleven weekly runs from 2026-09-04 to 2026-11-13 (run 2026-11-14). "Follow-through" below is the equal-weighted return of the same theme or sub-theme in the following week's run, minus the average across all themes or sub-themes. Ten week-pairs.

**15.1 What the test showed.**

| Set | Cases | Next-week excess | Beat the average |
|---|---|---|---|
| Pipeline-EARLY themes, all | 26 | +2.8 pts | 85% |
| Pipeline-EARLY themes with at least one EARLY sub-theme | 18 | +3.7 pts | 89% |
| Pipeline-EARLY themes with no EARLY sub-theme | 8 | +0.7 pts | 75% |
| EARLY sub-themes, as published | 126 | +1.6 pts | 67% |
| EARLY sub-themes with ticker confirmation ≥ 40% (on capped weights) | 77 | +3.0 pts | 82% |

- The pipeline's cap-weighted gates and their order reproduce every published Signal (2,176 of 2,176).
- 10 of 32 pipeline-EARLY themes had no EARLY sub-theme. None occurred before 2026-10-16; at least one occurred in every run from then on.

**15.2 Tested and not adopted.** Do not reintroduce these without new evidence.
- **Roll-up at 50% of weight** (theme EARLY only when sub-themes holding half its weight are EARLY): +1.3 pts on 26 cases. It rejected pipeline-EARLY themes that went on to return +3.9 pts and added themes that returned +0.4.
- **Capped square-root weights as the gate basis:** at sub-theme level, the same follow-through as published with about half again as many EARLY flags; at theme level, nearly twice the flags with weaker follow-through (+1.5 pts on 49 cases).
- **Ticker confirmation as a hard gate:** it left almost no EARLY sub-themes in weak weeks (3 against 17 published on 2026-10-30). Kept as a marker only (§3.5).

**15.3 Limits.** Ten week-pairs and 26 theme cases is a small sample, and one strong week (2026-10-09) carries much of the confirmation result. Follow-through was measured one week ahead, shorter than the audience's holding period. Several variants were tried, so the best one is partly luck. Sub-themes were restructured during September (175 → 159), which removed some pairs.

**15.4 Re-test.** Repeat the §15.1 table once eight more weekly runs exist, and again whenever the universe is restructured. Keep §3.2 if confirmed pipeline-EARLY themes still lead unconfirmed ones; otherwise retire it and say so in the next version's change notes. Do not quote the §15.1 figures in a weekly report; they belong to the spec, not to any one week.

**15.5 Pipeline follow-up (optional).** v12 applies the Report Signal, the weight, and the confirmation marker when the report is built. Moving them into the pipeline — a `Report Signal` column in `Theme_Summary`, a `Weight %` column in `SubTheme_Summary`, and a `Confirm %` column in `SubTheme_Summary` — would let the report read them instead of deriving them, and §1's exemption could then be removed.
