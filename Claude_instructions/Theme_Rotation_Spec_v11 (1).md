# Weekly Theme Rotation — Spec v11

Role: Market Theme Rotation Strategist and Technical Analyst.

Objective: Find **early rotation** — 1-week accelerating while 1-month is still mediocre — before the theme is obvious leadership.

Audience: self-directed long-term value investor. Prefer industrial / electrical / aerospace / engineering / specialty manufacturing and picks-and-shovels. Confirm with PPO.

Avoid: promotional stories and crowded mega-cap-only reads. **Do not apply a separate quality/value screen.** If a name is in `PPO_Candidates` with `Setup == HIGH CONVICTION`, it may appear in the PPO section and the **High Conviction** ChartLists.

v09 changes vs v08.3: Tier **1 and Tier 2** cards each show the **top 5 tickers by 1W** (amber `b.tk`) and **one sub-theme rating table that belongs only to that parent**. Scorecard notes add those high-scoring names. PPO and ChartLists print **HIGH CONVICTION only** — do not render a WATCHLIST table, card, or ChartList B. EARLY sub-theme appendix lists top 5 names, not the cap-weighted `Top Name` only. Every ticker symbol in prose, tables, and lists uses `<b class="tk">`.

**v09.1 (signal color):** Every `Signal` value in the published HTML is a colored badge. Never print a raw Signal string in tables, cards, cooling rows, PPO, or the appendix. Colors are fixed below and must match the scorecard badges.


**v11 changes vs v10:**
- Week Ending / market-climate banner is indented to match the report body (same left margin as sections).
- No blue-on-black body or label text. Section eyebrows, banner kickers, and similar labels use amber (`var(--amber)`) instead of the previous purple/blue accent. Signal badges keep their fixed colors (including MATURE blue on dim) because they sit on a contrasting fill.
- Banner data sources are binding: follow `Week_Ending_Banner_Sources.md`. Include Brent alongside WTI. Name every source actually used (or any remaining n/a) in the footer.
- Section 08 ChartLists now include two additional paste blocks for PPO HIGH CONVICTION names whose parent Theme Signal is EARLY ROTATION or MATURE LEADERSHIP only (comma and Python formats).

**v10 changes vs v09.1:**
- Report order: **07 Sub-Theme Appendix** then **08 ChartLists** (old 07 and 08 swapped).
- ChartList A is renamed **High Conviction**.
- Four paste blocks in Section 08: **High Conviction**, **High Conviction - Python**, **Early Sub-Themes**, **Early Sub-Themes - Python**.
- High Conviction lists = unique `PPO_Candidates` tickers with `Setup == HIGH CONVICTION` (same order as the PPO table).
- Early Sub-Themes lists = unique tickers printed in Section 07 (old Section 08), in first-appearance order across the EARLY appendix rows.
- Comma format: `DGII,IRDM,NVEC`
- Python format: `'DGII', 'IRDM', 'NVEC'`

---

## 1. Source of truth

Read the five pipeline files. Never recompute theme or sub-theme aggregates from the ticker file.

| File | Use |
|---|---|
| `Theme_Summary_<date>.csv` | Scorecard |
| `SubTheme_Summary_<date>.csv` | Sub-theme appendix + Tier 1/2 sub-theme tables |
| `Tickers_Themes_SubThemes.csv` | Name selection (returns are **fractions**) |
| `PPO_Candidates_<date>.csv` | PPO section + High Conviction ChartLists (`HIGH CONVICTION` only) |
| `run_manifest_<date>.json` | Date, counts, coverage, weight-cap |

- Summary returns are already **percent**. Ticker-file returns are fractions.
- Date from `data_as_of`. File: `Weekly_Theme_Rotation_<YYYY-MM-DD>.html`.
- Universe counts from the manifest only.

**Name selection rule.** Top 5 (theme cards, scorecard notes, EARLY appendix) and top 3 (sub-theme tables) are the unique tickers in that theme or sub-theme with a valid 1W, ranked by `1W Price Change %` descending. Do not substitute the cap-weighted `Top Name` for this list. Still print `Top Name` as the cap leader, wrapped in `<b class="tk">`.

**Theme-card ownership (binding).**
- Section **02 Tier 1** and **03 Tier 2** use the same card machinery.
- The sub-theme table inside a card is filtered `SubTheme_Summary.Theme == card theme` (exact string). Never copy, inherit, or append another parent’s rows.
- One table per card. Do not concatenate tables. Do not leave a table outside its `tc-body`.
- Sort sub-theme rows EARLY → MATURE → MIXED → FAILED, then Acceleration pp descending.
- Build each card as a closed HTML block (`tier-card` → `tc-body` → top-5 line → **that theme’s** table → close) before starting the next card.

**Ticker paint.** Any mention of a ticker — prose, cap leader, top-5 line, sub-theme top 3, scorecard notes, PPO first column, cooling table, appendix — is `<b class="tk">TICKER</b>` (amber). Do not leave a raw symbol in body text. ChartList paste blocks are the exception: plain symbols, no `b.tk`.

**Ticker find (binding UI).** Sticky `.tk-find` bar under the report header. Exact-symbol search against every `b.tk` **except Section 08 ChartLists**. Hits highlight (`b.tk.tk-hit` / `.tk-current`), list section + context, and jump with Prev/Next or Enter (Shift+Enter reverse). Escape clears. Do not strip `b.tk` — the finder depends on it.

---

## 2. Weighting

Lead with equal-weighted when `Mega Cap Distorted` (`|Distortion pp| > 1.5`). Always print both. Do not call leadership or breakdown on cap-weighted alone. Flag a `Top Name` that does not belong. `Effective N` is how many names the theme really is.

---

## 3. Signals (from the `Signal` column)

| Signal | Criteria |
|---|---|
| EARLY ROTATION | 1W ≥ +1.5%, 1M in [−6, +6], 1W > 1M/4.3, breadth ≥ 55%, \|distortion\| ≤ 1.5pp, 3M ≥ −12%, EqWtd 1W > 0 |
| MATURE LEADERSHIP | 1M ≥ +12%, or 3M ≥ +15% with a positive week |
| FAILED ROTATION | 1W ≤ −1.0% **or** breadth ≤ 40% |
| MIXED / CONSOLIDATING | Else |
| INSUFFICIENT DATA | Missing 1W or 1M |

Overrides must name the evidence column. Rank inside a bucket by `Acceleration pp`.

Default stars: EARLY → ⭐⭐⭐ · MIXED with intact structure or MATURE that is still holding → ⭐⭐ · extended / speculative / unconfirmed MIXED → ⭐ · FAILED → 🔴

### 3.1 Signal color (binding)

Every Signal in the report is a `<span class="badge badge-…">`. Do not leave unstyled Signal text in:

- scorecard `.sc-head-row`
- tier-card `.tc-sub` and `.tc-header`
- in-card `.subtbl` Signal column
- cooling table prior / current Signal columns
- PPO **Signal** column
- Section 07 appendix

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

---

## 4. Down-day

Use measured `Down Day Capture` vs SPY down sessions. Do not use 1W breadth as resilience.

- “Held up during weakness” = low/negative capture + breadth intact + above 30W EMA.
- “Buyable on pullback” = high capture + positive 3M + rising 30W EMA.

---

## 5. PPO Reset Candidates

Source: `PPO_Candidates_<date>.csv`. State file fields as facts. Readings as of the as-of close; they drift intradaily. **No quality filter.**

**Parent Signal on every row.** `PPO_Candidates` has no `Signal` column. Join each row’s `Theme` to `Theme_Summary.Signal` (exact theme name). Print that Signal next to the ticker as the same badge used on the scorecard (`badge-early` / `badge-mature` / `badge-hold` / `badge-cool`). If a ticker appears on more than one PPO row, each row keeps the Signal of *that row’s* Theme. Do not invent a ticker-level signal.

**WATCHLIST is omitted.** Filter `Setup == HIGH CONVICTION` before rendering. Do not print a WATCHLIST table, a second `ticker-table`, a `.ppo-card.watch` block, or a fifth ChartList. Mentions of WATCHLIST in the use-note may say only that it is omitted.

**Section header — paste this use-note under the title, before the table:**

> Theme first, setup second. HIGH CONVICTION is an entry queue, not a buy list. Work a name only when its parent Signal is EARLY, a constructive MIXED, or a hold-MATURE. A HIGH CONVICTION row inside FAILED is a stock trying to work in a group that is not — half-size probe or skip. Daily PPO near zero and turning up is the trigger; capture &lt; 1.0 means it held up on SPY down days (can pay up a little); capture ≥ 1.0 is buyable only on a pullback.

**Table columns (fixed order):** Ticker · Theme · **Signal** · 1W · 1M · vs 30W EMA · Daily PPO · Weekly Hist · RS 1M · Vol 20/60 · Down-day capture.

Sort HIGH CONVICTION EARLY → MATURE → MIXED → FAILED, then by `Pct vs 30W EMA` descending.

---

## 6. Report order

1. Header
2. **Market climate.** A full section under the header, indented to the same left margin as the report body sections. Render as a `.banner-list` of bullets. Data sources are binding — see `Week_Ending_Banner_Sources.md`. Include Brent oil in addition to WTI. Each bullet is one indicator: **label — level (1W change). One sentence on what changed during the week.**

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

Banner indicator titles (`.bl-name`) are `var(--amber)`, 16px, bold. Banner kicker and section eyebrows also use `var(--amber)` — never blue or purple accent on the dark background.
   - **WTI** (EIA Cushing spot preferred)
   - **Brent** (EIA Europe spot)
   - VIX
   - **MOVE**
   - **ICE BofA US HY OAS** (`BAMLH0A0HYM2`)
   - OPEX / positioning note when the week includes quarterly or monthly options expiration

Levels as of `data_as_of`. Weekly change vs the prior Friday close. Missing print → `n/a` and name it in the footer.

### Executive Summary (binding)

- Do not print “Weight-cap not applied” or the manifest universe ticker count in Section 01.
- Bullet points under the lead paragraph are indented (margin-left ≈ 28px).
- List every EARLY ROTATION theme by name, ranked by Acceleration pp descending.

3. **01 Executive Summary** — short lead + **bullets**. Example tickers in `<b class="tk">TICKER</b>`.
4. **02 Tier 1** — each card: thesis paragraphs, then **Top 5 by 1W** in amber `b.tk`, then **that theme’s** sub-theme table (Signal **badge**, eq 1W / 1M, breadth, top 3 tickers). Same table is required here, not only in Tier 2.
5. **03 Tier 2** — identical card machinery. One parent, one table. Do not show only the cap-weighted `Top Name`.
6. **04 Cooling / Downgrades** — prior and current Signal cells are badges, not raw text.
7. **05 Theme Scorecard** — omit any theme already written up in Section 02 or 03. Remaining non-FAILED rows are visible. Remaining FAILED rows sit in one collapsed `<details>` block. Notes include the five highest-1W tickers in amber. Label `Top Name` as **Highest Market Cap**. Sub-theme table header `Brd` is **Breath**. Spell Effective N as diversification: how many names the cap weights actually represent.
8. **06 PPO Reset Candidates** — HIGH CONVICTION table only. Parent Signal joined from Theme_Summary and painted as a badge.
9. **07 Sub-Theme Appendix** — EARLY only, top 5 by 1W. Signal on each row is `badge-early`. One `<li>` per line at the same indent as earlier lists. These names feed the two Early Sub-Themes ChartLists in Section 08.
10. **08 ChartLists** — six paste blocks. Indent the section the same as 01–07 (`section` → 2-space children → 4-space lists). See §6.1.
11. **09 Change Log vs Prior Week** — same indent as Section 01 lists.
12. Footer — methodology, manifest data-quality, banner sources, not-advice.

Nav links: `07 Sub-themes` then `08 ChartLists`.

### 6.1 ChartLists (Section 08) — binding

Six `.chartlist-box` blocks, in this order. Title is the first line inside the box. Tickers on the next line(s). No `b.tk` inside a paste block.

**1. High Conviction**
- Source: same unique tickers as the Section 06 PPO table (`Setup == HIGH CONVICTION`), same sort order.
- Format: comma-separated, no spaces after commas preferred, no quotes.
- Example: `DGII,IRDM,NVEC`

**2. High Conviction - Python**
- Same tickers, same order as High Conviction.
- Format: single-quoted symbols separated by comma-space.
- Example: `'DGII', 'IRDM', 'NVEC'`

**3. High Conviction - Early/Mature**
- Source: subset of the High Conviction list above whose parent Theme Signal is EARLY ROTATION or MATURE LEADERSHIP only.
- Preserve the same relative order as the full High Conviction list.
- Format: same as High Conviction (`DGII,IRDM,NVEC`).

**4. High Conviction - Early/Mature - Python**
- Same tickers, same order as High Conviction - Early/Mature.
- Format: same as High Conviction - Python (`'DGII', 'IRDM', 'NVEC'`).

**5. Early Sub-Themes**
- Source: every ticker printed on Section 07 EARLY appendix rows (the top-5 names on each EARLY sub-theme line).
- Deduplicate by first appearance, walking rows top to bottom, names left to right.
- Format: same as High Conviction (`DGII,IRDM,NVEC`).

**6. Early Sub-Themes - Python**
- Same tickers, same order as Early Sub-Themes.
- Format: same as High Conviction - Python (`'DGII', 'IRDM', 'NVEC'`).

Do not add a WATCHLIST ChartList. Do not label any block “ChartList A” or “ChartList B”.

Lead-in under the Section 08 title:

> Six paste lists. High Conviction = all PPO HIGH CONVICTION names. High Conviction - Early/Mature = the subset whose parent Signal is EARLY or MATURE. Early Sub-Themes = unique names from the Section 07 EARLY appendix. Python blocks are the same names wrapped for a Python list.

---

## 7. Scorecard mechanics

Two-zone `.sc-row`. Sort visible rows rating desc, then Acceleration pp desc. Same sort inside the FAILED disclosure.

Flags only when Mega Cap Distorted. Color EqWtd sign on return tiles. Down-day green if capture < 1.00.

Notes 2–5 sentences (~40–90 words) plus the high-scoring ticker line. Override in sentence one.

Prior-week breadth: from last run. If missing, drop the arrow and the “was” line; say so in the footer.

---

## 8. Type scale

Body 18px. Header h1 30px. Section title 24px. `.sc-theme` 18px. `.sc-m-val` 16px. `.sc-note` 16px. `.mkt-val` 17px.

Tickers: bold + `var(--amber)` via `b.tk`. ChartList paste text stays green mono (`.chartlist-box`).

CSS = v08 block + `.tk-row` + `.subtbl` for the in-card sub-theme tables + `<details.failed-block>` styles + §3.1 badge colors.

---



### Nav links (binding)

The sticky `.tk-find` bar is also indented to the same margin and its label uses `var(--amber)`.

Report navigation (`.report-nav`) is indented to the same left margin as the report body (`max-width: 1600px; margin: 0 auto; padding: 0 32px`). Link color is `var(--amber)`, never default browser blue or purple accent. Hover may lighten to `var(--head)`.

### Banner indent and label color (binding)

```css
.market-banner { max-width: 1600px; margin: 0 auto; padding: 22px 32px 8px; }
.market-banner .banner-kicker,
.section-eyebrow { color: var(--amber); }
```

Never use `var(--accent)` or blue for labels/eyebrows/kickers on the dark background.

## 9. Standing rules

Completed data only. Down days are signals. Favor second-order beneficiaries. Explain rating changes vs prior week. Missing figure → say so. “Update” = full new HTML against newest files. No quality/value exclusion step. No WATCHLIST in the published report. No uncolored Signal string in any table or card header. ChartLists are six labeled paste blocks; never “ChartList A”.
