#!/usr/bin/env python3
# =============================================================================
#  momentum_unified_v56.py
#  Unified Momentum · Squeeze · Buy/Sell Signal Monitor
#
#  v56 (display only: no scoring change; the Themes tab is untouched):
#    1) THEME SIGNALS TAB (new, after Themes): reads the weekly file Weekly_Theme_Signal.csv
#       (Config.theme_signal_csv) - Theme / Sub-Theme / Signal / Stars / Theme Breadth /
#       Sub-Theme Breadth - and shows it Theme -> Sub-Theme -> Ticker with breadcrumbs. It is
#       fully separate from the Themes tab: no Theme Score, no shared state, no links either way.
#       Tickers under a Sub-Theme come from the theme membership file (Config.themes_csv),
#       primary and secondary assignments (secondary ones are labelled). The tab badge counts the
#       Early Rotation sub-themes. A banner appears when the file is missing or older than
#       Config.theme_signal_stale_days. Inserting the tab moves the 7 / 8 / 9 number keys by one.
#
#  v55 (display only: no scoring change):
#    1) SIGNALS TABLE: Ticker / Theme / Signal columns tightened (table sizes to its content) so the
#       other columns sit further left.
#    2) QUALITY COLUMN: the Quality Score now shows next to Signal in every ticker table that has a
#       Signal column (dash when the ticker has none).
#    3) VOLUME CHART (Ticker page): high / low volume bars are green on up days, red on down days.
#    4) BONDS TAB (new): US Treasury yield curve (3M, 6M, 1Y, 5Y, 10Y, 20Y, 30Y) for today, 1 week,
#       1 month, 3 months and 1 year ago (FRED, Yahoo fallback, cached in treasury_cache.json), plus a
#       Bond ETF list (Config.bond_etfs: BND, EDV, ZROZ, BSV, VCSH, VGIT, VCIT, BLV, VGLT, VTEB, VTIP)
#       built like the ETFs tab.
#
#  v54 (methodology AND display: items 1, 4 and 5 DO change scores, regimes and signals):
#    1) MOMENTUM IS RANKED AGAINST YOUR UNIVERSE, NOT AGAINST SPY'S HISTORY. Each Trailing / Emerging
#       input is ranked across every name loaded on the same date (0-100). Returns are first divided by
#       the name's own 63-day volatility (floored at 8% a year) and the PPO histogram by ATR%, so a
#       volatile stock is no longer Strong or Weak just for moving more. The "Mom %" column is now
#       "RS Rating" (1-99). Dates with fewer than xs_min_names (30) names, and the Currency group, keep
#       the old anchor. The rank is RELATIVE: about half the list is always above 50, so the EMA200 gate
#       and the Market gate carry the absolute test. Config: pctile_anchor ("universe" | "benchmark"),
#       vol_adjust_momentum, vol_adj_window, vol_adj_floor_ann, xs_min_names.
#    2) IN TREND STATE (display only; Signal is unchanged). Opens on a Favorable alert, stays open until
#       an Unfavorable / Conflicted alert or a close under a trailing stop (highest close - 3 x ATR since
#       entry; never moves down). New "In Trend" and "Stop" columns on every Signals-style table, an
#       "In trend" filter, the stop drawn on the Ticker price chart, and a volatility-based "Suggested
#       size" on the Ticker page and drawer (1% portfolio risk / stop distance, capped at 10%).
#       Config: trend_state, trend_stop_atr_mult, risk_per_trade_pct, max_position_pct.
#    3) SCORECARD: (a) gate attribution - forward returns of the Favorable ratings each gate BLOCKED vs
#       those that passed; (b) calibration - forward return by POS / NEG score bucket; (c) "Dates" and a
#       95% range built from per-date averages on every row, because clustered signals overstate N;
#       (d) trend-trade record for item 2; (e) OUT-OF-SAMPLE record read from the dated snapshot CSVs
#       (the signals actually published each day). Config: scorecard_snapshots, snapshot_max_files,
#       score_buckets.
#    4) MARKET GATE REBUILT ON TREND AND BREADTH. The "SPY regime" gate no longer reads SPY's own
#       momentum regime (Mature/Cooling could close it in a steady uptrend). It now closes when SPY and
#       RSP are both under their 200-day EMA, OR fewer than 40% of your stocks are above their 200-day
#       AND fewer than 40% above their 50-day. New "Market gate" card on Market Health: state now, the
#       inputs, a day-by-day open/closed strip and the share of sessions closed. The Blocked-by label is
#       still "SPY regime". Config: market_gate_mode ("breadth" | "legacy" = v53 rule),
#       gate_breadth_200_min, gate_breadth_50_min, gate_breadth_min_names.
#    5) SYMMETRIC POS / NEG SCORING. One volatility discount, 1 - 0.65 x (1 - reliability), on both sides
#       (before: full discount on POS, a much lighter one on the NEG PPO points). A fresh bullish cross
#       still in force now gets a floor of 30, mirroring the bearish floor, and the bearish floor also
#       needs the cross still in force. Trend Persistence uses 60 sessions instead of 20 and its weight
#       in Emerging drops 0.20 -> 0.10 (PPO_Delta 0.25 -> 0.30, Momentum_Blended 0.20 -> 0.25).
#       Config: symmetric_scoring (False = v53 behaviour), vol_damping, buy_cross_floor, persist_window.
#    Also: the Shortlist self-test no longer fails when a shortlist name sits in a fund list (EWY).
#    FUNDAMENTALS ROW (display only, added 2026-11-12): the Ticker page shows Quality Score, CROIC,
#    Number of Profitable Qtrs in the last 20 quarters (Gross Profit / Net Profit), OI/Debt,
#    Shares Chg 3Y, Implied Growth and Piotroski F-Score above the price chart. Read from the "Score"
#    tab of the Google Sheet (Config.fundamentals_url), falling back to a local copy
#    (Config.fundamentals_csv = Score.csv beside this script). Names not in the sheet show no row.
#
#  v53:
#    1) MARKET-REGIME GATE NOW NEEDS SPY *AND* RSP TO FAIL. Before, SPY alone being Unfavorable (or
#       Weak / Mature/Cooling) blocked every Favorable rating. Now the gate only closes when BOTH the
#       benchmark (SPY) and the equal-weight S&P (RSP) are weak on the same bar; if only one of them is
#       weak the market is treated as mixed and Favorable ratings are not blocked. Applied to the live
#       panel and to every historical bar (Scorecard / chart markers). If RSP has no data the gate falls
#       back to SPY alone and says so on the Health tab. Config: regime_need_both (True), regime_confirm
#       ("RSP"). The Blocked-by label is still "SPY regime". Country ETFs and Currency funds are still exempt.
#    2) PPO TAB SPLIT INTO SUB-TABS. "All PPO" (the three tables as before), "Watch Favorable" and
#       "Watch Unfavorable" (each lists the names with that Signal and its PPO state). The combined
#       "Favorable / Unfavorable" filter on the crossover table is now two filters, Favorable and Unfavorable.
#
#  v52 (display only: NO score, threshold, gate or alert changed):
#    1) OVERVIEW TAB DELETED. Its KPI strip, the Favorable / Unfavorable / Watch action board and the
#       "Favorable vs Unfavorable count" chart are gone (Signals, Changes and the Ticker page still carry
#       every one of those names).
#    2) MARKET HEALTH now also holds what was on Overview:
#         - the SPY, QQQ and NEW RSP (equal-weight S&P) cards, under the main chart;
#         - four charts: Breadth (% of stocks above EMA200), Net Signals distribution, Regime
#           distribution, RSI(14) distribution (click a Regime bar to open Rankings, as before).
#    3) BREADTH is now measured on YOUR stocks, from the prices the dashboard already downloads. It no
#       longer needs the S&P constituent list, so it cannot fail when the holdings download does. ETFs,
#       index funds, sector / six pack / country / currency funds and anything Yahoo does not call an
#       EQUITY are left out (Config.breadth_exclude + a cached Yahoo quote-type lookup written to
#       quote_types_cache.json). Every "S&P" tag on the breadth cards is gone: the cards say "stocks" and
#       show how many were counted. It measures your list, not the whole market.
#    4) CONCENTRATION card removed (AI share of the S&P and the ten largest companies). The index weights
#       are still downloaded, but only to build the $SPXXAI line.
#
#  v51 (display only: NO score, threshold, gate or alert changed):
#    1) Market Health: NEW "Breadth over time" card under the main chart (follows the same 1W..1Y buttons):
#       A/D line (cumulative advancers minus decliners) plus % of S&P stocks above their 20/50/200-day.
#       Built from the SAME S&P stock download the breadth tiles already use (no extra download). Uses
#       today's members, so it approximates the official NYSE A/D line.
#    2) $SPXXAI line: if the live S&P weights AND the cached copy are both unavailable, the line is now drawn
#       from rounded APPROXIMATE weights of the ten AI names (flagged in the yellow note) instead of vanishing.
#       Concentration (top 10) and breadth tiles are skipped in that case, since they need the full list.
#
#  v50 (display only: NO score, threshold, gate or alert changed):
#    1) Sectors, ETFs, Tear's Short List, Frank's Short List, Country ETFs and Currency now use the
#       Signals page layout: same 19 columns, same filter buttons, same note. The KPI strip and the
#       Favorable/Neutral/Unfavorable card board were removed. Currency keeps USD read, rho SPY / rho UUP
#       and a one-line USD view above the table. Six Pack is unchanged.
#    2) Goldman's Picks tab deleted (tab, section, Rotation button, payload). Config.goldman_tickers is
#       kept only so those names stay in the data pull.
#    3) Market Health, Breadth and Concentration: both depended on ONE download (the State Street SPY
#       holdings .xlsx, which also needs openpyxl, missing from requirements.txt). Now: State Street ->
#       iShares IVV CSV -> last good copy cached in mh_weights_cache.json. The tab prints the reason for any
#       failure instead of "did not load".
#
#  v49 (display only: NO score, threshold, gate or alert changed):
#    NEW FIRST TAB "Market Health" (ported from github.com/hayesfj/the-whole-market):
#      1) "The S&P (SPX) and the market under it": SPX vs equal-weight (SPXEW), the S&P with the big AI
#         stocks removed ($SPXXAI), QQQ and optional IWM, all rebased to 100, with 1 week / 1 month /
#         3 months / 6 months / This year / 1 year views and a return tile per line for the chosen view.
#      2) Sectors against the S&P: 63-session correlation of each sector ETF with SPX vs its 10-year average.
#      3) Breadth (5-day new highs/lows, % above 20/50/200-day) and Concentration (AI share, top 10).
#    Needs `openpyxl` (SPY holdings file) in addition to requirements.txt. If any Market Health download fails
#    the tab shows a message and the rest of the dashboard is unaffected. Opens on this tab by default.
#
#  v48 (display only: NO score, threshold, gate or alert changed):
#    1) "Overall Momentum" is now called SIGNAL everywhere (column headers, KPI, narrative, Guide).
#       Values (Favorable / Watch Favorable / Neutral / Watch Unfavorable / Unfavorable) are unchanged.
#    2) SORT: Signal is the active sort on load in the Signals table and the Themes ticker list
#       (the other Signal tables already were). Inside one Signal category the highest signed
#       Net Bias comes first, whichever way the header is sorted. The Signals table no longer
#       uses the old |Net Bias| default, so -23 no longer ranks level with +23.
#    3) WATCH BADGE (the pill beside the regime on the cards) is green for Watch Favorable and red
#       for Watch Unfavorable (Watch both sides stays blue). Same colours as the Signal column.
#    4) CARDS (Favorable / Neutral / Watch / Exit boards on the sector, ETF, country, ... tabs): the
#       top-right "POS/NEG" pair on Neutral / Watch / Exit cards is replaced by the signed Net Bias, and
#       the bottom line reads "Net Bias +24 . POS 24 . NEG 0" with the Net figure in bold and
#       coloured by sign. The Changes-tab cards get the same bold Net Bias.
#    5) TICKER TAB VOLUME CHART: bars are coloured by share volume vs its rolling median
#       (Config.vol_rel_bars = 20): >= Config.vol_rel_hi (1.5x) bright, < Config.vol_rel_lo (0.7x)
#       faded, otherwise grey. A dashed median line is drawn over the bars, a one-line key sits
#       under the chart and hovering a bar shows its volume and the ratio.
#    6) HEALTH TAB no longer lists "Duplicate ticker 'X' removed from the universe" notes
#       (duplicates are still removed; the console message is unchanged).
#
#  v47 (display only: NO score, threshold, gate or alert changed):
#    1) REGIME is now labelled "Trailing/Emerging Momentum" everywhere it is shown. The values
#       (Strong, Dormant→Waking, Neutral, Mature/Cooling, Weak) and all logic are unchanged;
#       the Python/CSV column is still called Regime.
#    2) RECOMMENDATION is now shown as OVERALL MOMENTUM with five levels:
#         BUY alert                         -> Favorable
#         HOLD + Watch BUY (incl. gated)    -> Watch Favorable
#         HOLD, no watch (and EXIT)         -> Neutral   (EXIT keeps an amber badge: "conflicted")
#         HOLD + Watch SELL                 -> Watch Unfavorable
#         SELL alert                        -> Unfavorable
#       It is a relabelling of the existing alert logic. Internally rec/watch are unchanged, so
#       the scorecard, Changes tab and CSV still key off BUY/SELL/EXIT/HOLD.
#    3) NEW PPO TAB with three tables: signal-line crossovers (bullish / bearish, bars ago, still
#       in force), histogram direction (positive/negative x rising/falling) and zero-line crosses
#       (above / below). Payload gains bz_pos / bz_neg (bars since a zero-line cross).
#
#  v46 (signal-logic fixes; these DO change signals):
#    1) Config.validate() now compares sell_cross_floor with the LOWEST per-regime sell threshold
#       (not just the global 40), and the floor drops 35 -> 30. At 35 a lone fresh bearish cross
#       auto-fired SELL in Mature/Cooling and Weak (threshold 35).
#    2) The RSI-Extreme Buy cap is now (regime + ATR threshold - 1) per row. It used the global
#       40 - 1 = 39, which still cleared the 35 threshold of Strong and Dormant->Waking.
#    3) A PPO cross only triggers while it is still in force: BUY needs PPO histogram > 0, SELL
#       needs < 0. EXIT is now detected as a whipsaw (fresh up-cross AND fresh down-cross in the
#       window, both scores over threshold, within conflict_margin), since the signed triggers can
#       no longer both be true on one bar.
#    4) The post-score gates (SPY regime, relative strength, EMA200, top filter) are applied to
#       EVERY historical bar (apply_gates_history), so the Scorecard, Ticker-chart markers, breadth
#       counts, Changes tab and pinned live alerts all come from the same gated system as the panel.
#    5) Version strings: VERSION, filename, usage text and default output name all say v46.
#
#  v45:
#    • NEW GOLDMAN'S PICKS TAB: built exactly like Frank's Short List (Buy / Hold / Sell / Exit
#      board, sortable table with Theme and Sub-Theme, Rotation button, tab count). The list lives
#      in Config.goldman_tickers (CEG, VST, TLN, GEV, BE, VRT, ETN, ANET, SMCI, MSFT, AMZN, NVDA,
#      AVGO, AMD, CRWD, PANW, ZS). Names stay in the universe and every other tab.
#    • Display only: no score, alert or recommendation changed.
#
#  v44:
#    • HEADER: "For information only. Not Investment Advice." and "Copyright © Frank Hayes"
#      now sit under the Watchlist Momentum title. The same line is also in the page footer
#      (the header is hidden when printing) and at the top of the stand-alone Ticker HTML export.
#    • CHARTS: every line chart now repeats its Y-axis labels on the right side as well as the
#      left (the right margin matches the left, so the plot stays centred). Histogram, bar and
#      Rotation charts are unchanged.
#
#  v43:
#    • COUNTRY ETFs: (1) lower liquidity floor for the group, Config.country_min_dollar_vol
#      ($1M; stocks stay at $5M), so thinly traded country funds can alert; (2) the SPY
#      regime gate is skipped for the group (a country can trend independently of the US).
#      The relative-strength-vs-SPY gate and the below-EMA200 gate still apply.
#    • CHARTS: the legend is no longer cut off at the top (charts with a legend get extra top
#      margin) and the legend items are spaced further apart.
#    • TICKER TAB: Momentum percentiles chart: Trailing is now blue, Emerging yellow.
#    • Display / group handling only: no score or threshold changed.
#
#  v42:
#    • NEW CURRENCY TAB: Invesco CurrencyShares trusts (FXE euro, FXY yen, FXB pound,
#      FXF franc, FXA Aussie, FXC Canadian, FXS krona, FXM peso) plus UUP (the dollar
#      itself) as a reference row. They are a view on the US DOLLAR, not on SPY, so a
#      BUY on a currency fund reads "dollar weakening" and a SELL reads "dollar
#      strengthening". The tab has the usual Buy / Hold / Sell / Exit board and table,
#      a "USD view" summary (average and DXY-weighted net bias, UUP cross-check), a
#      "USD read" column and 60-day return correlations to SPY and UUP (hedge fit:
#      negative vs SPY = a hedge, positive = moves with equities).
#      The list lives in Config.currency_etfs (+ Config.currency_ref for UUP).
#    • SCORING FOR THE GROUP (the Buy/Sell logic itself is unchanged):
#        1) percentiles are anchored to the currency group's OWN pooled history instead
#           of SPY's (currency funds run at ~6-10% vol and would otherwise all sit mid-
#           percentile and never reach Strong / Weak). Config.currency_own_anchor.
#        2) the SPY-regime and relative-strength-vs-SPY gates are skipped for the group
#           (they say nothing about the dollar); the below-EMA200 gate still applies.
#        3) the liquidity floor is Config.currency_min_dollar_vol ($1M) for the group.
#    • These funds are left out of Rotation > All / regime buttons / Alerts, the Themes
#      aggregates and the "not in Theme file" list; Rotation has a "Currency" button.
#    • Guide: new "Currency tab" section; Gates section notes the group exemptions.
#
#  v41:
#    • GATE VISIBILITY: a BUY that the post-score gates (SPY weak-market, relative
#      strength vs SPY, below EMA200) convert to HOLD is no longer silent. It now gets
#      Watch = BUY and a Gate_Block reason, shown as a "Blocked by" column and a W
#      badge tooltip on every tab, as "Blocked BUY" / "Candidates" filters on Signals,
#      in the Overview watch cards, the Ticker narrative, and as a list on the Health tab.
#      Names that cleared the Buy threshold but failed a bar-level requirement inside
#      the score (no fresh cross, volume / close-location bar, liquidity) are labelled too.
#    • FRESH CROSS WINDOW: Config.ppo_fresh_bars 2 -> 3 (a PPO signal-line cross now counts
#      as fresh for 3 bars; this also widens the zero-line cross bonus and the sell floor).
#    • GUIDE: new "Gates" section that explains every gate, its exemption and its Config
#      switch, and what a Blocked BUY means.
#    • FIX: while the market is open, live tickers had their recommendation pinned to the
#      previous bar WITHOUT the gates. The gates are now re-applied after pinning.
#    • Scores, thresholds and the gate rules themselves are unchanged.
#
#  v40:
#    • SHORTLIST TAB RENAMED: the Shortlist tab (and its heading, Rotation button and
#      notes) is now "Frank's Short List". Config.shortlist_tickers is unchanged.
#    • TICKER TAB: the Trailing line on the Momentum percentiles chart is now yellow.
#    • RANKINGS TAB: new Bias column (Buy - Sell confidence), sortable, after Sell.
#    • Display only: no score, alert or recommendation changed.
#
#  v39:
#    • TICKER EXPORT + GUIDE: the stand-alone TICKER_YYYY_MM_DD.html file now ends with
#      the full Interpretation Guide (Recommendation / Regimes / Squeeze pillars / PMO /
#      Daily workflow, the Buy & Sell Score tables built from the live config, and the
#      Themes Theme-Score section), placed after the Ticker page under its own heading.
#      The guide is copied from the rendered Guide tab, so the exported file stays
#      self-contained (inline SVG / static HTML, no scripts, no history file, no network)
#      and the guide text cannot drift from the dashboard.
#    • Self-test fix: the Shortlist check no longer hard-codes 15 names (the list has 16).
#    • Nothing else changed: no score, alert, recommendation or other tab differs from v38.
#
#  v38:
#    • DOWNLOAD RETRY: v37 (and earlier) sent the whole universe to Yahoo in ONE
#      batch request and only fell back to per-ticker when the entire batch failed.
#      When Yahoo throttled or dropped part of a large batch, every missing name was
#      skipped for good (LLY, SNPS, PM ... on a normal run). Now:
#        1) the pull is split into chunks (Config.yf_batch_size, default 100);
#        2) tickers that come back missing / empty are retried in smaller chunks
#           (Config.yf_retry_rounds rounds, with a growing pause);
#        3) anything still missing is fetched one at a time;
#        4) only tickers that fail all of that are skipped, with the reason on the
#           Health tab, and a note records how many were recovered.
#    • Scoring, alerts and the dashboard are unchanged.
#
#  v37:
#    • NEW SHORTLIST TAB: a second carve-out list, built exactly like Tear's Short
#      List (Buy / Hold / Sell / Exit board plus a sortable table with Theme and
#      Sub-Theme columns, a Rotation button, and a tab count). The list lives in
#      Config.shortlist_tickers (GEV, PRDO, BE, PWR, ASML, VRT, LITE, COHR, AVGO,
#      FIX, VIAV, VICR, BUG, CRDO, PENG). Names stay in the universe and every other
#      tab; names also in the Tear list / ETF list simply appear on both tabs.
#      validate() adds any list name missing from the data pull.
#    • Display only: no score, alert or recommendation changed.
#    (v36 gate changes - above-EMA200 BUY gate, stronger top filter - are unchanged.)
#
#  v35:
#    • NEW TEAR'S SHORT LIST TAB: your 39-name short list carved out for special
#      emphasis, laid out like the ETF tab (Buy / Hold / Sell / Exit board plus a
#      sortable table with Theme and Sub-Theme columns). The list lives in
#      Config.tear_tickers. Unlike the ETFs these are ordinary stocks: they stay
#      in the universe, in every other tab, in Rotation > All and in the Themes /
#      Sub-Themes aggregates. Names that are also in Config.etf_tickers (e.g. KOID)
#      appear on both tabs. validate() adds any list name that is missing from the
#      data pull.
#    • ROTATION: new "Tear's Short List" button plots those names on their own.
#    • Display only: no score, alert or recommendation changed.
#
#  v34:
#    • TICKER TAB: new "Export HTML" button. Downloads the Ticker page you are
#      looking at as ONE stand-alone .html file named TICKER_YYYY_MM_DD.html
#      (e.g. NVDA_2026_10_15.html). Charts are inline SVG, so the file needs no
#      history file, scripts or network and can be emailed or archived as is.
#      (v33's print-to-PDF button is replaced.)
#
#  v32:
#    • UNIVERSE: new --universe both (or Config.universe_source = "both") = the
#      code list plus every ticker in the Theme file, de-duplicated.
#    • HEALTH: ETFs (Config.etf_tickers) are no longer listed under "Tickers not
#      found in the Theme file".
#    • CHANGES: now compare against the PRIOR SESSION'S CLOSE (the previous
#      trading day's bar, same gates applied), not the previous run's snapshot.
#    • THEMES: the ticker list of a sub-theme / theme is sorted by Net Bias,
#      highest first.
#
#  v31 (history split + website copy):
#    • EXTRA COPY: the dashboard is also written to Config.extra_html (default
#      G:\My Drive\Projects\SeriousDinero\WebSite\tools\watchlist-momentum.html),
#      with its own watchlist-momentum.history.js beside it. Upload both files.
#    • SEPARATE HISTORY FILE: the per-ticker history (the bulk of the dashboard)
#      is no longer embedded in the HTML. It is written next to it as
#      <dashboard name>.history.js and loaded with an ordinary <script src>, so
#      it still works when the HTML is opened straight from disk (file://),
#      where fetch() of a local JSON file is blocked by the browser. Keep the
#      two files together. The dashboard behaves exactly as before; if the
#      history file is missing or from a different run, a banner says so.
#      Use --inline-history to embed it in the HTML again (single file).
#
#  v30:
#    • SECONDARY THEMES: Assignment = "Secondary" rows of the Theme file are now
#      shown directly under the primary Theme > Sub-Theme (Overview cards, market
#      context, Ticker tab, drawer; the Theme column tooltip and the table filter
#      also cover them). Sub-themes are shown at normal strength, not muted.
#    • NEW THEMES TAB: Theme -> Sub-Theme -> Ticker drill-down with breadcrumbs.
#      Each theme / sub-theme gets a Theme Score (0-100) from its members:
#      Momentum 40% (median Mom percentile), Breadth 25% (% above EMA200, % bull
#      stacked, % PPO > 0), Signals 20% (average net bias), Acceleration 15%
#      (5-day change in median Emerging percentile and in net bias, plus median
#      20d return vs the benchmark). Medians are used so one outlier cannot drive
#      a theme. A 60-session score history is reconstructed for every theme.
#      Only PRIMARY assignments are counted in the aggregates; Sector / Six Pack /
#      ETF / Country ETF funds are left out. Themes with fewer than
#      Config.theme_min_members loaded names are greyed out ("n too small").
#    • ROTATION: new "Themes" and "Sub-Themes" choices (one bubble per theme at its
#      median trailing / emerging percentiles, with tails) and a theme picker that
#      plots the individual tickers of one theme.
#    • Display only: no score, alert or recommendation changed.
#
#  v29:
#    • UNIVERSE SOURCE: the ticker list can now come from the unique tickers in
#      Input_Ticker_List_by_Theme.csv instead of the list in the code. Switch
#      with --universe themes, or set Config.universe_source = "themes".
#      Default stays "list". BRK.B-style tickers become BRK-B for Yahoo; the
#      Sector / Six Pack / ETF / Country ETF lists are still merged in.
#
#  v28:
#    • NEW COUNTRY ETFs TAB: single-country ETFs (iShares / Global X / VanEck),
#      built like the ETFs tab. The list lives in Config.country_etfs
#      (ticker -> (country, full fund name)); validate() merges it into the data
#      pull and keeps those tickers out of the main list. Same scoring as every
#      other tab. Rotation gets a "Country ETFs" button; those funds are left out
#      of All, the regime buttons and Alerts only.
#    • FULL FUND NAMES: ETF and Country ETF names are never shortened - the
#      ellipsis cut-off is removed for them wherever they appear.
#    • Country ETFs use their COUNTRY as the Theme in the Signals / Squeeze /
#      Rankings tables, Ticker tab and drawer, and are not listed on the Health
#      tab's "not found in the Theme file" list.
#
#  v27:
#    • COMPANY NAMES: the "Company Name" column of Input_Ticker_List_by_Theme.csv
#      is now shown next to the ticker on Overview (cards and market-context
#      cards), Changes, Ticker, Signals, Rankings and Squeeze, and in the
#      ticker drop-down list and the Rotation hover pop-up. Display only.
#    • NEW ETFs TAB: a watchlist of specific ETFs, with its own list in the
#      code (Config.etf_tickers, seeded KOID, SMH, DRNZ, ARKG; separate from
#      Config.tickers, merged into the data pull by validate()). Same scoring
#      as every other tab. ETF names come from Config.etf_names (optional
#      overrides), then the Theme file, then a best-effort Yahoo lookup.
#    • ROTATION: new "ETFs" button plots those ETFs on their own; like Six Pack
#      and Sectors they are left out of All, the regime buttons and Alerts only.
#
#  v26:
#    • TICKER TAB (and the quick-view drawer): the ticker's Theme > Sub-Theme is
#      shown under the title.
#    • Sector ETFs and Six Pack ETFs use their SECTOR NAME / SIX PACK NAME as
#      the Theme everywhere a Theme is shown (Overview cards, market-context
#      cards, Signals / Squeeze / Rankings tables, Ticker tab, drawer). They no
#      longer appear in the Health tab's "not found in the Theme file" list.
#
#  v25:
#    • HEALTH TAB: new "Tickers not found in the Theme file" list (also printed
#      to the console at run time), so gaps in Input_Ticker_List_by_Theme.csv
#      are easy to spot and fill.
#    • THEME / SUB-THEME text on the Overview cards is larger.
#    • TICKER TAB: the RSI chart is now full width, the same size as the two
#      PPO charts. Buy / Sell confidence and Momentum percentiles sit side by
#      side below it, both the same size.
#    • THEME COLUMN: Signals, Squeeze and Rankings tables show the primary
#      Theme (only) right after the ticker; it is sortable and searchable.
#      The sector ETFs (not in the theme file) show their SECTOR NAME there.
#      Display only - no score, alert or recommendation changed.
#
#  v24:
#    • TICKER TAB: the Swenlin PMO chart now sits directly under the price
#      chart, and the PPO chart sits directly under the PMO at the same size
#      (full width, same height). The RSI / confidence / percentile charts
#      follow in their 2-column grid.
#    • THEMES: new input file Input_Ticker_List_by_Theme.csv
#      (Config.themes_csv). Each ticker's PRIMARY Theme and Sub Theme are
#      looked up and shown next to the ticker name on every Overview card
#      (Buy / Sell / Exit / Watch and the market-context cards). Tickers not
#      in the file (e.g. SPY, ETFs) simply show no theme. Display only - not
#      used in any score, alert or recommendation. A missing or unreadable
#      file only logs a warning.
#
#  v23:
#    • NINE BOX becomes SIX PACK: the Blend column is gone. Two style
#      columns (Growth / Value) x three cap rows (Large / Mid / Small):
#        Large: VOOG (growth)  VOOV (value)
#        Mid:   VOT   (growth) VOE  (value)
#        Small: VBK   (growth) VBR  (value)
#      VV, VO and VB are no longer pulled. The layout lives in Config.six_pack.
#    • ROTATION: "Six Pack" and "Sectors" are new choices on the Rotation tab.
#      Their ETFs are plotted only under those two buttons and are removed
#      from All, the regime buttons and Alerts only.
#    • TICKER LISTS: the Sector ETFs (Config.sector_names) and the Six Pack
#      ETFs (Config.six_pack) are now their own lists, separate from
#      Config.tickers. Config.validate() merges them into the data pull
#      (Config.tickers = main list + sectors + six pack, de-duplicated).
#      Config.core_tickers holds the main watchlist on its own.
#    • TICKER TAB: new chart for Carl Swenlin's Price Momentum Oscillator
#      (PMO 35/20 with a 10-period signal line). It is INFORMATIONAL ONLY -
#      it is not used in any score, alert or recommendation (--selftest
#      verifies that removing the PMO columns leaves every score unchanged).
#
#  v22:
#    • New NINE BOX tab: a 3x3 equity style box of nine Vanguard ETFs.
#      Columns = Growth / Blend / Value, rows = Large Cap / Mid Cap / Small Cap:
#        Large: VOOG (growth)  VV (blend)  VOOV (value)
#        Mid:   VOT   (growth) VO (blend)  VOE  (value)
#        Small: VBK   (growth) VB (blend)  VBR  (value)
#      Each cell shows the ETF's ticker, name, BUY/HOLD/SELL and scores, plus
#      a row/column summary and a sortable table. It reads the same scoring
#      as every other tab - nothing about the signals changed. The box layout
#      lives in Config.nine_box.
#
#  v21:
#    • New SECTORS tab: the 11 S&P 500 sector SPDR ETFs (XLK, XLV, XLF, XLY,
#      XLC, XLI, XLP, XLE, XLU, XLRE, XLB) on one page, each shown with its
#      ticker AND sector name, a Buy / Hold / Sell board, summary counts, and a
#      sortable table (scores, regime, trend, momentum rank, 20-day score
#      history). It reads the same scoring as every other tab — nothing about
#      the signals changed. Sector names live in Config.sector_names.
#
#  v20:
#    • Guide tab: new "Buy & Sell Score" section that explains every
#      component (PPO cross, RSI, EMA, Persistence/Weakness, Squeeze), its
#      point range and exact weighting, the per-regime weights, volatility
#      reliability damping, the sell floor, the per-regime alert thresholds,
#      and the gates an alert must pass. Regime weights, thresholds and caps
#      are read from the live config, so the guide cannot drift from the code.
#    • No change to scoring, alerts or data handling versus v19.
#
#  v19 and earlier (v19 notes were not carried in this header):
#
#  v18:
#    • Live intraday pricing: while the market is open, today's still-forming
#      bar is now used as-is instead of being dropped: its Close is the live
#      current price, and it flows through the exact same indicator/scoring
#      pipeline as any other day (Last_Close, RSI, PPO, EMAs, Buy/Sell
#      confidence, the dashboard — all reflect the current price). Previously
#      this bar was discarded while the session was open, so the dashboard
#      silently kept showing the prior day's close until the next day's
#      confirmed bar existed.
#    • Tickers priced this way are flagged everywhere (a green ● dot, a LIVE
#      badge on the Ticker tab and drawer, and a Health-tab line) so it's
#      always clear which numbers are live vs. a confirmed close. Pass
#      --eod-only to restore the old wait-for-close behaviour.
#
#  v17:
#    • New TICKER tab: a full single-name page — price with EMA20/50/200 and
#      BUY/SELL markers, PPO histogram, RSI, confidence & momentum-percentile
#      history (120 sessions), component breakdowns, peer rank within the
#      universe, a session log, and every past signal with its forward returns.
#      Deep-linkable (#ticker/NVDA); the drawer keeps the quick view.
#
#  v16 — a ground-up hardening of v15. What changed and why:
#
#  ROBUSTNESS
#    • No pandas_ta dependency. Every indicator (EMA, RSI, ADX/DMI, ATR,
#      Bollinger, Keltner, TTM Squeeze, OBV) is implemented natively and
#      vectorised, so the file runs on any numpy/pandas and computes ~10x
#      faster. `--selftest` checks the indicators against slow reference loops.
#    • Config.validate(): weights sum to 1, weight keys are real columns,
#      sell floor < alert threshold, tickers de-duplicated (SILC was listed
#      twice), thresholds ordered. Problems are printed AND shown on the
#      dashboard's Health tab.
#    • Indicators are computed on the FULL download, then trimmed. v15 trimmed
#      to 320 bars first, so EMA200 and Mom_252d were only half warmed up.
#    • Composite blends renormalise weights per row over the components that
#      exist, so a recent IPO with no 252-day return gets a real percentile
#      instead of NaN→50.
#    • Partial (intraday) bars are detected and dropped by default; stale
#      tickers, short histories, illiquid names and failed downloads are all
#      reported on the Health tab instead of only in the console.
#    • Volatility damping has a floor (min_reliability) so high-vol names can
#      still reach a BUY; v15 made a BUY structurally impossible above 100% HV.
#    • One scoring pass. v15 scored every ticker twice (before/after regime).
#    • Output path is failure-proof: the dashboard is written FIRST, CSV/snapshot
#      fall back to a local folder if the Drive path is unavailable, and writes
#      retry through OneDrive/Drive file locks.
#    • Squeeze strength is rescaled so 100 is reachable (v15 topped out at 85)
#      and the "Flat" chip now tests the same range the score awards.
#    • EXIT is reachable again: when both alerts fire and confidences are within
#      `conflict_margin`, the resolver de-risks. (In v15 step 1 always returned.)
#    • Adaptive regime thresholds removed — they were dead code (`dist.get(20)`
#      looked up an int key in a str-keyed dict). Fixed thresholds are config.
#    • Fixed `%H:%M %p` timestamp ("16:52 PM").
#
#  INSIGHT
#    • Reconstructed signal history: the same vectorised scorer is run over
#      every historical bar, giving per-ticker confidence sparklines, a
#      "What changed" tab, rotation tails, and a Signal Scorecard (forward
#      returns after BUY/SELL events, in-sample, informational).
#    • Prior snapshots are read back (v15 wrote them but never used them).
#
#  INTERFACE
#    • Single JSON payload, rendered client-side. Any ticker anywhere opens a
#      detail drawer. Real sortable columns (data-sort), live text filter,
#      sticky headers that actually stick, component breakdown bars,
#      near-trigger Watch list, market-context strip, Health + Scorecard tabs.
#    • No CDN: all charts are inline SVG. The file works offline.
#
#  USAGE
#    python momentum_unified_v53.py              # normal run
#    python momentum_unified_v53.py --demo       # synthetic data, no network
#    python momentum_unified_v53.py --selftest   # indicator & scoring checks
#    python momentum_unified_v53.py --tickers NVDA,AVGO,SPY --out-dir ./out
#    python momentum_unified_v52.py --eod-only   # ignore the live price; confirmed closes only
# =============================================================================

from __future__ import annotations

import argparse
import copy
import json
import math
import os
import sys
import time
import traceback
import warnings
import webbrowser
from dataclasses import dataclass, field
from datetime import datetime, date
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

VERSION = "v56"

LOCAL_TZ = ZoneInfo("America/Denver")
MARKET_TZ = ZoneInfo("America/New_York")


# =============================================================================
#  CONFIG
# =============================================================================

def _default_tickers() -> list[str]:
    return [
        'ACM', 'ADEA', 'AMPX', 'AMZN', 'APH', 'ASIX', 'AVGO', 'ALV', 'AIT', 'ACA', 'AMAT', 'ALAB', 'AXP', 'ALAB', 'AXTI',
        'BWXT', 'BWA', 'BELFA', 'BBIO',
        'CTVA', 'CLS', 'CDNS', 'CRM', 'COST', 'CRDO', 'CPRT',
        'DAVE', 'DT', 'DECK', 'DELL',
        'ENS', 'ETN', 'EQT', 'EL',
        'FIX', 'FROG', 'FLEX', 'FICO',
        'GEV', 'GOOG', 'GTLB', 'GWW', 'GEO',
        'HWM', 'HUBB', 'HPE',
        'KEX', 'KTOS',
        'INCY', 'INTC', 
        'JBL', 'JKHY',
        'LDOS', 'LECO',
        'MELI', 'MLI', 'MP', 'MNR',
        'NTR', 'NVDA', 'NOW', 'NVT', 'NUE', 'NOK', 'NFLX',
        'OSS', 'OMDA', 'OUST',
        'PLPC', 'PKOH', 'PWR', 'PENG', 'PEP',
        'Q',
        'RELL', 'RELY', 'RTX',
        'SILC', 'STRL', 'SNPS', 'SNOW', 'SLB', 'SMP', 'SNDK', 'STM', 'SPCX', 'SPOT',
        'TEM', 'TPL', 'TTMI', 'TSEM', 'TSM',
        'UMAC', 'UMC', 'UPS',
        'VEEV', 'VRT',
        'WMT', 'WCC', 'WDC', 'WM', 'WLK', 'WLKP',
 
        # Nuclear
        'UUUU', 'LEU',
 
        # Seeking Alpha
        'SNDK', 'CRDO', 'TTMI', 'LITE', 'STRL', 'VICR', 'SEZL', 'DAVE', 'PACS', 
        'AMZN', 'MU', 'AMD', 'COHR', 'CIEN', 'ATI', 'ALL', 'CLS', 'INCY', 'B', 
        'WLDN', 'WDC', 'BAC', 'LMT', 'ICHR', 'POWL', 'AGX', 'DXPE', 'PAYX',
 
        # Semiconductors
        'SMH', 'GFS', 
 
        # Robotics
        'ROC', 'KOID', 'GDYN', 'NOK', 'AMPX',
 
        # Agentic AI
        'DOCN', 'NET',
 
        # Congressional and Senate Trades
        'GS', 'MCHP', 'MRVL',
 
        # NanoTechnology - Healthcare and BioTecch
        'BRKR', 'DHR', 'A', 'MTD', 'ECL', 'TMO', 'BIO',
 
        # Cyber Security Software
        'PANW', 'CRWD', 'ZS', 'NTSK', 'OKTA', 'SAIL', 'S', 'MITK', 'CHKP', 'FTNT', 'DT', 
     
        # Power
        'CIFR', 'WULF', 'HUT', 'RIOT', 'GLXY', 'BE', 'INIO', 'SEI', 'WMB', 'LBRT', 'APLD', 'CIEN',
        'SBGSY', 'ABBNY', 'SIEGY', 'GEV', 'TT', 'CARR', 'NVT', 'TLN', 'VST', 'FPS', 'TVA',
        
        # Grid Build Out
        'PWR', 'ETN', 'HUBB',

        # Grid Build Out
        'PWR', 'ETN', 'HUBB',

        # Owners of Operating Data Centers
        'EQIX', 'DLR',

        # Holders of Powered Land and Grid Access
        'IREN', 'APLD', 'WULF', 'CIFR',

        # Long lead equipment
        'GEV', 'ETN', 'VRT', 'CAT', 'HUBB', 'CARR',

        # Power Producers and on-site generation
        'GEG', 'VST', 'TLN', 'BE', 'NRG',
 
        # Behind The Meter Power
        'BE', 'CAT', 'CMI',
 
        # Photonics
        'AAOI', 'AMKR', 'COHR', 'CRDO', 'FN', 'GLW', 'LITE', 'PENG', 'POWI', 'VIAV', 'VICR', 'HIMX',
 
        # Neo Clouds
        'CRWV', 'NBIS',
 
        # Quantum Computing
        'ANET', 'AKAM', 'HON', 'RGTI', 'QBTS', 'MRVL',
 
        # Edge Computing
         'IONQ', 'RGTI',
 
        # Metals
        'NIKL', 'COPJ', 'ERO',
 
        # Banks
        'JPM', 'GS',
 
        # Telecom
        'VZ', 'T', 'TMUS',
 
        # Broadband and Cable
        'CMCSA', 'CHTR',
 
        # (Sector and Six Pack ETFs are their own lists - Config.sector_names and
        #  Config.six_pack - and are merged into the data pull by Config.validate())
 
        # Indexes
        'SPY', 
 
        # High Conviction - Python
        'TENB', 'SLAB', 'WNC', 'GNK', 'IOT', 'SCCO', 'CGNX', 'AIT', 'IESC', 'LAUR', 'IEX', 
        'PWR', 'CSCO', 'GSAT', 'SBGSY', 'URI', 'FIX', 'FLEX', 'GLW', 'ROK', 'GRC', 'GEV', 'LECO', 
        'CAT', 'LOGI', 'CR', 'ABBNY', 'DBRG', 'ST', 'NOK', 'GOOGL', 'IRDM', 'PK', 'PEB', 'TECK', 
        'DCO', 'MOG-A', 'RS', 'HST', 'BJ', 'MTN', 'CECO',
 
        #2026-10-29 High Conviction
        'DCBO', 'BNED', 'HIPO', 'XOM', 'BIIB', 'BP', 'PSO', 'V', 'E', 'GDDY', 'WLY', 'EOG', 'COTY', 
        'MA', 'ELV', 'MH', 'MUR', 'MORN', 'ULTA', 'EBAY', 'EXPO', 'MO', 'COKE', 'LLY', 'BKH', 'HAS', 
        'TRI', 'CVSA', 'RMD', 'PG', 'PCTY', 'CLF', 'AMZN', 'RGA', 'VRSN', 'GSAT', 'MTN', 'RNR', 'HST', 
        'DIS', 'WRB', 'BRK-B', 'GOOGL', 'SAIC', 'DGII',
 
        # Early Sub-Themes - Python
        'DAC', 'KEX', 'GNK', 'SBLK', 'GSL', 'PRDO', 'CVSA', 'LAUR', 'DCBO', 'LINC', 'MPC', 'OXY', 
        'BP', 'DVN', 'EOG', 'PBF', 'DINO', 'VLO', 'PSX', 'PRIM', 'APG', 'IESC', 'GVA', 'MYRG', 
        'SEI', 'MPWR', 'INIO', 'TER', 'ROK', 'NOVT', 'RRX', 'SBGSY', 
 
        # Early PPO Sub Themes 2026-10-09
        'DCBO', 'BNED', 'HIPO', 'XOM', 'BIIB', 'BP', 'PSO', 'V', 'E', 'GDDY', 'WLY', 'EOG', 'COTY', 
        'MA', 'ELV', 'MH', 'MUR', 'MORN', 'ULTA', 'EBAY', 'EXPO', 'MO', 'COKE', 'LLY', 'BKH', 'HAS', 
        'TRI', 'CVSA', 'RMD', 'PG', 'PCTY', 'CLF', 'AMZN',
 
        # Early 2026-10-09
        'TDUP', 'SNAP', 'MELI', 'PINS', 'REAL', 'BRZE', 'FRSH', 'INTU', 'HUBS', 'PEGA', 'MORN', 
        'VRSK', 'CSGP', 'RELX', 'FDS', 'VTEX', 'LSPD', 'PDD', 'GDDY', 'WIX', 'AFRM', 'DLO', 'FOUR', 
        'V', 'MA', 'CBOE', 'TW', 'CME', 'BR', 'ICE', 'RBLX', 'NTES', 'TTWO', 'PLTK', 'HAS', 'CPNG', 
        'CART', 'WMT', 'CASY', 'KR', 'NU', 'MQ', 'DAVE', 'FIS', 'JKHY', 'MMS', 'ULS', 'HRB', 'ADP', 
        'PAYX', 'CEG', 'VST', 'BKH', 'NWE', 'PCG', 'MPC', 'TPL', 'COP', 'EOG', 'FANG', 'CNX', 'RRC', 
        'AR', 'EQT', 'BBWI', 'COTY', 'ULTA', 'CL', 'PG', 'U', 'LRN', 'SKIL', 'BNED', 'TAL', 'WLY', 
        'BRBR', 'STZ', 'PM', 'CELH', 'MO', 'SNOW', 'MDB', 'AI', 'NICE', 'SAP', 'DINO', 'VLO', 'PSX', 
        'KMI', 'OVV', 'BRO', 'WRB', 'MET', 'ESNT', 'UNM', 'CLF', 'NUE', 'CENX', 'STLD', 'FCX', 'BALL', 
        'RSG', 'WM', 'GFL', 'CWST', 'TEAM', 'BABA', 'ESTC', 'HAE', 'RMD', 'BDX', 'STE', 'PODD', 
        'SHEL', 'BP', 'XOM', 'CVX', 'E', 'ABBV', 'GILD', 'AMGN', 'EXEL', 'TNGX', 'SFIX', 'PVH', 
        'ANF', 'DECK', 'VFC', 'APP', 'MGNI', 'GOOGL', 'PLNT', 'MTN', 'EXPE', 'WH', 'CHH',
         
        #TEAR
        "PENG", "NBIS", "VIAV", "ENS", "MITK", "AMKR", "LITE", "COHR", "SILC",
        "SAIL", "NVT", "FIVN", "DT", "VICR", "FPS", "COPJ", "RKLB", "TWLO",
        "LRCX", "RELL", "PKOH", "POWL", "AVGO", "AMZN", "ADEA", "VPG", "TSEM",
        "SNDK", "HOOD", "Q", "MU", "AAOI", "CLMT", "BWXT", "LEU", 
         
        # Tear Watchlist
        'SITM', 'RELL', 'SIMO', 'SITM', 'SMCI', 'CRDO', 'MITK',
 
        # Goldman Sachs Conviction List
        'BURL', 'EL', 'ORLY', 'VIK',  
        'CFG', 'TPG', 'WFC', 
        'UNH', 'VRTX',
        'CSL', 'CWST', 'DAL', 'HII', 'UPS',
        'OXY', 'NXT',
        'AMZN', 'AMAT', 'CLS', 'DASH', 'MSFT', 'XYZ',
        'AXTI', 'DELL', 'CRDO',

        # Democrat
        'CNC', 'DGX', 'ENPH', 'FSLR', 'GFS', 'GOOGL', 'IBM', 'IQV', 'LEGH',
        'MOH', 'MPWR', 'NEE', 'NVTS', 'OSCR', 'VICR',
         
        ]

def _default_tickers_Tear() -> list[str]:
    return [
        "AXTI", "P", "IOVA", "FORM", "AEHR", "CRDO", "ABCL", "ONTO", "COHU", "MTRN",
        "ALAB", "TWST", "LITE", "SITM", "COHR", "MXL", "MTSI", "AAOI", "VIAV", "SMTC",
        "NBIS", "PENG", "FPS", "CDNA", "SNDK", "FN", "TSEM", "TWLO", "ACLS", "SEI",
        "FSLY", "TER", "CAMT", "IREN", "VECO", "PS", "GRAL", "LRCX", "TEM", "HPE",
        "CRWV", "ERO", "CAI", "MRVL", "AEIS", "INTC", "RKLB", "ASX", "AMAT", "MRNA",

        ]

@dataclass
class Config:
    # ---- Universe source (v29) ----------------------------------------------
    # "list"   = the ticker list in _default_tickers() (default)
    # "themes" = every UNIQUE ticker in Config.themes_csv (the Theme file)
    # "both"   = the code list AND the Theme file tickers, de-duplicated
    # Also switchable per run with --universe themes. Sector / Six Pack / ETF /
    # Country ETF lists are still merged in on top either way.
    universe_source: str = "both"

    # ---- Universe & data --------------------------------------------------
    #tickers: list[str] = field(default_factory=_default_tickers)
    tickers: list[str] = field(default_factory=_default_tickers)
    period: str = "2y"
    benchmark: str = "SPY"
    bench_period: str = "5y"
    context_tickers: tuple = ("SPY", "QQQ", "RSP")     # v52: shown as cards on Market Health
    # v52: Market Health breadth counts STOCKS only. Besides every fund list below, these are never counted
    # (index / thematic funds that sit in the main ticker list). Anything Yahoo does not call an EQUITY is
    # also left out when breadth_check_yahoo_type is on (result cached in quote_types_cache.json).
    breadth_exclude: tuple = ("SPY", "QQQ", "RSP", "IWM", "DIA", "SMH", "KOID", "COPJ", "NIKL", "BUG",
                              "IBB", "XBI", "ARKK", "TLT", "HYG", "GLD", "SLV", "IBIT")
    breadth_check_yahoo_type: bool = True
    breadth_type_budget_s: int = 120       # most seconds spent on first-time quote-type lookups
    breadth_min_names: int = 50            # fewer stocks than this -> breadth is not shown
    # S&P 500 sector ETFs for the Sectors tab (ticker -> sector name, in display order).
    # Its own list: merged into the data pull by validate().
    sector_names: dict = field(default_factory=lambda: {
        "XLK": "Technology", 
        "XLV": "Health Care", 
        "XLF": "Financials",
        "XLY": "Consumer Discretionary", 
        "XLC": "Communication Services",
        "XLI": "Industrials", 
        "XLP": "Consumer Staples", 
        "XLE": "Energy",
        "XLU": "Utilities", 
        "XLRE": "Real Estate", 
        "XLB": "Materials",
    })

    # Six Pack tab (v23; replaces the Nine Box - the Blend column is gone):
    # ticker -> (cap row, style column, fund name), in display order.
    # Its own list: merged into the data pull by validate().
    six_pack: dict = field(default_factory=lambda: {
        "VOOG": ("Large", "Growth", "S&P 500 Growth"),
        "VOOV": ("Large", "Value",  "S&P 500 Value"),
        "VOT":  ("Mid",   "Growth", "Mid-Cap Growth"),
        "VOE":  ("Mid",   "Value",  "Mid-Cap Value"),
        "VBK":  ("Small", "Growth", "Small-Cap Growth"),
        "VBR":  ("Small", "Value",  "Small-Cap Value"),
    })
    # ETFs tab (v27): your own ETF watchlist, SEPARATE from Config.tickers.
    # Add or remove tickers here; validate() merges them into the data pull.
    etf_tickers: list = field(default_factory=lambda: [
       "SMH", 'XSD',                    # Semiconductors
       "DRNZ",                          # Drones
       'GNOM',                          # Genomics
       'COPP', 'COPX',                  # Copper
       'BWET', 'PDBC', 'WOOD', 'HGER',  # Other Commodities
       'AIQ', 'THNQ', 'DRAM',           # Artificial Intelligence & Machine Learning
       'CIBR', 'BUG', 'HACK',           # Cyber Security
       'QTUP',                          # Qunatum Computing
       'PAVE', 'GRID',                  # AI Infrastructure & Power Generation
       'AIPO',                          # The Pure-Play AI Power Theme: Defiance AI & Power Infrastructure ETF - GEV, PWR, ETN, BE, NVT, HUBB, and VST.
       'POWR',                          # The Power Grid Build-Out Theme: iShares U.S. Power Infrastructure ETF - PWR, ETN, GEV, NVT, HUBB, CARR, TT, and VST.
       'NODE',                          # The Digital Infrastructure & Compute Theme: CIFR, WULF, HUT, RIOT, GLXY, APLD, alongside power giants like VST and CEG.
       'NUKZ', 'URA',  'SRUUF',         # Nuclear Energy
       'BOTZ', 'ARGQ', "KOID",          # Robotics
       'GLD', 'GDX', 'FGLD',            # Gold
       'IYT',                           # Transports
       'KRE',                           # Regional Banks
       'IGV',                           # Software
       'ITA',                           # Defense
       'SLV', 'SIL',                    # Silver
       'GSG',                           # Broad Based Commodities       
       'XOP',                           # Oil and Gas Exploration and Production
       'XDIV', 'BOXX',                  # CASH
       'AVDV', 'AVUV',                  # Small Cap
       'VXUS', 'VEXC',                  # Vanguard Ex US
       'FDFF',                          # Fidelity Finance and Data Processing
       'FMED',                          # Fidelity Healthcate, Biotech, and Medical Devices
       'FBOT',                          # Industrials and Technology infrastructure
       'IBB', 'BBH', 'IBQQ',            # Large Cap Biotehch
       'XBI', 'FBT',                    # Mid Cap and Small Cap Biotech
       'IBIT',                          # Bitcoin
       'TLT', 'ZROZ','HYG', 'EDV',      # Bonds
       'RSP', 'QQQ',                    # Indexes
       'COPJ', 'NIKL',                  # Metals
       'VNQ',                           # Real Estate

       'ARKK', 'ARKG', 'ARKW', 'ARKQ', 'ARKF', 'ARKX'  # ARK Family of ETFs

        ])
    # Optional display names for the ETFs, e.g. {"SMH": "VanEck Semiconductor ETF"}.
    # Anything not listed here is taken from the Theme file, then looked up on Yahoo.
    etf_names: dict = field(default_factory=dict)

    # Tear's Short List (v35): names carved out for special emphasis (own tab + Rotation
    # button). They remain ordinary universe members (Themes, Signals, Rotation > All ...).
    # validate() merges any that are missing into the data pull.
    tear_tickers: list = field(default_factory=lambda: [
    
        "BUG", "MITK", "PENG", "VICR", "RELL", "NVT", "NBIS", "DT", "BE", "SAIL",
        "ENS", "LITE", "FIVN", "VIAV", "AVGO", "AMKR", "CRDO", "COPJ", "COHR", "AXTI",
        "RKLB", "PKOH", "SILC", "TWLO", "FPS", "AMZN", "LRCX", "POWL", "ADEA", "VPG",
        "Q", "KOID", "SNDK", "MU", "HOOD", "BWXT", "AAOI", "LEU", "CLMT",
        ])
    
    # Frank's Short list (v37): a second carve-out list, treated exactly like Tear's Short List.
    shortlist_tickers: list = field(default_factory=lambda: [
        "GEV", "PRDO", "BE", "PWR", "VRT", "COHR", "AVGO", "FIX", 'GOOG',
        "VIAV", "VICR", "BUG", "PENG", "GLW", 'CRWD', 'AMKR', 'SKHY', 'EWY', 'RSP',
        'AVDV', 'AVUV',  "LYTE", "MOH", "CNC", "MSOS", 'VSAT', 'GEHC', 'CVNA', 'HD', 'LOW',
    ])

    # Goldman's names (v45). v50: the Goldman's Picks TAB was deleted; this list is kept only so these names stay in the data pull.
    goldman_tickers: list = field(default_factory=lambda: [
        "CEG", "VST", "TLN", "GEV", "BE", "VRT", "ETN", "ANET", "SMCI", "MSFT",
        "AMZN", "NVDA", "AVGO", "AMD", "CRWD", "PANW", "ZS",
    ])

    # Bonds tab: your Bond ETF list (same scoring / table as the ETFs tab) plus the Treasury yield curve.
    # validate() merges these into the data pull. Add / remove tickers freely.
    bond_etfs: list = field(default_factory=lambda: [
        "BND", "EDV", "ZROZ", "BSV", "VCSH", "VGIT", "VCIT", "BLV", "VGLT", "VTEB", "VTIP",
    ])
    # Treasury curve: label -> (years to maturity, FRED series id, Yahoo fallback symbol or "")
    treasury_curve: dict = field(default_factory=lambda: {
        "3M":  (0.25, "DGS3MO", "^IRX"),
        "6M":  (0.5,  "DGS6MO", ""),
        "1Y":  (1.0,  "DGS1",   ""),
        "5Y":  (5.0,  "DGS5",   "^FVX"),
        "10Y": (10.0, "DGS10",  "^TNX"),
        "20Y": (20.0, "DGS20",  ""),
        "30Y": (30.0, "DGS30",  "^TYX"),
    })

    # Country ETFs tab (v28): ticker -> (country, FULL fund name), in display order.
    # Its own list: merged into the data pull by validate(). Add / remove rows freely.
    country_etfs: dict = field(default_factory=lambda: {
        "ARGT": ("Argentina", "Global X MSCI Argentina ETF"),
        "ECH":  ("Chile", "iShares MSCI Chile ETF"),
        "EDEN": ("Denmark", "iShares MSCI Denmark ETF"),
        "EFNL": ("Finland", "iShares MSCI Finland ETF"),
        "EIDO": ("Indonesia", "iShares MSCI Indonesia ETF"),
        "EIRL": ("Ireland", "iShares MSCI Ireland ETF"),
        "EIS":  ("Israel", "iShares MSCI Israel ETF"),
        "ENOR": ("Norway", "iShares MSCI Norway ETF"),
        "ENZL": ("New Zealand", "iShares MSCI New Zealand ETF"),
        "EPHE": ("Philippines", "iShares MSCI Philippines ETF"),
        "EPOL": ("Poland", "iShares MSCI Poland ETF"),
        "EPU":  ("Peru", "iShares MSCI Peru and Global Exposure ETF"),
        "EWA":  ("Australia", "iShares MSCI Australia ETF"),
        "EWC":  ("Canada", "iShares MSCI Canada ETF"),
        "EWD":  ("Sweden", "iShares MSCI Sweden ETF"),
        "EWG":  ("Germany", "iShares MSCI Germany ETF"),
        "EWH":  ("Hong Kong", "iShares MSCI Hong Kong ETF"),
        "EWI":  ("Italy", "iShares MSCI Italy ETF"),
        "EWJ":  ("Japan", "iShares MSCI Japan ETF"),
        "EWK":  ("Belgium", "iShares MSCI Belgium ETF"),
        "EWL":  ("Switzerland", "iShares MSCI Switzerland ETF"),
        "EWM":  ("Malaysia", "iShares MSCI Malaysia ETF"),
        "EWN":  ("Netherlands", "iShares MSCI Netherlands ETF"),
        "EWO":  ("Austria", "iShares MSCI Austria ETF"),
        "EWP":  ("Spain", "iShares MSCI Spain ETF"),
        "EWQ":  ("France", "iShares MSCI France ETF"),
        "EWS":  ("Singapore", "iShares MSCI Singapore ETF"),
        "EWT":  ("Taiwan", "iShares MSCI Taiwan ETF"),
        "EWU":  ("United Kingdom", "iShares MSCI United Kingdom ETF"),
        "EWW":  ("Mexico", "iShares MSCI Mexico ETF"),
        "EWY":  ("South Korea", "iShares MSCI South Korea ETF"),
        "EWZ":  ("Brazil", "iShares MSCI Brazil ETF"),
        "EZA":  ("South Africa", "iShares MSCI South Africa ETF"),
        "GREK": ("Greece", "Global X MSCI Greece ETF"),
        "COLO": ("Colombia", "Global X MSCI Colombia ETF"),
        "INDA": ("India", "iShares MSCI India ETF"),
        "KSA":  ("Saudi Arabia", "iShares MSCI Saudi Arabia ETF"),
        "KWT":  ("Kuwait", "iShares MSCI Kuwait ETF"),
        "MCHI": ("China", "iShares MSCI China ETF"),
        "QAT":  ("Qatar", "iShares MSCI Qatar ETF"),
        "THD":  ("Thailand", "iShares MSCI Thailand ETF"),
        "TUR":  ("Turkey", "iShares MSCI Turkey ETF"),
        "UAE":  ("United Arab Emirates", "iShares MSCI UAE ETF"),
        "VNM":  ("Vietnam", "VanEck Vietnam ETF"),
    })
    # set by validate(): the main watchlist WITHOUT the Sector / Six Pack / ETF lists
    core_tickers: list = field(default_factory=list, repr=False)

    # Currency tab (v42): ticker -> (currency, FULL fund name). View on the US dollar:
    # these funds RISE when the foreign currency strengthens (dollar weakens).
    # Its own list: merged into the data pull by validate(). FXS / FXM are thin or may
    # no longer trade: any that fail to load show "no data" and appear on the Health tab.
    currency_etfs: dict = field(default_factory=lambda: {
        "FXE": ("Euro", "Invesco CurrencyShares Euro Trust"),
        "FXY": ("Japanese Yen", "Invesco CurrencyShares Japanese Yen Trust"),
        "FXB": ("British Pound", "Invesco CurrencyShares British Pound Sterling Trust"),
        "FXF": ("Swiss Franc", "Invesco CurrencyShares Swiss Franc Trust"),
        "FXA": ("Australian Dollar", "Invesco CurrencyShares Australian Dollar Trust"),
        "FXC": ("Canadian Dollar", "Invesco CurrencyShares Canadian Dollar Trust"),
        "FXS": ("Swedish Krona", "Invesco CurrencyShares Swedish Krona Trust"),
        "FXM": ("Mexican Peso", "Invesco CurrencyShares Mexican Peso Trust"),
    })
    # Reference row: the dollar itself (BUY here = dollar strengthening).
    currency_ref: dict = field(default_factory=lambda: {
        "UUP": "Invesco DB US Dollar Index Bullish Fund",
    })
    # Approximate US Dollar Index (DXY) weights, % (AUD and MXN are not in the index);
    # used only for the DXY-weighted "USD view" bias.
    currency_dxy_weights: dict = field(default_factory=lambda: {
        "FXE": 57.6, "FXY": 13.6, "FXB": 11.9, "FXC": 9.1, "FXS": 4.2, "FXF": 3.6})
    currency_own_anchor: bool = True          # percentiles vs the group's pooled history, not SPY's
    currency_min_dollar_vol: float = 1_000_000  # liquidity floor for the group (default floor is 5M)
    currency_corr_window: int = 60            # sessions for the SPY / UUP correlation columns
    # set by validate(): every ticker of the Currency tab (funds + reference)
    currency_group: list = field(default_factory=list, repr=False)
    # v43: Country ETFs use a lower liquidity floor than stocks and skip the SPY-regime gate
    country_min_dollar_vol: float = 1_000_000
    country_group: list = field(default_factory=list, repr=False)   # set by validate()

    # ---- Themes (v24; display only) ---------------------------------------
    themes_csv: Path = Path(r"G:\My Drive\Projects\Python\Stocks & Options\Themes\data\Input_Ticker_List_by_Theme.csv")
    # Theme Signals tab (v56; display only): weekly Theme / Sub-Theme signal file
    theme_signal_csv: Path = Path(r"G:\My Drive\Projects\Python\Stocks & Options\Themes\reports\Weekly_Theme_Signal.csv")
    theme_signal_stale_days: int = 8     # file older than this (vs the session date) -> warning banner
    # Theme scoring (v30; display only). Primary assignments only.
    theme_min_members: int = 3          # fewer loaded names -> greyed out ("n too small")
    theme_history_bars: int = 60        # sessions of theme-score history
    theme_weights: dict = field(default_factory=lambda: {
        "momentum": 0.40, "breadth": 0.25, "signals": 0.20, "accel": 0.15})

    # ---- Fundamentals (display only): the "Score" tab of the Quality spreadsheet ----
    # Tried in order: the Google Sheet (needs "anyone with the link can view"), then the local CSV.
    # Set fundamentals_url = "" to use only the local file.
    fundamentals_url: str = ("https://docs.google.com/spreadsheets/d/1cq3nR5sWRV7HZMzMcqoa6eIY_qPgZiJU6TrJmngQvt8"
                             "/export?format=csv&gid=36129353")
    fundamentals_csv: Path = Path(__file__).resolve().with_name("Score.csv")

    # ---- Paths (primary → fallback) --------------------------------------
    output_csv: Path = Path(r"G:\My Drive\Projects\Momentum\Results.csv")
    output_html: Path = Path(r"C:\Users\hayes\OneDrive\Desktop\Results.dashboard_v56.html")
    # Extra copies of the dashboard (v31). Each gets its own sibling
    # <name>.history.js, so every copy is self-contained. A copy that cannot be
    # written (e.g. the drive is offline) only logs a warning. Skipped with --out-dir.
    extra_html: list = field(default_factory=lambda: [
        Path(r"G:\My Drive\Projects\SeriousDinero\WebSite\watchlist-momentum\watchlist-momentum.html"),
    ])
    snapshot_dir: Path = Path(r"G:\My Drive\Projects\Momentum\snapshots")
    fallback_dir: Path = Path.home() / "Momentum_output"
    write_retries: int = 5
    write_retry_sleep: float = 1.5
    open_browser: bool = False

    # ---- Data quality -----------------------------------------------------
    min_bars: int = 300          # below this → Momentum_Data_OK = 0 (no alerts)
    min_load_bars: int = 60      # below this → ticker skipped entirely
    keep_bars: int = 320         # bars retained for history/scorecard after warm-up
    liq_window: int = 20
    min_dollar_vol: float = 5_000_000
    min_price: float = 5.00
    # False (default): while the market is open, use today's live/forming bar
    # — its Close is the current price — in the analysis. True (--eod-only):
    # ignore it and wait for a confirmed close (the old, conservative default).
    drop_partial_bar: bool = False
    stale_bdays: int = 3         # last bar older than this many business days → stale

    # ---- Momentum (multi-timeframe) ---------------------------------------
    mom_weights: dict = field(default_factory=lambda: {20: 0.40, 50: 0.30, 100: 0.20, 252: 0.10})

    # ---- PPO & trend ------------------------------------------------------
    ppo_fast: int = 12
    ppo_slow: int = 26
    ppo_sig: int = 9
    ppo_fresh_bars: int = 3          # v41: 2 -> 3
    ppo_persist_window: int = 5

    # ---- Swenlin PMO (Ticker tab chart only - NOT used in scoring) ---------
    pmo_roc_len: int = 35          # custom-EMA smoothing of 1-day ROC (multiplier 2/N)
    pmo_smooth_len: int = 20       # custom-EMA smoothing of 10 x the first stage (2/N)
    pmo_sig_len: int = 10          # signal line = standard EMA of the PMO

    # ---- Squeeze ----------------------------------------------------------
    sqz_bb_length: int = 20
    sqz_bb_std: float = 2.0
    sqz_kc_length: int = 20
    sqz_kc_scalar: float = 1.5
    sqz_mom: int = 12
    sqz_recent_window: int = 10
    min_compression: int = 15
    dmi_floor: float = -5.0

    # ---- EMAs -------------------------------------------------------------
    ema_fast: int = 20
    ema_mid: int = 50
    ema_slow: int = 200

    # ---- RSI zones --------------------------------------------------------
    rsi_healthy_low: float = 40
    rsi_healthy_high: float = 65

    # ---- Alerts (0-100 confidence) ---------------------------------------
    buy_alert_threshold: int = 40
    sell_alert_threshold: int = 40
    watch_margin: int = 8          # within this many points of a threshold → Watch list
    require_volume_confirm: bool = True
    vol_confirm_mult: float = 1.25  # cross-bar dollar vol vs 20d median
    # Ticker-tab volume chart (v48; display only): share volume vs its rolling median
    vol_rel_hi: float = 1.5         # bar >= this x the median -> highlighted (high volume)
    vol_rel_lo: float = 0.7         # bar <  this x the median -> faded (low volume)
    vol_rel_bars: int = 20          # rolling-median window (sessions)
    conflict_margin: int = 10      # both alerts & |buy−sell| ≤ margin → EXIT (de-risk)
    # Alerts always use the last confirmed close. The live bar still drives
    # displayed RSI/PPO/confidence so the dashboard moves during the session.
    alerts_eod_only: bool = True
    # PPO trigger: alerts require a fresh signed signal-line cross.
    require_ppo_cross_for_alert: bool = True
    # Causal percentile lookback (benchmark bars strictly before the scored bar)
    pctile_lookback: int = 504
    pctile_min_obs: int = 50
    # Relative strength vs benchmark (20d return minus SPY 20d)
    rs_gate: bool = True
    rs_lookback: int = 20
    # ---- New gates for improved accuracy (v36) -----------------------------
    require_above_ema200_for_buy: bool = True
    rs_min_excess_for_buy: float = 0.0          # 20d excess return % vs benchmark
    require_negative_rs_for_sell: bool = False  # optional
    stronger_top_detection: bool = True         # extra conditions for SELL/EXIT


    # ATR-aware haircut: names above this ATR% need extra conviction to alert
    atr_soft_cap: float = 6.0
    atr_extra_points: int = 10
    # Squeeze addend caps
    sqz_buy_add_cap: int = 10
    sqz_sell_add_cap: int = 8

    # ---- Sell-side risk tuning -------------------------------------------
    # A FRESH bearish signal-line cross guarantees at least `sell_cross_floor`.
    # It must sit BELOW sell_alert_threshold so the cross alone lands in
    # "review" territory and one confirming factor tips it over. v15 shipped
    # with floor 55 > threshold 40, which auto-fired SELL on every cross.
    sell_cross_floor: int = 30          # v46: 35 -> 30, below the lowest regime sell threshold (35)
    sell_vol_damping_on_cross: float = 0.35
    sell_regime_weight_floor: float = 0.85

    # ---- Volatility damping -----------------------------------------------
    # Signal_Reliability = 1 − (1 − min_reliability) · clip(HV/100, 0, 1)
    # v15 used a floor of 0, which made a BUY impossible for names with
    # 100%+ historical vol (RGTI, WULF, APLD …).
    min_reliability: float = 0.45

    # ---- v54: universe-relative, volatility-adjusted ranking -----------------
    # "universe"  = each component is ranked ACROSS the names loaded on the same date (0-100), so the
    #               Trailing / Emerging percentiles and the RS Rating say where a name stands among its
    #               peers today. "benchmark" = the pre-v54 behaviour (percentile of SPY's own history).
    # Dates with fewer than xs_min_names names (and the Currency group, which keeps its own pooled
    # anchor) fall back to the benchmark anchor.
    pctile_anchor: str = "universe"
    xs_min_names: int = 30
    # Returns and the PPO histogram are divided by the name's own volatility before ranking, so a
    # volatile name is not "Strong" or "Weak" just because it moves more than everything else.
    vol_adjust_momentum: bool = True
    vol_adj_window: int = 63            # sessions of daily returns for the volatility estimate
    vol_adj_floor_ann: float = 8.0      # % annualised floor (stops cash-like funds ranking at the top)

    # ---- v54: symmetric POS / NEG scoring ------------------------------------
    # True: ONE volatility discount, 1 - vol_damping x (1 - reliability), on both sides, and a fresh
    # bullish cross gets the same kind of floor a fresh bearish cross always had. False = pre-v54.
    symmetric_scoring: bool = True
    vol_damping: float = 0.65
    buy_cross_floor: int = 30           # must sit below the lowest buy threshold (35)
    persist_window: int = 60            # v54: 20 -> 60 sessions for the lag-1 autocorrelation

    # ---- v54: trend state (display only: never changes Signal) ---------------
    # A name is "In trend" from a Favorable alert until an Unfavorable / Conflicted alert or a close
    # under its trailing stop (highest [close - mult x ATR] since entry; it only ever rises).
    trend_state: bool = True
    trend_stop_atr_mult: float = 3.0
    risk_per_trade_pct: float = 1.0     # % of the portfolio risked between entry and the stop distance
    max_position_pct: float = 10.0      # cap on the suggested position size

    # ---- v54: market gate ------------------------------------------------------
    # "breadth" = the gate closes when the index is below its 200-day EMA (SPY, and RSP too when
    #             regime_need_both) OR breadth is washed out (% of stocks above the 200-day AND above
    #             the 50-day are both under the two minimums below).
    # "legacy"  = the v53 rule (SPY and RSP rated Unfavorable or in a Weak / Mature/Cooling regime).
    market_gate_mode: str = "breadth"
    gate_breadth_200_min: float = 40.0
    gate_breadth_50_min: float = 40.0
    gate_breadth_min_names: int = 30    # fewer stocks than this on a date -> breadth is ignored that day
    gate_history_bars: int = 252        # sessions shown on the Market Health gate strip

    # ---- v54: scorecard --------------------------------------------------------
    scorecard_snapshots: bool = True    # score the dated snapshot CSVs (true point-in-time record)
    snapshot_max_files: int = 260
    score_buckets: tuple = (0, 20, 35, 50, 65, 101)

    # ---- Regime thresholds (trailing × emerging percentiles) --------------
    regime_hi: float = 55
    regime_lo: float = 45
    regime_gap: float = 10

    # ---- Composite blends (keys must be columns on the indicator frame) ----
    trailing_weights: dict = field(default_factory=lambda: {
        "Mom_20d": 0.35, "Mom_50d": 0.25, "Mom_252d": 0.20,
        "ADX_Trend": 0.10, "High_52W_Ratio": 0.10,
    })
    emerging_weights: dict = field(default_factory=lambda: {
        # v54: Trend_Persistence 0.20 -> 0.10 (noisy); the weight moved to PPO_Delta and Momentum_Blended
        "PPO_Delta": 0.30, "DMI_Value": 0.20, "OBV_slope": 0.15,
        "Momentum_Blended": 0.25, "Trend_Persistence": 0.10,
    })
    spy_regime_gate: bool = True
    # v53: the market-regime gate closes only when SPY AND this confirming index are both weak
    regime_need_both: bool = True
    regime_confirm: str = "RSP"
    # Regime-conditional alert thresholds (fall back to buy/sell_alert_threshold)
    buy_thr_by_regime: dict = field(default_factory=lambda: {
        "Strong": 35, "Dormant→Waking": 35, "Neutral": 40,
        "Mature/Cooling": 50, "Weak": 55,
    })
    sell_thr_by_regime: dict = field(default_factory=lambda: {
        "Strong": 50, "Dormant→Waking": 50, "Neutral": 40,
        "Mature/Cooling": 35, "Weak": 35,
    })

    # ---- Scorecard --------------------------------------------------------
    fwd_horizons: tuple = (5, 10, 20)
    drawer_history_bars: int = 60      # sparklines / drawer
    ticker_history_bars: int = 120     # full Ticker tab
    session_log_rows: int = 30
    rotation_tail_bars: int = 5

    # ---- Downloads --------------------------------------------------------
    yf_retries: int = 3
    yf_retry_sleep: float = 2.0
    yf_batch_size: int = 100        # tickers per Yahoo request (v38)
    yf_chunk_sleep: float = 1.0     # pause between chunks
    yf_retry_rounds: int = 2        # re-request missing tickers in smaller chunks
    yf_retry_chunk: int = 20        # chunk size used for those retries

    # populated by validate()
    warnings: list = field(default_factory=list, repr=False)

    # -----------------------------------------------------------------------
    def __post_init__(self):
        self.validate()

    def validate(self) -> list[str]:
        """Sanity-check the configuration. Hard errors raise; soft issues are
        collected in self.warnings and surfaced on the dashboard."""
        w: list[str] = []

        # tickers: upper-case, de-duplicate preserving order
        seen, clean = set(), []
        for t in self.tickers:
            t = str(t).strip().upper()
            if not t:
                continue
            if t in seen:
                w.append(f"Duplicate ticker '{t}' removed from the universe")
                continue
            seen.add(t)
            clean.append(t)
        if not clean:
            raise ValueError("Config.tickers is empty")
        # Sector and Six Pack ETFs are their own lists; the data pull is the
        # main list followed by those two (de-duplicated, order preserved).
        group = []
        etfs: list = []
        for t in self.etf_tickers:
            t = str(t).strip().upper()
            if t and t not in etfs:
                etfs.append(t)
        self.etf_tickers = etfs
        bonds: list = []
        for t in self.bond_etfs:
            t = str(t).strip().upper()
            if t and t not in bonds:
                bonds.append(t)
        self.bond_etfs = bonds
        self.country_group = list(dict.fromkeys(str(t).strip().upper() for t in self.country_etfs))
        self.currency_group = list(dict.fromkeys(
            [str(t).strip().upper() for t in self.currency_etfs] + [str(t).strip().upper() for t in self.currency_ref]))
        for t in list(self.sector_names) + list(self.six_pack) + list(self.country_etfs) + self.currency_group + etfs + bonds:
            t = str(t).strip().upper()
            if t and t not in group:
                group.append(t)
        group_set = set(group)
        moved = [t for t in clean if t in group_set]
        if moved:
            w.append(f"{', '.join(moved)} also listed in the main tickers; kept only in the "
                     f"Sectors / Six Pack / ETF / Country ETF list (own Rotation choice)")
        self.core_tickers = [t for t in clean if t not in group_set]
        self.tickers = self.core_tickers + group
        # Tear's Short List: ordinary universe members; just make sure each is in the pull
        tear: list = []
        for t in self.tear_tickers:
            t = str(t).strip().upper()
            if t and t not in tear:
                tear.append(t)
        self.tear_tickers = tear
        in_pull = set(self.tickers)
        for t in tear:
            if t not in in_pull:
                self.core_tickers.append(t)
                self.tickers.append(t)
                in_pull.add(t)
        # Shortlist (v37): same treatment
        short: list = []
        for t in self.shortlist_tickers:
            t = str(t).strip().upper()
            if t and t not in short:
                short.append(t)
        self.shortlist_tickers = short
        for t in short:
            if t not in in_pull:
                self.core_tickers.append(t)
                self.tickers.append(t)
                in_pull.add(t)
        # Goldman's Picks (v45): same treatment
        gold: list = []
        for t in self.goldman_tickers:
            t = str(t).strip().upper()
            if t and t not in gold:
                gold.append(t)
        self.goldman_tickers = gold
        for t in gold:
            if t not in in_pull:
                self.core_tickers.append(t)
                self.tickers.append(t)
                in_pull.add(t)

        for name, d in (("mom_weights", self.mom_weights),
                        ("trailing_weights", self.trailing_weights),
                        ("emerging_weights", self.emerging_weights)):
            s = float(sum(d.values()))
            if not d:
                raise ValueError(f"{name} is empty")
            if any(v < 0 for v in d.values()):
                raise ValueError(f"{name} has a negative weight")
            if abs(s - 1.0) > 1e-6:
                w.append(f"{name} sums to {s:.3f}; weights are renormalised to 1.0")

        # v46: compare against the LOWEST threshold actually in force (the per-regime table),
        # not just the global default, or a cross alone can still auto-fire SELL in some regimes.
        lowest_sell = min([self.sell_alert_threshold, *self.sell_thr_by_regime.values()])
        if self.sell_cross_floor >= lowest_sell:
            w.append(
                f"sell_cross_floor ({self.sell_cross_floor}) ≥ the lowest sell threshold in force "
                f"({lowest_sell}): a fresh bearish cross alone will auto-fire SELL in that regime"
            )
        lowest_buy = min([self.buy_alert_threshold, *self.buy_thr_by_regime.values()])
        if self.symmetric_scoring and self.buy_cross_floor >= lowest_buy:
            w.append(
                f"buy_cross_floor ({self.buy_cross_floor}) ≥ the lowest buy threshold in force "
                f"({lowest_buy}): a fresh bullish cross alone will clear the POS threshold in that regime"
            )
        if self.pctile_anchor not in ("universe", "benchmark"):
            raise ValueError("pctile_anchor must be 'universe' or 'benchmark'")
        if self.market_gate_mode not in ("breadth", "legacy"):
            raise ValueError("market_gate_mode must be 'breadth' or 'legacy'")
        if not (0.0 <= self.vol_damping <= 1.0):
            raise ValueError("vol_damping must be within 0-1")
        if self.trend_stop_atr_mult <= 0 or self.risk_per_trade_pct <= 0 or self.max_position_pct <= 0:
            raise ValueError("trend_stop_atr_mult, risk_per_trade_pct and max_position_pct must be > 0")
        if self.persist_window < 10:
            raise ValueError("persist_window must be >= 10")
        if not (0 <= self.buy_alert_threshold <= 100 and 0 <= self.sell_alert_threshold <= 100):
            raise ValueError("alert thresholds must be within 0-100")
        if not (0.0 <= self.min_reliability <= 1.0):
            raise ValueError("min_reliability must be within 0-1")
        if not (0.0 <= self.sell_vol_damping_on_cross <= 1.0):
            raise ValueError("sell_vol_damping_on_cross must be within 0-1")
        if not (0 < self.vol_rel_lo < self.vol_rel_hi) or self.vol_rel_bars < 2:
            raise ValueError("vol_rel_lo must be > 0 and < vol_rel_hi, and vol_rel_bars >= 2")
        if self.regime_lo >= self.regime_hi:
            raise ValueError("regime_lo must be < regime_hi")
        if self.ppo_fast >= self.ppo_slow:
            raise ValueError("ppo_fast must be < ppo_slow")
        if not (self.ema_fast < self.ema_mid < self.ema_slow):
            raise ValueError("EMAs must be ordered fast < mid < slow")
        if self.min_load_bars > self.min_bars:
            raise ValueError("min_load_bars must be ≤ min_bars")
        if self.keep_bars < max(self.fwd_horizons) + 30:
            w.append("keep_bars is small; the scorecard will have few events")
        if self.benchmark not in self.tickers:
            w.append(f"Benchmark {self.benchmark} is not in the universe; it is fetched separately")

        self.warnings = w
        return w


CONFIG = Config()

# Indicator columns that must be finite before a row may alert
CORE_FIELDS = ("RSI_14", "PPO", "PPO_Delta", "EMA20", "EMA50", "Last_Close")
REGIMES = ("Strong", "Dormant→Waking", "Neutral", "Mature/Cooling", "Weak")


# =============================================================================
#  LOGGING & SMALL UTILITIES
# =============================================================================

def log(msg: str = "") -> None:
    print(msg, flush=True)


def log_warn(msg: str) -> None:
    print(f"  ⚠ {msg}", flush=True)


def log_ok(msg: str) -> None:
    print(f"  ✓ {msg}", flush=True)


def _jsonable(obj):
    """Recursively convert to JSON-safe python (NaN/Inf/NA → None, numpy → py)."""
    if isinstance(obj, dict):
        return {str(k): _jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_jsonable(v) for v in obj]
    if isinstance(obj, np.ndarray):
        return [_jsonable(v) for v in obj.tolist()]
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating, float)):
        f = float(obj)
        return None if (math.isnan(f) or math.isinf(f)) else f
    if isinstance(obj, (np.bool_,)):
        return bool(obj)
    if isinstance(obj, (pd.Timestamp, datetime, date)):
        return obj.strftime("%Y-%m-%d")
    if obj is pd.NA or obj is pd.NaT:
        return None
    return obj


def dumps_js(obj) -> str:
    return json.dumps(_jsonable(obj), allow_nan=False, separators=(",", ":"))


def _rnd(v, nd=2):
    """Round to nd digits, NaN-safe (returns None)."""
    try:
        if v is None or pd.isna(v):
            return None
        return round(float(v), nd)
    except (TypeError, ValueError):
        return None


# =============================================================================
#  ROBUST FILE OUTPUT
# =============================================================================

def _basename(p) -> str:
    """Filename of a path written for either OS (a Windows path on Linux too)."""
    from pathlib import PureWindowsPath, PurePosixPath
    s = str(p)
    return PureWindowsPath(s).name if "\\" in s else PurePosixPath(s).name


class OutputPaths:
    """Resolves primary → fallback output locations and records what happened."""

    def __init__(self, cfg: Config, out_dir: Path | None = None):
        self.cfg = cfg
        self.notes: list[str] = []
        if out_dir is not None:
            out_dir = Path(out_dir)
            self.html = out_dir / _basename(cfg.output_html)
            self.csv = out_dir / _basename(cfg.output_csv)
            self.snapshots = out_dir / "snapshots"
        else:
            self.html = self._pick(Path(cfg.output_html), "dashboard")
            self.csv = self._pick(Path(cfg.output_csv), "results CSV")
            self.snapshots = self._pick_dir(Path(cfg.snapshot_dir), "snapshots")
        # history lives beside the dashboard so a relative <script src> finds it
        self.history = self.html.with_name(self.html.stem + ".history.js")

    def _writable_dir(self, d: Path) -> bool:
        try:
            d.mkdir(parents=True, exist_ok=True)
            probe = d / f".probe_{os.getpid()}"
            probe.write_text("x", encoding="utf-8")
            probe.unlink()
            return True
        except Exception:
            return False

    def _pick(self, primary: Path, label: str) -> Path:
        if self._writable_dir(primary.parent):
            return primary
        fb = Path(self.cfg.fallback_dir) / _basename(primary)
        fb.parent.mkdir(parents=True, exist_ok=True)
        self.notes.append(f"{label}: '{primary.parent}' not writable → using '{fb.parent}'")
        return fb

    def _pick_dir(self, primary: Path, label: str) -> Path:
        if self._writable_dir(primary):
            return primary
        fb = Path(self.cfg.fallback_dir) / _basename(primary)
        fb.mkdir(parents=True, exist_ok=True)
        self.notes.append(f"{label}: '{primary}' not writable → using '{fb}'")
        return fb


def _atomic_replace(tmp: Path, path: Path, retries: int, sleep: float) -> None:
    last = None
    for attempt in range(1, retries + 1):
        try:
            tmp.replace(path)
            return
        except PermissionError as e:       # OneDrive / Drive holding a lock
            last = e
            if attempt < retries:
                time.sleep(sleep * attempt)
    raise last


def atomic_write_text(path: Path, text: str, cfg: Config = CONFIG) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    _atomic_replace(tmp, path, cfg.write_retries, cfg.write_retry_sleep)


def atomic_write_csv(df: pd.DataFrame, path: Path, cfg: Config = CONFIG) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    df.to_csv(tmp, index=False)
    _atomic_replace(tmp, path, cfg.write_retries, cfg.write_retry_sleep)


# =============================================================================
#  1. DATA
# =============================================================================

class DataHealth:
    """Collects everything the Health tab shows."""

    def __init__(self):
        self.skipped: list[dict] = []       # {ticker, reason}
        self.short: list[dict] = []         # {ticker, bars}
        self.stale: list[dict] = []         # {ticker, last_bar, as_of}
        self.illiquid: list[dict] = []      # {ticker, dollar_vol, price}
        self.partial_dropped: list[str] = []
        self.live_bars: list[str] = []      # tickers scored on today's live/forming bar
        self.notes: list[str] = []
        self.source: str = ""
        self.benchmark_note: str = ""
        self.timings: dict = {}


def _tidy(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(c).lower() for c in df.columns]
    need = ["open", "high", "low", "close", "volume"]
    missing = [c for c in need if c not in df.columns]
    if missing:
        raise ValueError(f"missing columns {missing}")
    df = df[need].apply(pd.to_numeric, errors="coerce")
    df = df.dropna(subset=["close"])
    df = df[~df.index.duplicated(keep="last")].sort_index()
    df.index = pd.to_datetime(df.index).tz_localize(None).normalize()
    return df


def _yf():
    try:
        import yfinance as yf  # lazy: --demo / --selftest need no network stack
    except ImportError as e:
        raise RuntimeError("yfinance is not installed (pip install yfinance)") from e
    return yf


def _yf_download(tickers, period: str, cfg: Config, *, group_by="ticker", threads=True):
    yf = _yf()
    last_err = None
    for attempt in range(1, cfg.yf_retries + 1):
        try:
            raw = yf.download(tickers, period=period, interval="1d", auto_adjust=True,
                              group_by=group_by, progress=False, threads=threads)
            if raw is not None and len(raw) > 0:
                return raw
            last_err = "empty response"
        except Exception as e:
            last_err = e
        if attempt < cfg.yf_retries:
            log_warn(f"Download attempt {attempt} failed ({last_err}); retrying in {cfg.yf_retry_sleep}s…")
            time.sleep(cfg.yf_retry_sleep)
    raise RuntimeError(f"yfinance download failed after {cfg.yf_retries} attempts: {last_err}")


def _split_batch(raw, batch: list[str], cfg: Config, out: dict, fail: dict) -> None:
    """Pull each ticker of a batch response into `out`; record why others failed."""
    for t in batch:
        try:
            if raw is None:
                raise ValueError("no response")
            if isinstance(raw.columns, pd.MultiIndex):
                if t not in raw.columns.get_level_values(0):
                    raise ValueError("not in batch response")
                df = _tidy(raw[t])
            elif len(batch) == 1:
                df = _tidy(raw)
            else:
                raise ValueError("not in batch response")
            if len(df) < cfg.min_load_bars:
                raise ValueError(f"only {len(df)} bars")
            out[t] = df
            fail.pop(t, None)
        except Exception as e:
            fail[t] = str(e)[:80]


def fetch_prices(tickers: list[str], period: str, cfg: Config, health: DataHealth) -> dict[str, pd.DataFrame]:
    """Chunked download with retries: chunk -> smaller-chunk retries -> one at a time.
    Yahoo silently drops names from big batches, so a missing ticker is retried
    before it is declared skipped."""
    out: dict[str, pd.DataFrame] = {}
    fail: dict[str, str] = {}

    def run(batch: list[str], threads: bool) -> None:
        try:
            raw = _yf_download(batch, period, cfg, group_by="ticker", threads=threads)
        except Exception as e:
            raw = None
            for t in batch:
                fail[t] = str(e)[:80]
            log_warn(f"Download chunk of {len(batch)} failed ({e})")
            return
        _split_batch(raw, batch, cfg, out, fail)

    size = max(1, int(cfg.yf_batch_size))
    for k in range(0, len(tickers), size):
        run(tickers[k:k + size], threads=True)
        if k + size < len(tickers):
            time.sleep(cfg.yf_chunk_sleep)
    first_miss = len(fail)

    for rnd in range(1, cfg.yf_retry_rounds + 1):
        todo = [t for t in tickers if t in fail]
        if not todo:
            break
        log_warn(f"Retry round {rnd}: re-requesting {len(todo)} ticker(s) that came back missing")
        time.sleep(cfg.yf_retry_sleep * rnd)
        step = max(1, int(cfg.yf_retry_chunk))
        for k in range(0, len(todo), step):
            run(todo[k:k + step], threads=False)
            time.sleep(cfg.yf_chunk_sleep)

    todo = [t for t in tickers if t in fail]
    if todo:
        log_warn(f"Fetching {len(todo)} remaining ticker(s) one at a time")
    for t in todo:
        try:
            df = fetch_one(t, period, cfg)
            if len(df) < cfg.min_load_bars:
                fail[t] = f"only {len(df)} bars"
            else:
                out[t] = df
                fail.pop(t, None)
        except Exception as e:
            fail[t] = str(e)[:80]
        time.sleep(0.3)

    recovered = first_miss - len(fail)
    if recovered > 0:
        health.notes.append(f"Download retry recovered {recovered} of {first_miss} ticker(s) missing from the first pass")
        log_ok(f"Retry recovered {recovered} of {first_miss} missing ticker(s)")
    for t in tickers:
        if t in fail:
            health.skipped.append({"ticker": t, "reason": fail[t]})
    return out


def fetch_one(ticker: str, period: str, cfg: Config) -> pd.DataFrame:
    raw = _yf_download(ticker, period, cfg, group_by="column", threads=False)
    if isinstance(raw.columns, pd.MultiIndex):
        raw.columns = raw.columns.droplevel(1)
    return _tidy(raw)


def market_session_closed(now: datetime | None = None) -> bool:
    """True once the regular US session has closed for today's date (ET)."""
    now = now or datetime.now(MARKET_TZ)
    now = now.astimezone(MARKET_TZ)
    return (now.hour, now.minute) >= (16, 5)


def apply_intraday_bar(prices: dict[str, pd.DataFrame], cfg: Config, health: DataHealth,
                       now: datetime | None = None) -> dict[str, pd.DataFrame]:
    """While the regular session is open, today's bar is still forming: its
    Close is the current, live price (the daily download already reflects it
    — that's the only thing that changes bar to bar during the day). By
    default we KEEP that bar — every indicator (RSI, PPO, EMAs …) and the
    Buy/Sell scoring then run on the current price, exactly like any other
    day, so the dashboard reflects what the ticker is doing right now
    instead of yesterday's close.

    Set cfg.drop_partial_bar = True (--eod-only on the CLI) to fall back to
    the old, conservative behaviour: ignore today's bar entirely until it is
    a confirmed close."""
    now = now or datetime.now(MARKET_TZ)
    today = pd.Timestamp(now.astimezone(MARKET_TZ).date())
    if market_session_closed(now):
        return prices
    out = {}
    for t, df in prices.items():
        is_todays_bar = len(df) and df.index[-1] == today
        if is_todays_bar and cfg.drop_partial_bar:
            df = df.iloc[:-1]
            health.partial_dropped.append(t)
        elif is_todays_bar:
            health.live_bars.append(t)
        out[t] = df
    if health.live_bars:
        ts = now.astimezone(MARKET_TZ).strftime("%I:%M %p %Z")
        health.notes.append(
            f"Market open — using the live current price for {len(health.live_bars)} "
            f"ticker(s) as of {ts}; today's bar is still forming and will finalize at the close"
        )
    if health.partial_dropped:
        health.notes.append(
            f"Session still open — ignored today's live bar for {len(health.partial_dropped)} "
            f"ticker(s) (--eod-only); using the last confirmed close instead"
        )
    return out


# ---- Synthetic data for --demo / tests ---------------------------------------

FX_DEMO = ("FXE", "FXY", "FXB", "FXF", "FXA", "FXC", "FXS", "FXM", "UUP")


def synthetic_prices(tickers: list[str], n_bars: int = 520, seed: int = 7,
                     end: pd.Timestamp | None = None) -> dict[str, pd.DataFrame]:
    """Regime-switching GBM with a shared market factor. Deterministic."""
    rng = np.random.default_rng(seed)
    end = end or pd.Timestamp(datetime.now(MARKET_TZ).date()) - pd.tseries.offsets.BDay(1)
    idx = pd.bdate_range(end=end, periods=n_bars)
    mkt = rng.normal(0.0004, 0.010, n_bars)
    out = {}
    for i, t in enumerate(tickers):
        n = n_bars
        # a few special cases to exercise the health checks
        if t in ("CRCL", "CRWV", "SAIL", "Q"):
            n = int(rng.integers(90, 260))            # recent IPOs → short history
        if t == "DRNZ":
            n = 40                                    # too short → skipped
        beta = rng.uniform(0.6, 1.8)
        vol = rng.uniform(0.012, 0.045)
        if t in ("RGTI", "WULF", "APLD", "CIFR"):
            vol = rng.uniform(0.06, 0.09)             # 100%+ annualised vol
        if t in FX_DEMO:                              # currency funds: low vol, ~no equity beta
            vol = 0.003 + 0.0015 * (i % 3)
            beta = 0.15 * (-1) ** i
        # regime drift: alternating trends
        seg = rng.integers(40, 120)
        drift = np.repeat(rng.normal(0.0, 0.0025, n // seg + 2), seg)[:n]
        if t in FX_DEMO:
            drift = drift * 0.2
        r = drift + beta * mkt[-n:] + rng.normal(0, vol, n)
        close = 100 * np.exp(np.cumsum(r)) * rng.uniform(0.2, 4.0)
        if t == "PKOH":
            close = close * 0.02                      # sub-$5 → illiquid flag
        hi = close * (1 + np.abs(rng.normal(0, 0.006, n)))
        lo = close * (1 - np.abs(rng.normal(0, 0.006, n)))
        op = np.r_[close[0], close[:-1]] * (1 + rng.normal(0, 0.003, n))
        volu = rng.lognormal(13.5, 0.5, n) * (1 + 0.6 * np.abs(r) / vol)
        if t in ("SMP", "PLPC"):
            volu = volu * 0.002                       # thin
        df = pd.DataFrame({"open": op, "high": hi, "low": lo, "close": close, "volume": volu},
                          index=idx[-n:])
        if t == "KOID":
            df = df.iloc[:-6]                         # stale: halted 6 sessions ago
        out[t] = df
    return out


# =============================================================================
#  2. NATIVE INDICATORS (vectorised)
# =============================================================================

def ema(s: pd.Series, n: int) -> pd.Series:
    return s.ewm(span=n, adjust=False, min_periods=n).mean()


def wilder(s: pd.Series, n: int) -> pd.Series:
    return s.ewm(alpha=1.0 / n, adjust=False, min_periods=n).mean()


def rsi(close: pd.Series, n: int = 14) -> pd.Series:
    d = close.diff()
    up = d.clip(lower=0.0)
    dn = (-d).clip(lower=0.0)
    au, ad = wilder(up, n), wilder(dn, n)
    rs = au / ad.replace(0, np.nan)
    out = 100 - 100 / (1 + rs)
    out = out.where(ad != 0, 100.0)
    return out.where(~(au.isna() | ad.isna()))


def true_range(h: pd.Series, l: pd.Series, c: pd.Series) -> pd.Series:
    pc = c.shift(1)
    return pd.concat([h - l, (h - pc).abs(), (l - pc).abs()], axis=1).max(axis=1)


def atr(h, l, c, n: int = 14) -> pd.Series:
    return wilder(true_range(h, l, c), n)


def adx_dmi(h: pd.Series, l: pd.Series, c: pd.Series, n: int = 14) -> pd.DataFrame:
    up = h.diff()
    dn = -l.diff()
    plus_dm = pd.Series(np.where((up > dn) & (up > 0), up, 0.0), index=h.index)
    minus_dm = pd.Series(np.where((dn > up) & (dn > 0), dn, 0.0), index=h.index)
    tr_s = wilder(true_range(h, l, c), n).replace(0, np.nan)
    pdi = 100 * wilder(plus_dm, n) / tr_s
    mdi = 100 * wilder(minus_dm, n) / tr_s
    dx = 100 * (pdi - mdi).abs() / (pdi + mdi).replace(0, np.nan)
    adx = wilder(dx, n)
    return pd.DataFrame({"ADX": adx, "DMP": pdi, "DMN": mdi})


def bbands(close: pd.Series, n: int = 20, k: float = 2.0) -> pd.DataFrame:
    mid = close.rolling(n).mean()
    sd = close.rolling(n).std(ddof=0)
    return pd.DataFrame({"lower": mid - k * sd, "mid": mid, "upper": mid + k * sd})


def keltner(h, l, c, n: int = 20, k: float = 1.5) -> pd.DataFrame:
    mid = ema(c, n)
    rng = ema(true_range(h, l, c), n)
    return pd.DataFrame({"lower": mid - k * rng, "mid": mid, "upper": mid + k * rng})


def rolling_slope(y: pd.Series, n: int) -> pd.Series:
    """OLS slope of y against 0..n-1 over a rolling window, fully vectorised."""
    idx = pd.Series(np.arange(len(y), dtype=float), index=y.index)
    sy = y.rolling(n).sum()
    sxy = (idx * y).rolling(n).sum()
    # shift window index so t runs 0..n-1: Σ k·y = Σ idx·y − (i−n+1)·Σ y
    start = idx - (n - 1)
    sky = sxy - start * sy
    sx = n * (n - 1) / 2.0
    sxx = (n - 1) * n * (2 * n - 1) / 6.0
    denom = n * sxx - sx * sx
    return (n * sky - sx * sy) / denom


def rolling_linreg_last(y: pd.Series, n: int) -> pd.Series:
    """Value of the rolling OLS line at the last point of the window."""
    slope = rolling_slope(y, n)
    mean_y = y.rolling(n).mean()
    return mean_y + slope * (n - 1) / 2.0


def obv(close: pd.Series, volume: pd.Series) -> pd.Series:
    sign = np.sign(close.diff()).fillna(0.0)
    return (sign * volume).cumsum()


def bars_since(flag: pd.Series) -> pd.Series:
    idx = np.arange(len(flag), dtype=float)
    last = pd.Series(np.where(flag.to_numpy(dtype=bool), idx, np.nan), index=flag.index).ffill()
    return pd.Series(idx, index=flag.index) - last


def momentum_layers(close: pd.Series, weights: dict) -> pd.DataFrame:
    frame = pd.DataFrame(index=close.index)
    for lb, w in weights.items():
        frame[f"Mom_{lb}d"] = close.pct_change(lb) * w
    cols = [f"Mom_{lb}d" for lb in weights]
    frame["Momentum_Blended"] = frame[cols].sum(axis=1, min_count=1)
    frame["Momentum_Direction"] = np.sign(frame["Momentum_Blended"].fillna(0.0))
    return frame


def trend_persistence(close: pd.Series, window: int = 20) -> pd.Series:
    r = close.pct_change()
    return r.rolling(window).corr(r.shift(1)).clip(-1, 1)


def ppo_block(close: pd.Series, cfg: Config) -> pd.DataFrame:
    fast, slow = ema(close, cfg.ppo_fast), ema(close, cfg.ppo_slow)
    ppo = (fast - slow) / slow * 100
    sig = ppo.ewm(span=cfg.ppo_sig, adjust=False, min_periods=cfg.ppo_sig).mean()
    hist = ppo - sig
    hp = hist.shift(1)
    pos_x = ((hist > 0) & (hp <= 0)).astype(int)
    neg_x = ((hist < 0) & (hp >= 0)).astype(int)
    # bars in current cross state: run length of sign(hist)
    sgn = np.sign(hist).fillna(0)
    run_id = (sgn != sgn.shift(1)).cumsum()
    bars_in = sgn.groupby(run_id).cumcount().astype(float)
    sep = (hist / sig.abs().clip(lower=0.01)).clip(-1, 1)
    expanding = (hist.abs() > hist.abs().shift(1)).astype(int)
    expand_up = ((hist > 0) & (hist > hist.shift(1))).astype(int)
    expand_dn = ((hist < 0) & (hist < hist.shift(1))).astype(int)
    w = cfg.ppo_persist_window
    frac_pos = (hist > 0).astype(float).rolling(w, min_periods=1).mean()
    frac_neg = (hist < 0).astype(float).rolling(w, min_periods=1).mean()
    pp = ppo.shift(1)
    zpos = ((ppo > 0) & (pp <= 0)).astype(int)
    zneg = ((ppo < 0) & (pp >= 0)).astype(int)
    return pd.DataFrame({
        "PPO": ppo, "PPO_Signal": sig, "PPO_Delta": hist, "PPO_Hist": hist,
        "PPO_Sig_Pos_Cross": pos_x, "PPO_Sig_Neg_Cross": neg_x,
        "PPO_Bars_In_Cross": bars_in,
        "PPO_Cross_Strength": sep.abs().fillna(0.0),
        "PPO_Hist_Expanding": expanding,
        "PPO_Hist_Expand_Up": expand_up,
        "PPO_Hist_Expand_Dn": expand_dn,
        "PPO_Persisted_Bull": (frac_pos > 0.6).astype(int),
        "PPO_Persisted_Bear": (frac_neg > 0.6).astype(int),
        "PPO_Above_Zero": (ppo > 0).astype(int),
        "PPO_Bars_Since_Pos": bars_since(pos_x),
        "PPO_Bars_Since_Neg": bars_since(neg_x),
        "PPO_Bars_Since_Zero_Pos": bars_since(zpos),
        "PPO_Bars_Since_Zero_Neg": bars_since(zneg),
    })


def squeeze_block(df: pd.DataFrame, cfg: Config) -> pd.DataFrame:
    h, l, c = df["high"], df["low"], df["close"]
    bb = bbands(c, cfg.sqz_bb_length, cfg.sqz_bb_std)
    kc = keltner(h, l, c, cfg.sqz_kc_length, cfg.sqz_kc_scalar)
    on = ((bb["lower"] > kc["lower"]) & (bb["upper"] < kc["upper"])).astype(int)
    off = ((bb["lower"] < kc["lower"]) & (bb["upper"] > kc["upper"])).astype(int)
    n = cfg.sqz_mom
    hh, ll = h.rolling(n).max(), l.rolling(n).min()
    basis = ((hh + ll) / 2 + c.rolling(n).mean()) / 2
    mom = rolling_linreg_last(c - basis, n)
    fired = ((on.shift(1) == 1) & (off == 1)).astype(int)
    recent = ((fired.rolling(cfg.sqz_recent_window, min_periods=1).max() > 0) & (on == 0)).astype(int)
    run = (on != on.shift(1)).cumsum()
    on_count = on.groupby(run).cumsum()
    run_len = on.groupby(run).transform("size")
    last_on_len = (run_len * on).replace(0, np.nan).ffill().fillna(0)
    prior_len = np.where(on == 1, on_count, last_on_len).astype(int)
    return pd.DataFrame({
        "Squeeze_On": on, "Squeeze_Off": off, "Squeeze_Mom": mom,
        "Squeeze_Mom_Pct": (mom / c.replace(0, np.nan)) * 100,
        "Squeeze_Fired": fired, "Squeeze_Recent_Fire": recent,
        "Squeeze_On_Count": on_count, "Squeeze_Prior_Length": prior_len,
    })


def volatility_block(df: pd.DataFrame, cfg: Config) -> pd.DataFrame:
    h, l, c = df["high"], df["low"], df["close"]
    a = atr(h, l, c, 14)
    bb = bbands(c, 20, 2.0)
    hv = c.pct_change().rolling(20).std() * np.sqrt(252) * 100
    rel = 1.0 - (1.0 - cfg.min_reliability) * (hv / 100.0).clip(0, 1)
    return pd.DataFrame({
        "ATR_Pct": a / c * 100,
        "BB_Width": (bb["upper"] - bb["lower"]) / c * 100,
        "Historical_Vol": hv,
        "Signal_Reliability": rel,
    })


def pmo_block(close: pd.Series, cfg: Config) -> pd.DataFrame:
    """Carl Swenlin's Price Momentum Oscillator (DecisionPoint).

        ROC      = 1-day % change
        stage 1  = custom EMA of ROC, multiplier 2/35
        PMO      = custom EMA (multiplier 2/20) of 10 x stage 1
        signal   = standard 10-period EMA of the PMO

    INFORMATIONAL ONLY: shown on the Ticker tab, never used in scoring. The
    first (roc_len + smooth_len) bars are blanked while the smoothing warms up.
    """
    roc = (close / close.shift(1) - 1.0) * 100.0
    s1 = roc.ewm(alpha=2.0 / cfg.pmo_roc_len, adjust=False).mean()
    pmo = (10.0 * s1).ewm(alpha=2.0 / cfg.pmo_smooth_len, adjust=False).mean()
    pmo.iloc[:cfg.pmo_roc_len + cfg.pmo_smooth_len] = np.nan
    sig = pmo.ewm(span=cfg.pmo_sig_len, adjust=False).mean()
    return pd.DataFrame({"PMO": pmo, "PMO_Signal": sig})


def compute_indicator_frame(df: pd.DataFrame, cfg: Config) -> pd.DataFrame:
    """All raw indicators for one ticker, for every bar."""
    c = df["close"]
    fr = momentum_layers(c, cfg.mom_weights)
    ad = adx_dmi(df["high"], df["low"], c, 14)
    fr["ADX_Trend"] = ad["ADX"]
    fr["DMI_Value"] = ad["DMP"] - ad["DMN"]
    fr["High_52W_Ratio"] = c / c.rolling(252, min_periods=126).max()
    fr = fr.join(ppo_block(c, cfg))
    fr = fr.join(pmo_block(c, cfg))      # informational only (Ticker tab) - not scored
    obv_norm = obv(c, df["volume"]) / df["volume"].rolling(cfg.liq_window).mean().replace(0, np.nan)
    fr["OBV_slope"] = rolling_slope(obv_norm, cfg.liq_window)
    fr["RSI_14"] = rsi(c, 14)
    fr["Trend_Persistence"] = trend_persistence(c, cfg.persist_window)
    fr = fr.join(squeeze_block(df, cfg))
    fr = fr.join(volatility_block(df, cfg))
    # v54: volatility-adjusted copies of the return components and the PPO histogram, used only for
    # the universe ranking (the raw columns are untouched and still drive the scores).
    sig_d = c.pct_change().rolling(cfg.vol_adj_window, min_periods=20).std()
    sig_d = sig_d.clip(lower=cfg.vol_adj_floor_ann / 100.0 / np.sqrt(252))
    va_cols = []
    for lb in cfg.mom_weights:
        fr[f"Mom_{lb}d_VA"] = fr[f"Mom_{lb}d"] / (sig_d * np.sqrt(lb))
        va_cols.append(f"Mom_{lb}d_VA")
    fr["Momentum_Blended_VA"] = fr[va_cols].sum(axis=1, min_count=1)
    fr["PPO_Delta_VA"] = fr["PPO_Delta"] / fr["ATR_Pct"].where(fr["ATR_Pct"] > 0)
    e20, e50, e200 = ema(c, cfg.ema_fast), ema(c, cfg.ema_mid), ema(c, cfg.ema_slow)
    fr["EMA20"], fr["EMA50"], fr["EMA200"] = e20, e50, e200
    fr["Close_vs_EMA20"] = (c / e20 - 1) * 100
    fr["Close_vs_EMA50"] = (c / e50 - 1) * 100
    fr["Close_vs_EMA200"] = (c / e200 - 1) * 100
    fr["Below_EMA20"] = (c < e20).astype(int)
    fr["Below_EMA50"] = (c < e50).astype(int)
    fr["Below_EMA200"] = (c < e200).astype(int)
    fr["EMA_Bull_Stack"] = ((e20 > e50) & (e50 > e200)).astype(int)
    fr["Last_Close"] = c
    fr["High"] = df["high"]
    fr["Low"] = df["low"]
    fr["Open"] = df["open"]
    fr["Ret_1d"] = c.pct_change() * 100
    fr["Ret_20d"] = c.pct_change(cfg.rs_lookback) * 100
    rng = (df["high"] - df["low"]).replace(0, np.nan)
    fr["Close_Loc"] = ((c - df["low"]) / rng).clip(0, 1)
    fr["Volume"] = df["volume"]
    fr["Dollar_Volume"] = c * df["volume"]
    fr["Dollar_Volume_20d"] = fr["Dollar_Volume"].rolling(cfg.liq_window, min_periods=15).median()
    fr["Vol_Ratio"] = fr["Dollar_Volume"] / fr["Dollar_Volume_20d"].replace(0, np.nan)
    return fr


# =============================================================================
#  3. COMPOSITES, REGIME & SCORING  (all vectorised over a DataFrame)
# =============================================================================

def build_distribution(frames: dict[str, pd.DataFrame], components: list[str]) -> dict:
    """Sorted arrays of each component, used for percentile anchoring."""
    dist = {}
    for comp in components:
        parts = [f[comp].to_numpy(dtype=float) for f in frames.values() if comp in f.columns]
        if not parts:
            continue
        vals = np.concatenate(parts)
        vals = vals[np.isfinite(vals)]
        if len(vals) >= 50:
            dist[comp] = np.sort(vals)
    return dist


def pct_vs_dist(values: pd.Series, arr: np.ndarray) -> pd.Series:
    v = values.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    ok = np.isfinite(v)
    out[ok] = 100.0 * np.searchsorted(arr, v[ok], side="right") / len(arr)
    return pd.Series(out, index=values.index)


def blend(df: pd.DataFrame, weights: dict, dist: dict) -> pd.Series:
    """Weighted percentile blend; weights renormalised per row over the
    components that are actually present (fixes NaN→50 for young tickers)."""
    parts, ws = [], []
    for comp, w in weights.items():
        if comp not in df.columns:
            continue
        arr = dist.get(comp)
        p = pct_vs_dist(df[comp], arr) if arr is not None else 100 * df[comp].rank(pct=True)
        parts.append(p.to_numpy(dtype=float))
        ws.append(float(w))
    if not parts:
        return pd.Series(np.nan, index=df.index)
    P = np.column_stack(parts)
    W = np.broadcast_to(np.array(ws), P.shape).copy()
    W[~np.isfinite(P)] = 0.0
    P = np.nan_to_num(P)
    tot = W.sum(axis=1)
    out = np.where(tot > 0, (P * W).sum(axis=1) / np.where(tot > 0, tot, 1), np.nan)
    return pd.Series(out, index=df.index)


def causal_pct_from_ref(dates, values, ref: pd.Series, lookback: int, min_obs: int) -> np.ndarray:
    """Percentile of `values` vs `ref` observations strictly before each date."""
    out = np.full(len(values), np.nan)
    ref = ref.dropna().sort_index()
    if ref.empty:
        return out
    rns = pd.DatetimeIndex(pd.to_datetime(ref.index)).asi8
    rval = ref.to_numpy(dtype=float)
    dns = pd.DatetimeIndex(pd.to_datetime(dates)).asi8
    vals = np.asarray(values, dtype=float)
    for d in np.unique(dns):
        end = int(np.searchsorted(rns, d, side="left"))
        start = max(0, end - lookback)
        arr = rval[start:end]
        arr = arr[np.isfinite(arr)]
        if len(arr) < min_obs:
            continue
        arr.sort()
        rows = dns == d
        vv = vals[rows]
        sl = np.full(rows.sum(), np.nan)
        ok = np.isfinite(vv)
        sl[ok] = 100.0 * np.searchsorted(arr, vv[ok], side="right") / len(arr)
        out[rows] = sl
    return out


def blend_causal(df: pd.DataFrame, weights: dict, dist: dict, ref_frame, dates,
                 cfg: Config) -> pd.Series:
    """Causal percentile blend when a dated reference frame is available."""
    parts, ws = [], []
    for comp, w in weights.items():
        if comp not in df.columns:
            continue
        if ref_frame is not None and comp in ref_frame.columns and dates is not None:
            p = causal_pct_from_ref(dates, df[comp].to_numpy(dtype=float),
                                    ref_frame[comp], cfg.pctile_lookback, cfg.pctile_min_obs)
        else:
            arr = dist.get(comp)
            p = pct_vs_dist(df[comp], arr).to_numpy(dtype=float) if arr is not None \
                else (100 * df[comp].rank(pct=True)).to_numpy(dtype=float)
        parts.append(p)
        ws.append(float(w))
    if not parts:
        return pd.Series(np.nan, index=df.index)
    P = np.column_stack(parts)
    W = np.broadcast_to(np.array(ws), P.shape).copy()
    W[~np.isfinite(P)] = 0.0
    P = np.nan_to_num(P)
    tot = W.sum(axis=1)
    out = np.where(tot > 0, (P * W).sum(axis=1) / np.where(tot > 0, tot, 1), np.nan)
    return pd.Series(out, index=df.index)


def blend_universe(df: pd.DataFrame, weights: dict, dates, cfg: Config) -> tuple[pd.Series, pd.Series]:
    """v54: cross-sectional percentile blend. Each component is ranked across the rows that share a
    date (0-100, highest = 100), using the volatility-adjusted column when there is one. Causal by
    construction: a bar is only compared with other names on the SAME bar. Returns (blend, names on
    that date); weights are renormalised per row over the components that are present."""
    key = pd.Series(pd.to_datetime(np.asarray(dates)), index=df.index)
    parts, ws = [], []
    for comp, w in weights.items():
        col = comp + "_VA" if (cfg.vol_adjust_momentum and comp + "_VA" in df.columns) else comp
        if col not in df.columns:
            continue
        v = pd.to_numeric(df[col], errors="coerce")
        parts.append((100.0 * v.groupby(key).rank(pct=True)).to_numpy(dtype=float))
        ws.append(float(w))
    n_date = key.groupby(key).transform("size").astype(float)
    if not parts:
        return pd.Series(np.nan, index=df.index), n_date
    P = np.column_stack(parts)
    W = np.broadcast_to(np.array(ws), P.shape).copy()
    W[~np.isfinite(P)] = 0.0
    P = np.nan_to_num(P)
    tot = W.sum(axis=1)
    out = np.where(tot > 0, (P * W).sum(axis=1) / np.where(tot > 0, tot, 1), np.nan)
    return pd.Series(out, index=df.index), n_date


def add_composites(df: pd.DataFrame, cfg: Config, dist: dict,
                   ref_frame=None, universe: bool = False) -> pd.DataFrame:
    dates = None
    if "Date" in df.columns:
        dates = df["Date"]
    elif isinstance(df.index, pd.DatetimeIndex):
        dates = df.index
    use = pd.Series(False, index=df.index)
    if universe and dates is not None and len(df):
        # v54: rank across the universe; thin dates fall back to the benchmark anchor below
        tb, n_date = blend_universe(df, cfg.trailing_weights, dates, cfg)
        eb, _ = blend_universe(df, cfg.emerging_weights, dates, cfg)
        use = n_date >= cfg.xs_min_names
        df["Rank_N"] = np.where(use, n_date, 0).astype(int)
        if (~use).any():
            sub = df[~use]
            sub_dates = pd.Series(np.asarray(dates), index=df.index)[~use]
            tb = tb.where(use, blend_causal(sub, cfg.trailing_weights, dist, ref_frame, sub_dates, cfg).reindex(df.index))
            eb = eb.where(use, blend_causal(sub, cfg.emerging_weights, dist, ref_frame, sub_dates, cfg).reindex(df.index))
    else:
        tb = blend_causal(df, cfg.trailing_weights, dist, ref_frame, dates, cfg)
        eb = blend_causal(df, cfg.emerging_weights, dist, ref_frame, dates, cfg)
        df["Rank_N"] = 0
    df["Momentum_Trailing_Pctile"] = tb.round(1)
    df["Momentum_Emerging_Pctile"] = eb.round(1)
    df["Momentum_Pctile"] = (0.60 * tb + 0.40 * eb).round(1)
    # v54: RS Rating 1-99 = the blended percentile as a whole number (rank in the universe when Rank_N > 0)
    df["RS_Rating"] = df["Momentum_Pctile"].round().clip(1, 99)
    df["Momentum_Dormancy_Pctile"] = (100 - tb).round(1)
    t = tb.fillna(50).to_numpy()
    e = eb.fillna(50).to_numpy()
    hi, lo, gap = cfg.regime_hi, cfg.regime_lo, cfg.regime_gap
    conds = [
        (t >= hi) & (e >= hi),
        (t < lo) & (e < lo),
        e > t + gap,
        t > e + gap,
    ]
    labels = ["Strong", "Weak", "Dormant→Waking", "Mature/Cooling"]
    df["Regime"] = np.select(conds, labels, default="Neutral")
    conf = np.select(conds, [
        np.minimum((t + e) / 100, 1.0),
        np.minimum((200 - t - e) / 200, 1.0),
        np.minimum((e - t) / 50, 1.0),
        np.minimum((t - e) / 50, 1.0),
    ], default=0.4)
    df["Regime_Confidence"] = np.round(conf, 2)
    return df


BUY_REGIME_W = {
    "Strong": (1.0, 0.6, 0.7), "Dormant→Waking": (1.2, 0.7, 0.8), "Neutral": (1.0, 0.8, 0.9),
    "Mature/Cooling": (0.8, 0.9, 1.1), "Weak": (1.5, 0.4, 1.2),
}
SELL_REGIME_W = {
    "Strong": (0.6, 1.0, 0.8), "Dormant→Waking": (0.7, 0.9, 0.7), "Neutral": (0.8, 0.9, 0.9),
    "Mature/Cooling": (1.1, 1.2, 1.0), "Weak": (0.9, 1.0, 1.1),
}


def _regime_w(regime: pd.Series, table: dict, k: int) -> np.ndarray:
    return regime.map(lambda r: table.get(r, table["Neutral"])[k]).to_numpy(dtype=float)


def _col(df, name, default=0.0) -> np.ndarray:
    if name in df.columns:
        return df[name].astype(float).fillna(default).to_numpy()
    return np.full(len(df), float(default))


def rsi_zone_arrays(r: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Vectorised RSI zone + confidence (0-1)."""
    zone = np.full(len(r), "Unknown", dtype=object)
    conf = np.zeros(len(r))
    ok = np.isfinite(r)
    z = np.select(
        [r < 30, r < 40, r <= 65, r <= 75, r > 75],
        ["Oversold", "Weak", "Healthy", "Overheated", "Extreme"], default="Unknown")
    c = np.select(
        [r < 30, r < 40, r <= 65, r <= 75, r > 75],
        [np.minimum(r / 30, 1.0), (40 - r) / 10, 1 - np.abs(r - 52.5) / 12.5,
         (r - 65) / 10, np.minimum((r - 75) / 5, 1.0)], default=0.0)
    zone[ok] = z[ok]
    conf[ok] = np.clip(c[ok], 0, 1)
    return zone, conf


def liquidity_floor(tickers, cfg: Config) -> np.ndarray:
    """Per-ticker 20-day median dollar-volume floor: lower for the Currency and Country ETF groups."""
    t = pd.Index(tickers)
    return np.select([t.isin(cfg.currency_group), t.isin(cfg.country_group)],
                     [cfg.currency_min_dollar_vol, cfg.country_min_dollar_vol],
                     default=cfg.min_dollar_vol).astype(float)


def score_frame(df: pd.DataFrame, cfg: Config) -> pd.DataFrame:
    """Buy/Sell confidence + components + alerts + recommendation, vectorised.
    Works on the latest-bar panel (one row per ticker) and on a full history
    (one row per bar) identically — that is what makes the scorecard possible."""
    n = len(df)
    regime = df["Regime"] if "Regime" in df.columns else pd.Series(["Neutral"] * n, index=df.index)
    rel = np.clip(_col(df, "Signal_Reliability", 1.0), 0, 1)
    # v54: one volatility discount for both sides (rel_b = rel_s = rel_sx). Pre-v54 the buy side took
    # the full discount and the sell-side PPO points a much lighter one, which pushed every volatile
    # name's Net Bias negative.
    if cfg.symmetric_scoring:
        rel_b = rel_s = rel_sx = 1 - cfg.vol_damping * (1 - rel)
    else:
        rel_b = rel_s = rel
        rel_sx = 1 - cfg.sell_vol_damping_on_cross * (1 - rel)
    rsi_v = _col(df, "RSI_14", np.nan)
    zone, zconf = rsi_zone_arrays(rsi_v)
    ppo_d = _col(df, "PPO_Delta")
    mdir = _col(df, "Momentum_Direction")
    strength = np.clip(_col(df, "PPO_Cross_Strength"), 0, 1)
    expand_up = _col(df, "PPO_Hist_Expand_Up")
    expand_dn = _col(df, "PPO_Hist_Expand_Dn")
    above0 = _col(df, "PPO_Above_Zero")
    persist = np.maximum(_col(df, "Trend_Persistence"), 0)
    b20, b50, b200 = _col(df, "Below_EMA20"), _col(df, "Below_EMA50"), _col(df, "Below_EMA200")
    bs_pos = _col(df, "PPO_Bars_Since_Pos", 99)
    bs_neg = _col(df, "PPO_Bars_Since_Neg", 99)
    bs_pos = np.where(np.isfinite(bs_pos), bs_pos, 99)
    bs_neg = np.where(np.isfinite(bs_neg), bs_neg, 99)
    bzp = np.nan_to_num(_col(df, "PPO_Bars_Since_Zero_Pos", 99), nan=99)
    bzn = np.nan_to_num(_col(df, "PPO_Bars_Since_Zero_Neg", 99), nan=99)
    fb = cfg.ppo_fresh_bars
    fresh_bull = bs_pos <= fb
    fresh_bear = bs_neg <= fb
    zero_up = bzp <= fb
    zero_dn = bzn <= fb
    hi52 = _col(df, "High_52W_Ratio", 1.0)
    atr_pct = _col(df, "ATR_Pct", 0.0)
    vol_ratio = _col(df, "Vol_Ratio", 1.0)
    close_loc = _col(df, "Close_Loc", 0.5)
    sq_rel = _col(df, "SQ_Release")
    sq_ppo = _col(df, "SQ_PPO_Turning")
    sq_room = _col(df, "SQ_Room_To_Run")
    sq_on = _col(df, "Squeeze_On")
    sq_mom = _col(df, "Squeeze_Mom")

    # RSI location multipliers (context, not a standalone pillar)
    rsi_buy_m = np.select(
        [zone == "Oversold", zone == "Weak", zone == "Healthy", zone == "Overheated", zone == "Extreme"],
        [1.15, 1.15, 1.00, 0.70, 0.00], default=1.00)
    rsi_sell_m = np.select(
        [zone == "Extreme", zone == "Overheated", zone == "Healthy", zone == "Weak", zone == "Oversold"],
        [1.15, 1.15, 1.00, 0.85, 0.65], default=1.00)
    # Oversold + still falling PPO: don't treat as a quality sell unless EMA50 is lost
    rsi_sell_m = np.where((zone == "Oversold") & (b50 == 0), 0.40, rsi_sell_m)

    # ---------------- BUY (PPO trigger + modifiers) ----------------
    wp, wr, we = (_regime_w(regime, BUY_REGIME_W, k) for k in range(3))
    fresh = np.maximum(0, 1 - bs_pos / 5.0)
    # 18 base for a fresh ↑, +8 signed expand, +9 fresh zero↑ / +4 already above zero
    b_base = 18.0 * fresh
    b_exp = 8.0 * expand_up * np.maximum(fresh, 0.4)
    b_zero = np.where(zero_up, 9.0, np.where(above0 > 0, 4.0, 0.0))
    b_str = 1.0 + 0.50 * strength
    b_ppo = np.minimum(np.floor((b_base + b_exp + b_zero) * b_str * wp * rel_b), 35)
    # RSI shown as points = residual after multiplier vs 1.0, plus a small zone tag
    buy_pre = b_ppo
    b_rsi = np.floor(np.clip((rsi_buy_m - 1.0) * np.maximum(b_ppo, 12) + np.select(
        [zone == "Oversold", zone == "Weak", zone == "Healthy"],
        [6.0, 4.0, 2.0], default=0.0) * wr * rel_b, 0, 18))
    ema_cnt = (1 - b20) + (1 - b50) + (1 - b200)
    b_ema = np.floor(12 * ema_cnt / 3.0 * we)
    b_ema = np.floor(np.where(ppo_d < 0, b_ema * 0.5, b_ema))
    # below EMA200: only keep EMA points in Dormant→Waking with squeeze room
    dorm = regime.eq("Dormant→Waking").to_numpy() if hasattr(regime, "eq") else np.array([str(x) == "Dormant→Waking" for x in regime])
    b_ema = np.where((b200 == 1) & ~((dorm == True) & (sq_room > 0) & (sq_rel > 0)), np.floor(b_ema * 0.35), b_ema)
    # crowded 52w high without squeeze room
    b_ema = np.where((hi52 > 0.97) & (sq_rel == 0), np.floor(b_ema * 0.6), b_ema)
    rising = (mdir > 0) | (ppo_d > 0)
    b_per = np.where(rising, np.floor(8 * persist * rel_b), 0)
    b_sqz = np.minimum(cfg.sqz_buy_add_cap, (6 * (sq_rel > 0) + 3 * (sq_ppo > 0) + 3 * (sq_room > 0)))
    buy = np.minimum(b_ppo + b_rsi + b_ema + b_per + b_sqz, 100)
    # v54: a fresh bullish cross that is still in force gets the mirror image of the sell floor
    # (below every buy threshold, so the cross alone is "review", never an alert).
    buy_floored = np.zeros(n, dtype=bool)
    if cfg.symmetric_scoring:
        buy_floored = fresh_bull & (ppo_d > 0) & (buy < cfg.buy_cross_floor)
        buy = np.where(fresh_bull & (ppo_d > 0), np.maximum(buy, cfg.buy_cross_floor), buy)
    # v46: alert thresholds are needed here so the RSI-Extreme cap is relative to the threshold
    # actually in force (regime + ATR bump). The old cap used the global 40 - 1 = 39, which still
    # cleared the 35 threshold of the Strong and Dormant->Waking regimes.
    buy_thr = regime.map(lambda r: cfg.buy_thr_by_regime.get(r, cfg.buy_alert_threshold)).to_numpy(dtype=float)
    sell_thr = regime.map(lambda r: cfg.sell_thr_by_regime.get(r, cfg.sell_alert_threshold)).to_numpy(dtype=float)
    buy_thr = np.where(atr_pct > cfg.atr_soft_cap, buy_thr + cfg.atr_extra_points, buy_thr)
    sell_thr = np.where(atr_pct > cfg.atr_soft_cap, sell_thr + cfg.atr_extra_points, sell_thr)
    buy = np.where(zone == "Extreme", np.minimum(buy, buy_thr - 1), buy)

    # ---------------- SELL ----------------
    sp, sr, se = (_regime_w(regime, SELL_REGIME_W, k) for k in range(3))
    sp = np.maximum(sp, cfg.sell_regime_weight_floor)
    rel_x = rel_sx
    fresh_n = np.maximum(0, 1 - bs_neg / 5.0)
    s_base = 18.0 * fresh_n
    s_exp = 8.0 * expand_dn * np.maximum(fresh_n, 0.4)
    s_zero = np.where(zero_dn, 9.0, np.where(above0 > 0, 0.0, 4.0))
    s_str = 1.0 + 0.50 * strength
    s_ppo = np.minimum(np.floor((s_base + s_exp + s_zero) * s_str * sp * rel_x), 35)
    s_rsi = np.floor(np.clip((rsi_sell_m - 1.0) * np.maximum(s_ppo, 12) + np.select(
        [zone == "Extreme", zone == "Overheated"],
        [8.0, 5.0], default=0.0) * sr * rel_s, 0, 18))
    s_ema = np.floor(12 * (b20 + b50 + b200) / 3.0 * se)
    s_ema = np.floor(np.where(ppo_d > 0, s_ema * 0.5, s_ema))
    falling = (mdir < 0) | (ppo_d < 0)
    s_per = np.where(falling, np.floor(8 * persist * rel_s), 0)
    failed_sq = (sq_on > 0) & (sq_mom < 0) | ((sq_rel > 0) & (ppo_d < 0) & (sq_mom < 0))
    s_sqz = np.where(failed_sq, np.minimum(cfg.sqz_sell_add_cap, 8), 0)
    sell = s_ppo + s_rsi + s_ema + s_per + s_sqz
    # v54 (symmetric): the floor only applies while the bearish cross is still in force (histogram < 0)
    bear_floor = (fresh_bear & (ppo_d < 0)) if cfg.symmetric_scoring else fresh_bear
    floored = bear_floor & (sell < cfg.sell_cross_floor)
    sell = np.minimum(np.where(bear_floor, np.maximum(sell, cfg.sell_cross_floor), sell), 100)

    out = df.copy()
    out["Buy_Confidence"] = buy
    out["Sell_Confidence"] = sell
    out["Buy_Component_PPO_Cross"] = b_ppo
    out["Buy_Component_RSI"] = b_rsi
    out["Buy_Component_EMA"] = b_ema
    out["Buy_Component_Persistence"] = b_per
    out["Buy_Component_Squeeze"] = b_sqz
    out["Sell_Component_PPO_Cross"] = s_ppo
    out["Sell_Component_RSI"] = s_rsi
    out["Sell_Component_EMA"] = s_ema
    out["Sell_Component_Weakness"] = s_per
    out["Sell_Component_Squeeze"] = s_sqz
    out["Sell_Floor_Applied"] = floored.astype(int)
    out["Buy_Floor_Applied"] = buy_floored.astype(int)
    out["RSI_Zone"] = zone
    out["Net_Bias"] = buy - sell
    out["RSI_Buy_Mult"] = rsi_buy_m
    out["RSI_Sell_Mult"] = rsi_sell_m

    # ---------------- gates, alerts, recommendation ----------------
    data_ok = _col(out, "Momentum_Data_OK", 1) > 0
    # name-level liquidity
    liq_floor = liquidity_floor(out["Ticker"], cfg) if "Ticker" in out.columns else cfg.min_dollar_vol
    liq_ok = _col(out, "Dollar_Volume_20d") >= liq_floor
    # cross-bar volume / range confirmation
    buy_bar_ok = (vol_ratio >= cfg.vol_confirm_mult) | (close_loc >= 0.66)
    sell_bar_ok = (vol_ratio >= cfg.vol_confirm_mult) | (close_loc <= 0.34)
    if not cfg.require_volume_confirm:
        buy_bar_ok = np.ones(n, dtype=bool)
        sell_bar_ok = np.ones(n, dtype=bool)

    # (buy_thr / sell_thr were computed above, before the RSI-Extreme cap)

    # v46: a cross is only a trigger while it is still in force. A PPO up-cross 3 bars ago that
    # has since rolled back under its signal line (histogram <= 0) is not a BUY trigger.
    ppo_buy_raw = fresh_bull if cfg.require_ppo_cross_for_alert else np.ones(n, dtype=bool)
    ppo_sell_raw = fresh_bear if cfg.require_ppo_cross_for_alert else np.ones(n, dtype=bool)
    ppo_buy_trig = (ppo_buy_raw & (ppo_d > 0)) if cfg.require_ppo_cross_for_alert else ppo_buy_raw
    ppo_sell_trig = (ppo_sell_raw & (ppo_d < 0)) if cfg.require_ppo_cross_for_alert else ppo_sell_raw

    buy_base = (buy >= buy_thr) & data_ok & liq_ok & buy_bar_ok
    sell_base = (sell >= sell_thr) & data_ok & liq_ok & sell_bar_ok
    buy_a = buy_base & ppo_buy_trig
    sell_a = sell_base & ppo_sell_trig
    # v46: EXIT = a whipsaw. Both a fresh up-cross AND a fresh down-cross sit inside the window,
    # both scores clear their thresholds, and the scores are within conflict_margin. (Because the
    # signed triggers above can no longer both be true on one bar, EXIT is detected from the raw
    # fresh-cross windows.) When the two sides conflict but are not a close call, the side that
    # matches the current histogram sign wins.
    close_call = np.abs(buy - sell) <= cfg.conflict_margin
    conflict = buy_base & sell_base & ppo_buy_raw & ppo_sell_raw & close_call
    rec = np.select([conflict, buy_a, sell_a], ["EXIT", "BUY", "SELL"], default="HOLD")
    out["Buy_Alert"] = (buy_a | conflict).astype(int)
    out["Sell_Alert"] = (sell_a | conflict).astype(int)
    out["Recommendation"] = rec
    # v41: why a name that cleared the Buy threshold is not a BUY (bar-level requirements).
    # The post-score gates (SPY / RS / EMA200) append their own reasons in _apply_gates().
    blk = np.full(n, "", dtype=object)
    cleared = (buy >= buy_thr) & (rec == "HOLD")
    for label, failed in (("No fresh cross", ~np.asarray(ppo_buy_trig, dtype=bool)),
                          ("Volume bar", ~np.asarray(buy_bar_ok, dtype=bool)),
                          ("Liquidity", ~np.asarray(liq_ok, dtype=bool)),
                          ("Short data", ~np.asarray(data_ok, dtype=bool))):
        hit = cleared & failed
        blk = np.where(hit, np.where(blk == "", label, blk + " + " + label), blk)
    out["Gate_Block"] = blk
    out["Buy_Threshold"] = buy_thr
    out["Sell_Threshold"] = sell_thr
    near_buy = (~buy_a) & (buy >= buy_thr - cfg.watch_margin) & data_ok
    near_sell = (~sell_a) & (sell >= sell_thr - cfg.watch_margin) & data_ok
    out["Watch"] = np.select([rec != "HOLD", near_buy & near_sell, near_buy, near_sell],
                             ["", "BOTH", "BUY", "SELL"], default="")

    # cross glyphs
    bzp = np.nan_to_num(_col(out, "PPO_Bars_Since_Zero_Pos", 99), nan=99)
    bzn = np.nan_to_num(_col(out, "PPO_Bars_Since_Zero_Neg", 99), nan=99)
    fb = cfg.ppo_fresh_bars
    out["PPO_Sig_Cross_Recent"] = np.select([bs_pos <= fb, bs_neg <= fb], ["↑", "↓"], default="—")
    out["PPO_Zero_Cross_Recent"] = np.select([bzp <= fb, bzn <= fb], ["↑", "↓"], default="—")
    return out


# ---- Squeeze setup scoring (vectorised) ---------------------------------------

SQZ_MAX = 85.0   # raw pillar maximum; strength is rescaled to 0-100


def squeeze_score_frame(df: pd.DataFrame, cfg: Config) -> pd.DataFrame:
    base_len = _col(df, "Squeeze_Prior_Length")
    base = np.select([base_len >= 50, base_len >= 30, base_len >= 15], [10, 7, 4], default=0)
    release = np.where(_col(df, "Squeeze_Recent_Fire") == 1, 10, 0)
    ppo_up = np.where(_col(df, "PPO_Delta") > 0, 15, 0)
    dmi_ok = np.where(_col(df, "DMI_Value") > cfg.dmi_floor, 15, 0)
    ratio = _col(df, "High_52W_Ratio", 1.0)
    room = np.where(ratio < 0.90, 10, 0)
    r = _col(df, "RSI_14", np.nan)
    rsi_ok = np.where(np.isfinite(r) & (r >= cfg.rsi_healthy_low) & (r <= cfg.rsi_healthy_high), 10, 0)
    obv_ok = np.where(_col(df, "OBV_slope") > 0, 8, 0)
    mom = _col(df, "Momentum_Pctile", np.nan)
    flat = np.where(np.isfinite(mom) & (mom >= 20) & (mom <= 80), 7, 0)

    out = df.copy()
    out["Sqz_Foundation"] = base + release          # max 20
    out["Sqz_Momentum"] = ppo_up + dmi_ok           # max 30
    out["Sqz_Condition"] = room + rsi_ok            # max 20
    out["Sqz_Confirmation"] = obv_ok + flat         # max 15
    raw = out["Sqz_Foundation"] + out["Sqz_Momentum"] + out["Sqz_Condition"] + out["Sqz_Confirmation"]
    out["Squeeze_Setup_Strength"] = np.round(100 * raw / SQZ_MAX).astype(int)
    out["Squeeze_Setup_Flag"] = ((out["Sqz_Foundation"] >= 14) & (out["Sqz_Momentum"] >= 20)
                                 & (out["Sqz_Condition"] >= 15) & (out["Sqz_Confirmation"] >= 10)).astype(int)
    out["SQ_Real_Base"] = (base_len >= cfg.min_compression).astype(int)
    out["SQ_Release"] = (release > 0).astype(int)
    out["SQ_PPO_Turning"] = (ppo_up > 0).astype(int)
    out["SQ_DMI_OK"] = (dmi_ok > 0).astype(int)
    out["SQ_RSI_Waking"] = (rsi_ok > 0).astype(int)
    out["SQ_Room_To_Run"] = (room > 0).astype(int)
    out["SQ_OBV_Positive"] = (obv_ok > 0).astype(int)
    out["SQ_Flat_Momentum"] = (flat > 0).astype(int)
    return out


# =============================================================================
#  4. PIPELINE
# =============================================================================

def prepare_frames(prices: dict[str, pd.DataFrame], cfg: Config, health: DataHealth,
                   as_of: pd.Timestamp) -> dict[str, pd.DataFrame]:
    """Indicators on the full history, trimmed to keep_bars, with data flags."""
    frames = {}
    stale_cutoff = as_of - pd.tseries.offsets.BDay(cfg.stale_bdays)
    for t, px in prices.items():
        try:
            fr = compute_indicator_frame(px, cfg)
        except Exception as e:
            health.skipped.append({"ticker": t, "reason": f"indicator error: {e}"[:80]})
            continue
        n_bars = len(px)
        fr = fr.tail(cfg.keep_bars).copy()
        fr["Ticker"] = t
        fr["N_Bars"] = n_bars
        fr["Last_Bar_Date"] = px.index[-1]
        core_ok = fr[list(CORE_FIELDS)].notna().all(axis=1)
        fr["Momentum_Data_OK"] = ((n_bars >= cfg.min_bars) & core_ok).astype(int)
        if n_bars < cfg.min_bars:
            health.short.append({"ticker": t, "bars": int(n_bars)})
        if px.index[-1] < stale_cutoff:
            health.stale.append({"ticker": t, "last_bar": px.index[-1].strftime("%Y-%m-%d"),
                                 "as_of": as_of.strftime("%Y-%m-%d")})
        frames[t] = fr
    return frames


def latest_panel(frames: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows = [f.iloc[-1] for f in frames.values()]
    panel = pd.DataFrame(rows)
    panel.index = [r["Ticker"] for r in rows]
    panel.index.name = "Ticker"
    return panel


def _market_weak(rec, regime) -> bool:
    """v53: one index counts as 'failing' when it is rated Unfavorable (SELL) or its regime is
    Weak / Mature/Cooling."""
    return str(rec) == "SELL" or str(regime) in ("Weak", "Mature/Cooling")


def _apply_gates(panel: pd.DataFrame, cfg: Config, health: "DataHealth | None" = None,
                 bench_bad: "pd.Series | None" = None, tickers=None) -> None:
    """Post-score gates, in place. Works on a one-row-per-ticker panel (index = ticker) AND,
    since v46, on the full per-bar history, so the history / scorecard / chart markers are
    gated exactly like the live panel.

    bench_bad : optional boolean Series aligned to `panel.index` - "the benchmark is in a weak
                market on this row's date". Omitted for a panel (derived from the benchmark's own row).
    tickers   : optional ticker per row (for the history, where the index is not the ticker).

    BUY gates (each can block on its own; all reasons that apply are recorded):
      SPY regime   - the benchmark (SPY) AND the equal-weight index (RSP) are both in a weak market (v53)
      Relative str - 20d return does not beat the benchmark by rs_min_excess_for_buy
      Below EMA200 - close is under the 200-day EMA
    Each gate has the same exemption: Regime Dormant->Waking with a full squeeze setup.
    A blocked BUY becomes HOLD, gets Watch = "BUY" and a Gate_Block reason (v41), so it
    stays visible instead of looking like an ordinary HOLD."""
    def note(msg):
        if health is not None:
            health.notes.append(msg)

    if "Gate_Block" not in panel.columns:
        panel["Gate_Block"] = ""
    panel["Gate_Block"] = panel["Gate_Block"].fillna("").astype(str)

    tick = pd.Index(panel.index if tickers is None else tickers)
    is_buy = (panel["Recommendation"] == "BUY") & pd.Series(np.asarray(tick != cfg.benchmark), index=panel.index)
    sqz_full = panel["Squeeze_Setup_Flag"] == 1 if "Squeeze_Setup_Flag" in panel.columns \
        else pd.Series(False, index=panel.index)
    early = (panel["Regime"] == "Dormant→Waking") & sqz_full          # exempt from every BUY gate
    reasons = pd.Series("", index=panel.index, dtype=object)
    blocked = pd.Series(False, index=panel.index)
    # v42: Currency funds are a view on the dollar, so the SPY-regime and RS-vs-SPY gates do not apply
    not_fx = pd.Series(np.asarray(~tick.isin(cfg.currency_group)), index=panel.index)
    # v43: Country ETFs also skip the SPY-regime gate (they keep the RS and EMA200 gates)
    no_spy = pd.Series(np.asarray(~(tick.isin(cfg.currency_group) | tick.isin(cfg.country_group))), index=panel.index)

    def block(mask, label, text):
        nonlocal reasons, blocked
        mask = mask & is_buy & ~early
        if mask.any():
            reasons = reasons.where(~mask, np.where(reasons == "", label, reasons + " + " + label))
            blocked = blocked | mask
            note(f"{text} blocked {int(mask.sum())} BUY(s)")

    # 1) SPY regime gate: only blanket-blocks weak-market BUYs
    if cfg.spy_regime_gate:
        if bench_bad is None and cfg.benchmark in panel.index:
            bad = _market_weak(panel.loc[cfg.benchmark, "Recommendation"], panel.loc[cfg.benchmark, "Regime"])
            if cfg.regime_need_both and cfg.regime_confirm and cfg.regime_confirm != cfg.benchmark:
                if cfg.regime_confirm in panel.index:      # v53: SPY AND RSP must both be weak
                    bad = bad and _market_weak(panel.loc[cfg.regime_confirm, "Recommendation"],
                                               panel.loc[cfg.regime_confirm, "Regime"])
                else:
                    note(f"{cfg.regime_confirm} not loaded: market-regime gate uses {cfg.benchmark} alone")
            bench_bad = pd.Series(bad, index=panel.index)
        if bench_bad is not None and bench_bad.any():
            block(no_spy & bench_bad.astype(bool), "SPY regime", f"{cfg.benchmark} regime gate")
    # 2) relative-strength gate
    if cfg.rs_gate and "RS_20d" in panel.columns:
        block((panel["RS_20d"].fillna(0) < cfg.rs_min_excess_for_buy) & not_fx, "Relative strength",
              f"RS<{cfg.benchmark} (excess < {cfg.rs_min_excess_for_buy}) gate")
    # 3) v36: require above EMA200
    if cfg.require_above_ema200_for_buy and "Below_EMA200" in panel.columns:
        block(panel["Below_EMA200"] == 1, "Below EMA200", "Below-EMA200 gate")

    if blocked.any():
        panel.loc[blocked, "Recommendation"] = "HOLD"
        panel.loc[blocked, "Buy_Alert"] = 0
        panel.loc[blocked, "Watch"] = "BUY"
        panel.loc[blocked, "Gate_Block"] = reasons[blocked]
        note(f"{int(blocked.sum())} BUY(s) converted to HOLD by the gates; shown as Watch with a 'Blocked by' reason")

    # v36: stronger top / exit detection
    if cfg.stronger_top_detection:
        # Convert weak SELLs that are still above EMA50 or have positive momentum to HOLD
        if "Below_EMA50" in panel.columns and "Momentum_Direction" in panel.columns:
            weak_sell = (panel["Recommendation"] == "SELL") & (panel["Below_EMA50"] == 0) & (panel["Momentum_Direction"] > 0)
            if weak_sell.any():
                panel.loc[weak_sell, "Recommendation"] = "HOLD"
                panel.loc[weak_sell, "Sell_Alert"] = 0
                note(f"Stronger top filter converted {int(weak_sell.sum())} weak SELL(s) to HOLD")


GATE_LABELS = ("SPY regime", "Relative strength", "Below EMA200")


def market_gate_series(hist: pd.DataFrame, cfg: Config, stocks=None) -> pd.DataFrame:
    """v54: the market gate for every date in the history, from data the run already has.

        index weak   = the benchmark closes under its 200-day EMA (and, with regime_need_both,
                       the confirming equal-weight index does too)
        breadth weak = % of stocks above their 200-day EMA < gate_breadth_200_min AND
                       % above their 50-day EMA < gate_breadth_50_min
        closed       = index weak OR breadth weak

    `stocks` is the breadth list (individual stocks only). Dates with fewer than
    gate_breadth_min_names of them are judged on the index alone. Returns a frame indexed by Date
    with spy_below, rsp_below, pct200, pct50, n, idx_weak, brd_weak, closed (empty if no benchmark)."""
    dts = pd.to_datetime(hist["Date"])

    def _below(tk):
        b = hist[hist["Ticker"] == tk]
        if not len(b):
            return None
        s = pd.Series((b["Below_EMA200"] == 1).to_numpy(), index=pd.DatetimeIndex(dts[b.index]))
        return s[~s.index.duplicated(keep="last")].sort_index()

    spy = _below(cfg.benchmark)
    if spy is None:
        return pd.DataFrame()
    g = pd.DataFrame({"spy_below": spy.astype(bool)})
    rsp = None
    if cfg.regime_need_both and cfg.regime_confirm and cfg.regime_confirm != cfg.benchmark:
        rsp = _below(cfg.regime_confirm)
    g["rsp_below"] = rsp.reindex(g.index) if rsp is not None else np.nan
    has_rsp = g["rsp_below"].notna()
    g["idx_weak"] = np.where(has_rsp, g["spy_below"] & g["rsp_below"].fillna(False).astype(bool), g["spy_below"])
    g["pct200"], g["pct50"], g["n"] = np.nan, np.nan, 0
    stocks = [t for t in (stocks or []) if t != cfg.benchmark]
    if stocks:
        s = hist[hist["Ticker"].isin(stocks) & hist["EMA200"].notna()]
        if len(s):
            a = pd.DataFrame({"Date": dts[s.index].to_numpy(),
                              "a200": (s["Below_EMA200"] == 0).to_numpy(dtype=float) * 100.0,
                              "a50": (s["Below_EMA50"] == 0).to_numpy(dtype=float) * 100.0})
            by = a.groupby("Date").agg(pct200=("a200", "mean"), pct50=("a50", "mean"), n=("a200", "size"))
            by = by.reindex(g.index)
            g["pct200"], g["pct50"], g["n"] = by["pct200"], by["pct50"], by["n"].fillna(0).astype(int)
    enough = g["n"] >= cfg.gate_breadth_min_names
    g["brd_weak"] = enough & (g["pct200"] < cfg.gate_breadth_200_min) & (g["pct50"] < cfg.gate_breadth_50_min)
    g["idx_weak"] = g["idx_weak"].astype(bool)
    g["closed"] = g["idx_weak"] | g["brd_weak"]
    return g


def apply_gates_history(hist: pd.DataFrame, cfg: Config, stocks=None) -> pd.DataFrame:
    """v46: run the post-score gates over EVERY historical bar (vectorised), in place.

    Before v46 only the latest panel and the prior-session panel were gated, so the Scorecard,
    the BUY/SELL markers on the Ticker chart, the breadth counts and the pinned live alerts all
    came from an UNGATED history and validated a different system than the dashboard shows.
    The benchmark's per-date "weak market" flag is computed BEFORE any gate or top-filter
    changes the benchmark's own recommendation, matching the panel logic."""
    bad = None
    if cfg.spy_regime_gate and cfg.market_gate_mode == "breadth":
        # v54: the gate is read from the index trend and breadth, not from SPY's own momentum regime
        g = market_gate_series(hist, cfg, stocks)
        if len(g):
            bad = pd.to_datetime(hist["Date"]).map(g["closed"]).fillna(False).astype(bool)
            bad.index = hist.index
    elif cfg.spy_regime_gate:
        def _flags(tk):
            b = hist[hist["Ticker"] == tk]
            if not len(b):
                return None
            flag = (b["Recommendation"] == "SELL") | b["Regime"].isin(["Weak", "Mature/Cooling"])
            fmap = pd.Series(flag.to_numpy(), index=pd.DatetimeIndex(pd.to_datetime(b["Date"])))
            return fmap[~fmap.index.duplicated(keep="last")]
        spy_f = _flags(cfg.benchmark)
        if spy_f is not None:
            dts = pd.to_datetime(hist["Date"])
            bad = dts.map(spy_f).fillna(False).astype(bool)
            if cfg.regime_need_both and cfg.regime_confirm and cfg.regime_confirm != cfg.benchmark:
                rsp_f = _flags(cfg.regime_confirm)          # v53: SPY AND RSP must both be weak on the bar
                if rsp_f is not None:
                    bad = bad & dts.map(rsp_f).fillna(False).astype(bool)
            bad.index = hist.index
    _apply_gates(hist, cfg, None, bench_bad=bad, tickers=hist["Ticker"])
    return hist


TREND_COLS = ("In_Trend", "Trend_Days", "Trend_Entry", "Trend_Entry_Date", "Trend_Ret_Pct", "Trend_Stop",
              "Trend_Stop_Dist_Pct", "Trend_Exit", "Trend_Closed_Ret", "Trend_Closed_Days")


def add_trend_state(hist: pd.DataFrame, cfg: Config) -> pd.DataFrame:
    """v54: a persistent "In trend" state per ticker, from the gated recommendations. DISPLAY ONLY:
    it never changes a score, an alert or Signal.

        enter : the bar Signal is Favorable (BUY) with complete data, at that close
        stop  : highest (close - trend_stop_atr_mult x ATR) seen since entry; it never moves down
        exit  : a close under the stop carried in from the previous bar ("Stop"), or an
                Unfavorable / Conflicted alert ("Signal")

    Size_Pct is a volatility-based position size: risk_per_trade_pct of the portfolio divided by the
    stop distance (trend_stop_atr_mult x ATR%), capped at max_position_pct."""
    n = len(hist)
    in_tr = np.zeros(n, dtype=int)
    days = np.full(n, np.nan)
    entry = np.full(n, np.nan)
    ret = np.full(n, np.nan)
    stop = np.full(n, np.nan)
    c_ret = np.full(n, np.nan)
    c_days = np.full(n, np.nan)
    e_date = np.full(n, "", dtype=object)
    exit_r = np.full(n, "", dtype=object)
    k = float(cfg.trend_stop_atr_mult)
    atr_pct = pd.to_numeric(hist.get("ATR_Pct", pd.Series(np.nan, index=hist.index)), errors="coerce")
    hist["Size_Pct"] = np.round(np.minimum(cfg.max_position_pct,
                                           100.0 * cfg.risk_per_trade_pct / (k * atr_pct.where(atr_pct > 0))), 1)
    if cfg.trend_state and n:
        pos = pd.Series(np.arange(n), index=hist.index)
        order = hist.sort_values(["Ticker", "Date"])
        close_a = order["Last_Close"].to_numpy(dtype=float)
        atr_a = (pd.to_numeric(order["ATR_Pct"], errors="coerce").to_numpy(dtype=float) / 100.0) * close_a
        rec_a = order["Recommendation"].astype(str).to_numpy()
        ok_a = (order["Momentum_Data_OK"].to_numpy() == 1) if "Momentum_Data_OK" in order.columns else np.ones(n, dtype=bool)
        tk_a = order["Ticker"].to_numpy()
        dt_a = pd.to_datetime(order["Date"]).dt.strftime("%Y-%m-%d").to_numpy()
        where = pos.loc[order.index].to_numpy()
        on, e_px, e_dt, st, d = False, np.nan, "", np.nan, 0
        prev_t = None
        for i in range(n):
            if tk_a[i] != prev_t:
                on, e_px, e_dt, st, d = False, np.nan, "", np.nan, 0
                prev_t = tk_a[i]
            c, j = close_a[i], where[i]
            if not np.isfinite(c):
                continue
            if on:
                d += 1
                reason = "Stop" if (np.isfinite(st) and c < st) else ("Signal" if rec_a[i] in ("SELL", "EXIT") else "")
                if reason:
                    exit_r[j] = reason
                    c_ret[j] = (c / e_px - 1) * 100
                    c_days[j] = d
                    on = False
                elif np.isfinite(atr_a[i]):
                    st = max(st, c - k * atr_a[i]) if np.isfinite(st) else c - k * atr_a[i]
            if not on and rec_a[i] == "BUY" and ok_a[i]:
                on, e_px, e_dt, d = True, c, dt_a[i], 0
                st = c - k * atr_a[i] if np.isfinite(atr_a[i]) else np.nan
            if on:
                in_tr[j], days[j], entry[j], e_date[j] = 1, d, e_px, e_dt
                ret[j] = (c / e_px - 1) * 100
                stop[j] = st
    hist["In_Trend"] = in_tr
    hist["Trend_Days"] = days
    hist["Trend_Entry"] = entry
    hist["Trend_Entry_Date"] = e_date
    hist["Trend_Ret_Pct"] = ret
    hist["Trend_Stop"] = stop
    hist["Trend_Stop_Dist_Pct"] = (hist["Last_Close"] / hist["Trend_Stop"] - 1) * 100
    hist["Trend_Exit"] = exit_r
    hist["Trend_Closed_Ret"] = c_ret
    hist["Trend_Closed_Days"] = c_days
    return hist


def finalize_panel(panel: pd.DataFrame, cfg: Config, health: DataHealth) -> pd.DataFrame:
    floor = liquidity_floor(panel.index, cfg)
    panel["Is_Tradeable"] = ((panel["Dollar_Volume_20d"].fillna(0) >= floor)
                             & (panel["Last_Close"] >= cfg.min_price)).astype(int)
    for t, r in panel[panel["Is_Tradeable"] == 0].iterrows():
        health.illiquid.append({"ticker": t, "dollar_vol": _rnd(r["Dollar_Volume_20d"], 0),
                                "price": _rnd(r["Last_Close"], 2)})
    panel["Is_Stale"] = panel.index.isin([s["ticker"] for s in health.stale]).astype(int)
    panel["Is_Live"] = panel.index.isin(health.live_bars).astype(int)
    # v46: the panel is the last bar of an already-gated history (see apply_gates_history), so the
    # gates are not re-applied here; just report how many BUYs they are holding back.
    held = panel[panel["Gate_Block"].fillna("").str.contains("SPY regime|Relative strength|Below EMA200")
                 & (panel["Recommendation"] == "HOLD")]
    if len(held):
        health.notes.append(f"{len(held)} BUY(s) held at HOLD by the gates; shown as Watch with a 'Blocked by' reason")
    panel["Rec"] = panel["Recommendation"]
    panel["Buy_Signal_Score"] = panel["Buy_Confidence"].astype(int)
    panel["Sell_Signal_Score"] = panel["Sell_Confidence"].astype(int)
    return panel


def apply_eod_alerts(panel: pd.DataFrame, hist: pd.DataFrame, cfg: Config,
                     health: DataHealth) -> pd.DataFrame:
    """Keep live confidence on the dashboard; pin alerts to last confirmed close."""
    if not cfg.alerts_eod_only:
        return panel
    live = panel.index[panel.get("Is_Live", 0) == 1]
    if len(live) == 0:
        return panel
    h = hist.sort_values("Date")
    n_pin = 0
    for t in live:
        g = h[h["Ticker"] == t]
        if len(g) < 2:
            continue
        prev = g.iloc[-2]
        panel.loc[t, "Buy_Alert"] = int(prev.get("Buy_Alert", 0))
        panel.loc[t, "Sell_Alert"] = int(prev.get("Sell_Alert", 0))
        panel.loc[t, "Recommendation"] = str(prev.get("Recommendation", "HOLD"))
        panel.loc[t, "Watch"] = str(prev.get("Watch", "") or "")
        panel.loc[t, "Gate_Block"] = str(prev.get("Gate_Block", "") or "")
        if "In_Trend" in panel.columns and "In_Trend" in g.columns:
            # v54: the trend state is pinned to the confirmed close too; the open return and the
            # distance to the stop are re-measured from the live price.
            for col in TREND_COLS:
                panel.loc[t, col] = prev.get(col)
            if int(prev.get("In_Trend", 0) or 0) == 1:
                px_now = float(panel.loc[t, "Last_Close"])
                panel.loc[t, "Trend_Ret_Pct"] = (px_now / float(prev["Trend_Entry"]) - 1) * 100
                if pd.notna(prev.get("Trend_Stop")):
                    panel.loc[t, "Trend_Stop_Dist_Pct"] = (px_now / float(prev["Trend_Stop"]) - 1) * 100
        n_pin += 1
    if n_pin:
        # v46: the previous bar in `hist` is already gated (apply_gates_history), so the pinned
        # recommendation is the gated one for the confirmed close. (v41 re-applied the gates here
        # using the LIVE bar's RS / EMA200, which mixed two different bars.)
        health.notes.append(
            f"Alerts pinned to last confirmed close for {n_pin} live ticker(s); "
            f"confidence/RSI/PPO still reflect the forming bar"
        )
    panel["Rec"] = panel["Recommendation"]
    return panel


def score_history(frames: dict[str, pd.DataFrame], cfg: Config, dist: dict,
                  ref_frame=None, group_refs=None, stocks=None) -> pd.DataFrame:
    """Run composites + scoring over every historical bar of every ticker."""
    hist = pd.concat(frames.values(), axis=0, ignore_index=False)
    hist.index.name = "Date"
    hist = hist.reset_index()
    if cfg.benchmark in frames and "Ret_20d" in frames[cfg.benchmark].columns:
        spy_ret = frames[cfg.benchmark]["Ret_20d"]
        hist["RS_20d"] = hist["Ret_20d"] - pd.to_datetime(hist["Date"]).map(spy_ret)
    uni = cfg.pctile_anchor == "universe"      # v54: rank across the universe (groups keep their own anchor)
    if group_refs:
        # v42: tickers in a group are percentile-ranked against THAT group's pooled history
        gmask = pd.Series(False, index=hist.index)
        parts = []
        for members, gref, gcfg in group_refs:
            m = hist["Ticker"].isin(members)
            gmask = gmask | m
            parts.append(add_composites(hist[m].copy(), gcfg, dist, ref_frame=gref))
        parts.append(add_composites(hist[~gmask].copy(), cfg, dist, ref_frame=ref_frame, universe=uni))
        hist = pd.concat(parts).sort_index()
    else:
        hist = add_composites(hist, cfg, dist, ref_frame=ref_frame, universe=uni)
    hist = squeeze_score_frame(hist, cfg)
    hist = score_frame(hist, cfg)
    hist = apply_gates_history(hist, cfg, stocks)   # v46: gate every bar, not just the latest
    hist = add_trend_state(hist, cfg)               # v54: persistent In-trend state (display only)
    return hist


def scorecard(hist: pd.DataFrame, cfg: Config, bench: str) -> dict:
    """Forward returns after NEW BUY / SELL events. In-sample, no costs —
    a sanity check on whether the signals carry information, not a backtest."""
    H = list(cfg.fwd_horizons)
    hist = hist.sort_values(["Ticker", "Date"]).copy()
    g = hist.groupby("Ticker", sort=False)["Last_Close"]
    for h in H:
        hist[f"Fwd_{h}"] = (g.shift(-h) / hist["Last_Close"] - 1) * 100
    # benchmark-relative
    if bench in set(hist["Ticker"]):
        b = hist[hist["Ticker"] == bench].set_index("Date")
        for h in H:
            hist[f"FwdX_{h}"] = hist[f"Fwd_{h}"] - hist["Date"].map(b[f"Fwd_{h}"])
    else:
        for h in H:
            hist[f"FwdX_{h}"] = np.nan
    ok = hist["Momentum_Data_OK"] == 1
    prev_rec = hist.groupby("Ticker")["Recommendation"].shift(1)
    events = {"BUY": ok & (hist["Recommendation"] == "BUY") & (prev_rec != "BUY"),
              "SELL": ok & (hist["Recommendation"] == "SELL") & (prev_rec != "SELL")}

    def stats(mask, h):
        s = hist.loc[mask, f"Fwd_{h}"].dropna()
        x = hist.loc[mask, f"FwdX_{h}"].dropna()
        if len(s) == 0:
            return {"n": 0}
        out = {"n": int(len(s)), "hit": _rnd(100 * (s > 0).mean(), 1), "mean": _rnd(s.mean(), 2),
               "median": _rnd(s.median(), 2), "excess": _rnd(x.mean(), 2) if len(x) else None,
               "hit_x": _rnd(100 * (x > 0).mean(), 1) if len(x) else None}
        # v54: uncertainty. Signals cluster on the same dates, so N overstates the evidence. The
        # range is +/- 1.96 standard errors of the PER-DATE average (excess return when there is a
        # benchmark, else the raw return). Overlapping windows still make it a little too narrow.
        col = f"FwdX_{h}" if len(x) else f"Fwd_{h}"
        v = hist.loc[mask, ["Date", col]].dropna()
        per = v.groupby("Date")[col].mean()
        out["nd"] = int(len(per))
        out["ci_on"] = "excess" if len(x) else "mean"
        if len(per) >= 5:
            se = float(per.std(ddof=1)) / np.sqrt(len(per))
            mid = float(v[col].mean())
            out["lo"], out["hi"] = _rnd(mid - 1.96 * se, 2), _rnd(mid + 1.96 * se, 2)
        return out

    summary = []
    for side, m in events.items():
        for h in H:
            summary.append({"side": side, "h": h, **stats(m, h), "base": stats(ok, h)})
    by_regime = []
    for reg in REGIMES:
        m = events["BUY"] & (hist["Regime"] == reg)
        by_regime.append({"regime": reg, **stats(m, 10)})
    by_ticker = []
    h10 = f"Fwd_{10 if 10 in H else H[0]}"
    for t, grp in hist[events["BUY"]].groupby("Ticker"):
        s = grp[h10].dropna()
        if len(s) >= 3:
            by_ticker.append({"ticker": t, "n": int(len(s)), "hit": _rnd(100 * (s > 0).mean(), 0),
                              "mean": _rnd(s.mean(), 2)})
    by_ticker.sort(key=lambda d: -(d["mean"] or 0))
    per_ticker_events: dict[str, list] = {}
    ev_mask = events["BUY"] | events["SELL"]
    for _, e in hist[ev_mask].sort_values("Date").iterrows():
        per_ticker_events.setdefault(e["Ticker"], []).append({
            "d": e["Date"].strftime("%Y-%m-%d"), "side": e["Recommendation"], "close": _rnd(e["Last_Close"], 2),
            "buy": int(e["Buy_Confidence"]), "sell": int(e["Sell_Confidence"]), "regime": e["Regime"],
            **{f"f{h}": _rnd(e[f"Fwd_{h}"], 2) for h in H}, **{f"x{h}": _rnd(e[f"FwdX_{h}"], 2) for h in H},
        })
    # ---- v54: gate attribution. What did the Favorable ratings each gate BLOCKED go on to do?
    hmain = 10 if 10 in H else H[0]
    gb = hist["Gate_Block"].fillna("").astype(str) if "Gate_Block" in hist.columns else pd.Series("", index=hist.index)
    is_blk = ok & (hist["Recommendation"] == "HOLD") & gb.str.contains("|".join(GATE_LABELS))
    prev_blk = is_blk.astype(int).groupby(hist["Ticker"]).shift(1).fillna(0) == 1
    blk_ev = is_blk & ~prev_blk & (prev_rec != "BUY")
    gates = [{"gate": "Passed every gate (Favorable)", "kind": "pass", **stats(events["BUY"], hmain)},
             {"gate": "Blocked by any gate", "kind": "any", **stats(blk_ev, hmain)}]
    for lab in GATE_LABELS:
        gates.append({"gate": lab, "kind": "gate", **stats(blk_ev & gb.str.contains(lab), hmain)})
        gates.append({"gate": lab + " only", "kind": "only", **stats(blk_ev & (gb == lab), hmain)})

    # ---- v54: calibration. Does a higher score earn a higher forward return?
    edges = list(cfg.score_buckets)
    calib = []
    for side, col in (("BUY", "Buy_Confidence"), ("SELL", "Sell_Confidence")):
        for lo_e, hi_e in zip(edges[:-1], edges[1:]):
            m = ok & (hist[col] >= lo_e) & (hist[col] < hi_e)
            calib.append({"side": side, **stats(m, hmain), "b_lo": int(lo_e), "b_hi": int(min(hi_e - 1, 100))})

    # ---- v54: trend trades (Favorable -> stop or Unfavorable), from add_trend_state
    trend = {"n": 0}
    if "Trend_Exit" in hist.columns:
        done = hist[hist["Trend_Exit"].astype(str) != ""]
        last = hist.groupby("Ticker").tail(1)
        open_ = last[last["In_Trend"] == 1]
        trend = {"n": int(len(done)), "open": int(len(open_)),
                 "open_mean": _rnd(open_["Trend_Ret_Pct"].mean(), 2) if len(open_) else None,
                 "mult": cfg.trend_stop_atr_mult}
        if len(done):
            r = done["Trend_Closed_Ret"].astype(float)
            trend.update({"win": _rnd(100 * (r > 0).mean(), 1), "mean": _rnd(r.mean(), 2), "median": _rnd(r.median(), 2),
                          "days": _rnd(done["Trend_Closed_Days"].astype(float).mean(), 1),
                          "avg_win": _rnd(r[r > 0].mean(), 2) if (r > 0).any() else None,
                          "avg_loss": _rnd(r[r <= 0].mean(), 2) if (r <= 0).any() else None,
                          "stop": int((done["Trend_Exit"] == "Stop").sum()),
                          "signal": int((done["Trend_Exit"] == "Signal").sum())})

    dates = hist["Date"]
    return {"gates": gates, "calib": calib, "trend": trend, "h_main": hmain,
            "summary": summary, "by_regime": by_regime, "by_ticker": by_ticker, "per_ticker": per_ticker_events,
            "n_bars": int(hist.groupby("Ticker").size().median()),
            "from": dates.min().strftime("%Y-%m-%d"), "to": dates.max().strftime("%Y-%m-%d"),
            "events": {k: int(v.sum()) for k, v in events.items()}}


# ---- Snapshots -------------------------------------------------------------------

def snapshot_scorecard(snap_dir, hist: pd.DataFrame, cfg: Config, bench: str) -> dict:
    """v54: OUT-OF-SAMPLE check. Each dated snapshot CSV holds the Signal the program actually
    published that day (whatever version and settings were live then), so nothing here is
    re-computed with hindsight. An event is a ticker whose snapshot recommendation is BUY / SELL
    and was not the same in the snapshot before it; forward returns come from today's adjusted
    closes. Snapshots older than the price history in this run cannot be scored."""
    out = {"ok": False, "n_files": 0, "rows": [], "note": ""}
    if not cfg.scorecard_snapshots or snap_dir is None:
        out["note"] = "switched off"
        return out
    try:
        files = sorted(Path(snap_dir).glob("Results_????-??-??.csv"))[-int(cfg.snapshot_max_files):]
    except Exception as e:
        out["note"] = f"snapshot folder not readable ({e})"
        return out
    if len(files) < 2:
        out["note"] = "fewer than two dated snapshots found"
        return out
    px = hist.pivot_table(index="Date", columns="Ticker", values="Last_Close", aggfunc="last").sort_index()
    px.index = pd.DatetimeIndex(pd.to_datetime(px.index))
    H = list(cfg.fwd_horizons)
    prev, ev, used = None, [], []
    for f in files:
        try:
            d = pd.Timestamp(f.stem[8:])
            df = pd.read_csv(f, usecols=lambda c: c in ("Ticker", "Recommendation"))
            recs = dict(zip(df["Ticker"].astype(str), df["Recommendation"].astype(str)))
        except Exception:
            continue
        if prev is not None and d in px.index:
            i = px.index.get_loc(d)
            used.append(d)
            for t, r in recs.items():
                if r not in ("BUY", "SELL") or prev.get(t) == r or t not in px.columns:
                    continue
                p0 = px[t].iloc[i]
                if not (np.isfinite(p0) and p0 > 0):
                    continue
                row = {"side": r, "Date": d}
                for h in H:
                    if i + h < len(px):
                        fw = (px[t].iloc[i + h] / p0 - 1) * 100
                        row[f"f{h}"] = fw
                        if bench in px.columns and np.isfinite(px[bench].iloc[i]) and px[bench].iloc[i] > 0:
                            row[f"x{h}"] = fw - (px[bench].iloc[i + h] / px[bench].iloc[i] - 1) * 100
                ev.append(row)
        prev = recs
    out["n_files"] = len(files)
    if not used:
        out["note"] = "no snapshot dates fall inside this run's price history"
        return out
    E = pd.DataFrame(ev)
    out.update({"ok": True, "from": used[0].strftime("%Y-%m-%d"), "to": used[-1].strftime("%Y-%m-%d"),
                "n_used": len(used), "events": {s: int((E["side"] == s).sum()) if len(E) else 0 for s in ("BUY", "SELL")}})
    for side in ("BUY", "SELL"):
        for h in H:
            sub = E[E["side"] == side] if len(E) else E
            s = sub[f"f{h}"].dropna() if len(sub) and f"f{h}" in sub.columns else pd.Series(dtype=float)
            x = sub[f"x{h}"].dropna() if len(sub) and f"x{h}" in sub.columns else pd.Series(dtype=float)
            if not len(s):
                out["rows"].append({"side": side, "h": h, "n": 0})
                continue
            out["rows"].append({"side": side, "h": h, "n": int(len(s)), "nd": int(sub.loc[s.index, "Date"].nunique()),
                                "hit": _rnd(100 * (s > 0).mean(), 1), "mean": _rnd(s.mean(), 2), "median": _rnd(s.median(), 2),
                                "excess": _rnd(x.mean(), 2) if len(x) else None,
                                "hit_x": _rnd(100 * (x > 0).mean(), 1) if len(x) else None})
    return out


def load_prior_snapshot(snap_dir: Path, as_of: str) -> tuple[pd.DataFrame | None, str]:
    """Most recent Results_YYYY-MM-DD.csv strictly before as_of."""
    try:
        files = sorted(Path(snap_dir).glob("Results_????-??-??.csv"))
    except Exception:
        return None, ""
    prior = [f for f in files if f.stem[8:] < as_of]
    if not prior:
        return None, ""
    f = prior[-1]
    try:
        df = pd.read_csv(f)
        if "Ticker" not in df.columns:
            return None, ""
        return df.set_index("Ticker"), f.stem[8:]
    except Exception:
        return None, ""


def compute_changes(panel: pd.DataFrame, hist: pd.DataFrame, cfg: Config) -> dict:
    """What changed vs the PREVIOUS SESSION'S CLOSE: each ticker's prior bar in
    the reconstructed history (the same model and gates as the dashboard), not
    the previous run's snapshot."""
    last_dates = hist.groupby("Ticker")["Date"].transform("max")
    prev = hist[hist["Date"] < last_dates].sort_values("Date").groupby("Ticker").tail(1)
    p = prev.set_index("Ticker").copy()
    # v46: hist is already gated per bar (apply_gates_history), so the prior bar needs no re-gating
    prior_date = p["Date"].max().strftime("%Y-%m-%d") if len(p) else ""
    src = "the prior session's close"
    cols = {"Recommendation": "rec", "Buy_Confidence": "buy", "Sell_Confidence": "sell",
            "Regime": "regime", "Last_Close": "close"}
    out = {"source": src, "prior_date": prior_date, "new_buy": [], "new_sell": [], "new_exit": [],
           "dropped": [], "regime": [], "movers": [], "new_tickers": []}
    for t, r in panel.iterrows():
        if t not in p.index:
            out["new_tickers"].append(t)
            continue
        q = p.loc[t]
        old_rec = str(q.get("Recommendation", "HOLD"))
        new_rec = str(r["Recommendation"])
        d_buy = float(r["Buy_Confidence"]) - float(q.get("Buy_Confidence", np.nan) or 0)
        d_sell = float(r["Sell_Confidence"]) - float(q.get("Sell_Confidence", np.nan) or 0)
        item = {"ticker": t, "old": old_rec, "new": new_rec, "buy": int(r["Buy_Confidence"]),
                "sell": int(r["Sell_Confidence"]), "d_buy": int(round(d_buy)), "d_sell": int(round(d_sell)),
                "regime": r["Regime"], "close": _rnd(r["Last_Close"], 2)}
        if new_rec != old_rec:
            if new_rec == "BUY":
                out["new_buy"].append(item)
            elif new_rec == "SELL":
                out["new_sell"].append(item)
            elif new_rec == "EXIT":
                out["new_exit"].append(item)
            else:
                out["dropped"].append(item)
        old_reg = str(q.get("Regime", ""))
        if old_reg and old_reg != r["Regime"]:
            out["regime"].append({"ticker": t, "old": old_reg, "new": r["Regime"], "rec": new_rec})
        out["movers"].append({"ticker": t, "d_buy": int(round(d_buy)), "d_sell": int(round(d_sell)),
                              "buy": int(r["Buy_Confidence"]), "sell": int(r["Sell_Confidence"]), "rec": new_rec})
    out["movers"].sort(key=lambda d: -max(abs(d["d_buy"]), abs(d["d_sell"])))
    out["movers"] = out["movers"][:15]
    return out


# ---- Build -----------------------------------------------------------------------

# v52: which tickers count as STOCKS for Market Health breadth ------------------------------------------
MH_QUOTE_CACHE = Path(__file__).resolve().with_name("quote_types_cache.json")


def _mh_quote_types(tickers: list[str], cfg: "Config") -> dict:
    """Yahoo quoteType per ticker (EQUITY, ETF, MUTUALFUND ...), cached on disk so only NEW tickers are looked up.
    Best effort: any failure just means the ticker is treated as a stock (unless a fund list already excludes it)."""
    cache: dict = {}
    try:
        cache = json.loads(MH_QUOTE_CACHE.read_text(encoding="utf-8"))
    except Exception:
        cache = {}
    todo = [t for t in tickers if t not in cache]
    if todo:
        from concurrent.futures import ThreadPoolExecutor, as_completed
        log(f"Breadth: looking up Yahoo quote type for {len(todo)} new ticker(s) (cached for next time) …")
        yf = _yf()

        def one(t):
            try:
                return t, str(yf.Ticker(t).get_info().get("quoteType") or "")
            except Exception:
                return t, ""

        ex = ThreadPoolExecutor(max_workers=8)
        futs = [ex.submit(one, t) for t in todo]
        got = 0
        try:
            for f in as_completed(futs, timeout=max(5, cfg.breadth_type_budget_s)):
                t, q = f.result()
                if q:
                    cache[t] = q
                    got += 1
        except Exception:
            log_warn(f"Breadth: quote-type lookup stopped early ({got}/{len(todo)} done); the rest are treated as stocks this run")
        finally:
            ex.shutdown(wait=False, cancel_futures=True)
        try:
            MH_QUOTE_CACHE.write_text(json.dumps(cache, indent=0, sort_keys=True), encoding="utf-8")
        except Exception as e:
            log_warn(f"Breadth: could not write quote-type cache ({e})")
    return cache


def breadth_stock_list(cfg: "Config", tickers: list[str], loaded, demo: bool = False) -> list[str]:
    """Stocks only: the main watchlist (+ theme file) minus every fund list, the benchmark / context tickers,
    Config.breadth_exclude and (live runs) anything Yahoo does not classify as an EQUITY."""
    fund = {str(cfg.benchmark).upper()} | {str(t).upper() for t in cfg.context_tickers} | {str(t).upper() for t in cfg.breadth_exclude}
    for grp in (cfg.sector_names, cfg.six_pack, cfg.etf_tickers, cfg.bond_etfs, cfg.country_etfs, cfg.currency_group):
        fund |= {str(t).upper() for t in grp}
    cand = [t for t in dict.fromkeys(tickers) if t in loaded and t not in fund]
    n_funds = len([t for t in dict.fromkeys(tickers) if t in loaded]) - len(cand)
    if cand and not demo and cfg.breadth_check_yahoo_type:
        try:
            q = _mh_quote_types(cand, cfg)
            keep = [t for t in cand if q.get(t, "EQUITY") == "EQUITY"]
            n_funds += len(cand) - len(keep)
            cand = keep
        except Exception as e:
            log_warn(f"Breadth: quote-type check skipped ({type(e).__name__}: {e}); using the fund lists only")
    log(f"Breadth universe: {len(cand)} stocks ({n_funds} funds / indexes left out)")
    return cand


def build(cfg: Config, *, demo: bool = False, snap_dir: Path | None = None,
          tickers: list[str] | None = None) -> dict:
    """Full pipeline. Returns dict(panel, hist, payload_parts, health)."""
    t0 = time.perf_counter()
    health = DataHealth()
    tickers = tickers or cfg.tickers
    health.notes.extend(w for w in cfg.warnings if not str(w).startswith("Duplicate ticker"))   # v48: not shown on the Health tab

    # --- prices
    if demo:
        health.source = "SYNTHETIC demo data (no network)"
        log(f"Generating synthetic prices for {len(tickers)} tickers …")
        prices = synthetic_prices(tickers)
        bench_px = synthetic_prices([cfg.benchmark], n_bars=1260, seed=99)[cfg.benchmark]
        for t in ("DRNZ",):
            if t in prices and len(prices[t]) < cfg.min_load_bars:
                health.skipped.append({"ticker": t, "reason": f"only {len(prices[t])} bars"})
                del prices[t]
    else:
        health.source = f"Yahoo Finance via yfinance ({cfg.period} daily, auto-adjusted)"
        log(f"Fetching {len(tickers)} tickers from Yahoo Finance ({cfg.period}) …")
        prices = fetch_prices(tickers, cfg.period, cfg, health)
        bench_px = None
        try:
            bench_px = fetch_one(cfg.benchmark, cfg.bench_period, cfg)
        except Exception as e:
            health.benchmark_note = f"Benchmark fetch failed ({e})"
    if not prices:
        raise SystemExit("No usable price data returned.")
    health.timings["download_s"] = round(time.perf_counter() - t0, 1)
    log_ok(f"Loaded {len(prices)}/{len(tickers)} tickers")

    prices = apply_intraday_bar(prices, cfg, health)
    prices = {t: df for t, df in prices.items() if len(df) >= cfg.min_load_bars}
    as_of = max(df.index[-1] for df in prices.values())

    # v52: closes of the STOCKS only, for Market Health breadth (display only)
    try:
        stocks = breadth_stock_list(cfg, tickers, prices, demo=demo)
        breadth_closes = pd.DataFrame({t: prices[t]["close"] for t in stocks})
    except Exception as e:
        log_warn(f"Breadth: stock list skipped ({type(e).__name__}: {e})")
        stocks, breadth_closes = [], pd.DataFrame()

    # --- indicators
    t1 = time.perf_counter()
    frames = prepare_frames(prices, cfg, health, as_of)
    if not frames:
        raise SystemExit("Indicator computation failed for every ticker.")

    # --- anchoring distribution (causal lookback uses bench_frame dates)
    components = list(cfg.trailing_weights) + list(cfg.emerging_weights)
    dist = {}
    bench_frame = None
    if bench_px is not None and len(bench_px) >= cfg.min_bars:
        try:
            bench_frame = compute_indicator_frame(bench_px, cfg)
            dist = build_distribution({cfg.benchmark: bench_frame}, components)
            health.benchmark_note = (f"Composites causally anchored to {cfg.benchmark} "
                                     f"({len(bench_px)} bars, lookback {cfg.pctile_lookback})")
        except Exception as e:
            health.benchmark_note = f"Benchmark indicators failed ({e})"
    if not dist:
        dist = build_distribution(frames, components)
        health.benchmark_note += " → using pooled-universe distribution instead"
        if bench_frame is None and cfg.benchmark in frames:
            bench_frame = frames[cfg.benchmark]
    log_ok(health.benchmark_note.strip(" →"))

    # --- history (every bar) and panel (latest bar) through the SAME code path
    group_refs = None
    cur = [t for t in cfg.currency_group if t in prices]
    if cfg.currency_own_anchor and len(cur) >= 3:
        comps_ = components
        pooled = []
        for t in cur:
            try:
                pooled.append(compute_indicator_frame(prices[t], cfg)[comps_])
            except Exception:
                pass
        if len(pooled) >= 3:
            ref_g = pd.concat(pooled).sort_index()
            cfg_g = copy.copy(cfg)
            cfg_g.pctile_lookback = cfg.pctile_lookback * len(pooled)
            cfg_g.pctile_min_obs = cfg.pctile_min_obs * len(pooled)
            group_refs = [(set(cur), ref_g, cfg_g)]
            health.notes.append(f"Currency tab: percentiles anchored to the group's own pooled history "
                                f"({len(pooled)} funds), not {cfg.benchmark}; SPY-regime and RS-vs-SPY gates skipped for the group")
    if any(t in prices for t in cfg.country_group):
        health.notes.append(f"Country ETFs: liquidity floor ${cfg.country_min_dollar_vol/1e6:.1f}M (stocks ${cfg.min_dollar_vol/1e6:.0f}M); "
                            f"SPY-regime gate skipped for the group")
    hist = score_history(frames, cfg, dist, ref_frame=bench_frame, group_refs=group_refs, stocks=stocks)
    if cfg.pctile_anchor == "universe":
        _last = hist[hist["Date"] == hist["Date"].max()]
        _n = int(_last["Rank_N"].max()) if len(_last) else 0
        health.notes.append(
            (f"Momentum percentiles / RS Rating: ranked across {_n} names on the latest bar "
             f"(volatility-adjusted: {'yes' if cfg.vol_adjust_momentum else 'no'})") if _n
            else f"Momentum percentiles: fewer than {cfg.xs_min_names} names on the latest bar, so the {cfg.benchmark} anchor was used")
    panel = hist.sort_values("Date").groupby("Ticker").tail(1).set_index("Ticker")
    panel = finalize_panel(panel, cfg, health)
    panel = apply_eod_alerts(panel, hist, cfg, health)
    panel["as_of_date"] = as_of.strftime("%Y-%m-%d")
    health.timings["compute_s"] = round(time.perf_counter() - t1, 1)

    # --- scorecard, changes
    card = scorecard(hist, cfg, cfg.benchmark)
    try:
        card["snapshots"] = ({"ok": False, "n_files": 0, "rows": [], "note": "not available with demo data"} if demo
                             else snapshot_scorecard(snap_dir, hist, cfg, cfg.benchmark))
    except Exception as e:
        card["snapshots"] = {"ok": False, "n_files": 0, "rows": [], "note": f"snapshot scorecard skipped ({type(e).__name__}: {e})"}
    try:
        gate_hist = market_gate_series(hist, cfg, stocks) if cfg.spy_regime_gate and cfg.market_gate_mode == "breadth" else pd.DataFrame()
    except Exception as e:
        log_warn(f"Market gate history skipped ({type(e).__name__}: {e})")
        gate_hist = pd.DataFrame()
    changes = compute_changes(panel, hist, cfg)
    health.timings["total_s"] = round(time.perf_counter() - t0, 1)

    # --- console summary
    log("")
    log("=" * 70)
    for side in ("BUY", "SELL", "EXIT"):
        sub = panel[panel["Recommendation"] == side]
        log(f"{side:5s} ({len(sub)}): " + (", ".join(sub.index) if len(sub) else "—"))
    log(f"Watch : " + ", ".join(f"{t}({w})" for t, w in panel["Watch"].items() if w) if panel["Watch"].any() else "Watch : —")
    log("=" * 70)
    log(f"Regimes: {panel['Regime'].value_counts().to_dict()}")
    if health.skipped:
        log_warn(f"Skipped: {', '.join(s['ticker'] for s in health.skipped)}")
    if health.stale:
        log_warn(f"Stale:   {', '.join(s['ticker'] for s in health.stale)}")
    if health.short:
        log_warn(f"Short history (no alerts): {', '.join(s['ticker'] for s in health.short)}")

    return {"panel": panel, "hist": hist, "health": health, "scorecard": card,
            "changes": changes, "as_of": panel["as_of_date"].iloc[0], "dist_components": sorted(dist),
            "breadth_stocks": stocks, "breadth_closes": breadth_closes, "market_gate": gate_hist}


# =============================================================================
#  5. DASHBOARD PAYLOAD
# =============================================================================

PANEL_COLS = {
    "rec": ("Recommendation", str), "watch": ("Watch", str), "gate": ("Gate_Block", str), "buy": ("Buy_Confidence", 0),
    "sell": ("Sell_Confidence", 0), "bias": ("Net_Bias", 0), "rsi": ("RSI_14", 1), "rsi_zone": ("RSI_Zone", str),
    "ppo": ("PPO", 3), "ppo_sig": ("PPO_Signal", 3), "ppo_d": ("PPO_Delta", 3),
    "sig_x": ("PPO_Sig_Cross_Recent", str), "zero_x": ("PPO_Zero_Cross_Recent", str),
    "bs_pos": ("PPO_Bars_Since_Pos", 0), "bs_neg": ("PPO_Bars_Since_Neg", 0),
    "bz_pos": ("PPO_Bars_Since_Zero_Pos", 0), "bz_neg": ("PPO_Bars_Since_Zero_Neg", 0),
    "e20": ("Close_vs_EMA20", 2), "e50": ("Close_vs_EMA50", 2), "e200": ("Close_vs_EMA200", 2),
    "stack": ("EMA_Bull_Stack", 0), "regime": ("Regime", str), "regime_conf": ("Regime_Confidence", 2),
    "mom": ("Momentum_Pctile", 1), "trail": ("Momentum_Trailing_Pctile", 1),
    "emerg": ("Momentum_Emerging_Pctile", 1), "dorm": ("Momentum_Dormancy_Pctile", 1),
    "sqz": ("Squeeze_Setup_Strength", 0), "sqz_full": ("Squeeze_Setup_Flag", 0),
    "sqz_f": ("Sqz_Foundation", 0), "sqz_m": ("Sqz_Momentum", 0), "sqz_c": ("Sqz_Condition", 0),
    "sqz_k": ("Sqz_Confirmation", 0), "sqz_on": ("Squeeze_On", 0), "sqz_len": ("Squeeze_Prior_Length", 0),
    "sq_base": ("SQ_Real_Base", 0), "sq_rel": ("SQ_Release", 0), "sq_ppo": ("SQ_PPO_Turning", 0),
    "sq_dmi": ("SQ_DMI_OK", 0), "sq_rsi": ("SQ_RSI_Waking", 0), "sq_room": ("SQ_Room_To_Run", 0),
    "sq_obv": ("SQ_OBV_Positive", 0), "sq_flat": ("SQ_Flat_Momentum", 0),
    "close": ("Last_Close", 2), "ret1": ("Ret_1d", 2), "hv": ("Historical_Vol", 1), "atr": ("ATR_Pct", 2),
    "rel": ("Signal_Reliability", 2), "adx": ("ADX_Trend", 1), "dmi": ("DMI_Value", 1),
    "hi52": ("High_52W_Ratio", 3), "obv": ("OBV_slope", 4), "persist": ("Trend_Persistence", 2),
    "dv": ("Dollar_Volume_20d", 0), "tradeable": ("Is_Tradeable", 0), "data_ok": ("Momentum_Data_OK", 0),
    "stale": ("Is_Stale", 0), "live": ("Is_Live", 0), "n_bars": ("N_Bars", 0), "last_bar": ("Last_Bar_Date", "date"),
    "b_ppo": ("Buy_Component_PPO_Cross", 0), "b_rsi": ("Buy_Component_RSI", 0),
    "b_ema": ("Buy_Component_EMA", 0), "b_per": ("Buy_Component_Persistence", 0),
    "s_ppo": ("Sell_Component_PPO_Cross", 0), "s_rsi": ("Sell_Component_RSI", 0),
    "s_ema": ("Sell_Component_EMA", 0), "s_per": ("Sell_Component_Weakness", 0),
    "s_floor": ("Sell_Floor_Applied", 0), "b_floor": ("Buy_Floor_Applied", 0),
    # v54
    "rs": ("RS_Rating", 0), "rank_n": ("Rank_N", 0), "rs20": ("RS_20d", 1),
    "in_tr": ("In_Trend", 0), "tr_days": ("Trend_Days", 0), "tr_entry": ("Trend_Entry", 2),
    "tr_date": ("Trend_Entry_Date", str), "tr_ret": ("Trend_Ret_Pct", 1), "tr_stop": ("Trend_Stop", 2),
    "tr_dist": ("Trend_Stop_Dist_Pct", 1), "tr_exit": ("Trend_Exit", str), "tr_cret": ("Trend_Closed_Ret", 1),
    "size": ("Size_Pct", 1), "buy_thr": ("Buy_Threshold", 0), "sell_thr": ("Sell_Threshold", 0),
}


def load_theme_universe(path) -> list[str]:
    """Unique tickers (first-seen order) from the Ticker column of the theme CSV.
    Yahoo style: BRK.B -> BRK-B. Returns [] and logs a warning on any problem."""
    import re
    try:
        df = pd.read_csv(path, encoding="utf-8-sig", dtype=str).fillna("")
        df.columns = [c.strip() for c in df.columns]
        if "Ticker" not in df.columns:
            log_warn(f"universe: {path} has no 'Ticker' column")
            return []
        out, seen = [], set()
        for t in df["Ticker"]:
            t = t.strip().upper().replace(".", "-")
            if not t or t in seen or not re.fullmatch(r"[A-Z0-9]{1,6}(-[A-Z0-9]{1,3})?", t):
                continue
            seen.add(t)
            out.append(t)
        return out
    except Exception as e:
        log_warn(f"universe: could not read {path} ({e})")
        return []


def load_themes(path) -> dict:
    """{TICKER: [theme, sub_theme]} from the theme CSV, PRIMARY assignment only.
    Display-only; any problem returns what was read so far (or {}) and logs a warning."""
    out: dict = {}
    try:
        df = pd.read_csv(path, encoding="utf-8-sig", dtype=str).fillna("")
        df.columns = [c.strip() for c in df.columns]
        need = {"Ticker", "Theme", "Sub Theme"}
        if not need.issubset(df.columns):
            log_warn(f"themes: {path} is missing column(s) {sorted(need - set(df.columns))}")
            return {}
        if "Assignment" in df.columns:
            prim = df[df["Assignment"].str.strip().str.lower() == "primary"]
            df = pd.concat([prim, df.drop(prim.index)])      # primary first; others only as a fallback
        for t, th, sb in zip(df["Ticker"], df["Theme"], df["Sub Theme"]):
            t = t.strip().upper()
            if t and t not in out:
                out[t] = [th.strip(), sb.strip()]
        log_ok(f"Themes    ← {path}  ({len(out)} tickers)")
    except Exception as e:
        log_warn(f"themes: could not read {path} ({e}) - Theme / Sub-Theme will not be shown")
    return out


def load_secondary_themes(path) -> dict:
    """{TICKER: [[theme, sub_theme], ...]} for Assignment == Secondary rows.
    Display-only; a secondary identical to the ticker's primary is dropped."""
    out: dict = {}
    try:
        df = pd.read_csv(path, encoding="utf-8-sig", dtype=str).fillna("")
        df.columns = [c.strip() for c in df.columns]
        need = {"Ticker", "Theme", "Sub Theme", "Assignment"}
        if not need.issubset(df.columns):
            return {}
        prim = {}
        for t, th, sb, a in zip(df["Ticker"], df["Theme"], df["Sub Theme"], df["Assignment"]):
            if a.strip().lower() == "primary":
                prim.setdefault(t.strip().upper(), (th.strip(), sb.strip()))
        for t, th, sb, a in zip(df["Ticker"], df["Theme"], df["Sub Theme"], df["Assignment"]):
            if a.strip().lower() != "secondary":
                continue
            t, pair = t.strip().upper(), [th.strip(), sb.strip()]
            if not t or not (pair[0] or pair[1]) or prim.get(t) == tuple(pair):
                continue
            lst = out.setdefault(t, [])
            if pair not in lst:
                lst.append(pair)
        log_ok(f"Secondary ← {path}  ({len(out)} tickers)")
    except Exception as e:
        log_warn(f"themes: could not read secondary assignments ({e})")
    return out


def _norm_col(c) -> str:
    """'Sub-Theme Breadth' / 'sub_theme breath' -> 'sub theme breath' (the file spells it Breath)."""
    return str(c).strip().lower().replace("-", " ").replace("_", " ").replace("breadth", "breath")


def load_theme_signals(path) -> dict:
    """Weekly Theme / Sub-Theme signal file (display only). Never raises: problems go to out["error"].
    rows: [{th, sb, sig, st, tb, sbr, upd}]  as_of = latest 'updated' value."""
    out = {"loaded": False, "rows": [], "as_of": "", "file": str(path), "error": ""}
    try:
        df = pd.read_csv(path, encoding="utf-8-sig", dtype=str).fillna("")
        cols = {_norm_col(c): c for c in df.columns}
        need = ["theme", "sub theme", "signal"]
        miss = [n for n in need if n not in cols]
        if miss:
            out["error"] = f"missing column(s): {', '.join(miss)}"
            log_warn(f"theme signals: {path} {out['error']}")
            return out

        def num(v, nd=1):
            try:
                return round(float(str(v).strip()), nd)
            except Exception:
                return None

        for _, r in df.iterrows():
            th, sb = str(r[cols["theme"]]).strip(), str(r[cols["sub theme"]]).strip()
            if not th or not sb:
                continue
            st = num(r[cols["stars"]], 0) if "stars" in cols else None
            out["rows"].append({
                "th": th, "sb": sb, "sig": str(r[cols["signal"]]).strip().upper(),
                "st": int(st) if st is not None else None,
                "tb": num(r[cols["theme breath"]]) if "theme breath" in cols else None,
                "sbr": num(r[cols["sub theme breath"]]) if "sub theme breath" in cols else None,
                "upd": str(r[cols["updated"]]).strip() if "updated" in cols else "",
            })
        out["as_of"] = max((r["upd"] for r in out["rows"] if r["upd"]), default="")
        out["loaded"] = bool(out["rows"])
        if not out["rows"]:
            out["error"] = "no data rows"
        else:
            log_ok(f"ThemeSig  ← {path}  ({len(out['rows'])} sub-themes, as of {out['as_of'] or '?'})")
    except Exception as e:
        out["error"] = str(e)
        log_warn(f"theme signals: could not read {path} ({e})")
    return out


def load_theme_members(path) -> dict:
    """{(theme, sub_theme): {TICKER: 'P'|'S'}} from the theme membership CSV, primary AND secondary
    assignments (primary wins when a ticker is listed both ways). Display only; {} on any problem."""
    out: dict = {}
    try:
        df = pd.read_csv(path, encoding="utf-8-sig", dtype=str).fillna("")
        df.columns = [c.strip() for c in df.columns]
        if not {"Ticker", "Theme", "Sub Theme"}.issubset(df.columns):
            return {}
        asg = df["Assignment"] if "Assignment" in df.columns else pd.Series(["Primary"] * len(df))
        for t, th, sb, a in zip(df["Ticker"], df["Theme"], df["Sub Theme"], asg):
            t, key = t.strip().upper(), (th.strip(), sb.strip())
            if not t or not key[0] or not key[1]:
                continue
            flag = "S" if str(a).strip().lower() == "secondary" else "P"
            cur = out.setdefault(key, {})
            if t not in cur or (cur[t] == "S" and flag == "P"):
                cur[t] = flag
    except Exception as e:
        log_warn(f"theme signals: could not read members from {path} ({e})")
    return out


def build_theme_signal(cfg: Config, tickers) -> dict:
    """Payload block for the Theme Signals tab: the weekly rows plus, per sub-theme, its loaded tickers."""
    out = load_theme_signals(cfg.theme_signal_csv)
    out["stale_days"] = cfg.theme_signal_stale_days
    members: dict = {}
    if out["rows"]:
        raw, have = load_theme_members(cfg.themes_csv), set(tickers)
        empty = []
        for r in out["rows"]:
            lst, seen = [], set()
            for t, a in raw.get((r["th"], r["sb"]), {}).items():
                tt = t if t in have else next((x for x in (t.replace("-", "."), t.replace(".", "-")) if x in have), None)
                if tt and tt not in seen:
                    seen.add(tt)
                    lst.append([tt, a])
            members[r["th"] + "\u0001" + r["sb"]] = lst
            if not lst:
                empty.append(r["sb"])
        if empty:
            log_warn(f"Theme Signals: {len(empty)} sub-theme(s) have no loaded tickers: {'; '.join(empty[:6])}{' ...' if len(empty) > 6 else ''}")
    out["members"] = members
    return out


def _theme_regime(t: float, e: float, cfg: Config) -> str:
    """Same trailing x emerging rules as add_composites, applied to medians."""
    if not (np.isfinite(t) and np.isfinite(e)):
        return "Neutral"
    hi, lo, gap = cfg.regime_hi, cfg.regime_lo, cfg.regime_gap
    if t >= hi and e >= hi:
        return "Strong"
    if t < lo and e < lo:
        return "Weak"
    if e > t + gap:
        return "Dormant→Waking"
    if t > e + gap:
        return "Mature/Cooling"
    return "Neutral"


def build_theme_stats(panel: pd.DataFrame, hist: pd.DataFrame, themes: dict, cfg: Config,
                      exclude=()) -> dict:
    """Aggregate PRIMARY theme / sub-theme scores (display only).

    themes  : {TICKER: [theme, sub_theme]} (primary assignment only)
    exclude : tickers left out (Sector / Six Pack / ETF / Country ETF funds)
    Pillars (each 0-100): momentum = median Mom percentile; breadth = mean of
    %% above EMA200, %% bull-stacked, %% PPO>0; signals = 50 + avg net bias / 2;
    accel = 50 + 2 x d5(median Emerging) + 0.25 x d5(avg bias) + 1.5 x median RS20.
    Score = weighted blend (Config.theme_weights). Computed for every session in
    the history window; counts (Buy/Sell/...) come from the panel as displayed."""
    ex = {str(t).upper() for t in exclude}
    members = {t: v for t, v in themes.items() if t in panel.index and t not in ex and v and v[0]}
    out = {"themes": [], "subs": [], "dates": [], "min_members": cfg.theme_min_members,
           "weights": cfg.theme_weights}
    if not members:
        return out
    nh = cfg.theme_history_bars
    tail_n = max(nh, cfg.rotation_tail_bars + 1)
    h = hist[hist["Ticker"].isin(members)].copy()
    dates = sorted(h["Date"].unique())[-(tail_n + 5):]
    h = h[h["Date"].isin(dates)]
    h["_th"] = h["Ticker"].map(lambda t: members[t][0])
    h["_sb"] = h["Ticker"].map(lambda t: members[t][1] or "(general)")
    h["_a200"] = (h["Below_EMA200"] == 0) * 100.0
    h["_stk"] = h["EMA_Bull_Stack"] * 100.0
    h["_ppo"] = h["PPO_Above_Zero"] * 100.0
    if "RS_20d" not in h.columns:
        h["RS_20d"] = np.nan
    W = cfg.theme_weights

    def agg(keys):
        g = h.groupby(keys + ["Date"]).agg(
            n=("Ticker", "size"), mom=("Momentum_Pctile", "median"),
            trail=("Momentum_Trailing_Pctile", "median"), emerg=("Momentum_Emerging_Pctile", "median"),
            a200=("_a200", "mean"), stk=("_stk", "mean"), ppo=("_ppo", "mean"),
            bias=("Net_Bias", "mean"), rs=("RS_20d", "median")).reset_index()
        g = g.sort_values(keys + ["Date"])
        gb = g.groupby(keys, sort=False)
        g["d_em"] = (g["emerg"] - gb["emerg"].shift(5))
        g["d_bias"] = (g["bias"] - gb["bias"].shift(5))
        g["p_mom"] = g["mom"].clip(0, 100)
        g["p_brd"] = ((g["a200"] + g["stk"] + g["ppo"]) / 3).clip(0, 100)
        g["p_sig"] = (50 + g["bias"] / 2).clip(0, 100)
        g["p_acc"] = (50 + 2 * g["d_em"].fillna(0) + 0.25 * g["d_bias"].fillna(0)
                      + 1.5 * g["rs"].fillna(0)).clip(0, 100)
        g["score"] = (W["momentum"] * g["p_mom"] + W["breadth"] * g["p_brd"]
                      + W["signals"] * g["p_sig"] + W["accel"] * g["p_acc"])
        return g

    pn = panel.loc[list(members)].copy()
    pn["_th"] = [members[t][0] for t in pn.index]
    pn["_sb"] = [members[t][1] or "(general)" for t in pn.index]

    def build(keys):
        g = agg(keys)
        rows = []
        for key, grp in g.groupby(keys, sort=False):
            key = key if isinstance(key, tuple) else (key,)
            grp = grp.sort_values("Date")
            last = grp.iloc[-1]
            m = pn
            for k, v in zip(keys, key):
                m = m[m[k] == v]
            n_now = int(len(m))
            def _s(col, nd, last_n):
                return [_rnd(x, nd) for x in grp[col].tail(last_n)]
            prev5 = grp["score"].iloc[-6] if len(grp) >= 6 else np.nan
            rows.append({
                "name": key[-1], **({"theme": key[0]} if len(keys) == 2 else {}),
                "n": n_now, "small": bool(n_now < cfg.theme_min_members),
                "score": _rnd(last["score"], 1), "d5": _rnd(last["score"] - prev5, 1),
                "p_mom": _rnd(last["p_mom"], 1), "p_brd": _rnd(last["p_brd"], 1),
                "p_sig": _rnd(last["p_sig"], 1), "p_acc": _rnd(last["p_acc"], 1),
                "mom": _rnd(last["mom"], 1), "trail": _rnd(last["trail"], 1), "emerg": _rnd(last["emerg"], 1),
                "regime": _theme_regime(last["trail"], last["emerg"], cfg),
                "a200": _rnd(last["a200"], 0), "stack": _rnd(last["stk"], 0), "ppo_pos": _rnd(last["ppo"], 0),
                "bias": _rnd(last["bias"], 1), "rs": _rnd(last["rs"], 1),
                "buy": int((m["Recommendation"] == "BUY").sum()), "sell": int((m["Recommendation"] == "SELL").sum()),
                "exit": int((m["Recommendation"] == "EXIT").sum()), "watch": int((m["Watch"] != "").sum()),
                "hist": _s("score", 1, nh), "tr": _s("trail", 1, cfg.rotation_tail_bars + 1),
                "em": _s("emerg", 1, cfg.rotation_tail_bars + 1),
                "tickers": sorted(m.index.tolist()),
            })
        return rows

    out["themes"] = build(["_th"])
    out["subs"] = build(["_th", "_sb"])
    out["dates"] = [pd.Timestamp(d).strftime("%m-%d") for d in dates[-nh:]]
    return out


def load_company_names(path) -> dict:
    """{TICKER: company name} from the 'Company Name' column of the theme CSV
    (primary rows first). Display-only; any problem returns {} and logs a warning."""
    out: dict = {}
    try:
        df = pd.read_csv(path, encoding="utf-8-sig", dtype=str).fillna("")
        df.columns = [c.strip() for c in df.columns]
        col = next((c for c in df.columns if c.lower().replace("_", " ") in ("company name", "company", "name")), None)
        if col is None or "Ticker" not in df.columns:
            log_warn(f"names: no 'Company Name' column in {path} - company names will not be shown")
            return {}
        if "Assignment" in df.columns:
            prim = df[df["Assignment"].str.strip().str.lower() == "primary"]
            df = pd.concat([prim, df.drop(prim.index)])
        for t, nm in zip(df["Ticker"], df[col]):
            t, nm = t.strip().upper(), nm.strip()
            if t and nm and t not in out:
                out[t] = nm
        log_ok(f"Names     ← {path}  ({len(out)} tickers)")
    except Exception as e:
        log_warn(f"names: could not read {path} ({e}) - company names will not be shown")
    return out


# ---------- Bonds tab: Treasury yield curve ----------------------------------------------------------------
TREASURY_CACHE = Path(__file__).resolve().with_name("treasury_cache.json")
CURVE_WHEN = [("now", "Current"), ("1w", "1 week ago"), ("1m", "1 month ago"), ("3m", "3 months ago"), ("1y", "1 year ago")]


def load_treasury_curve(cfg: "Config", offline: bool = False) -> dict:
    """Daily Treasury CMT yields (percent). Primary source: FRED's public CSV (no key). Fallback: Yahoo for the
    maturities it carries (3M, 5Y, 10Y, 30Y). The last good pull is cached so an offline run still shows a curve."""
    curve = cfg.treasury_curve
    labels = list(curve)

    def build(df: "pd.DataFrame", src: str) -> dict:
        df = df.sort_index().dropna(how="all")
        if df.empty:
            raise ValueError("no yield rows")
        last = df.index[-1]
        offs = {"now": pd.Timedelta(0), "1w": pd.Timedelta(days=7), "1m": pd.DateOffset(months=1),
                "3m": pd.DateOffset(months=3), "1y": pd.DateOffset(years=1)}
        out = {"ok": True, "src": src, "asof": str(last.date()), "labels": labels,
               "years": {l: curve[l][0] for l in labels}, "when": {}, "series": {}}
        for k, _nm in CURVE_WHEN:
            tgt = last - offs[k]
            sub = df.loc[:tgt]
            if sub.empty:
                out["series"][k] = {l: None for l in labels}
                out["when"][k] = None
                continue
            out["when"][k] = str(sub.index[-1].date())
            out["series"][k] = {l: (None if pd.isna(sub[l].ffill().iloc[-1]) else round(float(sub[l].ffill().iloc[-1]), 3)) for l in labels}
        return out

    if not offline:
        try:                                                      # FRED
            import io
            import urllib.request
            ids = ",".join(curve[l][1] for l in labels)
            start = (pd.Timestamp.today() - pd.DateOffset(years=1, months=1)).strftime("%Y-%m-%d")
            req = urllib.request.Request(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={ids}&cosd={start}",
                                         headers={"User-Agent": "Mozilla/5.0"})
            raw = urllib.request.urlopen(req, timeout=20).read().decode("utf-8")
            df = pd.read_csv(io.StringIO(raw))
            df = df.rename(columns={df.columns[0]: "date"})
            df["date"] = pd.to_datetime(df["date"])
            df = df.set_index("date")
            df = df.rename(columns={curve[l][1]: l for l in labels}).apply(pd.to_numeric, errors="coerce")
            res = build(df[[l for l in labels if l in df.columns]].reindex(columns=labels), "FRED (US Treasury constant-maturity yields)")
            TREASURY_CACHE.write_text(json.dumps(res), encoding="utf-8")
            log_ok(f"Treasuries ← FRED  (as of {res['asof']})")
            return res
        except Exception as e:
            log_warn(f"treasury curve: FRED not read ({e}) - trying Yahoo")
        try:                                                      # Yahoo fallback (partial curve)
            yf = _yf()
            cols = {}
            for l in labels:
                sym = curve[l][2]
                if not sym:
                    continue
                h = yf.Ticker(sym).history(period="14mo", auto_adjust=False)["Close"]
                h.index = pd.to_datetime(h.index).tz_localize(None).normalize()
                cols[l] = h
            if cols:
                res = build(pd.DataFrame(cols).reindex(columns=labels), "Yahoo Finance (only 3M, 5Y, 10Y, 30Y available)")
                TREASURY_CACHE.write_text(json.dumps(res), encoding="utf-8")
                log_ok(f"Treasuries ← Yahoo  (as of {res['asof']}, partial curve)")
                return res
        except Exception as e:
            log_warn(f"treasury curve: Yahoo not read ({e})")
    try:
        res = json.loads(TREASURY_CACHE.read_text(encoding="utf-8"))
        if res.get("ok"):
            res["src"] = str(res.get("src", "")) + " (cached)"
            log_warn(f"treasury curve: using the cached curve as of {res.get('asof')}")
            return res
    except Exception:
        pass
    return {"ok": False, "labels": labels}


FUND_FIELDS = {   # payload key -> spreadsheet column (matched ignoring case, spaces, "_", "-" and "/")
    "qs": "Quality_Score", "croic": "CROIC", "gp": "gp_5Y", "np": "np_5Y", "oid": "OI/Debt",
    "shr": "shares_chg_3Y", "ig": "implied_growth", "pf": "piotroski_f-score",
    "rd": "Report Date", "upd": "Updated",
}


def _fund_key(c) -> str:
    return "".join(ch for ch in str(c).lower() if ch.isalnum())


def _fund_table(df: pd.DataFrame) -> dict:
    """{TICKER: {key: text}} from the Score table. Values stay as the sheet shows them ("28%", "0.9")."""
    cols = {_fund_key(c): c for c in df.columns}
    tk = cols.get("ticker")
    if tk is None:
        raise RuntimeError("no Ticker column")
    use = {k: cols[_fund_key(c)] for k, c in FUND_FIELDS.items() if _fund_key(c) in cols}
    missing = [c for k, c in FUND_FIELDS.items() if k not in use and k not in ("rd", "upd")]
    if missing:
        log_warn(f"fundamentals: column(s) not found: {', '.join(missing)}")
    out: dict = {}
    for _, r in df.iterrows():
        t = str(r[tk]).strip().upper()
        if not t or t in out:
            continue
        d = {k: str(r[c]).strip() for k, c in use.items() if str(r[c]).strip()}
        if d:
            out[t] = d
    return out


def load_fundamentals(cfg: Config, offline: bool = False) -> dict:
    """Fundamentals for the Ticker page (display only). Google Sheet first, then the local CSV.
    Any problem returns {} and logs a warning; it never stops the run."""
    url = "" if offline else str(getattr(cfg, "fundamentals_url", "") or "")
    if url:
        try:
            import io
            import requests
            r = requests.get(url, timeout=30, headers=MH_UA)
            r.raise_for_status()
            txt = r.content.decode("utf-8-sig", errors="replace")
            if "ticker" not in txt[:2000].lower() or txt.lstrip()[:1] == "<":
                raise RuntimeError("the sheet did not return CSV - share it as 'anyone with the link can view'")
            out = _fund_table(pd.read_csv(io.StringIO(txt), dtype=str).fillna(""))
            log_ok(f"Fundament ← Google Sheet  ({len(out)} tickers)")
            return out
        except Exception as e:
            log_warn(f"fundamentals: Google Sheet not read ({e}) - trying {cfg.fundamentals_csv}")
    path = getattr(cfg, "fundamentals_csv", None)
    try:
        if not path or not Path(path).exists():
            log_warn(f"fundamentals: {path} not found - the Ticker page will not show the fundamentals row")
            return {}
        out = _fund_table(pd.read_csv(path, encoding="utf-8-sig", dtype=str).fillna(""))
        log_ok(f"Fundament ← {path}  ({len(out)} tickers)")
        return out
    except Exception as e:
        log_warn(f"fundamentals: could not read {path} ({e}) - the Ticker page will not show the fundamentals row")
        return {}


def lookup_fund_names(tickers) -> dict:
    """Best-effort Yahoo lookup of fund names for the ETF tab. Never raises."""
    out: dict = {}
    try:
        import yfinance as yf
    except Exception:
        return out
    for t in tickers:
        try:
            info = yf.Ticker(t).get_info() or {}
            nm = info.get("longName") or info.get("shortName")
            if nm:
                out[t] = str(nm).strip()
        except Exception:
            pass
    return out


def build_payload(res: dict, cfg: Config, run_ts: str, paths: "OutputPaths | None") -> dict:
    panel: pd.DataFrame = res["panel"]
    hist: pd.DataFrame = res["hist"]
    health: DataHealth = res["health"]

    rows = []
    for t, r in panel.iterrows():
        d = {"t": t}
        for key, (col, kind) in PANEL_COLS.items():
            v = r.get(col)
            if kind is str:
                d[key] = "" if v is None or (isinstance(v, float) and np.isnan(v)) else str(v)
            elif kind == "date":
                d[key] = pd.Timestamp(v).strftime("%Y-%m-%d") if not pd.isna(v) else ""
            else:
                d[key] = _rnd(v, kind)
        rows.append(d)

    # per-ticker history for the drawer & rotation tails
    hb = max(cfg.ticker_history_bars, cfg.drawer_history_bars)
    history = {}
    hist_sorted = hist.sort_values(["Ticker", "Date"])
    reg_code = {"Strong": "S", "Dormant→Waking": "D", "Neutral": "N", "Mature/Cooling": "M", "Weak": "W"}
    for t, g in hist_sorted.groupby("Ticker", sort=False):
        g = g.tail(hb)
        history[t] = {
            "d": [x.strftime("%Y-%m-%d") for x in g["Date"]],
            "c": [_rnd(x, 2) for x in g["Last_Close"]],
            "v": [_rnd(x, 0) for x in g["Volume"]],
            "e20": [_rnd(x, 2) for x in g["EMA20"]],
            "e50": [_rnd(x, 2) for x in g["EMA50"]],
            "e200": [_rnd(x, 2) for x in g["EMA200"]],
            "ppo": [_rnd(x, 3) for x in g["PPO"]],
            "sig": [_rnd(x, 3) for x in g["PPO_Signal"]],
            "h": [_rnd(x, 3) for x in g["PPO_Delta"]],
            "rsi": [_rnd(x, 1) for x in g["RSI_14"]],
            "b": [int(x) for x in g["Buy_Confidence"]],
            "s": [int(x) for x in g["Sell_Confidence"]],
            "rec": [str(x)[0] for x in g["Recommendation"]],          # B/S/E/H
            "reg": [reg_code.get(x, "N") for x in g["Regime"]],
            "tr": [_rnd(x, 1) for x in g["Momentum_Trailing_Pctile"]],
            "em": [_rnd(x, 1) for x in g["Momentum_Emerging_Pctile"]],
            "mom": [_rnd(x, 1) for x in g["Momentum_Pctile"]],
            "sq": [int(x) for x in g["Squeeze_On"]],
            "it": [int(x) for x in g["In_Trend"]],                     # v54: in-trend flag
            "st": [_rnd(x, 2) for x in g["Trend_Stop"]],               # v54: trailing stop (blank when flat)
            "hv": [_rnd(x, 0) for x in g["Historical_Vol"]],
            "pmo": [_rnd(x, 3) for x in g["PMO"]],           # informational, not scored
            "pmos": [_rnd(x, 3) for x in g["PMO_Signal"]],
        }

    load_themes_map = load_themes(cfg.themes_csv)
    # BRK-B / BRK.B style differences between the price feed and the theme file
    for t in panel.index:
        if t not in load_themes_map:
            for alt in (t.replace("-", "."), t.replace(".", "-")):
                if alt in load_themes_map:
                    load_themes_map[t] = load_themes_map[alt]
                    break

    sec_map = load_secondary_themes(cfg.themes_csv)
    for t in panel.index:                                # BRK-B / BRK.B style differences
        if t not in sec_map:
            for alt in (t.replace("-", "."), t.replace(".", "-")):
                if alt in sec_map:
                    sec_map[t] = sec_map[alt]
                    break

    names_map = load_company_names(cfg.themes_csv)
    for t in panel.index:                                # BRK-B / BRK.B style differences
        if t not in names_map:
            for alt in (t.replace("-", "."), t.replace(".", "-")):
                if alt in names_map:
                    names_map[t] = names_map[alt]
                    break
    fund_map = load_fundamentals(cfg, offline=str(health.source).startswith("SYNTHETIC"))
    treasury = load_treasury_curve(cfg, offline=str(health.source).startswith("SYNTHETIC"))
    for t in panel.index:                                # BRK-B / BRK.B style differences
        if t not in fund_map:
            for alt in (t.replace("-", "."), t.replace(".", "-")):
                if alt in fund_map:
                    fund_map[t] = fund_map[alt]
                    break
    etf_names = {str(k).strip().upper(): v for k, v in (cfg.etf_names or {}).items()}
    names_map.update({t: v for t, v in etf_names.items() if v})
    names_map.update({str(t).upper(): nm for t, (_c, nm) in cfg.country_etfs.items() if nm})   # full fund names
    names_map.update({str(t).upper(): nm for t, (_c, nm) in cfg.currency_etfs.items() if nm})
    names_map.update({str(t).upper(): nm for t, nm in cfg.currency_ref.items() if nm})
    need = [t for t in list(cfg.etf_tickers) + list(cfg.bond_etfs) if t in panel.index and t not in names_map]
    if need and "yfinance" in (res["health"].source or ""):
        names_map.update(lookup_fund_names(need))
    grp = set(cfg.sector_names) | set(cfg.six_pack) | set(cfg.country_etfs) | set(cfg.currency_group)      # these use their own names (country for Country ETFs) as the Theme
    no_theme = [t for t in panel.index if t not in load_themes_map and t not in grp and t not in set(cfg.etf_tickers) and t not in set(cfg.bond_etfs)] if load_themes_map else []
    if no_theme:
        log_warn(f"Not in the Theme file ({len(no_theme)}): {', '.join(no_theme)}")

    theme_stats = build_theme_stats(panel, hist, load_themes_map, cfg,
                                    exclude=set(grp) | set(cfg.etf_tickers) | set(cfg.bond_etfs))
    theme_signal = build_theme_signal(cfg, panel.index)        # v56: weekly Theme Signals tab (display only)
    n = len(panel)
    kpis = {
        "n": n,
        "buy": int((panel["Recommendation"] == "BUY").sum()),
        "sell": int((panel["Recommendation"] == "SELL").sum()),
        "exit": int((panel["Recommendation"] == "EXIT").sum()),
        "hold": int((panel["Recommendation"] == "HOLD").sum()),
        "watch": int((panel["Watch"] != "").sum()),
        "pct_above200": _rnd(100 * (panel["Below_EMA200"] == 0).mean(), 0),
        "pct_stack": _rnd(100 * (panel["EMA_Bull_Stack"] == 1).mean(), 0),
        "pct_ppo_pos": _rnd(100 * (panel["PPO_Above_Zero"] == 1).mean(), 0),
        "avg_bias": _rnd(panel["Net_Bias"].mean(), 1),
        "regimes": panel["Regime"].value_counts().reindex(REGIMES, fill_value=0).to_dict(),
    }
    # breadth history from reconstructed bars (last 60 sessions)
    ok_hist = hist[hist["Momentum_Data_OK"] == 1]
    stk = res.get("breadth_stocks") or []
    if stk:                                              # v52: stocks only (no ETFs / funds)
        ok_hist = ok_hist[ok_hist["Ticker"].isin(stk)]
    by_date = ok_hist.groupby("Date").agg(
        pct200=("Below_EMA200", lambda s: 100 * (s == 0).mean()),
        buys=("Recommendation", lambda s: int((s == "BUY").sum())),
        sells=("Recommendation", lambda s: int((s == "SELL").sum())),
        bias=("Net_Bias", "mean"),
    ).tail(hb)
    breadth = {"d": [x.strftime("%m-%d") for x in by_date.index],
               "pct200": [_rnd(x, 0) for x in by_date["pct200"]],
               "buys": by_date["buys"].tolist(), "sells": by_date["sells"].tolist(),
               "bias": [_rnd(x, 1) for x in by_date["bias"]], "n": int(ok_hist["Ticker"].nunique())}

    gb = panel[(panel["Gate_Block"].fillna("") != "") & (panel["Recommendation"] == "HOLD")
               & (panel["Buy_Confidence"] >= panel["Buy_Threshold"])].sort_values("Buy_Confidence", ascending=False)
    gate_blocked = [{"ticker": t, "reason": str(r["Gate_Block"]), "buy": int(r["Buy_Confidence"]),
                     "sell": int(r["Sell_Confidence"]), "regime": str(r["Regime"])} for t, r in gb.iterrows()]

    # v42: 60-day correlation of daily returns to the benchmark and to the dollar reference (hedge fit)
    fxcorr: dict = {}
    try:
        have_t = set(hist["Ticker"])
        cur = [t for t in cfg.currency_group if t in have_t]
        uup = next(iter(cfg.currency_ref), None)
        want = list(dict.fromkeys(cur + [cfg.benchmark]))
        pv = (hist[hist["Ticker"].isin(want)].pivot(index="Date", columns="Ticker", values="Ret_1d")
              .sort_index().tail(cfg.currency_corr_window))
        for t in cur:
            d = {}
            for key, other in (("spy", cfg.benchmark), ("uup", uup)):
                if other and other != t and other in pv.columns and t in pv.columns:
                    d[key] = _rnd(pv[t].corr(pv[other]), 2)
            fxcorr[t] = d
    except Exception as e:
        log_warn(f"currency correlations skipped ({e})")

    # v54: market gate history for the Market Health strip
    gate = {"ok": False, "mode": cfg.market_gate_mode, "on": bool(cfg.spy_regime_gate)}
    G = res.get("market_gate")
    if G is not None and len(G):
        G = G.sort_index().tail(cfg.gate_history_bars)
        last = G.iloc[-1]
        nb = lambda v: None if pd.isna(v) else bool(v)
        gate.update({
            "ok": True, "d": [x.strftime("%Y-%m-%d") for x in G.index],
            "closed": [int(bool(x)) for x in G["closed"]],
            "idx": [int(bool(x)) for x in G["idx_weak"]], "brd": [int(bool(x)) for x in G["brd_weak"]],
            "pct200": [_rnd(x, 0) for x in G["pct200"]], "pct50": [_rnd(x, 0) for x in G["pct50"]],
            "pct_closed": _rnd(100 * G["closed"].mean(), 0), "sessions": int(len(G)),
            "now": {"closed": bool(last["closed"]), "idx": bool(last["idx_weak"]), "brd": bool(last["brd_weak"]),
                    "spy_below": nb(last["spy_below"]), "rsp_below": nb(last["rsp_below"]),
                    "pct200": _rnd(last["pct200"], 0), "pct50": _rnd(last["pct50"], 0), "n": int(last["n"])},
            "min200": cfg.gate_breadth_200_min, "min50": cfg.gate_breadth_50_min, "min_names": cfg.gate_breadth_min_names,
        })

    out_paths = {}
    if paths is not None:
        out_paths = {"html": str(paths.html), "csv": str(paths.csv), "snapshots": str(paths.snapshots),
                     "notes": paths.notes}

    return {
        "version": VERSION, "run_ts": run_ts, "as_of": res["as_of"],
        "cfg": {
            "buy_thr": cfg.buy_alert_threshold, "sell_thr": cfg.sell_alert_threshold,
            "watch_margin": cfg.watch_margin, "fresh_bars": cfg.ppo_fresh_bars,
            "sell_floor": cfg.sell_cross_floor, "conflict_margin": cfg.conflict_margin,
            "benchmark": cfg.benchmark, "min_bars": cfg.min_bars, "min_dv": cfg.min_dollar_vol,
            "min_price": cfg.min_price, "min_rel": cfg.min_reliability,
            "regime_hi": cfg.regime_hi, "regime_lo": cfg.regime_lo, "horizons": list(cfg.fwd_horizons),
            "context": [t for t in cfg.context_tickers if t in panel.index],
            "sectors": [{"t": t, "name": n} for t, n in cfg.sector_names.items()],
            "six_pack": [{"t": t, "cap": c, "style": st, "name": n} for t, (c, st, n) in cfg.six_pack.items()],
            "etfs": [{"t": t, "name": names_map.get(t, "")} for t in cfg.etf_tickers],
            "bond_etfs": [{"t": t, "name": names_map.get(t, "")} for t in cfg.bond_etfs],
            "country_etfs": [{"t": t, "country": c, "name": n} for t, (c, n) in cfg.country_etfs.items()],
            "tear": [{"t": t, "name": names_map.get(t, "")} for t in cfg.tear_tickers],
            "shortlist": [{"t": t, "name": names_map.get(t, "")} for t in cfg.shortlist_tickers],
            "currency": [{"t": t, "currency": c, "name": n, "kind": "fx"} for t, (c, n) in cfg.currency_etfs.items()]
                        + [{"t": t, "currency": "US Dollar", "name": n, "kind": "ref"} for t, n in cfg.currency_ref.items()],
            "fx_w": cfg.currency_dxy_weights, "fx_floor": cfg.currency_min_dollar_vol, "country_floor": cfg.country_min_dollar_vol,
            "fx_anchor": cfg.currency_own_anchor, "fx_corr_win": cfg.currency_corr_window,
            "pmo": [cfg.pmo_roc_len, cfg.pmo_smooth_len, cfg.pmo_sig_len],
            "theme_w": cfg.theme_weights, "theme_min": cfg.theme_min_members,
            "tail_bars": cfg.rotation_tail_bars, "drawer_bars": cfg.drawer_history_bars, "log_rows": cfg.session_log_rows,
            "trailing_w": cfg.trailing_weights, "emerging_w": cfg.emerging_weights,
            "require_cross": cfg.require_ppo_cross_for_alert,
            "alerts_eod": cfg.alerts_eod_only, "rs_gate": cfg.rs_gate,
            "spy_gate": cfg.spy_regime_gate, "regime_both": cfg.regime_need_both, "regime_confirm": cfg.regime_confirm, "e200_gate": cfg.require_above_ema200_for_buy,
            "rs_min": cfg.rs_min_excess_for_buy, "top_filter": cfg.stronger_top_detection,
            "rs_lookback": cfg.rs_lookback,
            "vol_mult": cfg.vol_confirm_mult, "pctile_lb": cfg.pctile_lookback,
            "vol_rel_hi": cfg.vol_rel_hi, "vol_rel_lo": cfg.vol_rel_lo, "vol_rel_bars": cfg.vol_rel_bars,
            # v20: values the Guide's Buy/Sell score section displays
            "buy_thr_reg": cfg.buy_thr_by_regime, "sell_thr_reg": cfg.sell_thr_by_regime,
            "atr_cap": cfg.atr_soft_cap, "atr_extra": cfg.atr_extra_points,
            "sqz_buy_cap": cfg.sqz_buy_add_cap, "sqz_sell_cap": cfg.sqz_sell_add_cap,
            "sell_damp": cfg.sell_vol_damping_on_cross, "sell_wfloor": cfg.sell_regime_weight_floor,
            "buy_rw": BUY_REGIME_W, "sell_rw": SELL_REGIME_W,
            # v54
            "anchor": cfg.pctile_anchor, "vol_adj": cfg.vol_adjust_momentum, "xs_min": cfg.xs_min_names,
            "symmetric": cfg.symmetric_scoring, "vol_damp": cfg.vol_damping, "buy_floor": cfg.buy_cross_floor,
            "persist_win": cfg.persist_window, "trend_on": cfg.trend_state, "stop_mult": cfg.trend_stop_atr_mult,
            "risk_pct": cfg.risk_per_trade_pct, "max_pos": cfg.max_position_pct, "gate_mode": cfg.market_gate_mode,
            "gate200": cfg.gate_breadth_200_min, "gate50": cfg.gate_breadth_50_min,
        },
        "gate": gate,
        "kpis": kpis, "rows": rows, "history": history, "breadth": breadth, "fxcorr": fxcorr,
        "themes": {t: load_themes_map[t] for t in panel.index if t in load_themes_map},
        "themes2": {t: sec_map[t] for t in panel.index if t in sec_map},
        "tstats": theme_stats,
        "tsig": theme_signal,
        "names": {t: names_map[t] for t in panel.index if t in names_map},
        "fund": {t: fund_map[t] for t in panel.index if t in fund_map},
        "yields": treasury,
        "changes": res["changes"], "scorecard": res["scorecard"],
        "health": {
            "source": health.source, "benchmark": health.benchmark_note, "skipped": health.skipped,
            "short": health.short, "stale": health.stale, "illiquid": health.illiquid,
            "partial_dropped": health.partial_dropped, "live_bars": health.live_bars,
            "notes": health.notes, "timings": health.timings,
            "gate_blocked": gate_blocked,
            "universe": len(cfg.tickers), "loaded": n, "no_theme": no_theme, "themes_loaded": bool(load_themes_map), "dist_components": res["dist_components"],
            "paths": out_paths,
        },
    }


# =============================================================================
#  5b. MARKET HEALTH (v49) - display only, feeds the first tab. Never touches scores or alerts.
#      Ported from github.com/hayesfj/the-whole-market (compute.server.ts):
#        * SPX vs equal-weight vs "ex-AI" S&P vs QQQ vs IWM paths
#        * 63-session correlation of each sector ETF with SPX (vs its own history)
#        * Breadth of YOUR stocks (v52: new highs/lows, % above 20/50/200d, A/D line; no S&P list needed)
# =============================================================================

MH_WINDOW = 63
MH_BREADTH_DAYS = 5
MH_BREADTH_YEAR = 252
MH_SPY_HOLDINGS_URL = ("https://www.ssga.com/us/en/intermediary/etfs/library-content/products/"
                       "fund-data/etfs/us/holdings-daily-us-en-spy.xlsx")
MH_IVV_HOLDINGS_URL = ("https://www.ishares.com/us/products/239726/ishares-core-sp-500-etf/1467271812596.ajax"
                       "?fileType=csv&fileName=IVV_holdings&dataType=fund")
MH_WEIGHTS_CACHE = Path(__file__).resolve().with_name("mh_weights_cache.json")   # v50: last good S&P weights
MH_UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122 Safari/537.36"}
MH_AI = ["NVDA", "MSFT", "AMZN", "GOOG", "META", "AVGO", "ORCL", "AMD", "MU", "PLTR"]
# v51: LAST-RESORT rounded approximate S&P weights (fractions), used ONLY for the $SPXXAI line when no live or cached weights exist.
MH_AI_APPROX_W = {"NVDA": 0.075, "MSFT": 0.065, "AMZN": 0.038, "GOOG": 0.040, "META": 0.027,
                  "AVGO": 0.026, "ORCL": 0.009, "AMD": 0.006, "MU": 0.004, "PLTR": 0.006}
MH_SECTORS = [("XLE", "Energy", True), ("XLP", "Staples", True), ("XLU", "Utilities", True),
              ("XLV", "Health Care", True), ("XLF", "Financials", False), ("XLI", "Industrials", False),
              ("XLB", "Materials", False), ("XLRE", "Real Estate", False), ("XLY", "Discretionary", False),
              ("XLC", "Communications", False), ("XLK", "Technology", False)]
MH_INDEX = {"spx": "^GSPC", "ew": "^SPXEW", "qqq": "QQQ", "iwm": "IWM"}


def _mh_close_frame(raw, symbols: list[str]) -> pd.DataFrame:
    """Close prices (columns = symbols) from a yfinance download of several tickers."""
    out = {}
    if raw is None or len(raw) == 0:
        return pd.DataFrame()
    multi = isinstance(raw.columns, pd.MultiIndex)
    for s in symbols:
        try:
            ser = raw[s]["Close"] if multi else raw["Close"]
        except KeyError:
            continue
        ser = pd.to_numeric(ser, errors="coerce").dropna()
        if len(ser):
            out[s] = ser
    df = pd.DataFrame(out)
    df.index = pd.to_datetime(df.index).tz_localize(None).normalize()
    return df[~df.index.duplicated(keep="last")].sort_index()


def _mh_load_weights() -> list[dict]:
    """S&P 500 weights from the SPY holdings file (GOOG/GOOGL merged into one 'Alphabet' row)."""
    import io
    import requests
    r = requests.get(MH_SPY_HOLDINGS_URL, timeout=30,
                     headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122 Safari/537.36"})
    r.raise_for_status()
    tbl = pd.read_excel(io.BytesIO(r.content), header=None)   # needs openpyxl (added to requirements in v50)
    return _mh_weights_from_table(tbl)


def _mh_load_weights_ivv() -> list[dict]:
    """Second source (v50): iShares IVV holdings CSV. Plain CSV, so no Excel library is needed."""
    import io
    import requests
    r = requests.get(MH_IVV_HOLDINGS_URL, timeout=30, headers=MH_UA)
    r.raise_for_status()
    lines = r.content.decode("utf-8-sig", errors="replace").splitlines()
    at = next((i for i, ln in enumerate(lines[:40]) if ln.startswith("Ticker,")), None)
    if at is None:
        raise RuntimeError("IVV holdings file had no Ticker header")
    tbl = pd.read_csv(io.StringIO("\n".join(lines[at:])), thousands=",")
    tbl = tbl[tbl.get("Asset Class", "Equity") == "Equity"] if "Asset Class" in tbl.columns else tbl
    tbl = tbl.rename(columns={"Weight (%)": "Weight"})
    tbl["Ticker"] = tbl["Ticker"].astype(str).str.strip().replace({"BRKB": "BRK-B", "BFB": "BF-B"})   # iShares drops the dash
    return _mh_weights_from_table(pd.concat([pd.DataFrame([tbl.columns.tolist()]), pd.DataFrame(tbl.values)], ignore_index=True))


def _mh_weights_from_table(tbl: "pd.DataFrame") -> list[dict]:
    hdr = next((i for i in range(min(len(tbl), 40))
                if {"Ticker", "Weight"} <= set(str(x).strip() for x in tbl.iloc[i].tolist())), None)
    if hdr is None:
        raise RuntimeError("SPY holdings file had no Ticker/Weight header")
    tbl.columns = [str(x).strip() for x in tbl.iloc[hdr].tolist()]
    tbl = tbl.iloc[hdr + 1:]
    by: dict[str, dict] = {}
    for _, row in tbl.iterrows():
        tk = str(row.get("Ticker", "")).strip().upper()
        w = pd.to_numeric(row.get("Weight"), errors="coerce")
        if not tk or not tk.replace(".", "").replace("-", "").isalnum() or tk[0].isdigit() or not np.isfinite(w) or w <= 0:
            continue
        tk = tk.replace(".", "-")
        nm = str(row.get("Name", tk)).strip() or tk
        cur = by.get(tk)
        by[tk] = {"ticker": tk, "name": cur["name"] if cur else nm, "cap": (cur["cap"] if cur else 0.0) + float(w)}
    rows = list(by.values())
    g, gl = by.get("GOOG"), by.get("GOOGL")
    rows = [x for x in rows if x["ticker"] not in ("GOOG", "GOOGL")]
    if g and gl:
        hi, lo = max(g["cap"], gl["cap"]), min(g["cap"], gl["cap"])
        rows.append({"ticker": "GOOG", "name": "Alphabet", "cap": hi if lo > 0 and hi / lo < 1.05 else g["cap"] + gl["cap"]})
    elif g or gl:
        x = dict(g or gl); x["ticker"], x["name"] = "GOOG", "Alphabet"; rows.append(x)
    if len(rows) < 450:
        raise RuntimeError("S&P constituent table came back short")
    tot = sum(x["cap"] for x in rows)
    return [{"ticker": x["ticker"], "name": x["name"], "weight": x["cap"] / tot} for x in rows]


def _mh_clean_closes(closes: pd.DataFrame) -> pd.DataFrame:
    """v52: drop trailing sessions that most stocks do not have yet (a half-loaded last day would skew every
    percentage) and any all-empty columns."""
    if closes is None or closes.empty:
        return pd.DataFrame()
    c = closes.sort_index().dropna(axis=1, how="all")
    cover = c.notna().sum(axis=1) / max(1, c.shape[1])
    while len(c) > 1 and cover.iloc[-1] < 0.5:
        c, cover = c.iloc[:-1], cover.iloc[:-1]
    return c


def _mh_breadth(closes: pd.DataFrame, min_names: int = 50) -> dict:
    empty = {"ok": False, "universe": None, "new_highs": None, "new_lows": None,
             "above20": None, "above50": None, "above200": None}
    closes = _mh_clean_closes(closes)
    if closes is None or closes.empty:
        return {**empty, "error": "no stock prices were available"}
    uni = hi_n = lo_n = a20 = a50 = a200 = 0
    for tk in closes.columns:
        s = closes[tk].dropna().to_numpy(dtype=float)
        n = len(s)
        if n < MH_BREADTH_YEAR + MH_BREADTH_DAYS:
            continue
        uni += 1
        last = s[-1]
        a20 += last > s[-20:].mean()
        a50 += last > s[-50:].mean()
        a200 += last > s[-200:].mean()
        for i in range(n - MH_BREADTH_DAYS, n):
            prior = s[i - MH_BREADTH_YEAR:i]
            hi_n += s[i] >= prior.max()
            lo_n += s[i] <= prior.min()
    if uni < min_names:
        return {**empty, "error": f"only {uni} stocks had a year of history (need {min_names}+)"}
    out = {"ok": True, "universe": int(uni), "new_highs": int(hi_n), "new_lows": int(lo_n),
           "above20": int(a20), "above50": int(a50), "above200": int(a200)}
    try:
        out["history"] = _mh_breadth_history(closes)
    except Exception as e:                      # history is a bonus: the tiles must survive its failure
        log_warn(f"Market Health: breadth history skipped ({type(e).__name__}: {e})")
    return out


def _mh_breadth_history(closes: pd.DataFrame, days: int = 252) -> dict:
    """v51: daily breadth for the last `days` sessions from the same constituent closes.
    ad = running total of (advancers - decliners); p20/p50/p200 = % of stocks closing above that average."""
    c = closes.sort_index()
    c = c.loc[:, c.notna().sum() >= MH_BREADTH_YEAR + MH_BREADTH_DAYS]
    chg = c.diff()
    adv, dec = (chg > 0).sum(axis=1), (chg < 0).sum(axis=1)
    ad = (adv - dec).cumsum()
    def pct_above(n: int) -> pd.Series:
        ma = c.rolling(n).mean()
        ok = ma.notna() & c.notna()
        return ((c > ma) & ok).sum(axis=1) / ok.sum(axis=1).replace(0, np.nan) * 100.0
    p20, p50, p200 = pct_above(20), pct_above(50), pct_above(200)
    keep = c.index[-(days + 1):]
    def lst(sr, nd=1):
        return [None if not np.isfinite(v) else round(float(v), nd) for v in sr.reindex(keep).to_numpy(dtype=float)]
    return {"d": [d.strftime("%Y-%m-%d") for d in keep], "ad": [int(v) for v in ad.reindex(keep)],
            "p20": lst(p20), "p50": lst(p50), "p200": lst(p200),
            "adv": int(adv.iloc[-1]), "dec": int(dec.iloc[-1])}


def _mh_roll_corr(a: pd.Series, b: pd.Series) -> dict | None:
    """63-session correlation of daily log returns: latest, own-history average / stdev / z."""
    both = pd.concat([a, b], axis=1, join="inner").dropna()
    both = both[(both > 0).all(axis=1)]
    if len(both) < MH_WINDOW + 40:
        return None
    r = np.log(both).diff().dropna()
    roll = r.iloc[:, 0].rolling(MH_WINDOW).corr(r.iloc[:, 1]).dropna()
    if len(roll) < 40:
        return None
    latest, avg, sd = float(roll.iloc[-1]), float(roll.mean()), float(roll.std(ddof=1))
    z = (latest - avg) / sd if sd > 1e-8 else 0.0
    return {"latest": round(latest, 4), "average": round(avg, 4), "z": round(z, 3)}


def _mh_assemble(px: pd.DataFrame, weights: list[dict] | None, breadth: dict, note: str) -> dict:
    """Pure computation from prices + weights -> payload dict (shared by live and demo)."""
    for need in ("spx", "ew", "qqq", "iwm"):
        if MH_INDEX[need] not in px.columns:
            raise RuntimeError(f"missing {MH_INDEX[need]}")
    spx = px[MH_INDEX["spx"]].dropna()
    as_of = spx.index[-1].strftime("%Y-%m-%d")
    span_y = (spx.index[-1] - spx.index[0]).days / 365.25
    out: dict = {"ok": True, "as_of": as_of, "note": note,
                 "history_label": "10-year" if span_y >= 9 else f"{max(1, round(span_y))}-year",
                 "breadth": breadth, "window": MH_WINDOW}

    # ---- sectors vs SPX
    sectors = []
    for sym, name, called in MH_SECTORS:
        if sym not in px.columns:
            continue
        c = _mh_roll_corr(spx, px[sym])
        if c:
            sectors.append({"symbol": sym, "name": name, "called": called, **c})
    out["sectors"] = sectors

    # ---- paths (rebased to 100) with the ex-AI index when weights are known
    held = []
    if weights:
        wmap = {w["ticker"]: w for w in weights}
        held = [wmap[t] for t in MH_AI if t in wmap and t in px.columns]
    use_ai = len(held) >= 6
    cols = [MH_INDEX[k] for k in ("spx", "ew", "qqq", "iwm")] + ([h["ticker"] for h in held] if use_ai else [])
    al = px[cols].dropna()
    if len(al) < MH_WINDOW + 10:
        raise RuntimeError("not enough overlapping history for the paths")
    ret = al.pct_change().iloc[1:]
    rs, re_, rq, ri = (ret[MH_INDEX[k]] for k in ("spx", "ew", "qqq", "iwm"))
    lv = lambda r: 100.0 * (1 + r).cumprod()
    paths = {"t": [al.index[0].strftime("%Y-%m-%d")] + [d.strftime("%Y-%m-%d") for d in ret.index]}
    def with_base(s): return [100.0] + [round(float(v), 4) for v in lv(s)]
    paths["spx"], paths["ew"], paths["qqq"], paths["iwm"] = with_base(rs), with_base(re_), with_base(rq), with_base(ri)
    ex = {"available": use_ai}
    if use_ai:
        w_sum = sum(h["weight"] for h in held)
        wts = np.array([h["weight"] for h in held])
        ai_ret = ret[[h["ticker"] for h in held]].to_numpy() @ wts
        r_ex = ((rs.to_numpy() - ai_ret) / (1 - w_sum)).clip(-0.5, 0.5)
        paths["exai"] = [100.0] + [round(float(v), 4) for v in 100.0 * np.cumprod(1 + r_ex)]
        tail = min(MH_WINDOW, len(al) - 1)
        a0, a1 = al.iloc[-1 - tail], al.iloc[-1]
        ai_63 = float((wts * (a1[[h["ticker"] for h in held]].to_numpy() / a0[[h["ticker"] for h in held]].to_numpy() - 1)).sum())
        spx_63 = float(a1[MH_INDEX["spx"]] / a0[MH_INDEX["spx"]] - 1)
        ai_names_ret = float(np.average(a1[[h["ticker"] for h in held]].to_numpy() / a0[[h["ticker"] for h in held]].to_numpy() - 1, weights=wts))
        ex.update({"weight": round(w_sum, 4), "contribution63": round(ai_63, 4), "spx63": round(spx_63, 4),
                   "ai63": round(ai_names_ret, 4), "rest63": round((spx_63 - ai_63) / (1 - w_sum), 4),
                   "names": [{"ticker": h["ticker"], "name": h["name"], "weight": round(h["weight"], 4)} for h in held]})
    keep = 420
    out["paths"] = {k: v[-keep:] for k, v in paths.items()}
    out["ex_ai"] = ex
    return out


def build_market_health(cfg: Config, demo: bool = False, closes: "pd.DataFrame | None" = None) -> dict:
    """Never raises: on any failure returns {'ok': False, 'error': ...} and the tab shows a message.
    v52: `closes` = daily closes of the watchlist STOCKS (from the main download); breadth is built from them."""
    t0 = time.perf_counter()
    try:
        if demo:
            return _mh_demo(closes, cfg.breadth_min_names)
        syms = list(MH_INDEX.values()) + [s for s, _, _ in MH_SECTORS] + MH_AI
        log("Market Health: downloading index, sector and AI-stock history …")
        raw = _yf_download(syms, "11y", cfg)
        px = _mh_close_frame(raw, syms)
        weights, wnote, fails = None, "", []
        for label, loader in (("State Street SPY", _mh_load_weights), ("iShares IVV", _mh_load_weights_ivv)):
            try:
                weights = loader()
                try:
                    MH_WEIGHTS_CACHE.write_text(json.dumps({"saved": datetime.now().strftime("%Y-%m-%d"), "source": label,
                                                            "weights": weights}), encoding="utf-8")
                except Exception as e:
                    log_warn(f"Market Health: could not write weights cache ({e})")
                break
            except Exception as e:
                fails.append(f"{label}: {type(e).__name__}: {e}")
        if weights is None:
            try:
                c = json.loads(MH_WEIGHTS_CACHE.read_text(encoding="utf-8"))
                weights = c["weights"]
                wnote = f"Live S&P weights unavailable this run; using the last good copy from {c.get('saved', '?')} ({c.get('source', '?')}). " + " | ".join(fails)
            except Exception:
                weights = [{"ticker": t, "name": t, "weight": w} for t, w in MH_AI_APPROX_W.items()]
                wnote = ("Live S&P weights unavailable and no cached copy exists, so $SPXXAI uses rounded APPROXIMATE weights "
                         "for the AI names. " + " | ".join(fails))
        elif fails:
            wnote = "Note: " + " | ".join(fails) + " (fell back to the next source)."
        if wnote:
            log_warn("Market Health: " + wnote)
        try:
            breadth = _mh_breadth(closes, cfg.breadth_min_names)
        except Exception as e:
            breadth = {"ok": False, "error": f"{type(e).__name__}: {e}"}
            log_warn(f"Market Health: breadth skipped ({e})")
        if breadth.get("ok"):
            log_ok(f"Market Health: breadth from {breadth['universe']} stocks")
        elif breadth.get("error"):
            log_warn(f"Market Health: breadth not shown ({breadth['error']})")
        res = _mh_assemble(px, weights, breadth, wnote)
        log_ok(f"Market Health: ready ({time.perf_counter() - t0:.0f} s)")
        return res
    except Exception as e:
        log_warn(f"Market Health tab skipped ({e})")
        return {"ok": False, "error": str(e)}


def _mh_demo(closes: "pd.DataFrame | None" = None, min_names: int = 50) -> dict:
    """Synthetic, offline data so --demo and the self-test can exercise the whole tab."""
    rng = np.random.default_rng(11)
    idx = pd.bdate_range(end=pd.Timestamp.today().normalize(), periods=2600)
    common = rng.normal(0.0004, 0.009, len(idx))
    def mk(beta, vol, drift=0.0):
        return 100 * np.cumprod(1 + beta * common + rng.normal(drift, vol, len(idx)))
    cols = {"^GSPC": mk(1.0, 0.002), "^SPXEW": mk(0.95, 0.004), "QQQ": mk(1.2, 0.005), "IWM": mk(1.0, 0.008)}
    for s, _, _ in MH_SECTORS:
        cols[s] = mk(rng.uniform(0.4, 1.1), 0.006)
    ai = {}
    for t in MH_AI:
        cols[t] = mk(1.4, 0.012, 0.0004)
    px = pd.DataFrame(cols, index=idx)
    ws = [0.075, 0.07, 0.04, 0.035, 0.028, 0.026, 0.012, 0.006, 0.004, 0.006]
    weights = [{"ticker": t, "name": t + " Corp", "weight": w} for t, w in zip(MH_AI, ws)]
    rest = (1 - sum(ws)) / 480
    weights += [{"ticker": f"DEMO{i}", "name": f"Demo Co {i}", "weight": rest} for i in range(480)]
    cl = pd.DataFrame({f"DEMO{i}": mk(rng.uniform(0.5, 1.3), 0.008) for i in range(480)}, index=idx)
    use = closes if closes is not None and not closes.empty else cl      # v52: the demo's own synthetic stocks
    br = _mh_breadth(use, min_names)
    return _mh_assemble(px, weights, br, "SYNTHETIC demo data")


# =============================================================================
#  6. DASHBOARD TEMPLATE (inline SVG, no external resources)
# =============================================================================

DASHBOARD_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Watchlist Momentum __VERSION__</title>
<style>
  :root{
    --bg:#0d1117; --card:#161b22; --card2:#1c2128; --border:#30363d; --text:#e6edf3; --muted:#8b949e;
    --good:#3fb950; --good-bg:rgba(63,185,80,.14); --bad:#f85149; --bad-bg:rgba(248,81,73,.14);
    --warn:#d29922; --warn-bg:rgba(210,153,34,.16); --accent:#58a6ff; --accent-bg:rgba(88,166,255,.14);
    --mild:#c9a75c; --hdr-h:64px;
  }
  *{box-sizing:border-box}
  html{scroll-behavior:smooth}
  body{margin:0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;background:var(--bg);color:var(--text);line-height:1.45;font-size:14px}
  a{color:var(--accent)}
  header{height:var(--hdr-h);display:flex;align-items:center;gap:1rem;padding:0 1.25rem;border-bottom:1px solid var(--border);background:var(--card);position:sticky;top:0;z-index:30}
  header h1{margin:0;font-size:1.15rem;white-space:nowrap}
  header .ttl{display:flex;flex-direction:column;gap:.1rem;flex:0 0 auto}
  header .disc{color:var(--muted);font-size:.68rem;white-space:nowrap;line-height:1.1}
  header h1 small{color:var(--muted);font-weight:400;font-size:.8rem;margin-left:.4rem}
  header .meta{color:var(--muted);font-size:.78rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
  header .grow{flex:1}
  .jump{display:flex;gap:.4rem;align-items:center}
  .jump input{background:var(--bg);border:1px solid var(--border);color:var(--text);padding:.4rem .6rem;border-radius:6px;width:9rem;text-transform:uppercase;font-size:.9rem}
  .badge{display:inline-block;padding:.1rem .45rem;border-radius:999px;font-size:.7rem;font-weight:700;letter-spacing:.02em;border:1px solid transparent}
  .badge.BUY{background:var(--good-bg);color:var(--good);border-color:rgba(63,185,80,.4)}
  .badge.SELL{background:var(--bad-bg);color:var(--bad);border-color:rgba(248,81,73,.4)}
  .badge.EXIT{background:var(--warn-bg);color:var(--warn);border-color:rgba(210,153,34,.4)}
  .badge.HOLD{background:#21262d;color:var(--muted);border-color:var(--border)}
  .badge.WATCH{background:var(--accent-bg);color:var(--accent);border-color:rgba(88,166,255,.4)}
  .badge.WATCHF{background:var(--good-bg);color:var(--good);border:1px dashed rgba(63,185,80,.6)}
  .badge.WATCHU{background:var(--bad-bg);color:var(--bad);border:1px dashed rgba(248,81,73,.6)}
  .badge.INTRADAY{background:var(--warn-bg);color:var(--warn)}
  .badge.LIVE{background:var(--good-bg);color:var(--good);border-color:rgba(63,185,80,.4)}
  nav{display:flex;gap:.35rem;padding:.6rem 1.25rem;flex-wrap:wrap;border-bottom:1px solid var(--border);background:var(--bg);position:sticky;top:var(--hdr-h);z-index:29}
  nav button{background:var(--card);border:1px solid var(--border);color:var(--text);padding:.4rem .8rem;border-radius:6px;cursor:pointer;font-size:.85rem}
  nav button.active{background:#1f6feb;border-color:#1f6feb;color:#fff}
  nav button:hover:not(.active){border-color:var(--accent)}
  nav button .n{color:var(--muted);font-size:.75rem;margin-left:.3rem}
  nav button.active .n{color:#cfe3ff}
  main{padding:1rem 1.25rem 4rem}
  section{display:none}
  section.active{display:block}
  h2{font-size:1.05rem;margin:0 0 .75rem}
  h3{font-size:.9rem;margin:0 0 .5rem;color:var(--muted);font-weight:600;text-transform:uppercase;letter-spacing:.04em}
  .card{background:var(--card);border:1px solid var(--border);border-radius:8px;padding:.9rem;margin-bottom:1rem}
  .note{color:var(--muted);font-size:.78rem;margin:.5rem 0 0}
  .grid{display:grid;gap:1rem}
  .g2{grid-template-columns:1fr 1fr}.g3{grid-template-columns:1fr 1fr 1fr}
  @media(max-width:1000px){.g2,.g3{grid-template-columns:1fr}}
  .kpis{display:grid;grid-template-columns:repeat(8,1fr);gap:.6rem;margin-bottom:1rem}
  @media(max-width:1100px){.kpis{grid-template-columns:repeat(4,1fr)}}
  .kpis.fund{grid-template-columns:1fr 1fr 2.6fr 1fr 1fr 1fr 1fr;margin-bottom:.35rem}
  .kpis.fund .pair{display:flex;gap:1.5rem;align-items:baseline}
  .kpis.fund .pair small{font-size:.72rem;font-weight:400;color:var(--muted);margin-left:.3rem}
  .fund-note{margin:0 0 1rem}
  @media(max-width:1100px){.kpis.fund{grid-template-columns:repeat(4,1fr)}.kpis.fund .wide{grid-column:span 2}}
  .kpi{background:var(--card);border:1px solid var(--border);border-radius:8px;padding:.6rem .75rem;cursor:pointer}
  .kpi:hover{border-color:var(--accent)}
  .kpi .v{font-size:1.45rem;font-weight:700;line-height:1.1}
  .kpi .l{font-size:.68rem;color:var(--muted);text-transform:uppercase;letter-spacing:.04em;margin-top:.15rem}
  .kpi .d{font-size:.72rem;color:var(--muted)}
  .good{color:var(--good)}.bad{color:var(--bad)}.warn{color:var(--warn)}.mild{color:var(--mild)}.muted{color:var(--muted)}.accent{color:var(--accent)}
  .ctx{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:.75rem;margin-bottom:1rem}
  .ctx .card{margin:0;display:grid;grid-template-columns:1fr auto;gap:.5rem;align-items:center}
  .ctx .t{font-size:1.1rem;font-weight:700}
  .ctx .sub{font-size:.78rem;color:var(--muted)}
  .chips{display:flex;flex-wrap:wrap;gap:.3rem;margin-top:.35rem}
  .chip{font-size:.68rem;padding:.12rem .4rem;border-radius:4px;background:#21262d;border:1px solid var(--border);color:var(--muted)}
  .chip.on{background:var(--good-bg);color:var(--good);border-color:rgba(63,185,80,.4)}
  .chip.off{background:var(--bad-bg);color:var(--bad);border-color:rgba(248,81,73,.4)}
  .chip.warn{background:var(--warn-bg);color:var(--warn);border-color:rgba(210,153,34,.4)}
  .board{display:grid;grid-template-columns:1fr 1fr .8fr;gap:1rem;margin-bottom:1rem}
  @media(max-width:1000px){.board{grid-template-columns:1fr}}
  .col{background:var(--card);border:1px solid var(--border);border-radius:8px;padding:.75rem}
  .col h3{display:flex;justify-content:space-between}
  .stack{display:flex;flex-direction:column;gap:.5rem}
  .acard{border:1px solid var(--border);border-radius:8px;padding:.55rem .65rem;cursor:pointer;background:var(--bg)}
  .acard:hover{border-color:var(--accent)}
  .acard.buy{border-left:3px solid var(--good)}.acard.sell{border-left:3px solid var(--bad)}.acard.exit{border-left:3px solid var(--warn)}.acard.watch{border-left:3px solid var(--accent)}
  .acard .top{display:flex;justify-content:space-between;align-items:baseline;gap:.5rem}
  .acard .tk{font-size:1.05rem;font-weight:700}
  .acard .top .th{flex:1;min-width:0;display:flex;flex-direction:column;line-height:1.15}
  .acard .th .t1{font-size:.85rem;color:var(--accent);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
  .acard .th .t2{font-size:.78rem;color:var(--text);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
  .acard .th .t3{font-size:.72rem;color:var(--muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
  .heat{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:.5rem;margin-bottom:1rem}
  .tile{border:1px solid var(--border);border-radius:8px;padding:.5rem .65rem;cursor:pointer;display:flex;flex-direction:column;justify-content:space-between}
  .tile:hover{border-color:var(--accent)}
  .tile .nm{font-size:.82rem;font-weight:600;line-height:1.15}
  .tile .sc{font-size:1.35rem;font-weight:700}
  .tile.small{opacity:.45}
  .crumbs{display:flex;gap:.4rem;align-items:center;flex-wrap:wrap;margin-bottom:.75rem;font-size:.9rem}
  .crumbs button{background:#21262d;border:1px solid var(--border);color:var(--accent);border-radius:6px;padding:.2rem .6rem;cursor:pointer;font-size:.85rem}
  .crumbs .cur{font-weight:700}
  .tsg-badge{display:inline-block;font-size:.7rem;font-weight:600;padding:.08rem .45rem;border:1px solid;border-radius:999px;white-space:nowrap}
  .tsg-stars{color:#d29922;letter-spacing:.05em;white-space:nowrap}
  .tsg-stars .muted{opacity:.35}
  .tsg-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(190px,1fr));gap:.5rem;margin-bottom:1rem}
  .tsg-tile{border:1px solid var(--border);border-radius:8px;padding:.5rem .65rem;cursor:pointer;display:flex;flex-direction:column;gap:.3rem;min-height:84px}
  .tsg-tile:hover{border-color:var(--accent)}
  .tsg-tile .nm{font-size:.82rem;font-weight:600;line-height:1.15}
  .tsg-tile .ft{display:flex;justify-content:space-between;align-items:center;gap:.4rem;margin-top:auto;font-size:.72rem;color:var(--muted)}
  .tsg-pills{display:flex;flex-wrap:wrap;gap:.25rem}
  .tsg-pill{font-size:.68rem;font-weight:700;padding:.05rem .35rem;border-radius:4px;border:1px solid}
  .tsg-bar{display:inline-block;width:56px;height:6px;background:#21262d;border-radius:3px;vertical-align:middle;margin-left:.35rem;overflow:hidden}
  .tsg-bar i{display:block;height:100%}
  .acard .sc{font-size:1.25rem;font-weight:700}
  .acard .sub{font-size:.72rem;color:var(--muted)}
  .acard .row{display:flex;align-items:center;gap:.5rem;margin-top:.35rem}
  .cbar{display:flex;height:8px;border-radius:4px;overflow:hidden;background:#21262d;flex:1}
  .cbar span{height:100%;display:block}
  .cbar .p{background:var(--accent)}.cbar .r{background:#bc8cff}.cbar .e{background:#39c5cf}.cbar .s{background:#d2a8ff}
  .legend{font-size:.68rem;color:var(--muted);display:flex;gap:.7rem;flex-wrap:wrap;margin-top:.3rem}
  .legend i{display:inline-block;width:8px;height:8px;border-radius:2px;margin-right:.25rem;vertical-align:middle}
  .empty{color:var(--muted);font-size:.85rem;padding:.4rem 0}
  .toolbar{display:flex;gap:.4rem;flex-wrap:wrap;align-items:center;margin-bottom:.6rem}
  .toolbar button{background:#21262d;border:1px solid var(--border);color:var(--muted);padding:.3rem .7rem;border-radius:999px;cursor:pointer;font-size:.78rem}
  .toolbar button.on{background:#1f6feb;border-color:#1f6feb;color:#fff}
  .toolbar input{background:var(--bg);border:1px solid var(--border);color:var(--text);padding:.35rem .6rem;border-radius:6px;font-size:.85rem;width:11rem;margin-left:auto}
  .toolbar .cnt{color:var(--muted);font-size:.78rem}
  .twrap{max-height:calc(100vh - 230px);overflow:auto;border:1px solid var(--border);border-radius:8px;background:var(--card)}
  table{width:100%;border-collapse:separate;border-spacing:0;font-size:.82rem}
  th,td{padding:.4rem .55rem;text-align:right;border-bottom:1px solid var(--border);white-space:nowrap}
  th{position:sticky;top:0;background:var(--card2);color:var(--muted);font-weight:600;cursor:pointer;user-select:none;z-index:2}
  th.left,td.left{text-align:left}
  th:hover{color:var(--text)}
  th .arr{font-size:.65rem;margin-left:.2rem;color:var(--accent)}
  tbody tr{cursor:pointer}
  tbody tr:hover td{background:#1c2128}
  tr.BUY td:first-child{box-shadow:inset 3px 0 0 var(--good)}
  tr.SELL td:first-child{box-shadow:inset 3px 0 0 var(--bad)}
  tr.EXIT td:first-child{box-shadow:inset 3px 0 0 var(--warn)}
  td.g{color:var(--good);font-weight:600}td.b{color:var(--bad);font-weight:600}td.w{color:var(--warn)}td.m{color:var(--mild)}td.mu{color:var(--muted)}
  td.bg-g{background:var(--good-bg)}td.bg-b{background:var(--bad-bg)}td.bg-w{background:var(--warn-bg)}
  td b{font-weight:700}
  .flag{font-size:.65rem;color:var(--warn);margin-left:.3rem}
  .sqz{display:flex;gap:.25rem;align-items:center;justify-content:flex-end}
  .sqz b{margin-right:.2rem}
  .thc{font-size:.82rem;color:var(--accent)}
  .cn{font-size:.78rem;color:var(--muted);font-weight:400;margin-left:.4rem;max-width:14rem;display:inline-block;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;vertical-align:bottom}
  .tkw{display:flex;align-items:baseline;gap:.15rem;min-width:0;flex:0 1 auto}
  .acard .cn{max-width:7.5rem;margin-left:.25rem}
  .dhead .cn{font-size:1.1rem;max-width:none;white-space:normal}
  .cn.full,.acard .cn.full{max-width:none;overflow:visible;text-overflow:clip;white-space:normal}
  td .cn.full{white-space:nowrap}
  /* Signals table: compact Ticker / Theme / Signal so the remaining columns sit closer to the left */
  #sig-table table{width:max-content;min-width:0}
  #sig-table td:nth-child(1) .cn{max-width:9rem}
  #sig-table td:nth-child(2) .thc{display:inline-block;max-width:10rem;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;vertical-align:bottom}
  #sig-table th:nth-child(3),#sig-table td:nth-child(3){text-align:center;padding-left:.4rem;padding-right:.4rem}
  svg text{font-family:inherit}
  .chart-title{font-size:.8rem;color:var(--muted);margin-bottom:.3rem;display:flex;justify-content:space-between}
  .tip{position:fixed;pointer-events:none;background:#000c;color:#fff;font-size:.75rem;padding:.3rem .5rem;border-radius:4px;z-index:60;display:none;white-space:nowrap;border:1px solid var(--border)}
  /* drawer */
  #overlay{position:fixed;inset:0;background:#0008;z-index:40;display:none}
  #drawer{position:fixed;top:0;right:0;height:100vh;width:min(720px,100vw);background:var(--card);border-left:1px solid var(--border);z-index:50;transform:translateX(100%);transition:transform .2s ease;overflow:auto;padding:1rem 1.25rem 3rem}
  #drawer.open{transform:none}
  #overlay.open{display:block}
  .dhead{display:flex;align-items:baseline;gap:.75rem;flex-wrap:wrap;margin-bottom:.5rem}
  .dhead .tk{font-size:1.6rem;font-weight:800}
  .dhead .px{font-size:1.1rem}
  .dhead .x{margin-left:auto;background:none;border:1px solid var(--border);color:var(--text);border-radius:6px;padding:.25rem .6rem;cursor:pointer}
  .dnav{display:flex;gap:.4rem;margin-bottom:.75rem}
  .dnav button{background:#21262d;border:1px solid var(--border);color:var(--text);border-radius:6px;padding:.2rem .6rem;cursor:pointer;font-size:.8rem}
  .kv{display:grid;grid-template-columns:1fr auto;gap:.2rem 1rem;font-size:.85rem}
  .kv span:nth-child(odd){color:var(--muted)}
  .comp{display:grid;grid-template-columns:7rem 1fr 2.5rem;gap:.35rem .5rem;align-items:center;font-size:.8rem}
  .comp .bar{height:8px;background:#21262d;border-radius:4px;overflow:hidden}
  .comp .bar i{display:block;height:100%}
  .mini{display:grid;grid-template-columns:1fr 1fr;gap:.75rem}
  @media(max-width:600px){.mini{grid-template-columns:1fr}}
  .rot-wrap{position:relative}
  .rot-wrap svg{width:100%;height:auto;display:block}
  .pt{cursor:pointer}
  .pt:hover circle{stroke:#fff;stroke-width:2}
  .chg{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:.5rem}
  .chg .acard .sub{margin-top:.2rem}
  .delta{font-size:.75rem}
  ul.plain{margin:.25rem 0;padding-left:1.1rem}
  .warnbox{border-left:3px solid var(--warn);padding:.5rem .75rem;background:var(--warn-bg);border-radius:4px;margin-bottom:.75rem;font-size:.85rem}
  .okbox{border-left:3px solid var(--good);padding:.5rem .75rem;background:var(--good-bg);border-radius:4px;margin-bottom:.75rem;font-size:.85rem}
  kbd{background:#21262d;border:1px solid var(--border);border-radius:3px;padding:0 .3rem;font-size:.75rem}
  footer{color:var(--muted);font-size:.75rem;padding:1rem 1.25rem;border-top:1px solid var(--border)}
  @media print{header,nav,#drawer,#overlay{display:none!important}section{display:block!important}.twrap{max-height:none}}
</style>
</head>
<body>
<header>
  <div class="ttl"><h1>Watchlist Momentum <small>__VERSION__</small></h1>
    <div class="disc">For information only. Not Investment Advice. &nbsp;·&nbsp; Copyright © Frank Hayes</div></div>
  <div class="meta" id="hdr-meta"></div>
  <div class="grow"></div>
  <div class="jump"><input id="jump" placeholder="ticker  ( / )" autocomplete="off" list="tk-list"/><datalist id="tk-list"></datalist></div>
</header>
<nav id="nav"></nav>
<main>
  <section id="market"></section>
  <section id="changes"></section>
  <section id="ticker"></section>
  <section id="themes"></section>
  <section id="tsig"></section>
  <section id="signals"></section>
  <section id="ppo"></section>
  <section id="sectors"></section>
  <section id="sixpack"></section>
  <section id="etfs"></section>
  <section id="bonds"></section>
  <section id="tear"></section>
  <section id="shortlist"></section>
  <section id="country"></section>
  <section id="currency"></section>
  <section id="rank"></section>
  <section id="sqz"></section>
  <section id="rotation"></section>
  <section id="scorecard"></section>
  <section id="health"></section>
  <section id="guide"></section>
</main>
<footer id="foot"></footer>
<div id="overlay" onclick="closeDrawer()"></div>
<aside id="drawer"></aside>
<div class="tip" id="tip"></div>

__HISTORY_TAG__<script>
const P = __PAYLOAD__;
if (!P.history) {   // history is stored in the sibling .history.js file
  const HB = window.__MOMENTUM_HISTORY__;
  P.history = (HB && HB.data) || {};
  P.hist_state = !(HB && HB.data) ? 'missing' : (HB.run !== P.run_ts ? 'stale' : 'ok');
}
const CFG = P.cfg;
const ROWS = P.rows;
const BY = Object.fromEntries(ROWS.map(r => [r.t, r]));
const TICKERS = ROWS.map(r => r.t).sort();
const C = {good:'#3fb950', bad:'#f85149', warn:'#d29922', accent:'#58a6ff', muted:'#8b949e', grid:'#30363d', text:'#e6edf3'};
const REGIMES = ["Strong","Dormant→Waking","Neutral","Mature/Cooling","Weak"];
const REG_NAME = {S:'Strong',D:'Dormant→Waking',N:'Neutral',M:'Mature/Cooling',W:'Weak'};
const sliceH = (H, n) => { const o = {}; for (const k in H) o[k] = Array.isArray(H[k]) ? H[k].slice(-n) : H[k]; return o; };
const md = d => (d||'').slice(5);
const ord = v => { if (!isNum(v)) return '—'; const n = Math.round(v), m = n % 100; return n + (m >= 11 && m <= 13 ? 'th' : ['th','st','nd','rd'][n % 10] || 'th'); };

// ---------- formatting helpers ----------
const isNum = v => typeof v === 'number' && isFinite(v);
const f = (v, d=1, signed=false) => !isNum(v) ? '—' : (signed && v > 0 ? '+' : '') + v.toFixed(d);
const fi = v => isNum(v) ? String(Math.round(v)) : '—';
const fp = v => isNum(v) ? v.toLocaleString(undefined,{minimumFractionDigits:2,maximumFractionDigits:2}) : '—';
const fdv = v => !isNum(v) ? '—' : v >= 1e9 ? (v/1e9).toFixed(1)+'B' : v >= 1e6 ? (v/1e6).toFixed(1)+'M' : (v/1e3).toFixed(0)+'K';
const esc = s => String(s).replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const OM_NAME = {BUY:'Favorable', SELL:'Unfavorable', EXIT:'Neutral', HOLD:'Neutral'};
const badge = r => `<span class="badge ${r}"${r === 'EXIT' ? ' title="Conflicted: a fresh up-cross and a fresh down-cross are both in the window"' : ''}>${OM_NAME[r] || r}</span>`;
// Signal (v47): a relabelling of rec + watch. Favorable / Watch Favorable / Neutral / Watch Unfavorable / Unfavorable
const omKey = r => r.rec === 'BUY' ? 'Favorable' : r.rec === 'SELL' ? 'Unfavorable' : r.rec === 'EXIT' ? 'Neutral' : r.watch === 'BUY' ? 'Watch Favorable' : r.watch === 'SELL' ? 'Watch Unfavorable' : 'Neutral';
const watchBadge = r => r.watch ? `<span class="badge ${r.watch==='BUY'?'WATCHF':r.watch==='SELL'?'WATCHU':'WATCH'}" title="${wTip(r)}">${omWatchTxt(r).toUpperCase()}</span> ` : '';
const netCls = v => signCls(v)==='g' ? 'good' : signCls(v)==='b' ? 'bad' : 'muted';
const OM_ORDER = {'Favorable':0, 'Watch Favorable':1, 'Neutral':2, 'Watch Unfavorable':3, 'Unfavorable':4};
const omWatchTxt = r => r.watch === 'BUY' ? 'Watch Favorable' : r.watch === 'SELL' ? 'Watch Unfavorable' : 'Watch both sides';
const omOrder = r => (r.rec === 'EXIT' ? 2.5 : OM_ORDER[omKey(r)]);
const omBadge = r => {
  const k = omKey(r);
  if (k === 'Watch Favorable' || k === 'Watch Unfavorable') return `<span class="badge ${k === 'Watch Favorable' ? 'WATCHF' : 'WATCHU'}" title="${wTip(r)}">${k}</span>`;
  const b = badge(r.rec === 'BUY' || r.rec === 'SELL' || r.rec === 'EXIT' ? r.rec : 'HOLD');
  return r.watch === 'BOTH' ? b.replace('<span class="badge HOLD"', '<span class="badge HOLD" title="Both POS and NEG Signals are near their triggers"').replace('>Neutral<', '>Neutral<') : b;
};
const gateList = r => r.gate ? r.gate.split(' + ') : [];
const wTip = r => esc(r.gate ? 'Blocked Favorable: ' + r.gate + ' (see Guide → Gates)' : 'Within ' + CFG.watch_margin + ' points of a trigger');
const isCandidate = r => !!r.gate && r.rec === 'HOLD' && r.sig_x === '↑' && r.e200 >= 0 && gateList(r).every(g => g === 'Relative strength' || g === 'SPY regime');
const confCls = v => v >= 70 ? 'g' : v >= 55 ? 'g' : v >= 40 ? 'm' : 'mu';
const rsiCls = v => !isNum(v) ? '' : v >= 80 ? 'b' : v >= 70 ? 'w' : (v >= 40 && v <= 65) ? 'g' : v <= 30 ? 'm' : '';
const pctCls = v => !isNum(v) ? '' : v >= 70 ? 'g' : v >= 55 ? 'g' : v <= 30 ? 'b' : v <= 45 ? 'm' : '';
const regCls = r => ({Strong:'g','Dormant→Waking':'accent-c',Neutral:'','Mature/Cooling':'m',Weak:'b'}[r] || '');
const regColor = r => ({Strong:C.good,'Dormant→Waking':C.accent,Neutral:C.muted,'Mature/Cooling':C.warn,Weak:C.bad}[r] || C.muted);
const signCls = v => !isNum(v) ? '' : v > 0 ? 'g' : v < 0 ? 'b' : '';
const arrow = v => v === '↑' ? '<span class="good">↑</span>' : v === '↓' ? '<span class="bad">↓</span>' : '<span class="muted">—</span>';
const NAMES = P.names || {};
const coName = t => NAMES[t] || '';
const FULLN = new Set((CFG.etfs || []).concat(CFG.country_etfs || [], CFG.currency || []).map(x => x.t));
const FXCORR = P.fxcorr || {};   // ETF names are never shortened
const cn = t => coName(t) ? `<span class="cn${FULLN.has(t) ? ' full' : ''}" title="${esc(coName(t))}">${esc(coName(t))}</span>` : '';
const tk = t => `<b class="tkl" data-t="${t}">${t}</b>${cn(t)}`;
const flags = r => (r.live ? '<span class="flag" style="color:var(--good)" title="Live intraday price — not yet a confirmed close">●</span>' : '')
                 + (r.data_ok ? '' : '<span class="flag" title="Short history — alerts disabled">◐</span>')
                 + (r.stale ? '<span class="flag" title="Stale: last bar '+r.last_bar+'">⏱</span>' : '')
                 + (r.tradeable ? '' : '<span class="flag" title="Below liquidity/price floor">≋</span>');
const dl = (label, v, cls='') => `<span>${label}</span><span class="${cls}">${v}</span>`;

// ---------- SVG helpers ----------
function sparkline(vals, o={}) {
  const w = o.w || 120, h = o.h || 30, pad = 2;
  const xs = vals.map((v,i)=>i), ys = vals.map(v => isNum(v) ? v : null);
  const ok = ys.filter(v => v !== null);
  if (ok.length < 2) return `<svg width="${w}" height="${h}"></svg>`;
  let lo = o.min ?? Math.min(...ok), hi = o.max ?? Math.max(...ok);
  if (o.ref !== undefined) { lo = Math.min(lo, o.ref); hi = Math.max(hi, o.ref); }
  if (hi === lo) { hi += 1; lo -= 1; }
  const X = i => pad + (w-2*pad) * i / (vals.length-1), Y = v => h - pad - (h-2*pad) * (v-lo)/(hi-lo);
  let d = '', started = false;
  ys.forEach((v,i) => { if (v===null){started=false;return;} d += (started?'L':'M') + X(i).toFixed(1)+','+Y(v).toFixed(1); started=true; });
  const last = ok[ok.length-1], first = ok[0];
  const color = o.color || (last >= (o.ref ?? first) ? C.good : C.bad);
  let ref = '';
  if (o.ref !== undefined) ref = `<line x1="0" x2="${w}" y1="${Y(o.ref)}" y2="${Y(o.ref)}" stroke="${C.grid}" stroke-dasharray="2,2"/>`;
  let fill = '';
  if (o.fill) { const base = Y(o.ref ?? lo); fill = `<path d="${d} L${X(vals.length-1)},${base} L${X(ys.findIndex(v=>v!==null))},${base} Z" fill="${color}" opacity=".12"/>`; }
  return `<svg width="${w}" height="${h}" viewBox="0 0 ${w} ${h}">${ref}${fill}<path d="${d}" fill="none" stroke="${color}" stroke-width="1.5"/><circle cx="${X(vals.length-1)}" cy="${Y(last)}" r="2" fill="${color}"/></svg>`;
}

function rollMedian(a, n, minN) {
  return a.map((_, i) => { const w = a.slice(Math.max(0, i-n+1), i+1).filter(isNum); if (w.length < minN) return null; w.sort((x,y) => x-y); const m = w.length >> 1; return w.length % 2 ? w[m] : (w[m-1] + w[m]) / 2; });
}
function volumeChart(H, lab) {
  // share volume vs its rolling median: bright = high, faded = low, grey = normal; dashed line = median
  const hi = CFG.vol_rel_hi, lo = CFG.vol_rel_lo, nb = CFG.vol_rel_bars;
  const med = rollMedian(H.v, nb, Math.min(nb, 15));
  const ratio = H.v.map((v,i) => isNum(v) && isNum(med[i]) && med[i] > 0 ? v / med[i] : null);
  // up day = close above prior close (green), down day = below (red); flat/first bar keeps the old blue. Only the high and low thresholds are tinted.
  const dirCol = i => { const c = H.c || [], d = isNum(c[i]) && isNum(c[i-1]) ? c[i] - c[i-1] : 0; return d > 0 ? C.good : d < 0 ? C.bad : C.accent; };
  const colors = ratio.map((q,i) => q === null ? null : (q >= hi || q < lo) ? dirCol(i) : '#6e7681');
  const opacities = ratio.map(q => q === null ? .7 : q >= hi ? .95 : q < lo ? .3 : .7);
  const tips = H.v.map((v,i) => `${esc((H.d && H.d[i]) || lab[i] || '')}: ${fdv(v)} sh${ratio[i] === null ? '' : ' · ' + ratio[i].toFixed(2) + '× ' + nb + 'd median'}`);
  const key = (c, o, t) => `<span style="display:inline-flex;align-items:center;gap:.3rem;margin-right:.9rem"><span style="display:inline-block;width:9px;height:9px;background:${c};opacity:${o}"></span>${t}</span>`;
  return lineChart([{v:H.v,color:'#6e7681',bars:true,opacity:.7,colors,opacities,tips}, {v:med,color:C.warn,dash:'3,2',width:1.2}], {w:1300,h:80,min:0,labels:lab})
    + `<div class="muted" style="font-size:.75rem;margin-top:.15rem">Volume (shares) vs ${nb}-day median · ${key(C.good,.95,'≥ '+hi+'× high, up day')}${key(C.bad,.95,'≥ '+hi+'× high, down day')}${key('#6e7681',.7,'normal')}${key(C.good,.3,'< '+lo+'× low, up')}${key(C.bad,.3,'< '+lo+'× low, down')}<span style="color:${C.warn}">- - -</span> median · hover a bar for the ratio</div>`;
}

function lineChart(series, o={}) {
  // series: [{v:[...], color, width, dash, label}], shared x index; o: {w,h,min,max,hlines:[{y,color,label}],labels:[...],title}
  const w = o.w || 320, h = o.h || 120, L = o.w > 600 ? 44 : 34, R = o.w > 600 ? 44 : 34, T = (series.length > 1 && series.some(s => s.label)) ? 22 : 8, B = 18;
  const all = series.flatMap(s => s.v).filter(isNum);
  if (!all.length) return `<svg width="${w}" height="${h}"></svg>`;
  let lo = o.min ?? Math.min(...all), hi = o.max ?? Math.max(...all);
  (o.hlines||[]).forEach(hl => { lo = Math.min(lo, hl.y); hi = Math.max(hi, hl.y); });
  if (hi === lo) { hi += 1; lo -= 1; }
  const n = Math.max(...series.map(s => s.v.length));
  const X = i => L + (w-L-R) * i / Math.max(1,n-1), Y = v => T + (h-T-B) * (1 - (v-lo)/(hi-lo));
  let g = '';
  const ticks = 3;
  const tickFmt = v => Math.abs(hi) >= 1e4 ? fdv(v) : f(v, Math.abs(hi-lo) < 5 ? 2 : 0);
  for (let k=0;k<=ticks;k++){ const v = lo + (hi-lo)*k/ticks; g += `<line x1="${L}" x2="${w-R}" y1="${Y(v)}" y2="${Y(v)}" stroke="${C.grid}" stroke-width="1"/><text x="${L-4}" y="${Y(v)+3}" font-size="9" fill="${C.muted}" text-anchor="end">${tickFmt(v)}</text><text x="${w-R+4}" y="${Y(v)+3}" font-size="9" fill="${C.muted}" text-anchor="start">${tickFmt(v)}</text>`; }
  (o.hlines||[]).forEach(hl => { g += `<line x1="${L}" x2="${w-R}" y1="${Y(hl.y)}" y2="${Y(hl.y)}" stroke="${hl.color||C.muted}" stroke-dasharray="3,3"/>`; if (hl.label) g += `<text x="${w-R}" y="${Y(hl.y)-2}" font-size="9" fill="${hl.color||C.muted}" text-anchor="end">${hl.label}</text>`; });
  let paths = '';
  series.forEach(s => {
    let d = '', st = false;
    s.v.forEach((v,i) => { if (!isNum(v)) { st=false; return; } d += (st?'L':'M') + X(i).toFixed(1)+','+Y(v).toFixed(1); st=true; });
    if (s.bars) { const bw = Math.max(1, (w-L-R)/n*0.7), y0 = Y(Math.max(lo, Math.min(hi, 0))); s.v.forEach((v,i) => { if (!isNum(v)) return; const col = (s.colors && s.colors[i]) || (s.colorBySign ? (v >= 0 ? C.good : C.bad) : s.color); const y = Y(v); const op = (s.opacities && s.opacities[i]) || s.opacity || .85; paths += `<rect x="${(X(i)-bw/2).toFixed(1)}" y="${Math.min(y,y0).toFixed(1)}" width="${bw.toFixed(1)}" height="${Math.max(0.5,Math.abs(y-y0)).toFixed(1)}" fill="${col}" opacity="${op}">${s.tips && s.tips[i] ? `<title>${s.tips[i]}</title>` : ''}</rect>`; }); return; }
    if (s.fillTo !== undefined) { const b = Y(s.fillTo); const fi0 = s.v.findIndex(isNum); paths += `<path d="${d} L${X(s.v.length-1)},${b} L${X(fi0)},${b} Z" fill="${s.color}" opacity=".10"/>`; }
    paths += `<path d="${d}" fill="none" stroke="${s.color}" stroke-width="${s.width||1.8}" ${s.dash?`stroke-dasharray="${s.dash}"`:''}/>`;
  });
  (o.marks||[]).forEach(m => { if (!isNum(m.y)) return; const x = X(m.i), y = Y(m.y); paths += m.shape === 'down'
      ? `<path d="M${x-5},${y-9} L${x+5},${y-9} L${x},${y-2} Z" fill="${m.color}"><title>${m.label||''}</title></path>`
      : `<path d="M${x-5},${y+9} L${x+5},${y+9} L${x},${y+2} Z" fill="${m.color}"><title>${m.label||''}</title></path>`; });
  (o.vbands||[]).forEach(b => { paths = `<rect x="${X(b.from)}" y="${T}" width="${Math.max(1,X(b.to)-X(b.from))}" height="${h-T-B}" fill="${b.color}" opacity=".18"/>` + paths; });
  let xl = '';
  if (o.labels) { const step = Math.ceil(n/(w > 600 ? 12 : 5)); for (let i=0;i<n;i+=step) xl += `<text x="${X(i)}" y="${h-4}" font-size="9" fill="${C.muted}" text-anchor="middle">${o.labels[i]||''}</text>`; }
  let leg = '';
  if (series.length > 1) { const items = series.filter(s => s.label); const step = s => 24 + s.label.length*5.8; let x = w - R - items.reduce((a,s) => a + step(s), 0); items.forEach(s => { leg += `<rect x="${x}" y="5" width="8" height="3" fill="${s.color}"/><text x="${x+11}" y="11" font-size="9" fill="${C.muted}">${s.label}</text>`; x += step(s); }); }
  return `<svg width="${w}" height="${h}" viewBox="0 0 ${w} ${h}" style="width:100%;height:auto" preserveAspectRatio="none">${g}${paths}${xl}${leg}</svg>`;
}

function histogram(vals, o={}) {
  const w = o.w || 360, h = o.h || 150, L = 28, R = 8, T = 10, B = 20;
  const v = vals.filter(isNum);
  if (!v.length) return '<div class="empty">No data</div>';
  const lo = o.min ?? Math.floor(Math.min(...v)), hi = o.max ?? Math.ceil(Math.max(...v)), bins = o.bins || 20;
  const cnt = new Array(bins).fill(0);
  v.forEach(x => { let b = Math.floor((x-lo)/(hi-lo)*bins); b = Math.max(0, Math.min(bins-1, b)); cnt[b]++; });
  const mx = Math.max(...cnt, 1);
  const X = x => L + (w-L-R) * (x-lo)/(hi-lo), Y = c => T + (h-T-B) * (1 - c/mx);
  let g = '';
  (o.bands||[]).forEach(b => g += `<rect x="${X(b.from)}" y="${T}" width="${X(b.to)-X(b.from)}" height="${h-T-B}" fill="${b.color}" opacity=".12"/>`);
  cnt.forEach((c,i) => { const x0 = X(lo + (hi-lo)*i/bins), x1 = X(lo + (hi-lo)*(i+1)/bins); const col = o.colorAt ? o.colorAt(lo + (hi-lo)*(i+.5)/bins) : C.accent; g += `<rect x="${x0+1}" y="${Y(c)}" width="${Math.max(1,x1-x0-2)}" height="${h-B-Y(c)}" fill="${col}" rx="2"><title>${f(lo+(hi-lo)*i/bins,0)}–${f(lo+(hi-lo)*(i+1)/bins,0)}: ${c}</title></rect>`; });
  (o.vlines||[]).forEach(vl => g += `<line x1="${X(vl.x)}" x2="${X(vl.x)}" y1="${T}" y2="${h-B}" stroke="${vl.color}" stroke-dasharray="3,3"/><text x="${X(vl.x)+2}" y="${T+8}" font-size="9" fill="${vl.color}">${vl.label||''}</text>`);
  for (let k=0;k<=4;k++){ const x = lo + (hi-lo)*k/4; g += `<text x="${X(x)}" y="${h-6}" font-size="9" fill="${C.muted}" text-anchor="middle">${f(x,0)}</text>`; }
  g += `<text x="${L-3}" y="${T+8}" font-size="9" fill="${C.muted}" text-anchor="end">${mx}</text>`;
  return `<svg viewBox="0 0 ${w} ${h}" style="width:100%;height:auto">${g}</svg>`;
}

function barChart(items, o={}) {  // items: [{label, v, color}]
  const w = o.w || 360, h = o.h || 150, L = 28, R = 8, T = 10, B = 34;
  const mx = Math.max(...items.map(i => i.v), 1);
  const bw = (w-L-R)/items.length;
  const Y = v => T + (h-T-B) * (1 - v/mx);
  let g = '';
  items.forEach((it,i) => { const x = L + bw*i; g += `<rect class="pt" x="${x+4}" y="${Y(it.v)}" width="${bw-8}" height="${h-B-Y(it.v)}" fill="${it.color}" rx="3" data-k="${esc(it.label)}"><title>${it.label}: ${it.v}</title></rect><text x="${x+bw/2}" y="${Y(it.v)-3}" font-size="10" fill="${C.text}" text-anchor="middle">${it.v}</text><text x="${x+bw/2}" y="${h-B+12}" font-size="9" fill="${C.muted}" text-anchor="middle">${it.label.split('/')[0].replace('Dormant→','Dorm→')}</text>`; });
  return `<svg viewBox="0 0 ${w} ${h}" style="width:100%;height:auto">${g}</svg>`;
}

function compBar(parts) { // [{k, v, max}] -> stacked bar scaled to 100
  return `<div class="cbar">${parts.map(p => `<span class="${p.k}" style="width:${Math.max(0,p.v)}%" title="${p.label}: ${p.v}"></span>`).join('')}</div>`;
}

// ---------- tables ----------
const TABLES = {};
function makeTable(id, cols, rows, opts={}) {
  TABLES[id] = {cols, rows, opts, sortKey: opts.sortKey || null, sortDir: opts.sortDir || -1, filter: 'all', q: ''};
  renderTable(id);
}
function renderTable(id) {
  const T = TABLES[id], host = document.getElementById(id);
  if (!host) return;
  let rows = T.rows.slice();
  if (T.opts.filters && T.filter !== 'all') rows = rows.filter(r => T.opts.filters[T.filter](r));
  if (T.q) { const q = T.q.toUpperCase(); rows = rows.filter(r => (r.t||'').includes(q) || themeName(r.t).toUpperCase().includes(q) || (r.country||'').toUpperCase().includes(q) || coName(r.t).toUpperCase().includes(q) || (r.name||'').toUpperCase().includes(q) || secText(r.t).includes(q) || (r.regime||'').toUpperCase().includes(q) || (r.gate||'').toUpperCase().includes(q) || (r.rec||'').includes(q)); }
  if (T.sortKey) {
    const c = T.cols.find(c => c.key === T.sortKey);
    rows.sort((a,b) => {
      let av = c.sortVal ? c.sortVal(a) : a[c.key], bv = c.sortVal ? c.sortVal(b) : b[c.key];
      const an = av === null || av === undefined || av === '', bn = bv === null || bv === undefined || bv === '';
      if (an && bn) return 0; if (an) return 1; if (bn) return -1;
      const cmp = (typeof av === 'number' && typeof bv === 'number') ? (av-bv) * T.sortDir : String(av).localeCompare(String(bv)) * T.sortDir;
      if (cmp || c.key !== 'rec') return cmp;
      // v48: inside one Signal category the highest Net Bias (signed) comes first, whichever way the header is sorted
      return (isNum(b.bias) ? b.bias : -1e9) - (isNum(a.bias) ? a.bias : -1e9);
    });
  } else if (T.opts.defaultSort) rows.sort(T.opts.defaultSort);
  T.shown = rows;
  const head = T.cols.map(c => `<th class="${c.left?'left':''}" data-k="${c.key}" title="${c.tip||''}">${c.label}${T.sortKey===c.key ? `<span class="arr">${T.sortDir>0?'▲':'▼'}</span>`:''}</th>`).join('');
  const body = rows.map((r,i) => `<tr class="${r.rec||''}" data-t="${r.t||''}" data-i="${i}">${T.cols.map(c => { const v = c.render ? c.render(r,i) : r[c.key]; const cls = (c.cls ? c.cls(r) : '') + (c.left?' left':''); return `<td class="${cls}">${v===null||v===undefined?'—':v}</td>`; }).join('')}</tr>`).join('');
  let tb = '';
  if (T.opts.filters || T.opts.search !== false) {
    tb = `<div class="toolbar" data-table="${id}">` + (T.opts.filters ? Object.keys(T.opts.filters).map(k => `<button class="${T.filter===k?'on':''}" data-f="${k}">${T.opts.filterLabels?.[k] || k}</button>`).join('') + `<button class="${T.filter==='all'?'on':''}" data-f="all">All</button>` : '') +
         `<span class="cnt">${rows.length} rows</span><input placeholder="filter…" value="${esc(T.q)}" data-q="${id}"/></div>`;
  }
  host.innerHTML = tb + `<div class="twrap"><table><thead><tr>${head}</tr></thead><tbody>${body}</tbody></table></div>` + (T.opts.note ? `<p class="note">${T.opts.note}</p>` : '');
  host.querySelectorAll('th').forEach(th => th.onclick = () => { const k = th.dataset.k; if (T.sortKey === k) T.sortDir *= -1; else { T.sortKey = k; T.sortDir = -1; } renderTable(id); });
  host.querySelectorAll('.toolbar button').forEach(b => b.onclick = () => { T.filter = b.dataset.f; renderTable(id); });
  const inp = host.querySelector('.toolbar input');
  if (inp) { inp.oninput = e => { T.q = e.target.value; const pos = e.target.selectionStart; renderTable(id); const n = document.querySelector(`[data-q="${id}"]`); n.focus(); n.setSelectionRange(pos,pos); }; }
  host.querySelectorAll('tbody tr').forEach(tr => tr.onclick = () => { if (T.opts.onRow) T.opts.onRow(T.shown[+tr.dataset.i]); else if (tr.dataset.t) openDrawer(tr.dataset.t); });
}
function setFilter(id, key) { if (TABLES[id]) { TABLES[id].filter = key; renderTable(id); } }

// ---------- sections ----------
const CTX_ORDER = { BUY:0, SELL:1, EXIT:2, HOLD:3 };
const byBias = (a,b) => (CTX_ORDER[a.rec]-CTX_ORDER[b.rec]) || (Math.abs(b.bias)-Math.abs(a.bias)) || (b.mom-a.mom);

const THEMES = P.themes || {};
const GROUPNAME = {}; (CFG.sectors || []).concat(CFG.six_pack || []).forEach(x => GROUPNAME[x.t] = x.name);
(CFG.country_etfs || []).forEach(x => GROUPNAME[x.t] = x.country);
(CFG.currency || []).forEach(x => GROUPNAME[x.t] = x.currency);
const themePair = t => GROUPNAME[t] ? [GROUPNAME[t], ''] : (THEMES[t] || null);
const themeName = t => { const p = themePair(t); return p ? p[0] : ''; };
const SEC2 = P.themes2 || {};
const secPairs = t => SEC2[t] || [];
const pairText = p => p[0] + (p[1] ? ' › ' + p[1] : '');
const pairHtml = p => `<span class="accent">${esc(p[0])}</span>${p[1] ? ' › <span style="color:var(--text)">' + esc(p[1]) + '</span>' : ''}`;
const secText = t => secPairs(t).map(pairText).join(' | ').toUpperCase();
const themeLine = (t, style='') => { const p = themePair(t); if (!p) return ''; let h = `<div class="sub" style="${style}" title="${esc(pairText(p))}">${pairHtml(p)}</div>`; secPairs(t).forEach(sp => { h += `<div class="sub" style="${style}" title="Secondary: ${esc(pairText(sp))}"><span class="muted">also:</span> ${pairHtml(sp)}</div>`; }); return h; };
const themeCell = t => { const p = themePair(t); if (!p) return '<span class="muted">—</span>'; const sec = secPairs(t); const full = pairText(p) + (sec.length ? '\nAlso: ' + sec.map(pairText).join('; ') : ''); return `<span class="thc" title="${esc(full)}">${esc(p[0])}</span>${sec.length ? ' <span class="muted" style="font-size:.7rem">+' + sec.length + '</span>' : ''}`; };
const themeCol = {key:'theme', label:'Theme', left:true, render:r => themeCell(r.t), sortVal:r => themeName(r.t), tip:'Primary theme (sector / Six Pack name for those ETFs)'};
const qsCol = {key:'qs', label:'Quality', render:r => { const q = ((P.fund || {})[r.t] || {}).qs; return (q === undefined || q === null || q === '') ? '<span class="muted">—</span>' : esc(q); }, sortVal:r => { const q = parseFloat(((P.fund || {})[r.t] || {}).qs); return isNaN(q) ? null : q; }, tip:'Quality Score from the Quality Score sheet (display only; — = not in the sheet)'};   // Quality Score next to Signal; dash when the ticker has none
function themeTag(t) {
  const th = themePair(t); if (!th) return '';
  const sec = secPairs(t);
  const full = esc(pairText(th) + (sec.length ? '\nAlso: ' + sec.map(pairText).join('; ') : ''));
  const lines = sec.slice(0,2).map(sp => `<span class="t3">also: ${esc(pairText(sp))}</span>`).join('') + (sec.length > 2 ? `<span class="t3">+${sec.length-2} more</span>` : '');
  return `<span class="th" title="${full}"><span class="t1">${esc(th[0])}</span><span class="t2">${esc(th[1])}</span>${lines}</span>`;
}
// ---------- v54: universe ranking text, trend state, position size (display only) ----------
const UNI = CFG.anchor === 'universe';
const ANCHOR_TXT = UNI ? 'ranked across the universe on each date' + (CFG.vol_adj ? ', volatility-adjusted' : '') : `vs ${CFG.benchmark} history`;
const RS_TIP = 'RS Rating 1-99: blended momentum percentile (60% trailing, 40% emerging), ' + ANCHOR_TXT + '. 90 = stronger than 90% of the list.';
const FLOOR_NOTE = CFG.symmetric ? `A fresh cross that is still in force guarantees a score of at least ${CFG.buy_floor} (POS, bullish) or ${CFG.sell_floor} (NEG, bearish), shown with °.` : `A fresh bearish cross guarantees a NEG Signals score of ${CFG.sell_floor} (°).`;
const stopDown = r => r.in_tr && isNum(r.tr_stop) && isNum(r.close) && r.close > 0 ? (r.tr_stop / r.close - 1) * 100 : null;
const trendCell = r => r.in_tr ? `<span class="${r.tr_ret < 0 ? 'bad' : 'good'}" title="In trend since ${r.tr_date} (entry ${fp(r.tr_entry)})">${fi(r.tr_days)}d ${f(r.tr_ret,1,true)}%</span>` : r.tr_exit ? `<span class="warn" title="The trend closed on this bar: ${r.tr_exit === 'Stop' ? 'close under the trailing stop' : 'Unfavorable / Conflicted alert'}">exit ${f(r.tr_cret,1,true)}%</span>` : '<span class="muted">—</span>';
const stopCell = r => r.in_tr && isNum(r.tr_stop) ? `<span title="Trailing stop: highest (close − ${CFG.stop_mult} × ATR) since entry. It never moves down.">${fp(r.tr_stop)} <span class="muted">${f(stopDown(r),1,true)}%</span></span>` : '<span class="muted">—</span>';
const sizeTxt = r => isNum(r.size) ? `${f(r.size,1)}% of portfolio` : '—';
const TREND_COLS = CFG.trend_on ? [
  {key:'tr_ret', label:'In Trend', render:trendCell, sortVal:r => r.in_tr ? r.tr_ret : null, tip:'Sessions and return since the Favorable alert that started the current trend. The trend stays open until an Unfavorable / Conflicted alert or a close under the trailing stop. Display only: it does not change Signal.'},
  {key:'tr_stop', label:'Stop', render:stopCell, sortVal:r => r.in_tr ? stopDown(r) : null, tip:'Trailing stop for a name that is In Trend, and how far below the close it sits'},
] : [];

function renderChanges() {
  const ch = P.changes;
  const card = (it, cls) => `<div class="acard ${cls}" data-t="${it.ticker}"><div class="top"><span class="tkw"><span class="tk">${it.ticker}</span>${cn(it.ticker)}</span><span>${badge(it.old)} → ${badge(it.new)}</span></div>
    <div class="sub"><b class="${netCls(it.buy - it.sell)}">Net Bias ${f(it.buy - it.sell,0,true)}</b> · POS ${it.buy} <span class="delta ${signCls(it.d_buy)==='g'?'good':signCls(it.d_buy)==='b'?'bad':'muted'}">(${f(it.d_buy,0,true)})</span> · NEG ${it.sell} <span class="delta ${signCls(it.d_sell)==='g'?'bad':signCls(it.d_sell)==='b'?'good':'muted'}">(${f(it.d_sell,0,true)})</span> · ${it.regime} · ${fp(it.close)}</div></div>`;
  const sec = (title, items, cls) => `<div class="card"><h3>${title} <span class="muted">(${items.length})</span></h3>${items.length ? `<div class="chg">${items.map(i => card(i, cls)).join('')}</div>` : '<div class="empty">None</div>'}</div>`;
  let html = `<p class="note" style="margin:0 0 .75rem">Compared against <b>${esc(ch.source)}</b>${ch.prior_date?` (${ch.prior_date})`:''}. Each ticker is compared with its own bar from the prior trading day (same model and gates), not with the previous run.</p>`;
  html += sec('New Favorable', ch.new_buy, 'buy') + sec('New Unfavorable', ch.new_sell, 'sell') + sec('New Conflicted', ch.new_exit, 'exit') + sec('Dropped to Neutral', ch.dropped, '');
  html += `<div class="grid g2"><div class="card"><h3>Trailing/Emerging Momentum transitions <span class="muted">(${ch.regime.length})</span></h3>${ch.regime.length ? `<table><thead><tr><th class="left">Ticker</th><th>From</th><th>To</th><th>Signal</th></tr></thead><tbody>${ch.regime.map(x => `<tr data-t="${x.ticker}"><td class="left">${tk(x.ticker)}</td><td style="color:${regColor(x.old)}">${x.old}</td><td style="color:${regColor(x.new)}">${x.new}</td><td>${badge(x.rec)}</td></tr>`).join('')}</tbody></table>` : '<div class="empty">None</div>'}</div>
    <div class="card"><h3>Biggest confidence movers</h3><table><thead><tr><th class="left">Ticker</th><th>POS</th><th>Δ</th><th>NEG</th><th>Δ</th><th>Signal</th></tr></thead><tbody>${ch.movers.map(x => `<tr data-t="${x.ticker}"><td class="left">${tk(x.ticker)}</td><td>${x.buy}</td><td class="${signCls(x.d_buy)}">${f(x.d_buy,0,true)}</td><td>${x.sell}</td><td class="${signCls(-x.d_sell)}">${f(x.d_sell,0,true)}</td><td>${badge(x.rec)}</td></tr>`).join('')}</tbody></table></div></div>`;
  if (ch.new_tickers.length) html += `<p class="note">Not in prior set: ${ch.new_tickers.join(', ')}</p>`;
  document.getElementById('changes').innerHTML = html;
  document.querySelectorAll('#changes tbody tr').forEach(tr => tr.onclick = () => openDrawer(tr.dataset.t));
}

function renderSignals() {
  const cols = [
    {key:'t', label:'Ticker', left:true, render:r => tk(r.t)+flags(r)},
    themeCol,
    {key:'rec', label:'Signal', render:r => omBadge(r), sortVal:r => omOrder(r)},
    qsCol,
    {key:'gate', label:'Blocked by', left:true, render:r => r.gate ? `<span class="warn" title="${wTip(r)}">${esc(r.gate)}</span>` : '', sortVal:r => r.gate || '', tip:'Why a name that cleared the POS threshold is not Favorable (see Guide → Gates)'},
    ...TREND_COLS,
    {key:'buy', label:'POS Signals', cls:r => r.buy>=CFG.buy_thr?'g bg-g':confCls(r.buy), render:r => fi(r.buy) + (r.b_floor?'<span class="flag" title="fresh-cross floor applied">°</span>':''), tip:'POS Signals score 0-100'},
    {key:'sell', label:'NEG Signals', cls:r => r.sell>=CFG.sell_thr?'b bg-b':confCls(r.sell), render:r => fi(r.sell) + (r.s_floor?'<span class="flag" title="fresh-cross floor applied">°</span>':''), tip:'NEG Signals score 0-100'},
    {key:'bias', label:'Net Signals', cls:r => signCls(r.bias), render:r => f(r.bias,0,true)},
    {key:'hist', label:'20d B/S', render:r => { const H=P.history[r.t]; return H ? `<svg width="0" height="0"></svg>`.replace('<svg width="0" height="0"></svg>', lineSpark(H)) : '—'; }, sortVal:r => { const H=P.history[r.t]; return H ? H.b[H.b.length-1]-H.b[Math.max(0,H.b.length-6)] : null; }, tip:'POS Signals (green) and NEG Signals (red) over the last 20 sessions; sort = 5-day change in Buy'},
    {key:'rsi', label:'RSI', cls:r => rsiCls(r.rsi), render:r => f(r.rsi,1)},
    {key:'ppo', label:'PPO', cls:r => signCls(r.ppo), render:r => f(r.ppo,2,true)},
    {key:'sig_x', label:'Sig×', render:r => arrow(r.sig_x), sortVal:r => r.sig_x==='↑'?2:r.sig_x==='↓'?0:1, tip:'PPO crossed its signal line within '+CFG.fresh_bars+' bars'},
    {key:'zero_x', label:'Zero×', render:r => arrow(r.zero_x), sortVal:r => r.zero_x==='↑'?2:r.zero_x==='↓'?0:1},
    {key:'e20', label:'vs E20', cls:r => signCls(r.e20), render:r => f(r.e20,1,true)+'%'},
    {key:'e50', label:'vs E50', cls:r => signCls(r.e50), render:r => f(r.e50,1,true)+'%'},
    {key:'e200', label:'vs E200', cls:r => signCls(r.e200), render:r => f(r.e200,1,true)+'%'},
    {key:'regime', label:'Trailing/Emerging Momentum', render:r => `<span style="color:${regColor(r.regime)}">${r.regime}</span>`},
    {key:'mom', label:'RS Rating', cls:r => pctCls(r.mom), render:r => fi(isNum(r.rs) ? r.rs : r.mom), sortVal:r => r.mom, tip:RS_TIP},
    {key:'hv', label:'HV', render:r => f(r.hv,0), tip:'20d historical volatility, annualised %'},
    {key:'close', label:'Close', render:r => fp(r.close)},
  ];
  makeTable('sig-table', cols, ROWS, {
    sortKey: 'rec', sortDir: 1,   // v48: Signal is the active sort on load (category, then Net Bias high to low)
    filters: { BUY:r=>r.rec==='BUY', SELL:r=>r.rec==='SELL', EXIT:r=>r.rec==='EXIT', HOLD:r=>r.rec==='HOLD', WATCH:r=>!!r.watch, WATCHF:r=>r.watch==='BUY', WATCHU:r=>r.watch==='SELL', BLOCKED:r=>!!r.gate && r.rec==='HOLD', CANDS:isCandidate, INTREND:r=>!!r.in_tr, FRESH:r=>r.sig_x!=='—', ALERTS:r=>r.rec!=='HOLD', FLAGGED:r=>!r.data_ok||r.stale||!r.tradeable },
    filterLabels: { BUY:'Favorable', SELL:'Unfavorable', EXIT:'Conflicted', HOLD:'Neutral', WATCH:'Watch (any)', WATCHF:'Watch Favorable', WATCHU:'Watch Unfavorable', BLOCKED:'Blocked Favorable', CANDS:'Candidates', INTREND:'In trend', FRESH:'Fresh cross', ALERTS:'Any alert', FLAGGED:'Flagged' },
    note: `Favorable alert at POS ≥ ${CFG.buy_thr}, Unfavorable alert at NEG ≥ ${CFG.sell_thr}. ${FLOOR_NOTE} <b>In Trend</b> = sessions and return since the Favorable alert that opened the trend, with its trailing stop (display only). Both alerts within ${CFG.conflict_margin} points → Neutral (Conflicted). <b>Blocked Favorable</b> = cleared the POS threshold but a gate stopped it (reason in the Blocked by column; see Guide → Gates). <b>Candidates</b> = blocked Favorable ratings with a fresh ↑ cross and the close above EMA200 whose only blockers are relative strength and/or the SPY regime (SPY and RSP both weak). Flags: ● live intraday price · ◐ short history (no alerts) · ⏱ stale bar · ≋ below liquidity floor. Click any row for the detail drawer; click headers to sort.`
  });
  document.getElementById('signals').innerHTML = '<h2>Signals</h2><div id="sig-table"></div>';
  renderTable('sig-table');
}
function renderSixPack() {
  const host = document.getElementById('sixpack');
  const NB = (CFG.six_pack || []).map(x => ({...(BY[x.t] || {t:x.t, rec:'NODATA'}), name:x.name, cap:x.cap, style:x.style, t:x.t, nodata:!BY[x.t]}));
  const have = NB.filter(r => !r.nodata), missing = NB.filter(r => r.nodata);
  const COLS = ['Growth','Value'], ROWSN = ['Large','Mid','Small'];
  const cellOf = (cap, st) => NB.find(r => r.cap === cap && r.style === st);
  const n = rec => have.filter(r => r.rec === rec).length;
  const kpi = (v,l,cls='',d='') => `<div class="kpi" style="cursor:default"><div class="v ${cls}">${v}</div><div class="l">${l}</div><div class="d">${d}</div></div>`;
  const ofN = `of ${have.length} funds`;
  const recCls = r => r.rec === 'BUY' ? 'buy' : r.rec === 'SELL' ? 'sell' : r.rec === 'EXIT' ? 'exit' : (r.watch ? 'watch' : '');
  const scCls = r => r.rec === 'BUY' ? 'good' : r.rec === 'SELL' ? 'bad' : r.rec === 'EXIT' ? 'warn' : 'muted';
  const cell = r => {
    if (!r) return '<div class="empty">—</div>';
    if (r.nodata) return `<div class="acard" style="cursor:default"><div class="top"><span class="tk">${r.t}</span><span class="badge HOLD">no data</span></div><div class="sub">${esc(r.name)} · see Health tab</div></div>`;
    const H = sliceH(P.history[r.t] || {b:[],s:[]}, CFG.drawer_bars);
    const sp = r.rec === 'SELL' ? sparkline(H.s.slice(-20), {w:70,h:22,color:C.bad,ref:CFG.sell_thr,min:0,max:100}) : sparkline(H.b.slice(-20), {w:70,h:22,color:C.good,ref:CFG.buy_thr,min:0,max:100});
    const watch = watchBadge(r);
    return `<div class="acard ${recCls(r)}" data-t="${r.t}"><div class="top"><span><span class="tk">${r.t}${flags(r)}</span> ${omBadge(r)}</span><span class="sc ${scCls(r)}">${fi(r.buy)}/${fi(r.sell)}</span></div>
      <div class="sub">${esc(r.name)}</div>
      <div class="sub">${watch}<span style="color:${regColor(r.regime)}">${r.regime}</span> · RSI ${f(r.rsi)} · ${fp(r.close)} <span class="${signCls(r.ret1)==='g'?'good':signCls(r.ret1)==='b'?'bad':''}">${f(r.ret1,2,true)}%</span></div>
      <div class="row">${sp}<span class="sub">Mom ${f(r.mom,0)}%ile · vs E200 ${f(r.e200,1,true)}%</span></div></div>`;
  };
  const hdr = t => `<div style="text-align:center;font-weight:700;color:var(--muted);text-transform:uppercase;letter-spacing:.05em;font-size:.8rem;padding:.2rem 0">${t}</div>`;
  const rowLbl = t => `<div style="display:flex;align-items:center;justify-content:center;font-weight:700;color:var(--muted);text-transform:uppercase;letter-spacing:.05em;font-size:.8rem;writing-mode:vertical-rl;transform:rotate(180deg)">${t} Cap</div>`;
  const grid = `<div class="card"><div style="display:grid;grid-template-columns:2.2rem repeat(2,minmax(0,1fr));gap:.6rem;align-items:stretch">
    <div></div>${COLS.map(hdr).join('')}
    ${ROWSN.map(rw => rowLbl(rw) + COLS.map(c => `<div>${cell(cellOf(rw, c))}</div>`).join('')).join('')}
  </div></div>`;
  const avg = (rows, k) => rows.length ? rows.reduce((a,r) => a + (r[k] ?? 0), 0) / rows.length : null;
  const summ = (label, rows) => `<tr><td class="left"><b>${label}</b></td><td>${rows.length}</td><td class="g">${rows.filter(r=>r.rec==='BUY').length}</td><td>${rows.filter(r=>r.rec==='HOLD').length}</td><td class="b">${rows.filter(r=>r.rec==='SELL').length}</td><td>${f(avg(rows,'mom'),0)}</td><td class="${signCls(avg(rows,'bias'))}">${f(avg(rows,'bias'),0,true)}</td></tr>`;
  const sumTable = `<div class="card"><h3>Where the signals are</h3><table><thead><tr><th class="left">Group</th><th>Funds</th><th>Favorable</th><th>Neutral</th><th>Unfavorable</th><th>Avg mom %ile</th><th>Avg Net Signals</th></tr></thead><tbody>
    ${ROWSN.map(rw => summ(rw + ' Cap', have.filter(r => r.cap === rw))).join('')}
    ${COLS.map(c => summ(c, have.filter(r => r.style === c))).join('')}</tbody></table></div>`;
  const cols = [
    {key:'t', label:'Ticker', left:true, render:r => tk(r.t) + (r.nodata ? '' : flags(r))},
    {key:'name', label:'Fund', left:true, render:r => esc(r.name)},
    {key:'cap', label:'Cap', left:true, sortVal:r => ROWSN.indexOf(r.cap)},
    {key:'style', label:'Style', left:true, sortVal:r => COLS.indexOf(r.style)},
    {key:'rec', label:'Signal', render:r => r.nodata ? '<span class="muted">no data</span>' : omBadge(r), sortVal:r => r.nodata ? 9 : omOrder(r)},
    qsCol,
    {key:'buy', label:'POS Signals', cls:r => r.buy>=(r.buy_thr||CFG.buy_thr)?'g bg-g':confCls(r.buy), render:r => fi(r.buy)},
    {key:'sell', label:'NEG Signals', cls:r => r.sell>=(r.sell_thr||CFG.sell_thr)?'b bg-b':confCls(r.sell), render:r => fi(r.sell) + (r.s_floor?'<span class="flag" title="fresh-cross floor applied">°</span>':'')},
    {key:'bias', label:'Net Signals', cls:r => signCls(r.bias), render:r => f(r.bias,0,true)},
    {key:'hist', label:'20d B/S', render:r => { const H = P.history[r.t]; return H ? lineSpark(H) : '—'; }, sortVal:r => { const H = P.history[r.t]; return H ? H.b[H.b.length-1]-H.b[Math.max(0,H.b.length-6)] : null; }},
    {key:'regime', label:'Trailing/Emerging Momentum', render:r => r.nodata ? '—' : `<span style="color:${regColor(r.regime)}">${r.regime}</span>`},
    {key:'mom', label:'RS Rating', cls:r => pctCls(r.mom), render:r => fi(isNum(r.rs) ? r.rs : r.mom), sortVal:r => r.mom, tip:RS_TIP},
    {key:'ret1', label:'1d', cls:r => signCls(r.ret1), render:r => f(r.ret1,2,true)+'%'},
    {key:'e50', label:'vs E50', cls:r => signCls(r.e50), render:r => f(r.e50,1,true)+'%'},
    {key:'e200', label:'vs E200', cls:r => signCls(r.e200), render:r => f(r.e200,1,true)+'%'},
    {key:'rsi', label:'RSI', cls:r => rsiCls(r.rsi), render:r => f(r.rsi,1)},
    {key:'close', label:'Close', render:r => fp(r.close)},
  ];
  host.innerHTML = `<h2>Six Pack <span class="muted" style="font-weight:400;font-size:.85rem">Vanguard style grid · six ETFs · same scoring as every other tab</span></h2>
    <div class="kpis" style="grid-template-columns:repeat(4,1fr)">${kpi(n('BUY'),'Favorable', 'good',ofN)}${kpi(n('HOLD'),'Neutral', '', ofN)}${kpi(n('SELL'),'Unfavorable', 'bad',ofN)}${kpi(n('EXIT'),'Conflicted', 'warn','conflicting signals')}</div>
    ${missing.length ? `<div class="warnbox">No data loaded for: ${missing.map(r => `<b>${r.t}</b> (${esc(r.name)})`).join(', ')}. Check the Health tab.</div>` : ''}
    ${grid}${sumTable}<div id="six-table"></div>`;
  makeTable('six-table', cols, NB, {
    sortKey: 'rec', sortDir: 1,
    filters: { BUY:r=>r.rec==='BUY', HOLD:r=>r.rec==='HOLD', SELL:r=>r.rec==='SELL', EXIT:r=>r.rec==='EXIT' },
    filterLabels: { BUY:'Favorable', HOLD:'Neutral', SELL:'Unfavorable', EXIT:'Conflicted' },
    note: `Each cell shows POS/NEG Signals. Columns are investment style (Growth, Value); rows are market cap (Large, Mid, Small). Scoring and per-regime alert thresholds are identical to the Signals tab (see Guide → POS &amp; NEG Signals). Neutral means neither side has fired a confirmed alert. Click any cell or row for the detail drawer.`
  });
}
function lineSpark(H) {
  const b = H.b.slice(-20), s = H.s.slice(-20), w = 80, h = 22;
  const X = i => 1 + (w-2)*i/Math.max(1,b.length-1), Y = v => h-1 - (h-2)*v/100;
  const p = a => a.map((v,i) => (i?'L':'M')+X(i).toFixed(1)+','+Y(v).toFixed(1)).join('');
  return `<svg width="${w}" height="${h}"><line x1="0" x2="${w}" y1="${Y(CFG.buy_thr)}" y2="${Y(CFG.buy_thr)}" stroke="${C.grid}" stroke-dasharray="2,2"/><path d="${p(s)}" fill="none" stroke="${C.bad}" stroke-width="1.3" opacity=".9"/><path d="${p(b)}" fill="none" stroke="${C.good}" stroke-width="1.3"/></svg>`;
}

// v50: Sectors, ETFs, Tear's / Frank's Short List, Country ETFs and Currency now share the Signals page layout:
// title + filter toolbar + the same sortable table (same columns, same filters, same note). No KPI strip or card board.
function sigLikePage(o) {
  const host = document.getElementById(o.host);
  const items = (o.items || []).map(x => { const r = BY[x.t]; return {...(r || {t:x.t, rec:'NODATA'}), ...(o.extra ? o.extra(x) : {}), t:x.t, nodata:!r}; });
  const missing = items.filter(r => r.nodata);
  const base = [
    {key:'t', label:o.tickerLabel || 'Ticker', left:true, render:r => tk(r.t) + (r.nodata ? '' : flags(r)), sortVal:r => r.t},
    {...themeCol, label:o.groupLabel || 'Theme', tip:o.groupTip || themeCol.tip},
    {key:'rec', label:'Signal', render:r => r.nodata ? '<span class="muted">no data</span>' : omBadge(r), sortVal:r => r.nodata ? 9 : omOrder(r)},
    qsCol,
    ...(o.afterSignal || []),
    {key:'gate', label:'Blocked by', left:true, render:r => r.gate ? `<span class="warn" title="${wTip(r)}">${esc(r.gate)}</span>` : '', sortVal:r => r.gate || '', tip:'Why a name that cleared the POS threshold is not Favorable (see Guide → Gates)'},
    ...TREND_COLS,
    {key:'buy', label:'POS Signals', cls:r => r.buy>=(r.buy_thr||CFG.buy_thr)?'g bg-g':confCls(r.buy), render:r => fi(r.buy) + (r.b_floor?'<span class="flag" title="fresh-cross floor applied">°</span>':''), tip:'POS Signals score 0-100'},
    {key:'sell', label:'NEG Signals', cls:r => r.sell>=(r.sell_thr||CFG.sell_thr)?'b bg-b':confCls(r.sell), render:r => fi(r.sell) + (r.s_floor?'<span class="flag" title="fresh-cross floor applied">°</span>':''), tip:'NEG Signals score 0-100'},
    {key:'bias', label:'Net Signals', cls:r => signCls(r.bias), render:r => f(r.bias,0,true)},
    {key:'hist', label:'20d B/S', render:r => { const H=P.history[r.t]; return H ? lineSpark(H) : '—'; }, sortVal:r => { const H=P.history[r.t]; return H ? H.b[H.b.length-1]-H.b[Math.max(0,H.b.length-6)] : null; }, tip:'POS Signals (green) and NEG Signals (red) over the last 20 sessions; sort = 5-day change in Buy'},
    {key:'rsi', label:'RSI', cls:r => rsiCls(r.rsi), render:r => f(r.rsi,1)},
    {key:'ppo', label:'PPO', cls:r => signCls(r.ppo), render:r => f(r.ppo,2,true)},
    {key:'sig_x', label:'Sig×', render:r => arrow(r.sig_x), sortVal:r => r.sig_x==='↑'?2:r.sig_x==='↓'?0:1, tip:'PPO crossed its signal line within '+CFG.fresh_bars+' bars'},
    {key:'zero_x', label:'Zero×', render:r => arrow(r.zero_x), sortVal:r => r.zero_x==='↑'?2:r.zero_x==='↓'?0:1},
    {key:'e20', label:'vs E20', cls:r => signCls(r.e20), render:r => f(r.e20,1,true)+'%'},
    {key:'e50', label:'vs E50', cls:r => signCls(r.e50), render:r => f(r.e50,1,true)+'%'},
    {key:'e200', label:'vs E200', cls:r => signCls(r.e200), render:r => f(r.e200,1,true)+'%'},
    {key:'regime', label:'Trailing/Emerging Momentum', render:r => `<span style="color:${regColor(r.regime)}">${r.regime}</span>`},
    {key:'mom', label:'RS Rating', cls:r => pctCls(r.mom), render:r => fi(isNum(r.rs) ? r.rs : r.mom), sortVal:r => r.mom, tip:o.momTip || RS_TIP},
    {key:'hv', label:'HV', render:r => f(r.hv,0), tip:'20d historical volatility, annualised %'},
    ...(o.beforeClose || []),
    {key:'close', label:'Close', render:r => fp(r.close)},
  ];
  // rows with no data show a dash instead of NaN / undefined in every score column
  const cols = base.map(c => (c.key === 't' || c.key === 'theme' || c.key === 'rec') ? c : {...c, render:r => r.nodata ? '—' : c.render(r), cls:c.cls ? (r => r.nodata ? '' : c.cls(r)) : c.cls});
  host.innerHTML = `<h2>${o.title}${o.sub ? ` <span class="muted" style="font-weight:400;font-size:.85rem">${o.sub}</span>` : ''}</h2>
    ${o.banner ? o.banner(items) : ''}
    ${missing.length ? `<div class="warnbox">No data loaded for: ${missing.map(r => `<b>${r.t}</b>`).join(', ')}. Check the Health tab.</div>` : ''}
    ${items.length ? `<div id="${o.table}"></div>` : `<div class="empty">${o.empty || 'Nothing configured'}</div>`}`;
  if (!items.length) return;
  makeTable(o.table, cols, items, {
    sortKey: 'rec', sortDir: 1,
    filters: { BUY:r=>r.rec==='BUY', SELL:r=>r.rec==='SELL', EXIT:r=>r.rec==='EXIT', HOLD:r=>r.rec==='HOLD', WATCH:r=>!!r.watch, WATCHF:r=>r.watch==='BUY', WATCHU:r=>r.watch==='SELL', BLOCKED:r=>!!r.gate && r.rec==='HOLD', CANDS:isCandidate, INTREND:r=>!!r.in_tr, FRESH:r=>r.sig_x!=='—', ALERTS:r=>r.rec!=='HOLD', FLAGGED:r=>!r.nodata && (!r.data_ok||r.stale||!r.tradeable) },
    filterLabels: { BUY:'Favorable', SELL:'Unfavorable', EXIT:'Conflicted', HOLD:'Neutral', WATCH:'Watch (any)', WATCHF:'Watch Favorable', WATCHU:'Watch Unfavorable', BLOCKED:'Blocked Favorable', CANDS:'Candidates', INTREND:'In trend', FRESH:'Fresh cross', ALERTS:'Any alert', FLAGGED:'Flagged' },
    note: (o.note ? o.note + ' ' : '') + `Favorable alert at POS ≥ ${CFG.buy_thr}, Unfavorable alert at NEG ≥ ${CFG.sell_thr}. ${FLOOR_NOTE} <b>In Trend</b> = sessions and return since the Favorable alert that opened the trend, with its trailing stop (display only). Both alerts within ${CFG.conflict_margin} points → Neutral (Conflicted). <b>Blocked Favorable</b> = cleared the POS threshold but a gate stopped it (reason in the Blocked by column; see Guide → Gates). Flags: ● live intraday price · ◐ short history (no alerts) · ⏱ stale bar · ≋ below liquidity floor. Click any row for the detail drawer; click headers to sort.`
  });
}

// ---------- Bonds tab: Treasury yield curve + Bond ETF list ----------
function renderBonds() {
  const host = document.getElementById('bonds');
  host.innerHTML = '<h2>Bonds</h2><div id="bond-curve"></div><div id="bond-etfs"></div>';
  const Y = P.yields || {ok:false};
  const cv = document.getElementById('bond-curve');
  if (!Y.ok) {
    cv.innerHTML = '<div class="warnbox">Treasury yields could not be loaded (FRED and Yahoo both unreachable and no cached curve). Re-run with a network connection; the Bond ETF list below is unaffected.</div>';
  } else {
    const SER = [['now','Current',C.text,2.6,''],['1w','1 week ago','#f0883e',1.6,''],['1m','1 month ago','#bc8cff',1.6,''],['3m','3 months ago',C.accent,1.6,''],['1y','1 year ago',C.muted,1.6,'5,3']];
    const labs = Y.labels, yrs = labs.map(l => Y.years[l]);
    const vals = SER.flatMap(([k]) => labs.map(l => (Y.series[k] || {})[l])).filter(isNum);
    const w = 900, h = 340, L = 58, R = 16, T = 14, B = 44;
    let lo = Math.floor(Math.min(...vals) * 4) / 4 - .25, hi = Math.ceil(Math.max(...vals) * 4) / 4 + .25;
    const sq = v => Math.sqrt(v), x0 = sq(yrs[0]), x1 = sq(yrs[yrs.length-1]);
    const X = yv => L + (w-L-R) * (sq(yv) - x0) / (x1 - x0), Yp = v => T + (h-T-B) * (1 - (v-lo)/(hi-lo));
    let g = '';
    const step = (hi-lo) > 3 ? .5 : .25;
    for (let v = Math.ceil(lo/step)*step; v <= hi + 1e-9; v += step) g += `<line x1="${L}" x2="${w-R}" y1="${Yp(v)}" y2="${Yp(v)}" stroke="${C.grid}" stroke-width=".6"/><text x="${L-6}" y="${Yp(v)+3}" font-size="10" fill="${C.muted}" text-anchor="end">${v.toFixed(2)}%</text>`;
    labs.forEach((l,i) => g += `<line x1="${X(yrs[i])}" x2="${X(yrs[i])}" y1="${T}" y2="${h-B}" stroke="${C.grid}" stroke-width=".6" stroke-dasharray="2,3"/><text x="${X(yrs[i])}" y="${h-B+16}" font-size="11" fill="${C.muted}" text-anchor="middle">${l}</text>`);
    g += `<text x="${(L+w-R)/2}" y="${h-6}" font-size="10" fill="${C.muted}" text-anchor="middle">Duration (years to maturity, √ scale)</text><text transform="translate(11 ${(T+h-B)/2}) rotate(-90)" font-size="10" fill="${C.muted}" text-anchor="middle">Yield (%)</text>`;
    SER.slice().reverse().forEach(([k,nm,col,wd,dash]) => {
      const pts = labs.map((l,i) => [yrs[i], (Y.series[k] || {})[l], l]).filter(p => isNum(p[1]));
      if (!pts.length) return;
      g += `<path d="${pts.map((p,i) => (i?'L':'M') + X(p[0]).toFixed(1) + ',' + Yp(p[1]).toFixed(1)).join('')}" fill="none" stroke="${col}" stroke-width="${wd}"${dash ? ` stroke-dasharray="${dash}"` : ''}/>`;
      pts.forEach(p => g += `<circle cx="${X(p[0])}" cy="${Yp(p[1])}" r="${k==='now'?3.6:2.6}" fill="${col}"><title>${nm}${Y.when[k] ? ' (' + Y.when[k] + ')' : ''} · ${p[2]}: ${p[1].toFixed(2)}%</title></circle>`);
    });
    const key = SER.map(([k,nm,col,wd,dash]) => `<span style="display:inline-flex;align-items:center;gap:.35rem;margin-right:1rem"><svg width="22" height="8"><line x1="0" x2="22" y1="4" y2="4" stroke="${col}" stroke-width="${wd}"${dash ? ` stroke-dasharray="${dash}"` : ''}/></svg>${nm}</span>`).join('');
    const hdr = '<th class="left">Date</th><th class="left">Curve</th>' + labs.map(l => `<th>${l}</th>`).join('');
    const rows = SER.map(([k,nm,col]) => `<tr style="cursor:default"><td class="left">${Y.when[k] || '—'}</td><td class="left" style="color:${col};font-weight:600">${nm}</td>${labs.map(l => { const v = (Y.series[k] || {})[l]; return `<td>${isNum(v) ? v.toFixed(2) + '%' : '—'}</td>`; }).join('')}</tr>`).join('');
    const chg = k => `<tr style="cursor:default"><td class="left"></td><td class="left muted">Change vs ${k[1].toLowerCase()} (bp)</td>${labs.map(l => { const a = (Y.series.now || {})[l], b = (Y.series[k[0]] || {})[l]; if (!isNum(a) || !isNum(b)) return '<td>—</td>'; const d = (a-b)*100; return `<td class="${d>0?'b':d<0?'g':'mu'}">${d>0?'+':''}${d.toFixed(0)}</td>`; }).join('')}</tr>`;
    cv.innerHTML = `<div class="card"><div class="chart-title"><span>US Treasury yield curve</span><span class="muted">as of ${Y.asof} · ${esc(Y.src || '')}</span></div>
      <svg viewBox="0 0 ${w} ${h}" style="width:100%;height:auto;max-height:420px">${g}</svg>
      <div class="muted" style="font-size:.78rem;margin-top:.3rem">${key}hover a point for the exact yield</div>
      <div class="twrap" style="max-height:none;margin-top:.75rem"><table><thead><tr>${hdr}</tr></thead><tbody>${rows}${chg(['1w','1 week ago'])}${chg(['1m','1 month ago'])}${chg(['3m','3 months ago'])}${chg(['1y','1 year ago'])}</tbody></table></div>
      <p class="note">Rising yields (red) mean falling bond prices; the longer the maturity, the larger the price move per basis point. Yields are daily constant-maturity Treasury rates; the "ago" columns use the last trading day on or before that date.</p></div>`;
  }
  sigLikePage({host:'bond-etfs', table:'bond-table', title:'Bond ETFs', sub:'your bond fund list (Config.bond_etfs)', items:CFG.bond_etfs, tickerLabel:'Bond ETF', empty:'No bond ETFs configured - add tickers to Config.bond_etfs',
    extra:x => ({name: coName(x.t) || x.name || ''}),
    note:'Same scoring as the Signals tab. A rising price means falling yields.'});
}
function renderSectors() {
  sigLikePage({host:'sectors', table:'sector-table', title:'Sectors', sub:'S&amp;P 500 sector ETFs', items:CFG.sectors, groupLabel:'Sector', groupTip:'S&P 500 sector',
    note:'Same POS/NEG Signals scoring and per-regime alert thresholds as the Signals tab.'});
}
function renderEtfs() {
  sigLikePage({host:'etfs', table:'etf-table', title:'ETFs', sub:'your ETF watchlist (Config.etf_tickers)', items:CFG.etfs, tickerLabel:'ETF', empty:'No ETFs configured - add tickers to Config.etf_tickers',
    extra:x => ({name: coName(x.t) || x.name || ''}),
    note:'Same scoring as the Signals tab. These funds are also plotted on Rotation → ETFs.'});
}
function renderTear() {
  sigLikePage({host:'tear', table:'tear-table', title:"Tear's Short List", sub:`${(CFG.tear||[]).length} names (Config.tear_tickers)`, items:CFG.tear, empty:'No names configured - add tickers to Config.tear_tickers',
    note:"Same scoring as the Signals tab. This list is a carve-out for emphasis only: the names stay in the universe, the Themes / Sub-Themes aggregates and Rotation → All, and are also plotted at Rotation → Tear's Short List."});
}
function renderShortlist() {
  sigLikePage({host:'shortlist', table:'shortlist-table', title:"Frank's Short List", sub:`${(CFG.shortlist||[]).length} names (Config.shortlist_tickers)`, items:CFG.shortlist, empty:'No names configured - add tickers to Config.shortlist_tickers',
    note:"Same scoring as the Signals tab. This list is a carve-out for emphasis only: the names stay in the universe, the Themes / Sub-Themes aggregates and Rotation → All, and are also plotted at Rotation → Frank's Short List."});
}
function renderCountryEtfs() {
  sigLikePage({host:'country', table:'country-table', title:'Country ETFs', sub:'single-country ETFs (Config.country_etfs)', items:CFG.country_etfs, tickerLabel:'Country ETF', groupLabel:'Country', groupTip:'Country the fund tracks',
    extra:x => ({country:x.country, name:x.name || ''}),
    note:`Same scoring as the Signals tab. Country funds use a lower liquidity floor ($${((CFG.country_floor||0)/1e6).toFixed(1)}M) and are not blocked by the SPY-regime gate. Also plotted at Rotation → Country ETFs.`});
}
function renderCurrency() {
  const rhoCls = v => !isNum(v) ? '' : v <= -0.2 ? 'g' : v >= 0.3 ? 'w' : '';
  const usdRead = r => { if (r.nodata) return ''; const up = r.kind === 'ref' ? 'BUY' : 'SELL', dn = r.kind === 'ref' ? 'SELL' : 'BUY';
    return r.rec === up ? '<span class="accent">USD ↑</span>' : r.rec === dn ? '<span class="accent">USD ↓</span>' : '<span class="muted">—</span>'; };
  const banner = items => {
    const fx = items.filter(r => !r.nodata && r.kind === 'fx'), ref = items.find(r => r.kind === 'ref');
    if (!fx.length) return '';
    const avgBias = fx.reduce((a,r) => a + r.bias, 0) / fx.length;
    const W = CFG.fx_w || {}, wr = fx.filter(r => W[r.t]), wsum = wr.reduce((a,r) => a + W[r.t], 0);
    const wBias = wsum ? wr.reduce((a,r) => a + W[r.t] * r.bias, 0) / wsum : avgBias;
    const view = wBias >= 15 ? 'Dollar weakening' : wBias <= -15 ? 'Dollar strengthening' : 'No clear dollar trend';
    const uupBias = ref && !ref.nodata ? ref.bias : null;
    const disagree = uupBias !== null && ((wBias >= 15 && uupBias >= 15) || (wBias <= -15 && uupBias <= -15));
    return `<p class="note" style="margin:.2rem 0 .6rem"><b>USD view:</b> <span class="accent">${view}</span> · DXY-weighted net signals ${f(wBias,0,true)} · equal-weight ${f(avgBias,0,true)}${disagree ? ' · <span class="warn">UUP disagrees</span>' : ''}${ref && !ref.nodata ? ` · ${ref.t} (the dollar): ${omBadge(ref)}` : ''}</p>`;
  };
  sigLikePage({host:'currency', table:'currency-table', title:'Currency', sub:'view on the US dollar (Config.currency_etfs)', items:CFG.currency, tickerLabel:'Fund', groupLabel:'Currency', groupTip:'Currency the fund tracks', banner,
    momTip:"Percentile within the Currency group's own history",
    extra:x => ({currency:x.currency, name:x.name || '', kind:x.kind, rho:(FXCORR[x.t] || {})}),
    afterSignal:[{key:'usd', label:'USD read', render:r => usdRead(r), sortVal:r => r.nodata ? 9 : (r.kind === 'ref' ? (r.rec === 'BUY' ? 2 : r.rec === 'SELL' ? 0 : 1) : (r.rec === 'BUY' ? 0 : r.rec === 'SELL' ? 2 : 1)), tip:'What the signal says about the US dollar'}],
    beforeClose:[
      {key:'rho_spy', label:'ρ SPY', cls:r => rhoCls(r.rho.spy), render:r => isNum(r.rho.spy) ? f(r.rho.spy,2,true) : '—', sortVal:r => r.rho.spy ?? null, tip:'Correlation of daily returns with ' + CFG.benchmark + ' over the last ' + CFG.fx_corr_win + ' sessions. Negative = diversifies equities (hedge)'},
      {key:'rho_uup', label:'ρ UUP', render:r => isNum(r.rho.uup) ? f(r.rho.uup,2,true) : '—', sortVal:r => r.rho.uup ?? null, tip:'Correlation with the dollar fund (UUP): strongly negative means it tracks dollar weakness'}],
    note:`Read a currency fund against the dollar, not against ${CFG.benchmark}: Favorable = the currency is strengthening (dollar weakening), Unfavorable = the dollar is strengthening; UUP is the dollar itself, so its reading is the opposite. Own percentile base and gates: see Guide → Currency tab.`});
}
function renderRank() {
  const rows = ROWS.slice().sort((a,b) => (b.mom??-1)-(a.mom??-1)).map((r,i) => ({...r, rank:i+1}));
  const cols = [
    {key:'rank', label:'#', render:r => r.rank},
    {key:'t', label:'Ticker', left:true, render:r => tk(r.t)+flags(r)},
    themeCol,
    {key:'mom', label:'Mom %', cls:r=>pctCls(r.mom), render:r=>f(r.mom,1)},
    {key:'trail', label:'Trailing', cls:r=>pctCls(r.trail), render:r=>f(r.trail,1)},
    {key:'emerg', label:'Emerging', cls:r=>pctCls(r.emerg), render:r=>f(r.emerg,1)},
    {key:'dorm', label:'Dormancy', render:r=>f(r.dorm,1)},
    {key:'regime', label:'Trailing/Emerging Momentum', render:r => `<span style="color:${regColor(r.regime)}">${r.regime}</span> <span class="muted">${f(r.regime_conf,2)}</span>`},
    {key:'rec', label:'Signal', render:r=>omBadge(r), sortVal:r=>omOrder(r)},
    qsCol,
    {key:'buy', label:'POS Signals', cls:r=>confCls(r.buy), render:r=>fi(r.buy)},
    {key:'sell', label:'NEG Signals', cls:r=>confCls(r.sell), render:r=>fi(r.sell)},
    {key:'bias', label:'Net Signals', cls:r=>signCls(r.bias), render:r=>f(r.bias,0,true), tip:'Net Signals = POS Signals − NEG Signals'},
    {key:'rsi', label:'RSI', cls:r=>rsiCls(r.rsi), render:r=>f(r.rsi,1)},
    {key:'adx', label:'ADX', render:r=>f(r.adx,0)},
    {key:'hi52', label:'52w', render:r=>isNum(r.hi52)?f(100*r.hi52,0)+'%':'—', tip:'Close as % of 52-week high'},
    {key:'stack', label:'Stack', render:r=>r.stack?'<span class="good">✓</span>':'<span class="muted">—</span>'},
    {key:'sqz', label:'Sqz', render:r=>fi(r.sqz)},
    {key:'close', label:'Close', render:r=>fp(r.close)},
  ];
  document.getElementById('rank').innerHTML = `<h2>Momentum Rankings <span class="muted" style="font-weight:400;font-size:.85rem">percentiles ${ANCHOR_TXT}</span></h2><div id="rank-table"></div>`;
  makeTable('rank-table', cols, rows, {filters:{Strong:r=>r.regime==='Strong','Dormant→Waking':r=>r.regime==='Dormant→Waking',Neutral:r=>r.regime==='Neutral','Mature/Cooling':r=>r.regime==='Mature/Cooling',Weak:r=>r.regime==='Weak'}, note:'Trailing = realised momentum (20/50/252d returns, ADX, 52-week position). Emerging = acceleration (PPO histogram, DMI, OBV slope, blended momentum, persistence). Mom % = 0.6·Trailing + 0.4·Emerging. Regime confidence 0-1.'});
}

function renderSqueeze() {
  const chip = (on, l) => `<span class="chip ${on?'on':'off'}">${l}</span>`;
  const cell = (tot, chips) => `<div class="sqz"><b>${tot}</b>${chips}</div>`;
  const cols = [
    {key:'t', label:'Ticker', left:true, render:r => tk(r.t)+flags(r)},
    themeCol,
    {key:'sqz', label:'Strength', cls:r => r.sqz>=60?'g':r.sqz>=35?'m':'b', render:r => fi(r.sqz)},
    {key:'sqz_full', label:'Full', render:r => r.sqz_full ? '<span class="good">Yes</span>' : '<span class="muted">No</span>'},
    {key:'sqz_on', label:'State', render:r => r.sqz_on ? `<span class="warn">ON ${r.sqz_len}b</span>` : (r.sq_rel ? '<span class="good">Fired</span>' : `<span class="muted">off · last ${r.sqz_len}b</span>`), sortVal:r => r.sqz_on?2:r.sq_rel?1:0, tip:'Squeeze currently on (BB inside KC) with run length, or recently fired'},
    {key:'sqz_f', label:'Foundation /20', render:r => cell(r.sqz_f, chip(r.sq_base,'Base')+chip(r.sq_rel,'Release'))},
    {key:'sqz_m', label:'Momentum /30', render:r => cell(r.sqz_m, chip(r.sq_ppo,'PPO↑')+chip(r.sq_dmi,'DMI'))},
    {key:'sqz_c', label:'Condition /20', render:r => cell(r.sqz_c, chip(r.sq_rsi,'RSI')+chip(r.sq_room,'Room'))},
    {key:'sqz_k', label:'Confirm /15', render:r => cell(r.sqz_k, chip(r.sq_obv,'OBV')+chip(r.sq_flat,'Flat'))},
    {key:'regime', label:'Trailing/Emerging Momentum', render:r => `<span style="color:${regColor(r.regime)}">${r.regime}</span>`},
    {key:'rec', label:'Signal', render:r => omBadge(r), sortVal:r=>omOrder(r)},
    qsCol,
    {key:'close', label:'Close', render:r => fp(r.close)},
  ];
  document.getElementById('sqz').innerHTML = '<h2>Squeeze Setups</h2><div id="sqz-table"></div>';
  makeTable('sqz-table', cols, ROWS, {sortKey:'sqz', filters:{FULL:r=>!!r.sqz_full, ON:r=>!!r.sqz_on, FIRED:r=>!!r.sq_rel, BUY:r=>r.rec==='BUY'}, filterLabels:{FULL:'Full setup',ON:'Squeeze on',FIRED:'Recently fired',BUY:'Favorable'},
    note:'Strength = pillar sum rescaled to 0-100 (raw max 85). Full setup needs Foundation ≥ 14 (real base + release), Momentum ≥ 20, Condition ≥ 15, Confirmation ≥ 10. Base = compression ≥ 15 bars · Release = fired within 10 bars · Flat = Mom % 20-80.'});
}

function renderRotation() {
  const host = document.getElementById('rotation');
  host.innerHTML = `<h2>Relative Rotation</h2><div class="toolbar" id="rot-tb"><button class="on" data-f="all">All</button>${REGIMES.map(r => `<button data-f="${r}">${r}</button>`).join('')}<button data-f="alerts">Alerts only</button><button data-f="sixpack">Six Pack</button><button data-f="sectors">Sectors</button><button data-f="etfs">ETFs</button><button data-f="tear">Tear's Short List</button><button data-f="shortlist">Frank's Short List</button><button data-f="country">Country ETFs</button><button data-f="currency">Currency</button><button data-f="themes">Themes</button><button data-f="subthemes">Sub-Themes</button><select id="rot-theme" style="background:var(--bg);color:var(--text);border:1px solid var(--border);border-radius:6px;padding:.25rem .4rem;max-width:14rem"><option value="">Tickers in theme…</option>${TS.themes.map(x => `<option value="${esc(x.name)}">${esc(x.name)} (${x.n})</option>`).join("")}</select><label class="cnt">tails <select id="rot-tails" style="background:var(--bg);color:var(--text);border:1px solid var(--border);border-radius:4px;padding:.15rem .3rem"><option value="alerts">alerts &amp; watch</option><option value="all">all</option><option value="none">none</option></select></label><label class="cnt"><input type="checkbox" id="rot-labels" checked style="width:auto;margin:0 .3rem 0 0"/>labels</label></div><div class="card rot-wrap" id="rot-plot"></div>
    <p class="note">Trailing (x) vs Emerging (y) momentum percentiles. Colour = Signal (green Favorable, red Unfavorable, amber Conflicted, grey Neutral; blue ring = Watch). Size ∝ max(POS, NEG). Tails trace the last ${CFG.tail_bars} sessions — a name moving up-and-right is accelerating. Hover for detail, click to open. <b>Six Pack</b>, <b>Sectors</b>, <b>ETFs</b>, <b>Country ETFs</b> and <b>Currency</b> plot those funds on their own; they are left out of All, the regime buttons and Alerts only. <b>Tear's Short List</b> and <b>Frank's Short List</b> plot those lists on their own, but those names also stay in All. <b>Themes</b> and <b>Sub-Themes</b> plot one bubble per group at its median trailing / emerging percentiles (size ∝ members, colour = Theme Score, groups with too few names omitted; click to drill down); the picker plots the individual tickers of one theme.</p>`;
  let filt = 'all';
  const SEC = new Set((CFG.sectors||[]).map(x => x.t)), SIX = new Set((CFG.six_pack||[]).map(x => x.t)), ETF = new Set((CFG.etfs||[]).map(x => x.t)), COU = new Set((CFG.country_etfs||[]).map(x => x.t)), CUR = new Set((CFG.currency||[]).map(x => x.t)), TEAR = new Set((CFG.tear||[]).map(x => x.t)), SHORT = new Set((CFG.shortlist||[]).map(x => x.t));
  const GNAME = {}; (CFG.sectors||[]).concat(CFG.six_pack||[]).forEach(x => GNAME[x.t] = x.name);
  const draw = () => {
    const tailMode = document.getElementById('rot-tails').value, labels = document.getElementById('rot-labels').checked;
    const w = 1000, h = 620, L = 50, R = 20, T = 20, B = 45;
    const X = v => L + (w-L-R)*v/100, Y = v => T + (h-T-B)*(1-v/100);
    let rows = ROWS.filter(r => isNum(r.trail) && isNum(r.emerg));
    if (filt === 'themes' || filt === 'subthemes') rows = (filt === 'themes' ? TS.themes : TS.subs).filter(x => !x.small && isNum(x.trail) && isNum(x.emerg)).map(x => ({...x, t:(x.theme ? x.theme + ' › ' : '') + x.name, agg:true}));
    else if (filt.startsWith('theme:')) { const mem = new Set((TH_BY[filt.slice(6)] || {tickers:[]}).tickers); rows = rows.filter(r => mem.has(r.t)); }
    else if (filt === 'sixpack') rows = rows.filter(r => SIX.has(r.t));
    else if (filt === 'sectors') rows = rows.filter(r => SEC.has(r.t));
    else if (filt === 'etfs') rows = rows.filter(r => ETF.has(r.t));
    else if (filt === 'country') rows = rows.filter(r => COU.has(r.t));
    else if (filt === 'currency') rows = rows.filter(r => CUR.has(r.t));
    else if (filt === 'tear') rows = rows.filter(r => TEAR.has(r.t));
    else if (filt === 'shortlist') rows = rows.filter(r => SHORT.has(r.t));
    else { rows = rows.filter(r => !SIX.has(r.t) && !SEC.has(r.t) && !ETF.has(r.t) && !COU.has(r.t) && !CUR.has(r.t)); if (filt === 'alerts') rows = rows.filter(r => r.rec !== 'HOLD'); else if (filt !== 'all') rows = rows.filter(r => r.regime === filt); }
    let g = `<rect x="${L}" y="${T}" width="${w-L-R}" height="${h-T-B}" fill="#0d1117" stroke="${C.grid}"/>`;
    for (let v=0; v<=100; v+=25) g += `<line x1="${X(v)}" x2="${X(v)}" y1="${T}" y2="${h-B}" stroke="${C.grid}" stroke-width="${v===50?2:1}"/><line x1="${L}" x2="${w-R}" y1="${Y(v)}" y2="${Y(v)}" stroke="${C.grid}" stroke-width="${v===50?2:1}"/><text x="${X(v)}" y="${h-B+14}" font-size="11" fill="${C.muted}" text-anchor="middle">${v}</text><text x="${L-6}" y="${Y(v)+4}" font-size="11" fill="${C.muted}" text-anchor="end">${v}</text>`;
    g += `<rect x="${X(CFG.regime_lo)}" y="${Y(CFG.regime_hi)}" width="${X(CFG.regime_hi)-X(CFG.regime_lo)}" height="${Y(CFG.regime_lo)-Y(CFG.regime_hi)}" fill="${C.muted}" opacity=".08"/>`;
    g += `<text x="${X(25)}" y="${Y(94)}" font-size="12" fill="${C.accent}" text-anchor="middle">Dormant → Waking</text><text x="${X(75)}" y="${Y(94)}" font-size="12" fill="${C.good}" text-anchor="middle">Strong & accelerating</text><text x="${X(25)}" y="${Y(4)}" font-size="12" fill="${C.bad}" text-anchor="middle">Weak</text><text x="${X(75)}" y="${Y(4)}" font-size="12" fill="${C.warn}" text-anchor="middle">Mature / Cooling</text>`;
    g += `<text x="${(L+w-R)/2}" y="${h-6}" font-size="12" fill="${C.muted}" text-anchor="middle">Trailing momentum percentile</text><text transform="translate(14,${(T+h-B)/2}) rotate(-90)" font-size="12" fill="${C.muted}" text-anchor="middle">Emerging momentum percentile</text>`;
    const col = r => r.agg ? scoreColor(r.score) : r.rec==='BUY'?C.good:r.rec==='SELL'?C.bad:r.rec==='EXIT'?C.warn:'#6e7681';
    rows.forEach(r => { const H = r.agg ? {tr:r.tr, em:r.em} : sliceH(P.history[r.t] || {tr:[],em:[]}, CFG.tail_bars + 1); const tails = r.agg ? tailMode !== 'none' : (tailMode === 'all' || (tailMode === 'alerts' && (r.rec !== 'HOLD' || r.watch))); if (tails && H && H.tr.length > 1) { const pts = H.tr.map((x,i) => isNum(x)&&isNum(H.em[i]) ? `${X(x).toFixed(1)},${Y(H.em[i]).toFixed(1)}` : null).filter(Boolean); if (pts.length>1) g += `<polyline points="${pts.join(' ')}" fill="none" stroke="${col(r)}" stroke-width="1.2" opacity=".45"/>`; } });
    rows.forEach(r => { const rad = r.agg ? 6 + Math.min(16, Math.sqrt(r.n)*2.2) : 5 + 9*Math.max(r.buy,r.sell)/100; g += `<g class="pt" data-t="${esc(r.t)}"><circle cx="${X(r.trail)}" cy="${Y(r.emerg)}" r="${rad}" fill="${col(r)}" fill-opacity=".8" stroke="${r.watch?C.accent:'#0d1117'}" stroke-width="${r.watch?2:1}"/>${labels?`<text x="${X(r.trail)}" y="${Y(r.emerg)-rad-3}" font-size="10" fill="${C.text}" text-anchor="middle">${esc(r.agg ? r.name : r.t)}</text>`:''}</g>`; });
    document.getElementById('rot-plot').innerHTML = `<svg viewBox="0 0 ${w} ${h}">${g}</svg>`;
    document.querySelectorAll('#rot-plot .pt').forEach(el => { const AG = rows.find(x => x.agg && x.t === el.dataset.t); if (AG) { el.onclick = () => themeGo(AG.theme || AG.name, AG.theme ? AG.name : null); el.onmousemove = e => showTip(e, `<b>${esc(AG.name)}</b>${AG.theme ? '<br>' + esc(AG.theme) : ''}<br>Score ${f(AG.score,0)} (${f(AG.d5,1,true)} 5d) · ${AG.n} names · ${AG.regime}<br>Trailing ${f(AG.trail)} · Emerging ${f(AG.emerg)}<br>Favorable ${AG.buy} · Unfavorable ${AG.sell} · Conflicted ${AG.exit} · Net Signals ${f(AG.bias,1,true)}`); el.onmouseleave = hideTip; return; } const r = BY[el.dataset.t]; el.onclick = () => openDrawer(r.t); el.onmousemove = e => showTip(e, `<b>${r.t}</b> ${OM_NAME[r.rec]||r.rec} · ${r.regime}${coName(r.t) ? '<br>' + esc(coName(r.t)) : ''}${GNAME[r.t] ? '<br>' + esc(GNAME[r.t]) : ''}<br>Trailing ${f(r.trail)} · Emerging ${f(r.emerg)}<br>POS ${fi(r.buy)} · NEG ${fi(r.sell)} · RSI ${f(r.rsi)}<br>${fp(r.close)} (${f(r.ret1,2,true)}%)`); el.onmouseleave = hideTip; });
  };
  document.querySelectorAll('#rot-tb button').forEach(b => b.onclick = () => { document.querySelectorAll('#rot-tb button').forEach(x => x.classList.remove('on')); b.classList.add('on'); document.getElementById('rot-theme').value = ''; filt = b.dataset.f; draw(); });
  document.getElementById('rot-theme').onchange = e => { if (!e.target.value) return; document.querySelectorAll('#rot-tb button').forEach(x => x.classList.remove('on')); filt = 'theme:' + e.target.value; draw(); };
  document.getElementById('rot-tails').onchange = draw; document.getElementById('rot-labels').onchange = draw;
  draw();
}

function renderScorecard() {
  const S = P.scorecard;
  const cellR = (v, inv=false) => `<td class="${signCls(inv ? -v : v)}">${f(v,2,true)}%</td>`;
  const rng = (x, inv=false) => !isNum(x.lo) ? '<td class="mu" title="Needs at least 5 distinct dates">—</td>' : `<td class="${x.lo > 0 ? (inv ? 'b' : 'g') : x.hi < 0 ? (inv ? 'g' : 'b') : 'mu'}" title="${x.lo > 0 || x.hi < 0 ? 'The range does not include zero' : 'The range includes zero: not distinguishable from no effect'}">${f(x.lo,1,true)} to ${f(x.hi,1,true)}%</td>`;
  const PASSX = (S.gates || []).find(x => x.kind === 'pass' && x.n && isNum(x.excess));
  const sum = S.summary.map(x => { const inv = x.side === 'SELL'; const hitGood = inv ? x.hit <= 45 : x.hit >= 55, hitBad = inv ? x.hit >= 55 : x.hit < 45;
    return x.n ? `<tr><td class="left">${badge(x.side)}</td><td>${x.h}d</td><td>${x.n}</td><td class="${hitGood?'g':hitBad?'b':''}">${f(x.hit,0)}%</td>${cellR(x.mean,inv)}${cellR(x.median,inv)}${cellR(x.excess,inv)}<td>${f(x.hit_x,0)}%</td><td class="mu">${f(x.base.mean,2,true)}%</td>${cellR(x.mean-x.base.mean,inv)}<td>${fi(x.nd)}</td>${rng(x,inv)}</tr>` : `<tr><td class="left">${badge(x.side)}</td><td>${x.h}d</td><td>0</td><td colspan="9" class="mu">no events</td></tr>`; }).join('');
  // v54: by-date range, gate attribution, calibration, trend trades, snapshot (out-of-sample) record
  const hm = S.h_main || 10;
  const gateRows = (S.gates || []).map(x => { const lab = x.kind === 'only' ? `<span class="muted" style="padding-left:1rem">${esc(x.gate)}</span>` : x.kind === 'pass' ? `<b class="good">${esc(x.gate)}</b>` : `<b>${esc(x.gate)}</b>`;
    return x.n ? `<tr><td class="left">${lab}</td><td>${x.n}</td><td>${fi(x.nd)}</td><td>${f(x.hit,0)}%</td>${cellR(x.mean)}${cellR(x.excess)}${rng(x)}<td class="left" style="white-space:normal">${x.kind === 'pass' || !isNum(x.excess) || !PASSX ? '' : x.excess < PASSX.excess ? '<span class="good">gate helped: the blocked names did worse</span>' : '<span class="warn">gate cost return: the blocked names did better</span>'}</td></tr>` : `<tr><td class="left">${lab}</td><td>0</td><td colspan="6" class="mu">no events</td></tr>`; }).join('');
  const calRows = side => (S.calib || []).filter(x => x.side === side).map(x => { const inv = side === 'SELL'; return x.n ? `<tr><td class="left">${x.b_lo}–${x.b_hi}</td><td>${x.n}</td><td>${fi(x.nd)}</td><td>${f(x.hit,0)}%</td>${cellR(x.mean,inv)}${cellR(x.excess,inv)}${rng(x,inv)}</tr>` : `<tr><td class="left">${x.b_lo}–${x.b_hi}</td><td>0</td><td colspan="5" class="mu">no bars</td></tr>`; }).join('');
  const TR = S.trend || {n:0};
  const SN = S.snapshots || {ok:false, rows:[], note:'not run'};
  const snapRows = (SN.rows || []).map(x => { const inv = x.side === 'SELL'; return x.n ? `<tr><td class="left">${badge(x.side)}</td><td>${x.h}d</td><td>${x.n}</td><td>${fi(x.nd)}</td><td>${f(x.hit,0)}%</td>${cellR(x.mean,inv)}${cellR(x.median,inv)}${cellR(x.excess,inv)}<td>${f(x.hit_x,0)}%</td></tr>` : `<tr><td class="left">${badge(x.side)}</td><td>${x.h}d</td><td>0</td><td colspan="6" class="mu">no scoreable events yet</td></tr>`; }).join('');
  const reg = S.by_regime.map(x => `<tr><td class="left" style="color:${regColor(x.regime)}">${x.regime}</td><td>${x.n||0}</td><td>${x.n?f(x.hit,0)+'%':'—'}</td>${x.n?cellR(x.mean):'<td>—</td>'}${x.n?cellR(x.excess):'<td>—</td>'}</tr>`).join('');
  const tt = S.by_ticker;
  const tkRow = x => `<tr data-t="${x.ticker}"><td class="left">${tk(x.ticker)}</td><td>${x.n}</td><td>${f(x.hit,0)}%</td>${cellR(x.mean)}</tr>`;
  document.getElementById('scorecard').innerHTML = `<h2>Signal Scorecard <span class="muted" style="font-weight:400;font-size:.85rem">${S.from} → ${S.to} · ${S.events.BUY} Favorable / ${S.events.SELL} Unfavorable events</span></h2>
    <div class="warnbox">This is an <b>in-sample sanity check</b>, not a backtest: today's model is re-run over the last ~${S.n_bars} sessions of each ticker, ${UNI ? 'the universe is today\'s list (names that were dropped or delisted are missing)' : 'the percentile anchor uses the full benchmark history'}, and there are no costs, slippage or position sizing. Use it to see whether the signals carry information and which horizon they favour — not as a return expectation. "Event" = the first bar Signal becomes Favorable/Unfavorable. Base = all bars with complete data. Excess = minus ${CFG.benchmark} over the same window.</div>
    <div class="card"><h3>Forward returns after new signals</h3><table><thead><tr><th class="left">Signal</th><th>Horizon</th><th>N</th><th>Hit rate</th><th>Mean</th><th>Median</th><th>Excess vs ${CFG.benchmark}</th><th>Excess hit</th><th>Base mean</th><th>Edge vs base</th><th title="Distinct dates the events fall on">Dates</th><th title="95% range of the excess return, from the spread of the per-date averages">95% range (excess)</th></tr></thead><tbody>${sum}</tbody></table>
    <p class="note">For Unfavorable events a <b>negative</b> mean forward return is what you want (the exit avoided a decline). Hit rate for Unfavorable counts positive returns, so &lt; 50% is good there. <b>Dates</b> is the number of distinct days the events fall on: signals cluster, so 200 events on 12 days is closer to 12 observations than 200. The <b>95% range</b> is built from those per-date averages; a range that includes zero (grey) cannot be told apart from no effect. Overlapping forward windows still make it somewhat too narrow.</p></div>
    <div class="card"><h3>Do the gates earn their keep? <span class="muted">${hm}-day forward return of Favorable ratings that passed, and of those each gate blocked</span></h3>
      <div class="twrap" style="max-height:none"><table><thead><tr><th class="left">Group</th><th>N</th><th>Dates</th><th>Hit rate</th><th>Mean</th><th>Excess vs ${CFG.benchmark}</th><th>95% range (excess)</th><th class="left">Reading</th></tr></thead><tbody>${gateRows}</tbody></table></div>
      <p class="note">A blocked event is the first bar a name cleared everything else but a gate turned it back to Neutral. A gate is doing its job when the names it blocked went on to do <b>worse</b> than the ones that passed. “… only” rows are names stopped by that gate alone, which isolates its effect. Small N and wide ranges mean no verdict yet.</p></div>
    <div class="grid g2">
      <div class="card"><h3>Does a higher POS score pay? <span class="muted">${hm}-day forward return by score bucket, all bars</span></h3><table><thead><tr><th class="left">POS score</th><th>Bars</th><th>Dates</th><th>Hit</th><th>Mean</th><th>Excess</th><th>95% range</th></tr></thead><tbody>${calRows('BUY')}</tbody></table>
        <p class="note">If the score carries information, mean and excess should rise from the top row to the bottom row.</p></div>
      <div class="card"><h3>Does a higher NEG score warn? <span class="muted">${hm}-day forward return by score bucket, all bars</span></h3><table><thead><tr><th class="left">NEG score</th><th>Bars</th><th>Dates</th><th>Hit</th><th>Mean</th><th>Excess</th><th>95% range</th></tr></thead><tbody>${calRows('SELL')}</tbody></table>
        <p class="note">Here the returns should <b>fall</b> from the top row to the bottom row (green = lower returns after higher NEG scores).</p></div>
    </div>
    ${CFG.trend_on ? `<div class="card"><h3>Trend trades <span class="muted">Favorable alert → close under the ${TR.mult ?? CFG.stop_mult} × ATR trailing stop, or an Unfavorable / Conflicted alert</span></h3>
      ${TR.n ? `<div class="grid" style="grid-template-columns:repeat(auto-fit,minmax(140px,1fr))">${mhTile('Closed trades', TR.n)}${mhTile('Winners', f(TR.win,0) + '%', TR.win >= 50 ? 'good' : '')}${mhTile('Mean / median', f(TR.mean,1,true) + '% / ' + f(TR.median,1,true) + '%', TR.mean > 0 ? 'good' : 'bad')}${mhTile('Avg win / avg loss', f(TR.avg_win,1,true) + '% / ' + f(TR.avg_loss,1,true) + '%')}${mhTile('Avg sessions held', f(TR.days,0))}${mhTile('Closed by stop / signal', TR.stop + ' / ' + TR.signal)}${mhTile('Open now', TR.open + (isNum(TR.open_mean) ? ' · avg ' + f(TR.open_mean,1,true) + '%' : ''))}</div>` : `<div class="empty">No closed trend trades in the window${TR.open ? ' (' + TR.open + ' open)' : ''}.</div>`}
      <p class="note">Entry and exit at the close of the signal bar, no costs, in-sample. This is the record of the <b>In Trend</b> column, not of Signal itself.</p></div>` : ''}
    <div class="card"><h3>Out-of-sample record from your dated snapshots ${SN.ok ? `<span class="muted">${SN.from} → ${SN.to} · ${SN.n_used} snapshot days · ${SN.events.BUY} Favorable / ${SN.events.SELL} Unfavorable</span>` : ''}</h3>
      ${SN.ok ? `<table><thead><tr><th class="left">Signal</th><th>Horizon</th><th>N</th><th>Dates</th><th>Hit rate</th><th>Mean</th><th>Median</th><th>Excess vs ${CFG.benchmark}</th><th>Excess hit</th></tr></thead><tbody>${snapRows}</tbody></table>
      <p class="note">Unlike everything above, these are the signals the program <b>actually published</b> on each day (read from the Results_YYYY-MM-DD.csv snapshots), so there is no hindsight in them. They were produced by whichever version and settings were live at the time, so this is the record of the system as you ran it, not of v${P.version.replace('v','')} alone. An event is a ticker that was Favorable / Unfavorable in a snapshot and was not in the snapshot before it; a gap between runs can make a signal look newer than it was. Forward returns use today's adjusted closes.</p>` : `<div class="empty">Not available: ${esc(SN.note || 'no snapshots')}.</div>`}</div>
    <div class="grid g3"><div class="card"><h3>Favorable events by Trailing/Emerging Momentum (10d)</h3><table><thead><tr><th class="left">Trailing/Emerging Momentum</th><th>N</th><th>Hit</th><th>Mean</th><th>Excess</th></tr></thead><tbody>${reg}</tbody></table></div>
    <div class="card"><h3>Best Favorable tickers (10d, ≥3 events)</h3><table><thead><tr><th class="left">Ticker</th><th>N</th><th>Hit</th><th>Mean</th></tr></thead><tbody>${tt.slice(0,10).map(tkRow).join('') || '<tr><td colspan="4" class="mu">—</td></tr>'}</tbody></table></div>
    <div class="card"><h3>Worst Favorable tickers (10d, ≥3 events)</h3><table><thead><tr><th class="left">Ticker</th><th>N</th><th>Hit</th><th>Mean</th></tr></thead><tbody>${tt.slice(-10).reverse().map(tkRow).join('') || '<tr><td colspan="4" class="mu">—</td></tr>'}</tbody></table></div></div>`;
  document.querySelectorAll('#scorecard tbody tr[data-t]').forEach(tr => tr.onclick = () => openDrawer(tr.dataset.t));
}

function renderHealth() {
  const H = P.health, T = H.timings || {};
  const list = (title, items, fmt) => `<div class="card"><h3>${title} <span class="muted">(${items.length})</span></h3>${items.length ? `<ul class="plain">${items.map(fmt).join('')}</ul>` : '<div class="empty">None</div>'}</div>`;
  const issues = H.skipped.length + H.stale.length + H.notes.length;
  document.getElementById('health').innerHTML = `<h2>Data Health</h2>
    ${issues ? `<div class="warnbox">${issues} item(s) need attention — see below.</div>` : `<div class="okbox">All ${H.loaded} tickers loaded cleanly.</div>`}
    <div class="grid g2"><div class="card"><h3>Run</h3><div class="kv">${dl('Generated', esc(P.run_ts))}${dl('Session (as-of)', P.as_of)}${dl('Data source', esc(H.source))}${dl('Universe', `${H.loaded} loaded / ${H.universe} configured`)}${dl('Benchmark', esc(H.benchmark))}${dl('Anchored components', (H.dist_components||[]).join(', ') || '—')}${dl('Download', (T.download_s??'—')+' s')}${dl('Compute', (T.compute_s??'—')+' s')}${dl('Total', (T.total_s??'—')+' s')}</div></div>
    <div class="card"><h3>Output</h3><div class="kv">${dl('Dashboard', esc(H.paths.html||'—'))}${dl('Results CSV', esc(H.paths.csv||'—'))}${dl('Snapshots', esc(H.paths.snapshots||'—'))}</div>${(H.paths.notes||[]).map(n => `<div class="warnbox" style="margin-top:.5rem">${esc(n)}</div>`).join('')}</div></div>
    ${H.notes.length ? `<div class="card"><h3>Notes & config warnings</h3><ul class="plain">${H.notes.map(n => `<li>${esc(n)}</li>`).join('')}</ul></div>` : ''}
    <div class="grid g2">
      ${list('Skipped (not loaded)', H.skipped, s => `<li><b>${s.ticker}</b> — ${esc(s.reason)}</li>`)}
      ${list('Stale (last bar older than as-of)', H.stale, s => `<li><b class="tkl" data-t="${s.ticker}">${s.ticker}</b> — last bar ${s.last_bar} (session ${s.as_of}). Alerts still computed; treat with caution.</li>`)}
      ${list(`Short history (&lt; ${CFG.min_bars} bars → alerts disabled)`, H.short, s => `<li><b class="tkl" data-t="${s.ticker}">${s.ticker}</b> — ${s.bars} bars</li>`)}
      ${list(`Below liquidity floor ($${(CFG.min_dv/1e6).toFixed(0)}M / $${CFG.min_price})`, H.illiquid, s => `<li><b class="tkl" data-t="${s.ticker}">${s.ticker}</b> — $${fdv(s.dollar_vol)} 20d median · ${fp(s.price)}</li>`)}
    </div>
    ${H.themes_loaded === false ? `<div class="warnbox">The Theme file could not be read, so Theme / Sub-Theme are not shown and the missing-ticker list cannot be built. Check the path in Config.themes_csv.</div>` : `<div class="card"><h3>Tickers not found in the Theme file <span class="muted">(${(H.no_theme||[]).length})</span></h3>${(H.no_theme||[]).length ? `<div style="display:flex;flex-wrap:wrap;gap:.35rem;margin-top:.3rem">${H.no_theme.map(t => `<span class="chip tkl" data-t="${t}" style="cursor:pointer;font-size:.8rem">${t}</span>`).join('')}</div><div class="note">These show no Theme. Add them to Input_Ticker_List_by_Theme.csv to fill the gap (index funds such as SPY are expected to be listed here; Sector, Six Pack, Country and other ETFs are not listed).</div>` : '<div class="empty">Every ticker has a theme</div>'}</div>`}
    ${(H.gate_blocked||[]).length ? `<div class="card"><h3>Favorable ratings held back by a gate <span class="muted">(${H.gate_blocked.length})</span></h3><div class="twrap" style="max-height:340px"><table><thead><tr><th class="left">Ticker</th><th>POS</th><th>NEG</th><th class="left">Trailing/Emerging Momentum</th><th class="left">Blocked by</th></tr></thead><tbody>${H.gate_blocked.map(g => `<tr data-t="${g.ticker}"><td class="left">${tk(g.ticker)}</td><td>${g.buy}</td><td>${g.sell}</td><td class="left" style="color:${regColor(g.regime)}">${g.regime}</td><td class="left warn">${esc(g.reason)}</td></tr>`).join('')}</tbody></table></div><div class="note">POS Signals cleared the threshold but Signal stayed Neutral. Click a ticker for its detail; Guide → Gates explains each reason.</div></div>` : ''}
    ${H.live_bars && H.live_bars.length ? `<div class="card"><h3>Live intraday price <span class="muted">(${H.live_bars.length})</span></h3><div class="note">Market open — using the current price (today's still-forming bar) for: ${H.live_bars.join(', ')}. These will finalize at the close.</div></div>` : ''}
    ${H.partial_dropped.length ? `<div class="card"><h3>Partial bars dropped</h3><div class="note">${H.partial_dropped.join(', ')}</div></div>` : ''}`;
}

function renderGuide() {
  document.getElementById('guide').innerHTML = `<h2>Interpretation Guide</h2>
  <p class="note" style="margin:0 0 .75rem">While the market is open, tickers marked <span class="badge LIVE">LIVE</span> (●) are scored on the current intraday price — today's bar is still forming, so RSI, PPO, EMAs and the POS/NEG Signals will keep moving until the close. Pass --eod-only to score only confirmed closes instead.</p>
  <div class="grid g2">
  <div class="card"><h3>Signal</h3><ul class="plain">
    <li><b>Signal</b> replaces the former Buy / Hold / Sell / Exit / Watch labels. It is a relabelling of the same alert logic: no score, threshold or gate changed.</li>
    <li><b>Favorable</b> (was BUY) — fresh PPO signal-line ↑ (histogram still positive) plus buy score ≥ the regime threshold, volume/range confirmed. RSI Extreme caps the POS Signals score one point below the regime threshold.</li>
    <li><b>Unfavorable</b> (was SELL) — fresh PPO signal-line ↓ plus sell score ≥ the regime threshold. A lone bearish cross still floors at ${CFG.sell_floor} (review); expanding red hist or a zero-line ↓ is what should push it through.</li>
    <li><b>Neutral, conflicted</b> (was EXIT, amber badge) — a fresh ↑ and a fresh ↓ cross both fall inside the ${CFG.fresh_bars}-bar window, both scores clear their thresholds and are within ${CFG.conflict_margin} points: a whipsaw, so de-risk.</li>
    <li><b>Watch Favorable / Watch Unfavorable</b> (was Watch BUY / SELL) — the buy (or sell) score is close to its trigger without a fresh cross, <b>or a Favorable that a gate blocked</b> (shown in the Blocked by column; see Gates below).</li>
    <li><b>Neutral</b> (was HOLD) — neither side dominates.</li>
    ${CFG.trend_on ? `<li><b>In Trend</b> (its own column, new in v54) — Signal is an <i>event</i>: Favorable needs a cross within ${CFG.fresh_bars} bars, so it lapses to Neutral within days even when the move continues. In Trend carries the state forward: it opens on the Favorable alert and stays open until an Unfavorable / Conflicted alert or a close under the trailing stop (highest close − ${CFG.stop_mult} × ATR since entry; it never moves down). The column shows sessions and return since entry; <b>Stop</b> shows the stop and its distance. It does not change Signal.</li>
    <li><b>Suggested size</b> (Ticker page and drawer) — ${CFG.risk_pct}% of the portfolio at risk ÷ the stop distance (${CFG.stop_mult} × ATR%), capped at ${CFG.max_pos}%. A calm name gets a larger size than a volatile one for the same risk. Change <code>risk_per_trade_pct</code> / <code>max_position_pct</code> to suit.</li>` : ''}</ul>
  <h3 style="margin-top:.75rem">How the scores are built</h3><ul class="plain">
    <li><b>PPO is the trigger; everything else is context.</b> An alert needs a fresh PPO signal-line cross — the other components size the confidence but cannot create an alert alone.</li>
    <li>Full component-by-component weightings, regime weights, thresholds and gates are in <b>POS &amp; NEG Signals</b> below.</li>
    <li>Alerts use the last <b>confirmed</b> close even when the dashboard shows the live bar. Percentiles are ${UNI ? 'a rank across the names loaded on the same bar (no look-ahead)' : 'causal vs ' + CFG.benchmark + ' history before that bar'}.</li></ul></div>
  <div class="card"><h3>Trailing/Emerging Momentum (formerly Regime)</h3><ul class="plain">
    ${UNI ? `<li><b>What the percentiles mean (v54).</b> Each input is ranked across every name loaded on the same date, so 80 means “stronger than 80% of the list today”. ${CFG.vol_adj ? 'Returns are first divided by the name\'s own volatility (and the PPO histogram by its ATR%), so a volatile stock is not Strong or Weak just because it moves more.' : ''} Before v54 the yardstick was ${CFG.benchmark}'s own history. Because the rank is relative, about half the list is always above 50: in a falling market “Strong” means holding up best, not rising. The EMA200 gate and the Market gate supply the absolute test. Dates with fewer than ${CFG.xs_min} names, and the Currency group, still use the older anchor. <b>RS Rating</b> is the blended percentile as a whole number, 1–99.</li>` : ''}
    <li><b>Strong</b> — both ≥ ${CFG.regime_hi}: trend plus acceleration.</li>
    <li><b>Dormant→Waking</b> — emerging leads trailing by 10+: coiled, early.</li>
    <li><b>Mature/Cooling</b> — trailing leads emerging by 10+: strong on paper, losing thrust.</li>
    <li><b>Weak</b> — both &lt; ${CFG.regime_lo}.</li>
    <li><b>Neutral</b> — everything else.</li></ul>
  <h3 style="margin-top:.75rem">Squeeze pillars</h3><ul class="plain">
    <li><b>Foundation</b> — compression length + a recent release.</li>
    <li><b>Momentum</b> — PPO histogram rising + DMI above floor.</li>
    <li><b>Condition</b> — healthy RSI + room below the 52-week high.</li>
    <li><b>Confirmation</b> — positive OBV slope + non-extreme momentum.</li></ul>
  <h3 style="margin-top:.75rem">PMO (Ticker tab)</h3><ul class="plain">
    <li>Carl Swenlin's Price Momentum Oscillator, drawn for reference only — it is <b>not</b> part of any score, alert or recommendation.</li>
    <li>Sectors and the Six Pack have their own buttons on the Rotation tab and are not mixed into its other views.</li></ul>
  <h3 style="margin-top:.75rem">Daily workflow</h3><ol class="plain">
    <li><b>Changes</b> first — what flipped since yesterday and why.</li>
    <li><b>Market Health</b> — the backdrop: how the S&amp;P, equal-weight and Nasdaq are doing, how many of your stocks are above their averages, and the SPY / QQQ / RSP cards.</li>
    <li><b>Signals → Watch</b> and <b>Fresh cross</b> — set-ups for tomorrow.</li>
    <li><b>Ticker</b> — the full page for one name: charts with signal markers, why it scores what it scores, how it ranks against the universe, and how its past signals worked out. <kbd>Shift</kbd>+<kbd>Enter</kbd> in the search box opens it directly.</li>
    <li>Squeeze Full + Favorable = strongest long set-up; Dormant→Waking with a fresh ↑ = earliest.</li>
    <li>Check <b>Health</b> whenever a name looks odd — stale bars and short histories are listed there.</li></ol>
  <p class="note">Keyboard: <kbd>/</kbd> jump to ticker · <kbd>Esc</kbd> close drawer · <kbd>1</kbd>–<kbd>9</kbd> switch tabs.</p></div></div>
  ${scoreGuide()}${gateGuide()}${currencyGuide()}${themeGuide()}${themeSignalGuide()}`;
}

function scoreGuide() {
  const fx = (v, d=2) => isNum(v) ? (+v).toFixed(d).replace(/\.?0+$/, '') : '—';
  const RW = (tbl, reg, k) => (tbl && tbl[reg]) ? tbl[reg][k] : null;
  const regRows = REGIMES.map(g => {
    const bw = CFG.buy_rw?.[g] || [], sw = CFG.sell_rw?.[g] || [];
    const spEff = Math.max(sw[0] ?? 0, CFG.sell_wfloor ?? 0);
    const cell = v => `<td>${fx(v)}</td>`;
    return `<tr><td class="left" style="color:${regColor(g)}">${g}</td>${cell(bw[0])}${cell(bw[1])}${cell(bw[2])}<td class="mu">|</td>${cell(sw[0])}<td>${fx(spEff)}</td>${cell(sw[1])}${cell(sw[2])}<td class="mu">|</td><td class="g">${CFG.buy_thr_reg?.[g] ?? CFG.buy_thr}</td><td class="b">${CFG.sell_thr_reg?.[g] ?? CFG.sell_thr}</td></tr>`;
  }).join('');
  const T = (head, rows) => `<div class="twrap" style="max-height:none"><table><thead><tr>${head}</tr></thead><tbody>${rows}</tbody></table></div>`;
  const tr = (a, b, c, d) => `<tr><td class="left"><b>${a}</b></td><td>${b}</td><td class="left" style="white-space:normal">${c}</td>${d !== undefined ? `<td class="left" style="white-space:normal">${d}</td>` : ''}</tr>`;
  const relLow = fx(CFG.min_rel);
  const buyRows =
    tr('PPO cross', '0–35', '<b>The trigger.</b> 18 × freshness (1.0 on the cross bar, falling 0.2 per bar to 0 after 5 bars) <b>+ 8</b> if the histogram is positive and still rising (× max(freshness, 0.4)) <b>+ 9</b> for a zero-line cross ↑ within ' + CFG.fresh_bars + ' bars, or <b>+ 4</b> if PPO is already above zero. That sum is multiplied by (1 + 0.5 × cross strength), the regime PPO weight and volatility reliability, then capped at 35.') +
    tr('RSI', '0–18', 'Location, not a second oscillator. Adds (zone multiplier − 1) × max(PPO points, 12) plus a zone bonus of <b>6</b> Oversold, <b>4</b> Weak or <b>2</b> Healthy (bonus × regime RSI weight × reliability); negative results are clipped to 0. Zone multipliers: Oversold 1.15 · Weak 1.15 · Healthy 1.00 · Overheated 0.70 · Extreme 0.00. Overheated and Extreme therefore add nothing, and Extreme also caps the POS Signals score one point below the regime threshold.') +
    tr('EMA', '0–12', '12 × (number of EMA20/50/200 the close is above ÷ 3) × regime EMA weight. Halved if the PPO histogram is negative. Cut to 35% when below EMA200 (kept only in Dormant→Waking with a squeeze release and room to run). Cut to 60% when within 3% of the 52-week high with no squeeze release.') +
    tr('Persistence', '0–8', '8 × trend persistence (lag-1 return autocorrelation over ' + CFG.persist_win + ' sessions, floored at 0) × reliability. Only counts when momentum direction or the PPO histogram is rising.') +
    tr('Squeeze', '0–' + CFG.sqz_buy_cap, 'Small add-on: <b>+6</b> recent squeeze release, <b>+3</b> PPO turning up, <b>+3</b> room below the 52-week high, capped at ' + CFG.sqz_buy_cap + '. Cannot create an alert on its own.');
  const sellRows =
    tr('PPO cross', '0–35', '<b>The trigger.</b> 18 × freshness of the bearish cross <b>+ 8</b> if the histogram is negative and still falling <b>+ 9</b> for a zero-line cross ↓ within ' + CFG.fresh_bars + ' bars, or <b>+ 4</b> if PPO is already below zero (0 if above). Multiplied by (1 + 0.5 × cross strength), the regime PPO weight (never below ' + fx(CFG.sell_wfloor) + ') and ' + (CFG.symmetric ? 'the same volatility discount as the buy side, 1 − ' + fx(CFG.vol_damp) : 'a <i>lighter</i> volatility discount, 1 − ' + fx(CFG.sell_damp)) + ' × (1 − reliability). Capped at 35.') +
    tr('RSI', '0–18', 'Only overbought conditions add to a sell. Adds (zone multiplier − 1) × max(PPO points, 12) plus a bonus of <b>8</b> Extreme or <b>5</b> Overheated (bonus × regime RSI weight × reliability). Multipliers: Extreme 1.15 · Overheated 1.15 · Healthy 1.00 · Weak 0.85 · Oversold 0.65, dropping to 0.40 if an Oversold name is still above EMA50. Weak and Oversold therefore add nothing — a washed-out stock is not treated as a quality sell.') +
    tr('EMA', '0–12', '12 × (number of EMA20/50/200 the close is below ÷ 3) × regime EMA weight. Halved if the PPO histogram is positive.') +
    tr('Weakness', '0–8', '8 × trend persistence (floored at 0) × reliability, only when momentum direction or the PPO histogram is falling.') +
    tr('Squeeze (failed)', '0 or ' + CFG.sqz_sell_cap, 'Adds ' + CFG.sqz_sell_cap + ' when a squeeze is on with negative squeeze momentum, or has just released with a falling PPO histogram and negative momentum.');
  const head3 = '<th class="left">Component</th><th>Points</th><th class="left">How it is calculated</th>';
  return `<div class="card" style="margin-top:1rem">
    <h2 style="margin-bottom:.4rem">POS &amp; NEG Signals — how the 0–100 confidence is built</h2>
    <p class="note" style="margin:0 0 .75rem">Each score is the <b>sum of its components in points</b>, capped at 100 (the realistic ceilings are about 83 for POS and 81 for NEG). They are scored independently: a name can have a high POS and a high NEG at once, which is what the Conflicted rule looks for. The bars on the action cards and the Ticker tab show exactly these components.</p>
    <h3>POS Signals</h3>${T(head3, buyRows)}
    <h3 style="margin-top:1rem">NEG Signals score</h3>${T(head3, sellRows)}
    <p class="note">${CFG.symmetric ? `<b>Floors (both sides, v54).</b> A fresh bullish cross that is still in force guarantees a POS score of at least ${CFG.buy_floor}, exactly as a fresh bearish cross guarantees a NEG score of at least ${CFG.sell_floor}. Both floors sit below every alert threshold. Before v54 only the NEG side had one, which tilted Net Signals negative. ` : ''}<b>NEG floor.</b> A fresh bearish signal-line cross${CFG.symmetric ? ' that is still in force' : ''} guarantees a NEG Signals score of at least ${CFG.sell_floor} (shown with a ° and “floor applied”). The floor sits below the alert threshold, so the cross alone means “review”; one confirming factor — usually an expanding red histogram, a zero-line cross ↓, or the close below an EMA — tips it into Unfavorable.</p>

    <h3 style="margin-top:1rem">Weightings by regime</h3>
    <p class="note" style="margin:0 0 .5rem">Regime weights multiply the PPO, RSI and EMA components (1.00 = no change). Alert thresholds are also regime-specific: it is easier to buy in Strong and Dormant→Waking regimes and harder in Mature/Cooling and Weak ones, and the reverse for selling.</p>
    ${T('<th class="left" rowspan="2">Trailing/Emerging Momentum</th><th colspan="3">POS weights</th><th></th><th colspan="4">NEG weights</th><th></th><th colspan="2">Alert threshold (POS Signals / NEG Signals)</th>',
        '<tr class="mu"><td class="left"></td><td>PPO</td><td>RSI</td><td>EMA</td><td></td><td>PPO (raw)</td><td>PPO (used)</td><td>RSI</td><td>EMA</td><td></td><td>POS ≥</td><td>NEG ≥</td></tr>' + regRows)}
    <p class="note">NEG “PPO (used)” applies the ${fx(CFG.sell_wfloor)} floor on the sell PPO weight so a strong trend cannot fully mute a genuine bearish cross. Thresholds rise by <b>${CFG.atr_extra}</b> points when the name’s ATR exceeds ${fx(CFG.atr_cap,1)}% of price, because very volatile names produce noisier crosses.</p>

    <h3 style="margin-top:1rem">Volatility reliability</h3>
    <p class="note" style="margin:0 0 .5rem">Reliability = 1 − (1 − ${relLow}) × min(20-day annualised volatility ÷ 100%, 1), so it runs from 1.00 for a calm name down to ${relLow} for anything at 100% volatility or more. ${CFG.symmetric ? `<b>From v54 one discount is used on both sides:</b> every reliability-scaled component (PPO, RSI bonus, persistence / weakness) is multiplied by 1 − ${fx(CFG.vol_damp)} × (1 − reliability), so the most volatile names keep ${fx(1 - CFG.vol_damp * (1 - CFG.min_rel))} of their points on POS and NEG alike. Before v54 the buy side took the full discount and the sell-side PPO points a much lighter one, so volatile names leaned negative on Net Signals by construction.` : 'It scales the PPO, RSI bonus and persistence points on the buy side. On the sell side the PPO points use the gentler discount above, so high-volatility names are damped but never silenced.'}</p>

    <h3 style="margin-top:1rem">What an alert must pass</h3>
    <ol class="plain">
      <li><b>Score ≥ the regime threshold</b> (table above, plus the ATR adjustment).</li>
      <li><b>A fresh PPO cross</b> in the same direction within ${CFG.fresh_bars} bars, still in force (histogram on the same side of zero)${CFG.require_cross ? '' : ' (currently switched off in the config)'}.</li>
      <li><b>Complete data:</b> at least ${CFG.min_bars} bars of history and no missing core indicators.</li>
      <li><b>Liquidity:</b> 20-day median dollar volume of at least $${(CFG.min_dv/1e6).toFixed(0)}M.</li>
      <li><b>Bar confirmation:</b> the cross bar’s dollar volume is at least ${fx(CFG.vol_mult)}× its 20-day median, <i>or</i> it closed in the top third of its range (buy) / bottom third (sell).</li>
      <li><b>Conflicted override:</b> if both a POS and a NEG setup pass (fresh ↑ and ↓ crosses both in the window) and the scores are within ${CFG.conflict_margin} points, the call is Neutral (shown with a Conflicted badge); otherwise the side matching the current histogram direction wins.</li>
    </ol>
    <p class="note">A name that scores within ${CFG.watch_margin} points of its threshold but fails a gate (no fresh cross, thin volume, high ATR) is listed as <b>Watch</b>, not as an alert.</p>
  </div>`;
}



function gateGuide() {
  const on = v => v ? '<span class="good">on</span>' : '<span class="bad">off</span>';
  const T = (head, rows) => `<div class="twrap" style="max-height:none"><table><thead><tr>${head}</tr></thead><tbody>${rows}</tbody></table></div>`;
  const row = (a, b, c, d) => `<tr><td class="left"><b>${a}</b></td><td class="left" style="white-space:normal">${b}</td><td class="left" style="white-space:normal">${c}</td><td class="left" style="white-space:normal">${d}</td></tr>`;
  const post =
    row('SPY regime', CFG.gate_mode === 'breadth' ? `The <b>Market gate</b> is closed (see the card on Market Health): ${CFG.benchmark}${CFG.regime_both ? ' and ' + CFG.regime_confirm + ' both close' : ' closes'} under the 200-day EMA, <b>or</b> fewer than ${CFG.gate200}% of your stocks are above their 200-day EMA and fewer than ${CFG.gate50}% above their 50-day. (Before v54 this read ${CFG.benchmark}'s own momentum regime, which could close the gate in a steady uptrend.)` : CFG.regime_both ? `Both ${CFG.benchmark} and ${CFG.regime_confirm} (equal-weight S&amp;P) fail on the same bar: each is rated Unfavorable, or has a Weak or Mature/Cooling regime. If only one of the two fails, the gate stays open.` : `The benchmark (${CFG.benchmark}) is rated Unfavorable, or its regime is Weak or Mature/Cooling.`, 'Blocks every Favorable rating on the list, because buying into a broadly weak market has the poorest record. Country ETF and Currency funds are exempt.', `Switch: <code>spy_regime_gate</code> (${on(CFG.spy_gate)})`) +
    row('Relative strength', `The name's ${CFG.rs_lookback}-day return does not beat ${CFG.benchmark}'s by at least ${CFG.rs_min}% (excess return &lt; ${CFG.rs_min}).`, 'Blocks BUYs that are rising but lagging the market — you would rather own the leaders.', `Switch: <code>rs_gate</code> (${on(CFG.rs_gate)}) · bar: <code>rs_min_excess_for_buy</code>`) +
    row('Below EMA200', 'The close is under its 200-day EMA.', 'Blocks BUYs in a long-term downtrend, where PPO crosses are most often bear-market bounces.', `Switch: <code>require_above_ema200_for_buy</code> (${on(CFG.e200_gate)})`);
  const bar =
    row('No fresh cross', `The score is high enough but PPO has not crossed its signal line within the last ${CFG.fresh_bars} bars.`, 'The cross is the trigger; without one the name is a setup, not a signal.', `<code>ppo_fresh_bars</code> = ${CFG.fresh_bars} · <code>require_ppo_cross_for_alert</code>`) +
    row('Volume bar', `Neither condition holds: dollar volume ≥ ${(+CFG.vol_mult).toFixed(2)}× its 20-day median, or the close in the top third of the day's range.`, 'Wants evidence of real buying on the signal bar.', '<code>require_volume_confirm</code>, <code>vol_confirm_mult</code>') +
    row('Liquidity', `20-day median dollar volume is under $${(CFG.min_dv/1e6).toFixed(0)}M.`, 'Too thin to trade.', '<code>min_dollar_vol</code>') +
    row('Short data', `Fewer than ${CFG.min_bars} bars of history, or a core indicator is missing.`, 'The percentiles and EMA200 are not reliable yet.', '<code>min_bars</code>');
  const head = '<th class="left">Gate</th><th class="left">It blocks Favorable when…</th><th class="left">Why it exists</th><th class="left">Where to change it</th>';
  return `<div class="card" style="margin-top:1rem">
    <h2 style="margin-bottom:.4rem">Gates — why a high POS Signals score is not always Favorable</h2>
    <p class="note" style="margin:0 0 .75rem">Favorable needs more than a score above the threshold. After the score is calculated, a name has to pass a series of <b>gates</b>. If it fails one, Signal stays <b>Neutral</b>, but since v41 the name is also marked <b>Watch</b> and the reason is shown in the <b>Blocked by</b> column (Signals tab), in the W badge tooltip, on the Ticker page and on the Health tab. Several reasons can apply at once (shown joined with “+”).</p>
    <h3>Gates applied after the score (the usual reason a strong name shows Neutral)</h3>
    ${T(head, post)}
    <p class="note"><b>Exemption.</b> The three gates above all let through a name in the <b>Dormant→Waking</b> regime that also has a <b>full squeeze setup</b> (see Squeeze → Full). These are the earliest long set-ups and are deliberately not held to the trend and relative-strength tests. The benchmark itself is never gated. Currency-tab funds (see below) also skip the SPY regime and relative-strength gates, because neither says anything about the dollar; they still face the EMA200 gate. <b>Country ETFs</b> skip the SPY regime gate only (a country can trend independently of the US); they keep the relative-strength gate (is it beating the US?) and the EMA200 gate, and use a lower liquidity floor ($${((CFG.country_floor||0)/1e6).toFixed(1)}M).</p>
    <h3 style="margin-top:1rem">Requirements inside the score (checked before the gates above)</h3>
    ${T(head, bar)}
    <h3 style="margin-top:1rem">How to read a blocked name</h3>
    <ul class="plain">
      <li><b>Only “Relative strength” or “SPY regime”</b> — the stock itself looks fine (fresh cross, above EMA200) and is being held back by the market or by lagging ${CFG.benchmark}. These are the <b>Candidates</b> filter on the Signals tab: the likeliest names to graduate to Favorable if the market or the relative-strength picture improves.</li>
      <li><b>“Below EMA200”</b> — an early repair attempt inside a long-term downtrend. Treat with more caution; only the Dormant→Waking + full-squeeze exemption lets these through.</li>
      <li><b>“No fresh cross”</b> — nothing wrong; the trigger has not fired (or fired more than ${CFG.fresh_bars} bars ago).</li>
      <li><b>Several reasons</b> — the more gates a name fails, the less this is a timing problem and the more it is a quality problem.</li>
    </ul>
    <h3 style="margin-top:1rem">Unfavorable-side filter</h3>
    <p class="note" style="margin:0">Switch: <code>stronger_top_detection</code> (${on(CFG.top_filter)}). An Unfavorable rating is turned back into Neutral when the close is still above EMA50 and momentum direction is positive — a pullback inside an uptrend rather than a top. Unfavorable ratings have no “Blocked by” label.</p>
    <h3 style="margin-top:1rem">Live prices and alerts</h3>
    <p class="note" style="margin:0">${CFG.alerts_eod ? 'While the market is open, alerts are pinned to the last confirmed close (the POS/NEG Signals, RSI and PPO still move with the live bar). The gates are applied to that pinned recommendation as well.' : 'Alerts follow the live bar.'} Use the Health tab's <b>Favorable ratings held back by a gate</b> list for a ticker-by-ticker view.</p>
  </div>`;
}


function currencyGuide() {
  const cur = (CFG.currency || []).filter(x => x.kind === 'fx').map(x => `${x.t} (${esc(x.currency)})`).join(', ');
  const ref = (CFG.currency || []).find(x => x.kind === 'ref');
  const W = CFG.fx_w || {};
  const wtxt = Object.keys(W).map(t => `${t} ${W[t]}%`).join(' · ');
  return `<div class="card" style="margin-top:1rem"><h2 style="margin-bottom:.4rem">Currency tab — a view on the US dollar</h2>
    <p class="note" style="margin:0 0 .5rem">${cur}${ref ? ` — plus <b>${ref.t}</b>, the dollar itself, as a reference` : ''}. These funds hold the foreign currency, so their price rises when that currency strengthens and the dollar weakens. The tab is a portfolio-hedge tool: it is not a view on the stock market.</p>
    <ul class="plain">
      <li><b>Reading the signals.</b> Favorable on a currency fund = the currency is strengthening (<b>dollar weakening</b>). Unfavorable = <b>dollar strengthening</b>. For ${ref ? ref.t : 'the dollar fund'} it is the other way round. The <b>USD read</b> column spells this out.</li>
      <li><b>USD view.</b> The headline is the average Net Signals (POS − NEG) of the currency funds, weighted by approximate US Dollar Index weights (${wtxt}; AUD and MXN are not in the index and are left out of the weighted figure). A weighted Net Signals of +15 or more reads “dollar weakening”, −15 or less “dollar strengthening”, otherwise no clear trend. If ${ref ? ref.t : 'the dollar fund'} points the same way as the currency funds, the card says it disagrees. EUR is more than half of the index, so FXE dominates the reading.</li>
      <li><b>Hedge fit (ρ SPY).</b> The correlation of daily returns with ${CFG.benchmark} over the last ${CFG.fx_corr_win} sessions. <span class="good">Negative</span> means the fund tended to rise when stocks fell, which is what a hedge should do (yen and franc often); <span class="warn">positive</span> means it moves with equities (AUD, CAD and MXN often), so it would add to equity risk rather than hedge it. <b>ρ UUP</b> shows how closely it tracks the dollar. Correlations change, so check them before sizing a hedge.</li>
      <li><b>One bet, not eight.</b> All of these are largely the same trade (dollar weakness), so signals across the group usually agree. Disagreement between them points to a currency-specific story rather than a dollar move.</li>
    </ul>
    <h3 style="margin-top:.75rem">What is different from the other tabs</h3>
    <ul class="plain">
      <li><b>Own percentile base.</b> ${CFG.fx_anchor ? `Momentum percentiles are measured against the Currency group's own pooled history (not ${CFG.benchmark}'s). Currency funds move a fraction as much as stocks, so against ${CFG.benchmark} they would all sit near the middle and never reach Strong or Weak.` : `Percentiles are anchored to ${CFG.benchmark} like everything else (the group-anchor option is off in the config).`} Regimes and Mom % on this tab therefore mean “strong for a currency”, not “strong versus the S&amp;P 500”.</li>
      <li><b>Gates.</b> The SPY-regime and relative-strength-vs-${CFG.benchmark} gates do not apply. The below-EMA200 gate still does, so a Favorable rating on a currency in a long-term downtrend shows up as a blocked Favorable.</li>
      <li><b>Liquidity floor.</b> $${((CFG.fx_floor || 0)/1e6).toFixed(1)}M of 20-day median dollar volume for this group (other tabs use $${(CFG.min_dv/1e6).toFixed(0)}M), because several of these trusts trade thinly. Funds that cannot be loaded, or that no longer trade, are listed on the Health tab and shown as “no data”.</li>
      <li><b>Left out elsewhere.</b> The group is not in Rotation → All, the regime buttons or Alerts only (it has its own Rotation → Currency button), the Themes aggregates, or the missing-from-Theme-file list.</li>
    </ul>
    <p class="note">The funds track spot exchange rates less fees. They are a signal and hedge-sizing aid built on the same momentum model as the rest of the dashboard; they are not forecasts of currency moves.</p></div>`;
}


// ---------- PPO tab (v47) ----------
function ppoRows() {
  const nz = v => isNum(v) ? v : 99;
  return ROWS.map(r => {
    const H = P.history[r.t] || {}, h = (H.h || []).filter(isNum), n = h.length;
    const hn = n ? h[n-1] : r.ppo_d, hp = n > 1 ? h[n-2] : null;
    const hchg = isNum(hn) && isNum(hp) ? hn - hp : null;
    let streak = 0;
    if (isNum(hchg) && hchg !== 0) { const up = hchg > 0; for (let i = n-1; i > 0; i--) { const d = h[i] - h[i-1]; if (d !== 0 && (d > 0) === up) streak++; else break; } }
    const hstate = !isNum(hn) || !isNum(hchg) ? '' : (hn > 0 ? 'Positive' : 'Negative') + ' & ' + (hchg > 0 ? 'rising' : hchg < 0 ? 'falling' : 'flat');
    const bp = nz(r.bs_pos), bn = nz(r.bs_neg), xbars = Math.min(bp, bn), xdir = bp <= bn ? 'Bullish' : 'Bearish';
    const inforce = xdir === 'Bullish' ? r.ppo_d > 0 : r.ppo_d < 0;
    const zp = nz(r.bz_pos), zn = nz(r.bz_neg), zbars = Math.min(zp, zn), zdir = zp <= zn ? 'Above' : 'Below';
    return {...r, hn, hp, hchg, hstreak: streak, hstate, xbars, xdir, inforce, zbars, zdir, zside: r.ppo > 0 ? 'Above zero' : 'Below zero'};
  });
}
let PPOSUB = 'all';
function renderPPO() {
  const host = document.getElementById('ppo');
  const R = ppoRows(), W = 10, FB = CFG.fresh_bars;
  const xr = R.filter(r => r.xbars <= W), zr = R.filter(r => r.zbars <= W);
  const cnt = fn => R.filter(fn).length;
  const kpi = (v,l,cls='',d='') => `<div class="kpi" style="cursor:default"><div class="v ${cls}">${v}</div><div class="l">${l}</div><div class="d">${d}</div></div>`;
  const xdirTxt = r => r.xdir === 'Bullish' ? '<span class="good">▲ Bullish</span>' : '<span class="bad">▼ Bearish</span>';
  const zdirTxt = r => r.zdir === 'Above' ? '<span class="good">▲ Above zero</span>' : '<span class="bad">▼ Below zero</span>';
  const hCls = {'Positive & rising':'g', 'Positive & falling':'w', 'Negative & rising':'m', 'Negative & falling':'b', 'Positive & flat':'mu', 'Negative & flat':'mu'};
  const base = [
    {key:'t', label:'Ticker', left:true, render:r => tk(r.t) + flags(r)},
    themeCol,
    {key:'rec', label:'Signal', render:r => omBadge(r), sortVal:r => omOrder(r)},
    qsCol,
  ];
  const tail = [
    {key:'ppo', label:'PPO', cls:r => signCls(r.ppo), render:r => f(r.ppo,2,true)},
    {key:'ppo_sig', label:'Signal', render:r => f(r.ppo_sig,2,true)},
    {key:'ppo_d', label:'Hist', cls:r => signCls(r.ppo_d), render:r => f(r.ppo_d,3,true), tip:'PPO histogram = PPO minus its signal line'},
    {key:'regime', label:'Trailing/Emerging Momentum', render:r => `<span style="color:${regColor(r.regime)}">${r.regime}</span>`},
    {key:'close', label:'Close', render:r => fp(r.close)},
  ];
  const xCols = [...base,
    {key:'xdir', label:'Signal-line cross', render:xdirTxt, sortVal:r => r.xdir === 'Bullish' ? 1 : 0},
    {key:'xbars', label:'Bars ago', cls:r => r.xbars <= FB ? 'g' : '', render:r => r.xbars, tip:'0 = crossed on the latest bar. Within ' + FB + ' bars counts as fresh.'},
    {key:'inforce', label:'Still in force', render:r => r.inforce ? '<span class="good">✓</span>' : '<span class="muted">—</span>', sortVal:r => r.inforce ? 1 : 0, tip:'Histogram still on the side of the cross (an alert needs this)'},
    ...tail];
  const hCols = [...base,
    {key:'hstate', label:'Histogram', cls:r => hCls[r.hstate] || '', render:r => r.hstate || '—'},
    {key:'hn', label:'Hist now', cls:r => signCls(r.hn), render:r => f(r.hn,3,true)},
    {key:'hp', label:'Prior bar', render:r => f(r.hp,3,true)},
    {key:'hchg', label:'Change', cls:r => signCls(r.hchg), render:r => f(r.hchg,3,true)},
    {key:'hstreak', label:'Bars in direction', render:r => r.hstreak || '—', tip:'Consecutive bars the histogram has moved the same way'},
    {key:'sig_x', label:'Sig×', render:r => arrow(r.sig_x), sortVal:r => r.sig_x==='↑'?2:r.sig_x==='↓'?0:1},
    {key:'ppo', label:'PPO', cls:r => signCls(r.ppo), render:r => f(r.ppo,2,true)},
    {key:'regime', label:'Trailing/Emerging Momentum', render:r => `<span style="color:${regColor(r.regime)}">${r.regime}</span>`},
    {key:'close', label:'Close', render:r => fp(r.close)}];
  const zCols = [...base,
    {key:'zdir', label:'Zero-line cross', render:zdirTxt, sortVal:r => r.zdir === 'Above' ? 1 : 0},
    {key:'zbars', label:'Bars ago', cls:r => r.zbars <= FB ? 'g' : '', render:r => r.zbars},
    {key:'zside', label:'PPO now', cls:r => r.ppo > 0 ? 'g' : 'b', render:r => r.zside},
    {key:'sig_x', label:'Sig×', render:r => arrow(r.sig_x), sortVal:r => r.sig_x==='↑'?2:r.sig_x==='↓'?0:1},
    ...tail];
  const nPos = cnt(r => r.ppo > 0);
  const WF = R.filter(r => omKey(r) === 'Watch Favorable'), WU = R.filter(r => omKey(r) === 'Watch Unfavorable');
  const subDefs = [['all', 'All PPO', R.length], ['wf', 'Watch Favorable', WF.length], ['wu', 'Watch Unfavorable', WU.length]];
  const lastX = r => r.xbars >= 99 ? '<span class="muted">—</span>' : xdirTxt(r) + ' <span class="muted">' + r.xbars + ' bar' + (r.xbars === 1 ? '' : 's') + ' ago</span>';
  const wCols = (side) => [...base,
    {key:'buy', label:'POS Signals', cls:r => r.buy >= CFG.buy_thr ? 'g bg-g' : confCls(r.buy), render:r => fi(r.buy)},
    {key:'sell', label:'NEG Signals', cls:r => r.sell >= CFG.sell_thr ? 'b bg-b' : confCls(r.sell), render:r => fi(r.sell)},
    ...(side === 'F' ? [{key:'gate', label:'Blocked by', left:true, render:r => r.gate ? `<span class="warn" title="${wTip(r)}">${esc(r.gate)}</span>` : '<span class="muted">—</span>', sortVal:r => r.gate || '', tip:'Why a name that cleared the POS threshold is not Favorable (see Guide → Gates)'}] : []),
    {key:'xbars', label:'Last signal-line cross', render:lastX, sortVal:r => r.xbars, tip:'Most recent signal-line cross and how many bars ago'},
    {key:'inforce', label:'Still in force', render:r => r.xbars >= 99 ? '<span class="muted">—</span>' : r.inforce ? '<span class="good">✓</span>' : '<span class="muted">—</span>', sortVal:r => r.inforce ? 1 : 0},
    {key:'hstate', label:'Histogram', cls:r => hCls[r.hstate] || '', render:r => r.hstate || '—'},
    {key:'hchg', label:'Change', cls:r => signCls(r.hchg), render:r => f(r.hchg,3,true)},
    ...tail];
  host.innerHTML = `<h2>PPO <span class="muted" style="font-weight:400;font-size:.85rem">PPO(${12},${26},${9}) · the trigger behind every alert · crossovers, histogram direction and zero-line crosses</span></h2>
    <div class="kpis" style="grid-template-columns:repeat(7,1fr)">
      ${kpi(cnt(r => r.sig_x === '↑'), 'Bullish crosses', 'good', 'within ' + FB + ' bars')}
      ${kpi(cnt(r => r.sig_x === '↓'), 'Bearish crosses', 'bad', 'within ' + FB + ' bars')}
      ${kpi(cnt(r => isNum(r.hchg) && r.hchg > 0), 'Histogram rising', 'good', 'vs prior bar')}
      ${kpi(cnt(r => isNum(r.hchg) && r.hchg < 0), 'Histogram falling', 'bad', 'vs prior bar')}
      ${kpi(cnt(r => r.zbars <= FB && r.zdir === 'Above'), 'Crossed above zero', 'good', 'within ' + FB + ' bars')}
      ${kpi(cnt(r => r.zbars <= FB && r.zdir === 'Below'), 'Crossed below zero', 'bad', 'within ' + FB + ' bars')}
      ${kpi(Math.round(100 * nPos / Math.max(1, R.length)) + '%', 'PPO above zero', '', nPos + ' of ' + R.length)}
    </div>
    ${P.hist_state === 'missing' ? '<div class="warnbox">History file not found: histogram direction needs it.</div>' : ''}
    <div class="toolbar" id="ppo-sub" style="margin:.5rem 0 .75rem">${subDefs.map(d => `<button data-s="${d[0]}" class="${PPOSUB === d[0] ? 'on' : ''}">${d[1]} <span class="muted">(${d[2]})</span></button>`).join('')}</div>
    <div id="ppo-pane-all" style="display:${PPOSUB === 'all' ? 'block' : 'none'}">
    <h3>Signal-line crossovers <span class="muted">(last ${W} bars)</span></h3><div id="ppo-x-table"></div>
    <h3 style="margin-top:1.25rem">Histogram direction <span class="muted">(all names)</span></h3><div id="ppo-h-table"></div>
    <h3 style="margin-top:1.25rem">Zero-line crosses <span class="muted">(last ${W} bars)</span></h3><div id="ppo-z-table"></div>
    </div>
    <div id="ppo-pane-wf" style="display:${PPOSUB === 'wf' ? 'block' : 'none'}"><h3>Watch Favorable <span class="muted">(${WF.length} names)</span></h3><div id="ppo-wf-table"></div></div>
    <div id="ppo-pane-wu" style="display:${PPOSUB === 'wu' ? 'block' : 'none'}"><h3>Watch Unfavorable <span class="muted">(${WU.length} names)</span></h3><div id="ppo-wu-table"></div></div>`;
  host.querySelectorAll('#ppo-sub button').forEach(btn => btn.onclick = () => {
    PPOSUB = btn.dataset.s;
    host.querySelectorAll('#ppo-sub button').forEach(x => x.classList.toggle('on', x === btn));
    ['all','wf','wu'].forEach(k => { document.getElementById('ppo-pane-' + k).style.display = k === PPOSUB ? 'block' : 'none'; });
  });
  makeTable('ppo-x-table', xCols, xr, {sortKey:'xbars', sortDir:1,
    filters:{BULL:r=>r.xdir==='Bullish', BEAR:r=>r.xdir==='Bearish', FRESH:r=>r.xbars<=FB, INFORCE:r=>r.inforce, FAV:r=>r.rec==='BUY', UNFAV:r=>r.rec==='SELL'},
    filterLabels:{BULL:'Bullish', BEAR:'Bearish', FRESH:'Fresh (≤' + FB + ' bars)', INFORCE:'Still in force', FAV:'Favorable', UNFAV:'Unfavorable'},
    note:`Shows the most recent signal-line cross for every name that has crossed within ${W} bars. A cross is only a trigger while it is still in force (histogram on the same side of zero) and within ${FB} bars; it must also clear the score, volume and gate tests before Signal turns Favorable or Unfavorable.`});
  makeTable('ppo-h-table', hCols, R.filter(r => r.hstate), {sortKey:'hchg', sortDir:-1,
    filters:{RISING:r=>isNum(r.hchg)&&r.hchg>0, FALLING:r=>isNum(r.hchg)&&r.hchg<0, PR:r=>r.hstate==='Positive & rising', PF:r=>r.hstate==='Positive & falling', NR:r=>r.hstate==='Negative & rising', NF:r=>r.hstate==='Negative & falling'},
    filterLabels:{RISING:'Rising', FALLING:'Falling', PR:'Positive & rising', PF:'Positive & falling', NR:'Negative & rising', NF:'Negative & falling'},
    note:`Histogram = PPO − signal line, compared with the prior bar. <b>Positive &amp; rising</b> = bullish momentum accelerating; <b>Positive &amp; falling</b> = bullish momentum fading (a bearish cross is closer); <b>Negative &amp; rising</b> = bearish pressure easing (a bullish cross is closer); <b>Negative &amp; falling</b> = bearish momentum accelerating. A histogram sign change is the same event as a signal-line cross, so crosses are listed above rather than here.`});
  makeTable('ppo-z-table', zCols, zr, {sortKey:'zbars', sortDir:1,
    filters:{ABOVE:r=>r.zdir==='Above', BELOW:r=>r.zdir==='Below', FRESH:r=>r.zbars<=FB},
    filterLabels:{ABOVE:'Crossed above zero', BELOW:'Crossed below zero', FRESH:'Fresh (≤' + FB + ' bars)'},
    note:`Zero-line cross = the PPO line itself crossing zero (the 12-day EMA crossing the 26-day EMA). A fresh zero-line cross adds points to the POS or NEG Signals score. Names whose last zero-line cross is older than ${W} bars are not listed.`});
  makeTable('ppo-wf-table', wCols('F'), WF, {sortKey:'buy', sortDir:-1,
    filters:{GATED:r=>!!r.gate, UNGATED:r=>!r.gate, FRESHUP:r=>r.sig_x==='↑', INFORCE:r=>r.xdir==='Bullish' && r.inforce, CANDS:isCandidate, HRISE:r=>isNum(r.hchg) && r.hchg > 0},
    filterLabels:{GATED:'Blocked by a gate', UNGATED:'Near trigger (no gate)', FRESHUP:'Fresh ↑ cross', INFORCE:'Bullish cross in force', CANDS:'Candidates', HRISE:'Histogram rising'},
    note:`Names rated <b>Watch Favorable</b>: either a Favorable that a gate held back (reason in Blocked by) or POS Signals within ${CFG.watch_margin} points of the trigger. The PPO columns show how close the trigger is: a fresh bullish cross that is still in force is what an alert needs. The market-regime gate closes only when ${CFG.benchmark} <i>and</i> ${CFG.regime_confirm} both fail.`});
  makeTable('ppo-wu-table', wCols('U'), WU, {sortKey:'sell', sortDir:-1,
    filters:{FRESHDN:r=>r.sig_x==='↓', INFORCE:r=>r.xdir==='Bearish' && r.inforce, HFALL:r=>isNum(r.hchg) && r.hchg < 0, BELOW0:r=>r.ppo < 0},
    filterLabels:{FRESHDN:'Fresh ↓ cross', INFORCE:'Bearish cross in force', HFALL:'Histogram falling', BELOW0:'PPO below zero'},
    note:`Names rated <b>Watch Unfavorable</b>: NEG Signals within ${CFG.watch_margin} points of the trigger but no Unfavorable alert yet. A fresh bearish cross that is still in force (histogram negative) is the missing trigger.`});
}

// ---------- Themes tab (v30) ----------
const TS = P.tstats || {themes:[], subs:[], dates:[]};
const TH_BY = Object.fromEntries(TS.themes.map(x => [x.name, x]));
const SUB_BY = {}; TS.subs.forEach(x => SUB_BY[x.theme + '\u0001' + x.name] = x);
let THM = {theme:null, sub:null, all:false};
const scoreColor = v => !isNum(v) ? '#6e7681' : v >= 60 ? C.good : v >= 52 ? '#7fb069' : v >= 48 ? '#6e7681' : v >= 40 ? C.warn : C.bad;
const heat = v => !isNum(v) ? '#161b22' : v >= 50 ? `rgba(63,185,80,${(.08 + Math.min(1,(v-50)/30)*.42).toFixed(2)})` : `rgba(248,81,73,${(.08 + Math.min(1,(50-v)/30)*.42).toFixed(2)})`;
function themeGo(theme, sub, all) { THM = {theme: theme || null, sub: sub || null, all: !!all}; renderThemes(); showTab('themes'); }
function aggCols(level) {
  const small = r => r.small ? 'mu' : '';
  return [
    {key:'name', label: level === 'themes' ? 'Theme' : 'Sub-Theme', left:true, render:r => `<b class="${r.small ? 'muted' : ''}">${esc(r.name)}</b>${r.small ? ' <span class="chip" title="fewer than ' + TS.min_members + ' loaded names">n too small</span>' : ''}`},
    {key:'n', label:'Names', cls:small, render:r => r.n},
    {key:'score', label:'Score', cls:r => r.small ? 'mu' : r.score >= 60 ? 'g bg-g' : r.score <= 40 ? 'b bg-b' : 'm', render:r => f(r.score,0), tip:'Theme Score 0-100: Momentum ' + Math.round(100*TS.weights.momentum) + '% · Breadth ' + Math.round(100*TS.weights.breadth) + '% · Signals ' + Math.round(100*TS.weights.signals) + '% · Acceleration ' + Math.round(100*TS.weights.accel) + '%'},
    {key:'d5', label:'Δ5d', cls:r => r.small ? 'mu' : signCls(r.d5), render:r => f(r.d5,1,true)},
    {key:'hist', label:'Score history', render:r => sparkline(r.hist, {w:90,h:22,ref:50,min:0,max:100}), sortVal:r => r.d5},
    {key:'p_mom', label:'Mom', cls:small, render:r => f(r.p_mom,0), tip:'Momentum pillar: median Mom percentile'},
    {key:'p_brd', label:'Brd', cls:small, render:r => f(r.p_brd,0), tip:'Breadth pillar: mean of % above EMA200, % bull stack, % PPO > 0'},
    {key:'p_sig', label:'Sig', cls:small, render:r => f(r.p_sig,0), tip:'Signals pillar: 50 + average Net Signals / 2'},
    {key:'p_acc', label:'Acc', cls:small, render:r => f(r.p_acc,0), tip:'Acceleration pillar: 5d change in median Emerging, 5d change in Net Signals, median 20d return vs ' + CFG.benchmark},
    {key:'trail', label:'Trailing', cls:r => r.small ? 'mu' : pctCls(r.trail), render:r => f(r.trail,0)},
    {key:'emerg', label:'Emerging', cls:r => r.small ? 'mu' : pctCls(r.emerg), render:r => f(r.emerg,0)},
    {key:'regime', label:'Trailing/Emerging Momentum', render:r => `<span style="color:${regColor(r.regime)}">${r.regime}</span>`},
    {key:'a200', label:'> E200', cls:small, render:r => f(r.a200,0) + '%'},
    {key:'stack', label:'Stack', cls:small, render:r => f(r.stack,0) + '%'},
    {key:'ppo_pos', label:'PPO>0', cls:small, render:r => f(r.ppo_pos,0) + '%'},
    {key:'buy', label:'Fav.', cls:r => r.buy ? 'g' : 'mu', render:r => r.buy, tip:'Names with Signal = Favorable'},
    {key:'sell', label:'Unfav.', cls:r => r.sell ? 'b' : 'mu', render:r => r.sell, tip:'Names with Signal = Unfavorable'},
    {key:'exit', label:'Confl.', cls:r => r.exit ? 'w' : 'mu', render:r => r.exit, tip:'Conflicted (POS and NEG both firing)'},
    {key:'watch', label:'Watch', cls:r => r.watch ? 'accent' : 'mu', render:r => r.watch},
    {key:'bias', label:'Net Signals', cls:r => r.small ? 'mu' : signCls(r.bias), render:r => f(r.bias,1,true)},
  ];
}
function heatGrid(items, onPick) {
  const sorted = items.slice().sort((a,b) => (b.score ?? -1) - (a.score ?? -1));
  const html = `<div class="heat">${sorted.map((x,i) => `<div class="tile ${x.small ? 'small' : ''}" data-i="${i}" style="background:${heat(x.score)};min-height:${54 + Math.min(40, x.n*2)}px" title="${esc(x.name)} · ${x.n} names${x.small ? ' · too small to rank' : ''}"><div class="nm">${esc(x.name)}</div><div style="display:flex;justify-content:space-between;align-items:baseline"><span class="sc" style="color:${x.small ? 'var(--muted)' : scoreColor(x.score)}">${f(x.score,0)}</span><span class="sub">${x.n} names · <span class="${signCls(x.d5) === 'g' ? 'good' : signCls(x.d5) === 'b' ? 'bad' : ''}">${f(x.d5,1,true)}</span></span></div></div>`).join('')}</div>`;
  return {html, bind: host => host.querySelectorAll('.tile').forEach(el => el.onclick = () => onPick(sorted[+el.dataset.i]))};
}
function pillarBars(x) {
  const bar = (label, v, w) => `<span>${label} <span class="muted">(${Math.round(100*w)}%)</span></span><div class="bar"><i style="width:${Math.max(0,v||0)}%;background:${scoreColor(v)}"></i></div><span>${f(v,0)}</span>`;
  const W = TS.weights;
  return `<div class="comp" style="grid-template-columns:9rem 1fr 2.5rem">${bar('Momentum', x.p_mom, W.momentum)}${bar('Breadth', x.p_brd, W.breadth)}${bar('Signals', x.p_sig, W.signals)}${bar('Acceleration', x.p_acc, W.accel)}</div>`;
}
function renderThemes() {
  const host = document.getElementById('themes');
  if (!TS.themes.length) { host.innerHTML = '<h2>Themes</h2><div class="empty">No theme data. Check Config.themes_csv (Health tab) - themes need the Theme file and at least one ticker with a primary assignment.</div>'; return; }
  const kpi = (v,l,cls='',d='') => `<div class="kpi" style="cursor:default"><div class="v ${cls}">${v}</div><div class="l">${l}</div><div class="d">${d}</div></div>`;
  const dates = TS.dates || [];
  const noteBase = `Primary assignments only (a ticker counts once); Sector, Six Pack, ETF and Country ETF funds are left out. Medians are used so one outlier cannot drive a theme. Themes with fewer than ${TS.min_members} loaded names are greyed out. Display only - nothing here feeds any alert or recommendation.`;
  const crumb = (parts) => `<div class="crumbs">${parts.map((p,i) => p.go ? `<button data-go="${i}">${esc(p.label)}</button><span class="muted">›</span>` : `<span class="cur">${esc(p.label)}</span>`).join('')}</div>`;
  const bindCrumb = (parts) => host.querySelectorAll('.crumbs button').forEach(b => b.onclick = () => parts[+b.dataset.go].go());

  // ---- level 3: tickers
  if (THM.theme && (THM.sub || THM.all) && TH_BY[THM.theme]) {
    const T0 = TH_BY[THM.theme], X = THM.sub ? SUB_BY[THM.theme + '\u0001' + THM.sub] : T0;
    if (!X) { THM = {theme:THM.theme, sub:null, all:false}; return renderThemes(); }
    const parts = [{label:'Themes', go:() => themeGo()}, {label:THM.theme, go:() => themeGo(THM.theme)}, {label: THM.sub || 'All tickers'}];
    const med = X.mom;
    const rows = X.tickers.map(t => ({...BY[t], vs: isNum(BY[t].mom) && isNum(med) ? BY[t].mom - med : null, subname: (THEMES[t] || ['',''])[1]})).filter(r => r.t);
    const cols = [
      {key:'t', label:'Ticker', left:true, render:r => tk(r.t) + flags(r)},
      ...(THM.sub ? [] : [{key:'subname', label:'Sub-Theme', left:true, render:r => esc(r.subname || '—')}]),
      {key:'also', label:'Also in', left:true, render:r => secPairs(r.t).length ? secPairs(r.t).map(sp => `<span class="thc">${esc(pairText(sp))}</span>`).join('<br>') : '<span class="muted">—</span>', sortVal:r => secText(r.t)},
      {key:'rec', label:'Signal', render:r => omBadge(r), sortVal:r => omOrder(r)},
      qsCol,
      {key:'buy', label:'POS Signals', cls:r => r.buy >= (CFG.buy_thr) ? 'g bg-g' : confCls(r.buy), render:r => fi(r.buy)},
      {key:'sell', label:'NEG Signals', cls:r => r.sell >= (CFG.sell_thr) ? 'b bg-b' : confCls(r.sell), render:r => fi(r.sell)},
      {key:'bias', label:'Net Signals', cls:r => signCls(r.bias), render:r => f(r.bias,0,true)},
      {key:'mom', label:'RS Rating', cls:r => pctCls(r.mom), render:r => fi(isNum(r.rs) ? r.rs : r.mom), sortVal:r => r.mom, tip:RS_TIP},
      {key:'vs', label:'vs median', cls:r => signCls(r.vs), render:r => f(r.vs,0,true), tip:'Momentum percentile minus the ' + (THM.sub ? 'sub-theme' : 'theme') + ' median: positive = leader'},
      {key:'regime', label:'Trailing/Emerging Momentum', render:r => `<span style="color:${regColor(r.regime)}">${r.regime}</span>`},
      {key:'rsi', label:'RSI', cls:r => rsiCls(r.rsi), render:r => f(r.rsi,1)},
      {key:'ppo', label:'PPO', cls:r => signCls(r.ppo), render:r => f(r.ppo,2,true)},
      {key:'sig_x', label:'Sig×', render:r => arrow(r.sig_x), sortVal:r => r.sig_x === '↑' ? 2 : r.sig_x === '↓' ? 0 : 1},
      {key:'e50', label:'vs E50', cls:r => signCls(r.e50), render:r => f(r.e50,1,true) + '%'},
      {key:'e200', label:'vs E200', cls:r => signCls(r.e200), render:r => f(r.e200,1,true) + '%'},
      {key:'close', label:'Close', render:r => fp(r.close)},
    ];
    host.innerHTML = `<h2>Themes</h2>${crumb(parts)}
      <div class="kpis" style="grid-template-columns:repeat(5,1fr)">${kpi(f(X.score,0), 'Theme score', X.score >= 60 ? 'good' : X.score <= 40 ? 'bad' : '', X.small ? 'too small to rank' : (isNum(X.d5) ? f(X.d5,1,true) + ' vs 5d ago' : ''))}${kpi(X.n, 'Names', '', 'primary assignments')}${kpi(`<span style="font-size:1.05rem;color:${regColor(X.regime)}">${X.regime}</span>`, 'Trailing/Emerging Momentum (medians)', '', `trailing ${f(X.trail,0)} · emerging ${f(X.emerg,0)}`)}${kpi(`${X.buy} / ${X.sell}`, 'Favorable / Unfavorable', '', `${X.exit} conflicted · ${X.watch} watch`)}${kpi(f(X.bias,1,true), 'Avg net signals', signCls(X.bias) === 'g' ? 'good' : signCls(X.bias) === 'b' ? 'bad' : '', '')}</div>
      <div class="grid g2"><div class="card"><div class="chart-title"><span>Theme score history (${dates.length} sessions)</span></div>${lineChart([{v:X.hist,color:C.accent,width:2,fillTo:50}], {h:130,min:0,max:100,labels:dates,hlines:[{y:50,color:C.muted}]})}</div>
      <div class="card"><h3>Score pillars</h3>${pillarBars(X)}</div></div>
      <div id="thm-tk-table"></div>`;
    bindCrumb(parts);
    makeTable('thm-tk-table', cols, rows, {sortKey:'rec', sortDir:1, filters:{BUY:r=>r.rec==='BUY', SELL:r=>r.rec==='SELL', EXIT:r=>r.rec==='EXIT', WATCH:r=>!!r.watch, LEADERS:r=>isNum(r.vs) && r.vs > 0, LAGGARDS:r=>isNum(r.vs) && r.vs < 0}, filterLabels:{BUY:'Favorable', SELL:'Unfavorable', EXIT:'Conflicted', WATCH:'Watch', LEADERS:'Leaders', LAGGARDS:'Laggards'},
      note:`Tickers whose PRIMARY assignment is ${esc(THM.theme)}${THM.sub ? ' › ' + esc(THM.sub) : ''}. "Also in" lists secondary assignments (display only - not counted in any aggregate). Click a row for the quick view.`});
    return;
  }
  // ---- level 2: sub-themes of one theme
  if (THM.theme && TH_BY[THM.theme]) {
    const X = TH_BY[THM.theme];
    const parts = [{label:'Themes', go:() => themeGo()}, {label:THM.theme}];
    const subs = TS.subs.filter(x => x.theme === THM.theme);
    const hg = heatGrid(subs, x => themeGo(THM.theme, x.name));
    host.innerHTML = `<h2>Themes</h2>${crumb(parts)}
      <div class="kpis" style="grid-template-columns:repeat(5,1fr)">${kpi(f(X.score,0), 'Theme score', X.score >= 60 ? 'good' : X.score <= 40 ? 'bad' : '', X.small ? 'too small to rank' : (isNum(X.d5) ? f(X.d5,1,true) + ' vs 5d ago' : ''))}${kpi(X.n, 'Names', '', subs.length + ' sub-theme(s)')}${kpi(`<span style="font-size:1.05rem;color:${regColor(X.regime)}">${X.regime}</span>`, 'Trailing/Emerging Momentum (medians)', '', `trailing ${f(X.trail,0)} · emerging ${f(X.emerg,0)}`)}${kpi(`${X.buy} / ${X.sell}`, 'Favorable / Unfavorable', '', `${X.exit} conflicted · ${X.watch} watch`)}${kpi(f(X.bias,1,true), 'Avg net signals', signCls(X.bias) === 'g' ? 'good' : signCls(X.bias) === 'b' ? 'bad' : '', '')}</div>
      <div class="grid g2"><div class="card"><div class="chart-title"><span>Theme score history (${dates.length} sessions)</span></div>${lineChart([{v:X.hist,color:C.accent,width:2,fillTo:50}], {h:130,min:0,max:100,labels:dates,hlines:[{y:50,color:C.muted}]})}</div>
      <div class="card"><h3>Score pillars</h3>${pillarBars(X)}<div style="margin-top:.75rem"><button class="crumbs-btn" id="thm-all" style="background:#1f6feb;border:1px solid #1f6feb;color:#fff;border-radius:6px;padding:.3rem .8rem;cursor:pointer">All ${X.n} tickers in ${esc(THM.theme)} →</button></div></div></div>
      <h3>Sub-themes</h3>${hg.html}<div id="thm-table"></div>`;
    bindCrumb(parts); hg.bind(host);
    document.getElementById('thm-all').onclick = () => themeGo(THM.theme, null, true);
    makeTable('thm-table', aggCols('subs'), subs, {sortKey:'score', onRow:r => themeGo(THM.theme, r.name), note:noteBase + ' Click a sub-theme to list its tickers.'});
    return;
  }
  // ---- level 1: all themes
  const ranked = TS.themes.filter(x => !x.small && isNum(x.score)).sort((a,b) => b.score - a.score);
  const hot = ranked[0], cold = ranked[ranked.length-1];
  const rising = ranked.filter(x => isNum(x.d5) && x.d5 > 0).length;
  const hg = heatGrid(TS.themes, x => themeGo(x.name));
  host.innerHTML = `<h2>Themes <span class="muted" style="font-weight:400;font-size:.85rem">Theme → Sub-Theme → Ticker · score from primary members · click to drill down</span></h2>
    <div class="kpis" style="grid-template-columns:repeat(5,1fr)">${kpi(ranked.length, 'Themes ranked', '', `${TS.themes.length - ranked.length} too small · ${TS.subs.length} sub-themes`)}${kpi(hot ? esc(hot.name) : '—', 'Hottest', 'good', hot ? 'score ' + f(hot.score,0) : '')}${kpi(cold ? esc(cold.name) : '—', 'Coldest', 'bad', cold ? 'score ' + f(cold.score,0) : '')}${kpi(ranked.filter(x => x.regime === 'Strong').length, 'In Strong regime', 'good', 'trailing and emerging medians ≥ ' + CFG.regime_hi)}${kpi(rising + ' / ' + ranked.length, 'Rising (5d)', '', 'score up vs 5 sessions ago')}</div>
    ${hg.html}<div id="thm-table"></div>`;
  hg.bind(host);
  makeTable('thm-table', aggCols('themes'), TS.themes, {sortKey:'score', onRow:r => themeGo(r.name), note:noteBase + ' Click a theme to see its sub-themes.'});
}
function themeGuide() {
  const W = TS.weights || {momentum:.4,breadth:.25,signals:.2,accel:.15}, pc = v => Math.round(100*v) + '%';
  return `<div class="card" style="margin-top:1rem"><h2 style="margin-bottom:.4rem">Themes tab — how the Theme Score is built</h2>
    <p class="note" style="margin:0 0 .5rem">Each theme (and sub-theme) is scored 0–100 from the loaded tickers whose <b>primary</b> assignment it is. Secondary assignments are displayed but never counted. Sector, Six Pack, ETF and Country ETF funds are excluded. The score is display-only and feeds no alert.</p>
    <ul class="plain">
      <li><b>Momentum (${pc(W.momentum)})</b> — median Momentum percentile of the members.</li>
      <li><b>Breadth (${pc(W.breadth)})</b> — average of % above EMA200, % with a bull stack (20&gt;50&gt;200) and % with PPO above zero.</li>
      <li><b>Signals (${pc(W.signals)})</b> — 50 + average Net Signals ÷ 2, so a theme full of Favorable-leaning names scores above 50.</li>
      <li><b>Acceleration (${pc(W.accel)})</b> — 50 + 2 × the 5-session change in median Emerging percentile + 0.25 × the 5-session change in average Net Signals + 1.5 × median 20-day return vs ${CFG.benchmark}, capped 0–100.</li>
    </ul>
    <p class="note">Themes with fewer than ${TS.min_members || CFG.theme_min} loaded names are greyed out as too small to rank. The regime is the usual trailing × emerging rule applied to the member medians. The score history is reconstructed by re-running the model over each past session, like the rest of the dashboard history. On Rotation, <b>Themes</b> and <b>Sub-Themes</b> plot one bubble per group at its median trailing / emerging percentiles, and the theme picker plots the individual tickers of one theme.</p></div>`;
}

// ---------- Theme Signals tab (v56): weekly signal file, own Theme > Sub-Theme > Ticker drill-down ----------
// Completely separate from the Themes tab: own data (P.tsig), own state, own functions, no Theme Score.
const TG = P.tsig || {loaded:false, rows:[], members:{}, as_of:'', file:'', error:''};
const TG_SIGS = [
  {k:'EARLY ROTATION',        label:'Early Rotation',        short:'Early',  color:C.good,   ord:0},
  {k:'MATURE LEADERSHIP',     label:'Mature Leadership',     short:'Mature', color:C.accent, ord:1},
  {k:'MIXED / CONSOLIDATING', label:'Mixed / Consolidating', short:'Mixed',  color:C.warn,   ord:2},
  {k:'FAILED ROTATION',       label:'Failed Rotation',       short:'Failed', color:C.bad,    ord:3},
];
const TG_BYSIG = Object.fromEntries(TG_SIGS.map(s => [s.k, s]));
const tgSig = k => TG_BYSIG[k] || {k, label:k || '—', short:k || '—', color:C.muted, ord:9};
const tgBadge = k => { const s = tgSig(k); return `<span class="tsg-badge" style="color:${s.color};border-color:${s.color}">${esc(s.label)}</span>`; };
const tgStars = n => isNum(n) ? `<span class="tsg-stars" title="${n} of 3">${'★'.repeat(Math.max(0,Math.min(3,n)))}<span class="muted">${'★'.repeat(Math.max(0,3-n))}</span></span>` : '<span class="muted">—</span>';
const tgBar = (v, color) => isNum(v) ? `${f(v,0)}<span class="tsg-bar"><i style="width:${Math.max(0,Math.min(100,v))}%;background:${color || C.accent}"></i></span>` : '<span class="muted">—</span>';
const tgBrCls = v => !isNum(v) ? '' : v >= 70 ? 'g' : v <= 30 ? 'b' : v <= 45 ? 'm' : '';
const tgPill = (k, n) => { const s = tgSig(k); return `<span class="tsg-pill" style="color:${s.color};border-color:${s.color}" title="${esc(s.label)}">${n} ${s.short}</span>`; };

const TG_ROWS = (TG.rows || []).map(r => ({...r, key: r.th + '\u0001' + r.sb, nt: ((TG.members || {})[r.th + '\u0001' + r.sb] || []).length, name: r.sb}));
const TG_SUBKEY = {}; TG_ROWS.forEach(r => TG_SUBKEY[r.key] = r);
const TG_THEMES = (() => {
  const m = {};
  TG_ROWS.forEach(r => { (m[r.th] = m[r.th] || {name:r.th, subs:[], tb:r.tb}).subs.push(r); });
  return Object.values(m).map(x => {
    const cnt = k => x.subs.filter(r => r.sig === k).length;
    const stars = x.subs.reduce((a, r) => a + (r.st || 0), 0), n = x.subs.length, tk = new Set();
    x.subs.forEach(r => ((TG.members || {})[r.key] || []).forEach(([t]) => tk.add(t)));
    return {...x, n, stars, avg: n ? stars / n : 0, early:cnt('EARLY ROTATION'), mature:cnt('MATURE LEADERSHIP'), mixed:cnt('MIXED / CONSOLIDATING'), failed:cnt('FAILED ROTATION'), nt:tk.size};
  });
})();
const TG_TH = Object.fromEntries(TG_THEMES.map(x => [x.name, x]));
let TSG = {theme:null, sub:null, all:false};
function tsgGo(theme, sub, all) { TSG = {theme: theme || null, sub: sub || null, all: !!all}; renderThemeSignals(); showTab('tsig'); }

function renderThemeSignals() {
  const host = document.getElementById('tsig');
  if (!TG.loaded || !TG_ROWS.length) {
    host.innerHTML = `<h2>Theme Signals</h2><div class="warnbox"><b>Weekly theme signal file not loaded.</b> ${esc(TG.error || 'no data')}<br>Check <code>Config.theme_signal_csv</code>: <code>${esc(TG.file || '')}</code></div>`;
    return;
  }
  const kpi = (v, l, cls='', d='') => `<div class="kpi" style="cursor:default"><div class="v ${cls}">${v}</div><div class="l">${l}</div><div class="d">${d}</div></div>`;
  const crumb = parts => `<div class="crumbs">${parts.map((p,i) => p.go ? `<button data-go="${i}">${esc(p.label)}</button><span class="muted">›</span>` : `<span class="cur">${esc(p.label)}</span>`).join('')}</div>`;
  const bindCrumb = parts => host.querySelectorAll('.crumbs button').forEach(b => b.onclick = () => parts[+b.dataset.go].go());
  const age = (TG.as_of && P.as_of) ? Math.round((new Date(P.as_of) - new Date(TG.as_of)) / 864e5) : null;
  const stale = isNum(age) && age > (TG.stale_days || 8);
  const banner = stale ? `<div class="warnbox"><b>Weekly signal file is ${age} days old</b> (as of ${esc(TG.as_of)}; session ${esc(P.as_of)}). Re-run the weekly theme report.</div>` : '';
  const asof = `<span class="muted" style="font-weight:400;font-size:.85rem">weekly file as of ${esc(TG.as_of || '?')} · Theme → Sub-Theme → Ticker · click to drill down</span>`;
  const note = 'Source: Weekly_Theme_Signal.csv (weekly). Stars 0-3 and the Breadth figures are taken straight from that file. Tickers come from the theme membership file; "Secondary" names also sit in another sub-theme. Display only - nothing here feeds any alert or recommendation.';
  const sigCount = k => TG_ROWS.filter(r => r.sig === k).length;

  // ---- level 3: tickers of one sub-theme (or of the whole theme)
  if (TSG.theme && (TSG.sub || TSG.all) && TG_TH[TSG.theme]) {
    const T0 = TG_TH[TSG.theme], X = TSG.sub ? TG_SUBKEY[TSG.theme + '\u0001' + TSG.sub] : null;
    if (TSG.sub && !X) { TSG = {theme:TSG.theme, sub:null, all:false}; return renderThemeSignals(); }
    const parts = [{label:'Theme Signals', go:() => tsgGo()}, {label:TSG.theme, go:() => tsgGo(TSG.theme)}, {label: TSG.sub || 'All tickers'}];
    const subs = X ? [X] : T0.subs;
    const rows = [];
    subs.forEach(sr => ((TG.members || {})[sr.key] || []).forEach(([t, a]) => { if (BY[t]) rows.push({...BY[t], assign:a, subname:sr.sb, subsig:sr.sig, substars:sr.st}); }));
    const cols = [
      {key:'t', label:'Ticker', left:true, render:r => tk(r.t) + flags(r)},
      ...(X ? [] : [{key:'subname', label:'Sub-Theme', left:true, render:r => esc(r.subname)},
                    {key:'subsig', label:'Sub-Theme signal', render:r => tgBadge(r.subsig), sortVal:r => tgSig(r.subsig).ord}]),
      {key:'assign', label:'Assignment', render:r => r.assign === 'S' ? '<span class="chip" title="Secondary assignment: this ticker\'s primary theme is elsewhere">secondary</span>' : 'Primary', sortVal:r => r.assign === 'S' ? 1 : 0},
      {key:'rec', label:'Signal', render:r => omBadge(r), sortVal:r => omOrder(r)},
      qsCol,
      {key:'buy', label:'POS Signals', cls:r => r.buy >= (CFG.buy_thr) ? 'g bg-g' : confCls(r.buy), render:r => fi(r.buy)},
      {key:'sell', label:'NEG Signals', cls:r => r.sell >= (CFG.sell_thr) ? 'b bg-b' : confCls(r.sell), render:r => fi(r.sell)},
      {key:'bias', label:'Net Signals', cls:r => signCls(r.bias), render:r => f(r.bias,0,true)},
      {key:'mom', label:'RS Rating', cls:r => pctCls(r.mom), render:r => fi(isNum(r.rs) ? r.rs : r.mom), sortVal:r => r.mom, tip:RS_TIP},
      {key:'regime', label:'Trailing/Emerging Momentum', render:r => `<span style="color:${regColor(r.regime)}">${r.regime}</span>`},
      {key:'rsi', label:'RSI', cls:r => rsiCls(r.rsi), render:r => f(r.rsi,1)},
      {key:'ppo', label:'PPO', cls:r => signCls(r.ppo), render:r => f(r.ppo,2,true)},
      {key:'sig_x', label:'Sig×', render:r => arrow(r.sig_x), sortVal:r => r.sig_x === '↑' ? 2 : r.sig_x === '↓' ? 0 : 1},
      {key:'e50', label:'vs E50', cls:r => signCls(r.e50), render:r => f(r.e50,1,true) + '%'},
      {key:'e200', label:'vs E200', cls:r => signCls(r.e200), render:r => f(r.e200,1,true) + '%'},
      {key:'close', label:'Close', render:r => fp(r.close)},
    ];
    const head = X
      ? kpi(`<span style="font-size:1.05rem">${tgBadge(X.sig)}</span>`, 'Sub-theme signal', '', `updated ${esc(X.upd || TG.as_of)}`) + kpi(tgStars(X.st), 'Stars', '', 'of 3') + kpi(isNum(X.sbr) ? f(X.sbr,0) : '—', 'Sub-theme breadth', tgBrCls(X.sbr) === 'g' ? 'good' : tgBrCls(X.sbr) === 'b' ? 'bad' : '', 'from the weekly file') + kpi(isNum(X.tb) ? f(X.tb,0) : '—', 'Theme breadth', '', esc(TSG.theme)) + kpi(rows.length, 'Tickers loaded', '', `${rows.filter(r => r.assign === 'S').length} secondary`)
      : kpi(T0.early + ' / ' + T0.mature, 'Early / Mature', 'good', `${T0.mixed} mixed · ${T0.failed} failed`) + kpi(T0.stars, 'Total stars', '', `${f(T0.avg,1)} avg per sub-theme`) + kpi(isNum(T0.tb) ? f(T0.tb,0) : '—', 'Theme breadth', '', 'from the weekly file') + kpi(T0.n, 'Sub-themes', '', esc(TSG.theme)) + kpi(rows.length, 'Ticker rows', '', `${T0.nt} unique names`);
    host.innerHTML = `<h2>Theme Signals ${asof}</h2>${banner}${crumb(parts)}
      <div class="kpis" style="grid-template-columns:repeat(5,1fr)">${head}</div><div id="tsg-tk-table"></div>`;
    bindCrumb(parts);
    makeTable('tsg-tk-table', cols, rows, {sortKey:'rec', sortDir:1, filters:{BUY:r=>r.rec==='BUY', SELL:r=>r.rec==='SELL', EXIT:r=>r.rec==='EXIT', WATCH:r=>!!r.watch, PRIMARY:r=>r.assign==='P'}, filterLabels:{BUY:'Favorable', SELL:'Unfavorable', EXIT:'Conflicted', WATCH:'Watch', PRIMARY:'Primary only'},
      note:`Tickers listed under ${esc(TSG.theme)}${TSG.sub ? ' › ' + esc(TSG.sub) : ''} in the theme membership file. Ticker columns are the same as the Signals tab. Click a row for the quick view.`});
    return;
  }
  // ---- level 2: sub-themes of one theme
  if (TSG.theme && TG_TH[TSG.theme]) {
    const X = TG_TH[TSG.theme], subs = X.subs.slice().sort((a,b) => (tgSig(a.sig).ord - tgSig(b.sig).ord) || ((b.st||0) - (a.st||0)) || ((b.sbr||0) - (a.sbr||0)));
    const parts = [{label:'Theme Signals', go:() => tsgGo()}, {label:TSG.theme}];
    const tiles = subs.map((r,i) => { const s = tgSig(r.sig); return `<div class="tsg-tile" data-i="${i}" style="background:${s.color}1f" title="${esc(r.sb)} · ${r.nt} tickers"><div class="nm">${esc(r.sb)}</div><div>${tgBadge(r.sig)}</div><div class="ft"><span>${tgStars(r.st)}</span><span>breadth ${isNum(r.sbr) ? f(r.sbr,0) : '—'} · ${r.nt} names</span></div></div>`; }).join('');
    const cols = [
      {key:'sb', label:'Sub-Theme', left:true, render:r => `<b>${esc(r.sb)}</b>`},
      {key:'sig', label:'Signal', render:r => tgBadge(r.sig), sortVal:r => tgSig(r.sig).ord},
      {key:'st', label:'Stars', render:r => tgStars(r.st), sortVal:r => r.st},
      {key:'sbr', label:'Sub-Theme Breadth', cls:r => tgBrCls(r.sbr), render:r => tgBar(r.sbr, tgSig(r.sig).color), tip:'Sub-theme breadth from the weekly file'},
      {key:'tb', label:'Theme Breadth', cls:r => tgBrCls(r.tb), render:r => f(r.tb,1)},
      {key:'nt', label:'Tickers', render:r => r.nt, tip:'Loaded tickers listed under this sub-theme (primary + secondary)'},
      {key:'upd', label:'Updated', render:r => esc(r.upd || '—')},
    ];
    host.innerHTML = `<h2>Theme Signals ${asof}</h2>${banner}${crumb(parts)}
      <div class="kpis" style="grid-template-columns:repeat(5,1fr)">${kpi(X.early, 'Early Rotation', 'good', 'sub-themes')}${kpi(X.mature, 'Mature Leadership', '', 'sub-themes')}${kpi(X.mixed + ' / ' + X.failed, 'Mixed / Failed', '', 'sub-themes')}${kpi(X.stars, 'Total stars', '', `${f(X.avg,1)} avg of 3`)}${kpi(isNum(X.tb) ? f(X.tb,0) : '—', 'Theme breadth', tgBrCls(X.tb) === 'g' ? 'good' : tgBrCls(X.tb) === 'b' ? 'bad' : '', `${X.nt} unique tickers`)}</div>
      <div style="margin-bottom:.75rem"><button id="tsg-all" style="background:#1f6feb;border:1px solid #1f6feb;color:#fff;border-radius:6px;padding:.3rem .8rem;cursor:pointer">All ${X.nt} tickers in ${esc(TSG.theme)} →</button></div>
      <h3>Sub-themes</h3><div class="tsg-grid">${tiles}</div><div id="tsg-sub-table"></div>`;
    bindCrumb(parts);
    host.querySelectorAll('.tsg-tile').forEach(el => el.onclick = () => tsgGo(TSG.theme, subs[+el.dataset.i].sb));
    document.getElementById('tsg-all').onclick = () => tsgGo(TSG.theme, null, true);
    makeTable('tsg-sub-table', cols, subs, {sortKey:'sig', sortDir:1, onRow:r => tsgGo(TSG.theme, r.sb), note:note + ' Click a sub-theme to list its tickers.'});
    return;
  }
  // ---- level 1: all themes
  const themes = TG_THEMES.slice().sort((a,b) => (b.early - a.early) || (b.stars - a.stars));
  const tiles = themes.map((x,i) => `<div class="tsg-tile" data-i="${i}" style="background:rgba(63,185,80,${(.04 + Math.min(1, x.avg / 2.2) * .26).toFixed(2)})" title="${esc(x.name)} · ${x.n} sub-themes"><div class="nm">${esc(x.name)}</div><div class="tsg-pills">${[['EARLY ROTATION',x.early],['MATURE LEADERSHIP',x.mature],['MIXED / CONSOLIDATING',x.mixed],['FAILED ROTATION',x.failed]].filter(p => p[1]).map(p => tgPill(p[0], p[1])).join('')}</div><div class="ft"><span>${f(x.avg,1)} avg ★</span><span>breadth ${isNum(x.tb) ? f(x.tb,0) : '—'}</span></div></div>`).join('');
  const tcols = [
    {key:'name', label:'Theme', left:true, render:r => `<b>${esc(r.name)}</b>`},
    {key:'n', label:'Sub-Themes', render:r => r.n},
    {key:'early', label:'Early', cls:r => r.early ? 'g bg-g' : 'mu', render:r => r.early, sortVal:r => r.early * 100 + r.stars, tip:'Early Rotation sub-themes (ties broken by total stars)'},
    {key:'mature', label:'Mature', cls:r => r.mature ? 'g' : 'mu', render:r => r.mature},
    {key:'mixed', label:'Mixed', cls:r => r.mixed ? 'm' : 'mu', render:r => r.mixed},
    {key:'failed', label:'Failed', cls:r => r.failed ? 'b' : 'mu', render:r => r.failed},
    {key:'stars', label:'Stars', render:r => r.stars, tip:'Sum of the sub-theme stars (0-3 each)'},
    {key:'avg', label:'Avg ★', render:r => f(r.avg,1), tip:'Average stars per sub-theme'},
    {key:'tb', label:'Theme Breadth', cls:r => tgBrCls(r.tb), render:r => tgBar(r.tb, C.accent)},
    {key:'nt', label:'Tickers', render:r => r.nt, tip:'Unique loaded tickers across the theme'},
  ];
  const scols = [
    {key:'th', label:'Theme', left:true, render:r => esc(r.th)},
    {key:'sb', label:'Sub-Theme', left:true, render:r => `<b>${esc(r.sb)}</b>`},
    {key:'sig', label:'Signal', render:r => tgBadge(r.sig), sortVal:r => tgSig(r.sig).ord},
    {key:'st', label:'Stars', render:r => tgStars(r.st), sortVal:r => r.st},
    {key:'sbr', label:'Sub-Theme Breadth', cls:r => tgBrCls(r.sbr), render:r => tgBar(r.sbr, tgSig(r.sig).color)},
    {key:'tb', label:'Theme Breadth', cls:r => tgBrCls(r.tb), render:r => f(r.tb,1)},
    {key:'nt', label:'Tickers', render:r => r.nt},
  ];
  const filt = {}, filtLbl = {}; TG_SIGS.forEach(s => { filt[s.k] = r => r.sig === s.k; filtLbl[s.k] = s.short; });
  host.innerHTML = `<h2>Theme Signals ${asof}</h2>${banner}
    <div class="kpis" style="grid-template-columns:repeat(5,1fr)">${kpi(TG.as_of || '—', 'Weekly file as of', stale ? 'bad' : '', isNum(age) ? age + ' days before the session' : '')}${TG_SIGS.map(s => kpi(sigCount(s.k), s.label, s.k === 'EARLY ROTATION' ? 'good' : s.k === 'FAILED ROTATION' ? 'bad' : '', 'of ' + TG_ROWS.length + ' sub-themes')).join('')}</div>
    <div class="tsg-grid">${tiles}</div>
    <h3>Themes</h3><div id="tsg-th-table"></div>
    <h3 style="margin-top:1.25rem">All sub-themes</h3><div id="tsg-all-table"></div>`;
  host.querySelectorAll('.tsg-tile').forEach(el => el.onclick = () => tsgGo(themes[+el.dataset.i].name));
  makeTable('tsg-th-table', tcols, TG_THEMES, {sortKey:'early', onRow:r => tsgGo(r.name), note:note + ' Click a theme to see its sub-themes.'});
  makeTable('tsg-all-table', scols, TG_ROWS, {sortKey:'sig', sortDir:1, filters:filt, filterLabels:filtLbl, onRow:r => tsgGo(r.th, r.sb), note:'Every sub-theme in the weekly file; use the buttons to list one signal across all themes. Click a row to list its tickers.'});
}
function themeSignalGuide() {
  return `<div class="card" style="margin-top:1rem"><h2 style="margin-bottom:.4rem">Theme Signals tab — the weekly theme signal</h2>
    <p class="note" style="margin:0 0 .5rem">This tab shows the weekly theme report (Weekly_Theme_Signal.csv) as it is: Signal, Stars (0-3) and the Theme / Sub-Theme Breadth figures are not recalculated here. It is independent of the Themes tab and its Theme Score. Drill down Theme → Sub-Theme → Ticker; the tickers come from the theme membership file.</p>
    <ul class="plain">
      <li><b>Early Rotation</b> — a sub-theme that has just started to lead (3 stars).</li>
      <li><b>Mature Leadership</b> — an established leader.</li>
      <li><b>Mixed / Consolidating</b> — no clear direction.</li>
      <li><b>Failed Rotation</b> — a rotation that did not hold (0 stars).</li>
    </ul>
    <p class="note">The tab badge counts the Early Rotation sub-themes. A banner appears if the file is missing or older than ${TG.stale_days || 8} days against the session date. Display only - nothing here feeds any alert or recommendation.</p></div>`;
}

// ---------- Ticker tab ----------
let currentTicker = null;
function pctRank(key, val, higherIsBetter=true) {
  const vals = ROWS.map(r => r[key]).filter(isNum); if (!isNum(val) || !vals.length) return null;
  const below = vals.filter(v => higherIsBetter ? v < val : v > val).length; return Math.round(100 * below / vals.length);
}
function narrative(r, H, ev) {
  const p = [];
  const trend = r.e200 >= 0 && r.e50 >= 0 ? 'in an established uptrend (above EMA50 and EMA200)' : r.e200 < 0 && r.e50 < 0 ? 'in a downtrend (below EMA50 and EMA200)' : r.e200 >= 0 ? 'above its EMA200 but below EMA50 — a pullback inside an uptrend' : 'above EMA50 but still below EMA200 — an early repair attempt';
  p.push(`<b>${r.t}</b> closed at ${fp(r.close)} (${f(r.ret1,2,true)}%), ${trend}.`);
  const ppo = r.ppo_d > 0 ? 'above' : 'below';
  const cross = r.sig_x === '↑' ? `A <b>bullish signal-line cross</b> fired ${fi(r.bs_pos)} bar(s) ago` : r.sig_x === '↓' ? `A <b>bearish signal-line cross</b> fired ${fi(r.bs_neg)} bar(s) ago` : `The last PPO cross was ${Math.min(r.bs_pos ?? 99, r.bs_neg ?? 99)} bars ago (${(r.bs_pos ?? 99) < (r.bs_neg ?? 99) ? 'bullish' : 'bearish'})`;
  p.push(`${cross}; PPO is ${f(r.ppo,2,true)} (${r.ppo > 0 ? 'positive' : 'negative'}) and ${ppo} its signal line.`);
  p.push(`RSI ${f(r.rsi,1)} is <b>${r.rsi_zone}</b>. Momentum ranks in the ${ord(r.mom)} percentile ${r.rank_n ? 'of the ' + r.rank_n + ' names ranked that day' + (CFG.vol_adj ? ' (volatility-adjusted)' : '') : 'vs ' + CFG.benchmark + ' history'} (trailing ${fi(r.trail)}, emerging ${fi(r.emerg)}) → Trailing/Emerging Momentum <b style="color:${regColor(r.regime)}">${r.regime}</b>.`);
  if (r.in_tr) p.push(`It has been <b>In Trend</b> for ${fi(r.tr_days)} session(s) since the Favorable alert of ${r.tr_date} at ${fp(r.tr_entry)} (<span class="${r.tr_ret < 0 ? 'bad' : 'good'}">${f(r.tr_ret,1,true)}%</span>); the trailing stop is ${fp(r.tr_stop)}, ${f(stopDown(r),1,true)}% from the close.`);
  else if (r.tr_exit) p.push(`Its trend <b>closed on this bar</b> (${r.tr_exit === 'Stop' ? 'close under the trailing stop' : 'Unfavorable / Conflicted alert'}) at ${f(r.tr_cret,1,true)}% from entry.`);
  const b = H.b, s = H.s, n = b.length;
  const db = n > 5 ? b[n-1]-b[n-6] : 0, ds = n > 5 ? s[n-1]-s[n-6] : 0;
  let verdict;
  if (r.rec === 'BUY') verdict = `Signal is <b class="good">Favorable</b> (POS ${fi(r.buy)} vs NEG ${fi(r.sell)}), driven mainly by ${topComp(r,'b')}.`;
  else if (r.rec === 'SELL') verdict = `Signal is <b class="bad">Unfavorable</b> (NEG ${fi(r.sell)} vs POS ${fi(r.buy)}), driven mainly by ${topComp(r,'s')}${r.s_floor ? ' — the fresh-cross floor is holding the score up' : ''}.`;
  else if (r.rec === 'EXIT') verdict = `Both alerts are firing within ${CFG.conflict_margin} points of each other → Signal is <b class="warn">Neutral</b>, conflicted (a whipsaw: de-risk until they disagree less).`;
  else if (r.gate) verdict = `POS Signals (${fi(r.buy)}) cleared the alert threshold, but Signal was held at <b class="warn">Watch Favorable</b> by: <b>${esc(r.gate)}</b>. This name is on the Watch list as a blocked Favorable — see Guide → Gates for what each block means.`;
  else if (r.watch) verdict = `No alert yet, but it is on the <b class="accent">Watch</b> list: ${r.watch === 'BOTH' ? 'both POS and NEG Signals are' : (r.watch === 'BUY' ? 'POS Signals' : 'NEG Signals') + ' is'} within ${CFG.watch_margin} points of the trigger.`;
  else verdict = `Signal is <b>Neutral</b> — neither side is near its trigger (POS ${fi(r.buy)}, NEG ${fi(r.sell)}).`;
  p.push(verdict + ` Over the last 5 sessions POS Signals moved ${f(db,0,true)} and NEG Signals ${f(ds,0,true)}.`);
  { const cx = (CFG.currency || []).find(x => x.t === r.t); if (cx) p.push(cx.kind === 'ref' ? `<span class="accent">${r.t} is the dollar itself: ${r.rec === 'BUY' ? 'Favorable means the dollar is strengthening' : r.rec === 'SELL' ? 'a SELL means the dollar is weakening' : 'no dollar signal right now'}.</span>` : `<span class="accent">${r.t} tracks the ${esc(cx.currency)} against the US dollar: ${r.rec === 'BUY' ? 'Favorable means the dollar is weakening against it' : r.rec === 'SELL' ? 'a SELL means the dollar is strengthening against it' : 'no dollar signal right now'}.</span>`); }
  if (r.live) p.push(`<span class="accent">This reflects the live intraday price — today's bar is still forming and will finalize at the close.</span>`);
  if (ev && ev.length) { const last = ev[ev.length-1]; p.push(`Last signal event: <b>${last.side}</b> on ${last.d} at ${fp(last.close)}${isNum(last.f10) ? ` (10d later: ${f(last.f10,1,true)}%)` : ''}. ${ev.length} event(s) in the reconstructed window.`); }
  if (!r.data_ok) p.push(`<span class="warn">Only ${r.n_bars} bars of history — alerts are disabled for this name until it reaches ${CFG.min_bars}.</span>`);
  if (r.stale) p.push(`<span class="warn">Last bar is ${r.last_bar}, older than the session date — data may be stale.</span>`);
  if (!r.tradeable) p.push(`<span class="warn">Below the liquidity/price floor (${fdv(r.dv)} · ${fp(r.close)}).</span>`);
  return p.join(' ');
}
function topComp(r, side) {
  const parts = side === 'b' ? [['PPO cross',r.b_ppo],['RSI',r.b_rsi],['EMA',r.b_ema],['persistence',r.b_per]] : [['PPO cross',r.s_ppo],['RSI',r.s_rsi],['EMA',r.s_ema],['weakness',r.s_per]];
  parts.sort((a,b) => b[1]-a[1]); return parts.filter(p => p[1] > 0).slice(0,2).map(p => `${p[0]} (${p[1]})`).join(' and ') || 'no component';
}
function fundRow(t) {
  // Fundamentals from the "Score" spreadsheet tab (display only). Nothing is drawn for names not in the sheet.
  const F = (P.fund || {})[t]; if (!F) return '';
  const v = k => F[k] !== undefined && F[k] !== '' ? esc(F[k]) : '—';
  const k1 = (val, l, tip='') => `<div class="kpi" style="cursor:default"${tip ? ` title="${tip}"` : ''}><div class="v">${val}</div><div class="l">${l}</div></div>`;
  const src = [F.rd ? 'report date ' + esc(F.rd) : '', F.upd ? 'sheet updated ' + esc(F.upd) : ''].filter(Boolean).join(' · ');
  return `<div class="kpis fund">${k1(v('qs'),'Quality Score')}${k1(v('croic'),'CROIC','Cash return on invested capital')}<div class="kpi wide" style="cursor:default"><div class="v pair"><span>${v('gp')}<small>Gross Profit</small></span><span>${v('np')}<small>Net Profit</small></span></div><div class="l">Number of Profitable Qtrs in the last 20 quarters</div></div>${k1(v('oid'),'OI/Debt','Operating income ÷ debt')}${k1(v('shr'),'Shares Chg 3Y','Change in share count over 3 years')}${k1(v('ig'),'Implied Growth')}${k1(v('pf'),'Piotroski F-Score','0–9')}</div>
    <p class="note fund-note">Fundamentals from the Quality Score sheet${src ? ' · ' + src : ''} · not used in scoring.</p>`;
}
function renderTicker(t) {
  const r = BY[t], H = P.history[t], ev = (P.scorecard.per_ticker||{})[t] || [];
  const host = document.getElementById('ticker');
  if (!r || !H) { host.innerHTML = '<div class="empty">Unknown ticker</div>'; return; }
  const n = H.d.length, lab = H.d.map(md);
  const idx = TICKERS.indexOf(t), prev = TICKERS[(idx-1+TICKERS.length)%TICKERS.length], next = TICKERS[(idx+1)%TICKERS.length];
  const evIdx = H.rec.map((x,i) => i>0 && x!==H.rec[i-1] && x!=='H' ? {i, x} : null).filter(Boolean);
  const marks = evIdx.map(e => ({i:e.i, y:H.c[e.i], color:e.x==='B'?C.good:e.x==='S'?C.bad:C.warn, shape:e.x==='S'?'down':'up', label:`${H.d[e.i]} ${e.x==='B'?'BUY':e.x==='S'?'SELL':'EXIT'} @ ${fp(H.c[e.i])}`}));
  const sqBands = []; let st = null; H.sq.forEach((v,i) => { if (v && st===null) st = i; if (!v && st!==null) { sqBands.push({from:st,to:i-1,color:C.warn}); st = null; } }); if (st!==null) sqBands.push({from:st,to:n-1,color:C.warn});
  const kpi = (v,l,cls='') => `<div class="kpi" style="cursor:default"><div class="v ${cls}">${v}</div><div class="l">${l}</div></div>`;
  const comp = (label, v, max, color) => `<span>${label}</span><div class="bar"><i style="width:${100*Math.max(0,v)/max}%;background:${color}"></i></div><span>${fi(v)}<span class="muted">/${max}</span></span>`;
  const rank = (label, key, val, hib=true, fmt=v=>f(v,1)) => { const p = pctRank(key, val, hib); return `<span>${label}</span><div class="bar"><i style="width:${p??0}%;background:${p>=70?C.good:p<=30?C.bad:C.accent}"></i></div><span>${p===null?'—':p+'%'}</span><span class="muted" style="text-align:right">${fmt(val)}</span>`; };
  const ret = (a, k) => a.length > k ? (a[a.length-1]/a[a.length-1-k]-1)*100 : null;
  const lastOf = a => { for (let i = a.length-1; i >= 0; i--) if (isNum(a[i])) return a[i]; return null; };
  const pmoH = H.pmo.map((v,i) => isNum(v) && isNum(H.pmos[i]) ? v - H.pmos[i] : null);
  const logRows = []; for (let i = n-1; i >= Math.max(0, n-CFG.log_rows); i--) { const rc = {B:'BUY',S:'SELL',E:'EXIT',H:'HOLD'}[H.rec[i]]; const r1 = i>0 ? (H.c[i]/H.c[i-1]-1)*100 : null;
    logRows.push(`<tr class="${rc}"><td class="left">${H.d[i]}</td><td>${fp(H.c[i])}</td><td class="${signCls(r1)}">${f(r1,2,true)}%</td><td>${fdv(H.v[i])}</td><td class="${rsiCls(H.rsi[i])}">${f(H.rsi[i],1)}</td><td class="${signCls(H.ppo[i])}">${f(H.ppo[i],2,true)}</td><td class="${signCls(H.h[i])}">${f(H.h[i],3,true)}</td><td class="${H.b[i]>=CFG.buy_thr?'g':''}">${H.b[i]}</td><td class="${H.s[i]>=CFG.sell_thr?'b':''}">${H.s[i]}</td><td>${badge(rc)}</td><td style="color:${regColor(REG_NAME[H.reg[i]])}">${REG_NAME[H.reg[i]]}</td><td>${f(H.mom[i],0)}</td><td>${H.sq[i]?'<span class="warn">on</span>':'<span class="muted">—</span>'}</td></tr>`); }
  const evRows = ev.slice().reverse().map(e => `<tr class="${e.side}"><td class="left">${e.d}</td><td>${badge(e.side)}</td><td>${fp(e.close)}</td><td>${e.buy}</td><td>${e.sell}</td><td style="color:${regColor(e.regime)}">${e.regime}</td>${CFG.horizons.map(h => `<td class="${signCls(e.side==='SELL' ? -(e['f'+h]??0) : e['f'+h])}">${f(e['f'+h],1,true)}%</td>`).join('')}${CFG.horizons.map(h => `<td class="${signCls(e.side==='SELL' ? -(e['x'+h]??0) : e['x'+h])}">${f(e['x'+h],1,true)}%</td>`).join('')}</tr>`).join('');
  const evStats = side => { const es = ev.filter(e => e.side===side && isNum(e.f10)); if (!es.length) return '—'; const m = es.reduce((a,e)=>a+e.f10,0)/es.length; const hit = es.filter(e => side==='SELL' ? e.f10 < 0 : e.f10 > 0).length; return `${es.length} · ${Math.round(100*hit/es.length)}% ${side==='SELL'?'fell':'rose'} · mean 10d ${f(m,2,true)}%`; };
  host.innerHTML = `
    <div class="toolbar" style="margin-bottom:.75rem"><input id="tk-pick" list="tk-list" placeholder="ticker…" style="margin:0;width:9rem;text-transform:uppercase" autocomplete="off"/><button onclick="showTicker('${prev}')">← ${prev}</button><button onclick="showTicker('${next}')">${next} →</button><button onclick="openDrawer('${t}')">Quick view</button><button onclick="exportTickerHtml('${t}')" title="Download this page as a stand-alone HTML file: ${t}_YYYY_MM_DD.html" style="background:#1f6feb;border-color:#1f6feb;color:#fff">Export HTML</button><span class="cnt">← → keys step through the universe · link: <code>#ticker/${t}</code></span></div>
    <div class="dhead" style="margin-bottom:.75rem"><span class="tk" style="font-size:2rem">${t}</span>${cn(t)}<span class="px" style="font-size:1.3rem">${fp(r.close)} <span class="${signCls(r.ret1)==='g'?'good':'bad'}">${f(r.ret1,2,true)}%</span></span>${omBadge(r)}<span style="color:${regColor(r.regime)};font-weight:600">${r.regime}</span><span class="muted">RSI ${r.rsi_zone}</span>${r.live?'<span class="badge LIVE">LIVE</span>':''}${r.sqz_on?'<span class="badge INTRADAY">SQUEEZE ON</span>':''}${r.sqz_full?'<span class="badge BUY">SQZ FULL</span>':''}${r.data_ok?'':'<span class="badge INTRADAY">SHORT HISTORY</span>'}${r.stale?'<span class="badge INTRADAY">STALE</span>':''}${r.tradeable?'':'<span class="badge INTRADAY">ILLIQUID</span>'}</div>
    ${themeLine(t, 'font-size:1rem;margin:-.25rem 0 .75rem')}
    <div class="card" style="font-size:.95rem;line-height:1.55">${narrative(r, H, ev)}</div>
    <div class="kpis">${kpi(fi(r.buy),'POS Signals', r.buy>=CFG.buy_thr?'good':'')}${kpi(fi(r.sell),'NEG Signals', r.sell>=CFG.sell_thr?'bad':'')}${kpi(f(r.bias,0,true),'Net Signals', signCls(r.bias)==='g'?'good':signCls(r.bias)==='b'?'bad':'')}${kpi(fi(isNum(r.rs) ? r.rs : r.mom),'RS Rating', pctCls(r.mom)==='g'?'good':pctCls(r.mom)==='b'?'bad':'')}${kpi(f(ret(H.c,20),1,true)+'%','20d return', signCls(ret(H.c,20))==='g'?'good':'bad')}${kpi(f(r.e200,1,true)+'%','vs EMA200', r.e200>=0?'good':'bad')}${kpi(f(r.hv,0)+'%','Hist. vol','')}${kpi(fi(r.sqz),'Squeeze strength', r.sqz>=60?'good':'')}</div>
    ${fundRow(t)}
    <div class="card"><div class="chart-title"><span>Price with EMA20 / 50 / 200 · ▲ Favorable ▼ Unfavorable events · shaded = squeeze on${CFG.trend_on ? ' · red dots = trailing stop while In Trend' : ''}</span><span class="muted">${n} sessions</span></div>${lineChart([{v:H.c,color:C.text,label:'Close',width:2},{v:H.e20,color:C.accent,dash:'4,3',label:'EMA20'},{v:H.e50,color:'#bc8cff',dash:'4,3',label:'EMA50'},{v:H.e200,color:C.warn,dash:'6,3',label:'EMA200'}].concat(CFG.trend_on && H.st && H.st.some(isNum) ? [{v:H.st,color:C.bad,dash:'2,4',label:'Trail stop',width:1.6}] : []),{w:1300,h:300,labels:lab,marks,vbands:sqBands})}
      ${volumeChart(H, lab)}</div>
    <div class="card"><div class="chart-title"><span>Swenlin PMO (${CFG.pmo[0]}/${CFG.pmo[1]}, signal ${CFG.pmo[2]}) · informational only — not used in scoring</span><span class="muted">PMO ${f(lastOf(H.pmo),2,true)} · signal ${f(lastOf(H.pmos),2,true)}</span></div>${lineChart([{v:pmoH,color:C.accent,bars:true,colorBySign:true,opacity:.45},{v:H.pmo,color:C.accent,label:'PMO',width:2},{v:H.pmos,color:C.warn,dash:'4,3',label:'Signal'}],{w:1300,h:170,labels:lab,hlines:[{y:0,color:C.muted}]})}<p class="note">Carl Swenlin's Price Momentum Oscillator: a double-smoothed 1-day rate of change. Above zero = positive momentum; PMO crossing its signal line is the usual trigger. Shown for reference only — it does not feed the POS/NEG Signals score, alerts or recommendations.</p></div>
    <div class="card"><div class="chart-title"><span>PPO, signal line and histogram</span><span class="muted">bars since ↑ ${fi(r.bs_pos)} · ↓ ${fi(r.bs_neg)}</span></div>${lineChart([{v:H.h,color:C.accent,bars:true,colorBySign:true,opacity:.55},{v:H.ppo,color:C.accent,label:'PPO'},{v:H.sig,color:C.warn,dash:'4,3',label:'Signal'}],{w:1300,h:170,labels:lab,hlines:[{y:0,color:C.muted}]})}</div>
    <div class="card"><div class="chart-title"><span>RSI(14)</span><span class="muted">${r.rsi_zone} · healthy band 40–65</span></div>${lineChart([{v:H.rsi,color:'#bc8cff',width:2}],{w:1300,h:170,min:0,max:100,labels:lab,hlines:[{y:70,color:C.warn,label:'70'},{y:30,color:C.accent,label:'30'},{y:65,color:C.grid},{y:40,color:C.grid}]})}</div>
    <div class="grid g2">
      <div class="card"><div class="chart-title"><span>POS / NEG Signals</span><span class="muted">alert lines at ${CFG.buy_thr} / ${CFG.sell_thr}</span></div>${lineChart([{v:H.b,color:C.good,label:'POS Signals',width:2,fillTo:0},{v:H.s,color:C.bad,label:'NEG Signals',width:2,fillTo:0}],{w:640,h:170,min:0,max:100,labels:lab,hlines:[{y:CFG.buy_thr,color:C.good},{y:CFG.sell_thr,color:C.bad}]})}</div>
      <div class="card"><div class="chart-title"><span>Momentum percentiles</span><span class="muted">regime bands ${CFG.regime_lo}–${CFG.regime_hi}</span></div>${lineChart([{v:H.tr,color:C.accent,label:'Trailing',width:2},{v:H.em,color:'#f2cc0c',label:'Emerging',width:2},{v:H.mom,color:C.text,dash:'3,3',label:'Blended'}],{w:640,h:170,min:0,max:100,labels:lab,hlines:[{y:CFG.regime_hi,color:C.grid},{y:CFG.regime_lo,color:C.grid}]})}</div>
    </div>
    <div class="grid g3">
      <div class="card"><h3>POS Signals <span class="good" style="float:right">${fi(r.buy)}${r.b_floor?' <span class="warn" style="font-size:.7rem">floor '+CFG.buy_floor+'</span>':''}</span></h3><div class="comp">${comp('PPO cross',r.b_ppo,35,'#58a6ff')}${comp('RSI',r.b_rsi,25,'#bc8cff')}${comp('EMA',r.b_ema,20,'#39c5cf')}${comp('Persistence',r.b_per,10,'#d2a8ff')}</div>
        <h3 style="margin-top:1rem">NEG Signals score <span class="bad" style="float:right">${fi(r.sell)}${r.s_floor?' <span class="warn" style="font-size:.7rem">floor '+CFG.sell_floor+'</span>':''}</span></h3><div class="comp">${comp('PPO cross',r.s_ppo,35,'#58a6ff')}${comp('RSI',r.s_rsi,25,'#bc8cff')}${comp('EMA',r.s_ema,20,'#39c5cf')}${comp('Weakness',r.s_per,10,'#d2a8ff')}</div>
        <p class="note">Regime weights (${r.regime}) and reliability ${f(r.rel,2)} are already applied.</p></div>
      <div class="card"><h3>Rank within universe <span class="muted" style="float:right">${ROWS.length} names</span></h3><div class="comp" style="grid-template-columns:7rem 1fr 2.5rem 4rem">${rank('Momentum %','mom',r.mom)}${rank('POS Signals','buy',r.buy,true,fi)}${rank('NEG Signals','sell',r.sell,true,fi)}${rank('Net Signals','bias',r.bias,true,v=>f(v,0,true))}${rank('vs EMA200','e200',r.e200,true,v=>f(v,1,true)+'%')}${rank('vs EMA20','e20',r.e20,true,v=>f(v,1,true)+'%')}${rank('RSI','rsi',r.rsi)}${rank('ADX','adx',r.adx)}${rank('52w position','hi52',r.hi52,true,v=>isNum(v)?f(100*v,0)+'%':'—')}${rank('Squeeze','sqz',r.sqz,true,fi)}${rank('Low vol','hv',r.hv,false,v=>f(v,0)+'%')}${rank('$ volume','dv',r.dv,true,v=>'$'+fdv(v))}</div><p class="note">Bar = share of the universe this name beats on that metric (higher is better; for volatility, lower is better).</p></div>
      <div class="card"><h3>Trend & momentum detail</h3><div class="kv">
        ${dl('PPO / signal / Δ', `${f(r.ppo,3)} / ${f(r.ppo_sig,3)} / <span class="${signCls(r.ppo_d)}">${f(r.ppo_d,3,true)}</span>`)}${dl('Signal × · Zero ×', `${arrow(r.sig_x)} · ${arrow(r.zero_x)}`)}
        ${dl('vs EMA20 / 50 / 200', `<span class="${signCls(r.e20)}">${f(r.e20,1,true)}%</span> / <span class="${signCls(r.e50)}">${f(r.e50,1,true)}%</span> / <span class="${signCls(r.e200)}">${f(r.e200,1,true)}%</span>`)}${dl('Bull stack', r.stack?'<span class="good">Yes</span>':'No')}
        ${dl('Returns 5 / 20 / 60d', `<span class="${signCls(ret(H.c,5))}">${f(ret(H.c,5),1,true)}%</span> / <span class="${signCls(ret(H.c,20))}">${f(ret(H.c,20),1,true)}%</span> / <span class="${signCls(ret(H.c,60))}">${f(ret(H.c,60),1,true)}%</span>`)}
        ${dl('Trailing / Emerging / Dormancy', `${f(r.trail)} / ${f(r.emerg)} / ${f(r.dorm)}`)}${dl('Regime confidence', f(r.regime_conf,2))}${dl('ADX · DMI', `${f(r.adx)} · ${f(r.dmi,1,true)}`)}${dl('52-week position', isNum(r.hi52)?f(100*r.hi52,1)+'%':'—')}${dl('Persistence (acf)', f(r.persist,2))}${dl('OBV slope', f(r.obv,3))}
        ${CFG.trend_on ? dl('In trend', trendCell(r)) + dl('Trailing stop', stopCell(r)) : ''}${dl('Suggested size', `<span title="${CFG.risk_pct}% of the portfolio at risk ÷ a stop ${CFG.stop_mult} × ATR away, capped at ${CFG.max_pos}%">${sizeTxt(r)}</span>`)}${dl('RS vs ' + CFG.benchmark + ' (' + CFG.rs_lookback + 'd)', `<span class="${signCls(r.rs20)}">${f(r.rs20,1,true)}%</span>`)}
        ${dl('Hist vol · ATR%', `${f(r.hv,0)}% · ${f(r.atr,2)}%`)}${dl('ATR $ · 1.5× / 2×', (() => { const atrD = isNum(r.atr) && isNum(r.close) ? (r.atr/100)*r.close : null; return isNum(atrD) ? fp(atrD) + ' · ' + fp(r.close - 1.5*atrD) + ' / ' + fp(r.close - 2*atrD) : '—'; })())}${dl('Reliability', f(r.rel,2))}${dl('$ volume (20d med.)', '$'+fdv(r.dv))}${dl('Bars · last bar', `${r.n_bars} · ${r.last_bar}`)}</div>

        <h3 style="margin-top:.75rem">Squeeze <span style="float:right">${fi(r.sqz)} ${r.sqz_full?'<span class="good">FULL</span>':''}</span></h3>
        <div class="comp" style="grid-template-columns:7rem 1fr 3rem">${comp('Foundation',r.sqz_f,20,C.accent)}${comp('Momentum',r.sqz_m,30,C.accent)}${comp('Condition',r.sqz_c,20,C.accent)}${comp('Confirmation',r.sqz_k,15,C.accent)}</div>
        <div class="chips" style="margin-top:.5rem"><span class="chip ${r.sqz_on?'warn':''}">${r.sqz_on?'ON '+r.sqz_len+'b':'off · last '+r.sqz_len+'b'}</span>${[['sq_base','Base'],['sq_rel','Release'],['sq_ppo','PPO↑'],['sq_dmi','DMI'],['sq_rsi','RSI'],['sq_room','Room'],['sq_obv','OBV'],['sq_flat','Flat']].map(([k,l]) => `<span class="chip ${r[k]?'on':'off'}">${l}</span>`).join('')}</div></div>
    </div>
    <div class="card"><h3>Signal events in window <span class="muted" style="float:right">BUY: ${evStats('BUY')} · SELL: ${evStats('SELL')}</span></h3>
      ${ev.length ? `<div class="twrap" style="max-height:340px"><table><thead><tr><th class="left">Date</th><th>Signal</th><th>Close</th><th>POS</th><th>NEG</th><th>Regime</th>${CFG.horizons.map(h=>`<th>+${h}d</th>`).join('')}${CFG.horizons.map(h=>`<th>+${h}d vs ${CFG.benchmark}</th>`).join('')}</tr></thead><tbody>${evRows}</tbody></table></div><p class="note">Forward returns are in-sample (today's model re-run over history). For Unfavorable events a negative forward return is coloured green — the exit avoided a decline. Blank = not enough bars yet.</p>` : '<div class="empty">No Favorable/Unfavorable events in the reconstructed window.</div>'}</div>
    <div class="card"><h3>Session log <span class="muted">(last ${Math.min(CFG.log_rows,n)} sessions)</span></h3><div class="twrap" style="max-height:480px"><table><thead><tr><th class="left">Date</th><th>Close</th><th>Δ%</th><th>Volume</th><th>RSI</th><th>PPO</th><th>Hist</th><th>POS</th><th>NEG</th><th>Signal</th><th>Trailing/Emerging Momentum</th><th>Mom%</th><th>Sqz</th></tr></thead><tbody>${logRows.join('')}</tbody></table></div></div>`;
  const pick = document.getElementById('tk-pick');
  pick.onchange = pick.onkeydown = e => { if (e.type === 'change' || e.key === 'Enter') { const v = pick.value.trim().toUpperCase(); if (BY[v]) showTicker(v); } };
  host.querySelectorAll('tbody tr').forEach(tr => tr.style.cursor = 'default');
}

// ---------- drawer ----------
let drawerTicker = null;
function openDrawer(t) {
  const r = BY[t]; if (!r) return;
  drawerTicker = t;
  const H = sliceH(P.history[t] || {d:[],c:[],e20:[],ppo:[],sig:[],rsi:[],b:[],s:[],rec:[]}, CFG.drawer_bars); H.d = H.d.map(md);
  const comp = (label, v, max, color) => `<span>${label}</span><div class="bar"><i style="width:${100*Math.max(0,v)/max}%;background:${color}"></i></div><span>${fi(v)}<span class="muted">/${max}</span></span>`;
  const idx = TICKERS.indexOf(t), prev = TICKERS[(idx-1+TICKERS.length)%TICKERS.length], next = TICKERS[(idx+1)%TICKERS.length];
  const recMarks = H.rec.map((x,i) => x==='B'?i:x==='S'?-i-1:null).filter(v => v!==null);
  const events = H.rec.map((x,i) => i>0 && x!==H.rec[i-1] && x!=='H' ? `${H.d[i]} ${x==='B'?'BUY':x==='S'?'SELL':'EXIT'}` : null).filter(Boolean).slice(-6);
  const sc = (P.scorecard.by_ticker||[]).find(x => x.ticker===t);
  document.getElementById('drawer').innerHTML = `
    <div class="dhead"><span class="tk">${t}</span><span class="px">${fp(r.close)} <span class="${signCls(r.ret1)==='g'?'good':'bad'}">${f(r.ret1,2,true)}%</span></span>${omBadge(r)}<span style="color:${regColor(r.regime)}">${r.regime}</span>${r.live?'<span class="badge LIVE">LIVE</span>':''}${r.data_ok?'':'<span class="badge INTRADAY">SHORT HISTORY</span>'}${r.stale?'<span class="badge INTRADAY">STALE '+r.last_bar+'</span>':''}<button class="x" onclick="closeDrawer()">✕</button></div>
    ${themeLine(t, 'font-size:.9rem;margin:-.25rem 0 .5rem')}
    <div class="dnav"><button onclick="openDrawer('${prev}')">← ${prev}</button><button onclick="openDrawer('${next}')">${next} →</button><button onclick="closeDrawer();showTicker('${t}')" style="background:#1f6feb;border-color:#1f6feb;color:#fff">Full page ↗</button><span class="muted" style="margin-left:auto;font-size:.75rem">${H.d.length} sessions · last bar ${r.last_bar}</span></div>
    <div class="mini">
      <div class="card"><div class="chart-title"><span>Close & EMA20</span></div>${lineChart([{v:H.c,color:C.text,label:'Close'},{v:H.e20,color:C.accent,dash:'4,3',label:'EMA20'}],{h:130,labels:H.d})}</div>
      <div class="card"><div class="chart-title"><span>PPO & signal</span><span class="muted">bars since ↑ ${fi(r.bs_pos)} · ↓ ${fi(r.bs_neg)}</span></div>${lineChart([{v:H.ppo,color:C.accent,label:'PPO'},{v:H.sig,color:C.warn,dash:'4,3',label:'Signal'}],{h:130,labels:H.d,hlines:[{y:0,color:C.muted}]})}</div>
      <div class="card"><div class="chart-title"><span>POS / NEG Signals</span></div>${lineChart([{v:H.b,color:C.good,label:'POS Signals'},{v:H.s,color:C.bad,label:'NEG Signals'}],{h:130,min:0,max:100,labels:H.d,hlines:[{y:CFG.buy_thr,color:C.grid,label:'alert '+CFG.buy_thr}]})}</div>
      <div class="card"><div class="chart-title"><span>RSI(14)</span><span class="muted">${r.rsi_zone}</span></div>${lineChart([{v:H.rsi,color:'#bc8cff'}],{h:130,min:0,max:100,labels:H.d,hlines:[{y:70,color:C.warn},{y:30,color:C.accent},{y:50,color:C.grid}]})}</div>
    </div>
    <div class="mini" style="margin-top:.75rem">
      <div class="card"><h3>POS Signals <span class="good" style="float:right">${fi(r.buy)}${r.b_floor?' <span class="warn" style="font-size:.7rem">floor '+CFG.buy_floor+'</span>':''}</span></h3><div class="comp">${comp('PPO cross',r.b_ppo,35,'#58a6ff')}${comp('RSI',r.b_rsi,25,'#bc8cff')}${comp('EMA',r.b_ema,20,'#39c5cf')}${comp('Persistence',r.b_per,10,'#d2a8ff')}</div></div>
      <div class="card"><h3>NEG Signals <span class="bad" style="float:right">${fi(r.sell)}${r.s_floor?' <span class="warn" style="font-size:.7rem">floor</span>':''}</span></h3><div class="comp">${comp('PPO cross',r.s_ppo,35,'#58a6ff')}${comp('RSI',r.s_rsi,25,'#bc8cff')}${comp('EMA',r.s_ema,20,'#39c5cf')}${comp('Weakness',r.s_per,10,'#d2a8ff')}</div></div>
    </div>
    <div class="mini" style="margin-top:.75rem">
      <div class="card"><h3>Trend & momentum</h3><div class="kv">
        ${dl('PPO / signal / Δ', `${f(r.ppo,3)} / ${f(r.ppo_sig,3)} / <span class="${signCls(r.ppo_d)}">${f(r.ppo_d,3,true)}</span>`)}
        ${dl('Signal cross · Zero cross', `${arrow(r.sig_x)} · ${arrow(r.zero_x)}`)}
        ${dl('vs EMA20 / 50 / 200', `<span class="${signCls(r.e20)}">${f(r.e20,1,true)}%</span> / <span class="${signCls(r.e50)}">${f(r.e50,1,true)}%</span> / <span class="${signCls(r.e200)}">${f(r.e200,1,true)}%</span>`)}
        ${dl('Bull stack', r.stack ? '<span class="good">Yes</span>' : 'No')}
        ${dl('RS Rating (trail / emerg)', `<b>${fi(isNum(r.rs) ? r.rs : r.mom)}</b> (${f(r.trail)} / ${f(r.emerg)})`)}
        ${dl('Dormancy', f(r.dorm))}${dl('ADX · DMI', `${f(r.adx)} · ${f(r.dmi,1,true)}`)}
        ${dl('52-week position', isNum(r.hi52)?f(100*r.hi52,1)+'%':'—')}${dl('Persistence (acf)', f(r.persist,2))}${dl('OBV slope', f(r.obv,3))}
      </div></div>
      <div class="card"><h3>Risk & data</h3><div class="kv">
        ${dl('Hist. vol (20d, ann.)', f(r.hv,0)+'%')}${dl('ATR %', f(r.atr,2)+'%')}${dl('Signal reliability', f(r.rel,2))}
        ${CFG.trend_on ? dl('In trend', trendCell(r)) + dl('Trailing stop', stopCell(r)) : ''}${dl('Suggested size', sizeTxt(r))}
        ${dl('$ volume (20d median)', '$'+fdv(r.dv))}${dl('Tradeable', r.tradeable?'<span class="good">Yes</span>':'<span class="bad">No</span>')}
        ${dl('Bars loaded', r.n_bars)}${dl('Data complete', r.data_ok?'<span class="good">Yes</span>':'<span class="warn">No — alerts disabled</span>')}
      </div>
      <h3 style="margin-top:.75rem">Squeeze <span style="float:right">${fi(r.sqz)} ${r.sqz_full?'<span class="good">FULL</span>':''}</span></h3>
      <div class="chips"><span class="chip ${r.sqz_on?'warn':''}">${r.sqz_on?'ON '+r.sqz_len+'b':'off · last '+r.sqz_len+'b'}</span>${[['sq_base','Base'],['sq_rel','Release'],['sq_ppo','PPO↑'],['sq_dmi','DMI'],['sq_rsi','RSI'],['sq_room','Room'],['sq_obv','OBV'],['sq_flat','Flat']].map(([k,l]) => `<span class="chip ${r[k]?'on':'off'}">${l}</span>`).join('')}</div>
      <h3 style="margin-top:.75rem">Recent signal events</h3><div class="note" style="margin:0">${events.length ? events.join(' · ') : 'none in window'}</div>
      ${sc ? `<div class="note">Scorecard: ${sc.n} Favorable events, ${f(sc.hit,0)}% hit, mean 10d ${f(sc.mean,2,true)}%</div>` : ''}
      </div>
    </div>`;
  document.getElementById('drawer').classList.add('open'); document.getElementById('overlay').classList.add('open');
  document.getElementById('drawer').scrollTop = 0;
}
function closeDrawer(){ document.getElementById('drawer').classList.remove('open'); document.getElementById('overlay').classList.remove('open'); drawerTicker = null; }

// ---------- tooltip ----------
function showTip(e, html){ const t = document.getElementById('tip'); t.innerHTML = html; t.style.display='block'; t.style.left = (e.clientX+14)+'px'; t.style.top = (e.clientY+14)+'px'; }
function hideTip(){ document.getElementById('tip').style.display='none'; }

// ---------- tabs & init ----------
// ---------- Market Health (v49) ----------
let MH_RANGE = '1M', MH_IWM = false;
const MH_RANGES = [['1W','1 week'],['1M','1 month'],['3M','3 months'],['6M','6 months'],['YTD','This year'],['1Y','1 year']];
const MH_SESSIONS = {'1W':5,'1M':21,'3M':63,'6M':126,'1Y':252};
function mhStart(pt, range) {
  const n = pt.t.length;
  if (range === 'YTD') {
    const yr = pt.t[n-1].slice(0,4);
    const i = pt.t.findIndex(d => d.startsWith(yr));
    return Math.max(0, i - 1);                     // base = last close of the prior year
  }
  return Math.max(0, n - 1 - MH_SESSIONS[range]);  // base = close N sessions ago
}
function mhFp(v, d=1) { return !isNum(v) ? '—' : (v >= 0 ? '+' : '') + (v*100).toFixed(d) + '%'; }
function mhFc(v) { return !isNum(v) ? '—' : (v >= 0 ? '+' : '−') + Math.abs(v).toFixed(2); }
function mhTile(label, val, cls='') { return `<div class="kpi" style="cursor:default"><div class="muted" style="font-size:.74rem">${label}</div><div class="${cls}" style="font-size:1.25rem;font-weight:600">${val}</div></div>`; }
function mhBar(label, v) {
  if (!isNum(v)) return '';
  return `<div style="margin:.55rem 0"><div style="display:flex;justify-content:space-between;font-size:.82rem"><span>${label}</span><b>${(v*100).toFixed(1)}%</b></div><div style="height:8px;border-radius:99px;background:var(--card2);margin-top:.25rem"><div style="height:8px;border-radius:99px;background:var(--accent);width:${Math.min(100, v*100)}%"></div></div></div>`;
}
function mhPaths(M) {
  const pt = M.paths, s = mhStart(pt, MH_RANGE), n = pt.t.length;
  const rebase = a => a.slice(s).map(v => v / a[s] * 100);
  const defs = [['spx','S&P (SPX)',C.text,true],['ew','Equal-weight (SPXEW)',C.accent,true],['exai','$SPXXAI (ex-AI)',C.warn,!!pt.exai],['qqq','Nasdaq 100 (QQQ)',C.good,true],['iwm','Russell 2000 (IWM)',C.muted,MH_IWM]].filter(d => d[3] && pt[d[0]]);
  const series = defs.map(([k,l,c]) => ({v:rebase(pt[k]), color:c, label:l, width:k==='spx'?2.4:1.6}));
  const short = n - s <= 70;
  const labels = pt.t.slice(s).map(d => short ? d.slice(5) : d.slice(2,7));
  const tiles = defs.map(([k,l,c]) => { const r = pt[k][n-1] / pt[k][s] - 1; return mhTile(l, mhFp(r, 2), r >= 0 ? 'good' : 'bad'); }).join('');
  return {chart: lineChart(series, {w:900, h:320, labels}), tiles, from: pt.t[s], to: pt.t[n-1], sessions: n-1-s};
}
function mhBreadthCard(B) {
  const H = B && B.history;
  if (!B || !B.ok || !H || !H.d || H.d.length < 30) return '';
  const n = H.d.length;
  let s;
  if (MH_RANGE === 'YTD') { const yr = H.d[n-1].slice(0,4); s = Math.max(0, H.d.findIndex(d => d.startsWith(yr)) - 1); }
  else s = Math.max(0, n - 1 - MH_SESSIONS[MH_RANGE]);
  const short = n - s <= 70, labels = H.d.slice(s).map(d => short ? d.slice(5) : d.slice(2,7));
  const base = H.ad[s], ad = H.ad.slice(s).map(v => v - base), chg = ad[ad.length-1];
  const ln = (k, col, lab) => ({v:H[k].slice(s), color:col, label:lab, width:1.6});
  const last = k => H[k][n-1];
  const pf = v => isNum(v) ? v.toFixed(0) + '%' : '—';
  return `<div class="card" style="margin-top:1rem"><div class="chart-title"><span><b>Breadth over time</b> · ${B.universe} stocks · ${H.d[s]} → ${H.d[n-1]} · same range buttons as above</span></div>
    <div class="grid g2">
      <div><div class="note" style="margin-top:0"><b>A/D line</b>: running total of stocks up minus stocks down. Change over this view: <b class="${chg >= 0 ? 'good' : 'bad'}">${f(chg,0,true)}</b>. If the S&amp;P climbs while this line falls, fewer stocks are carrying the move.</div>
        ${lineChart([{v:ad, color:C.accent, label:'A/D line (change)', width:2, fillTo:0}], {w:440, h:200, labels, hlines:[{y:0, color:C.muted}]})}</div>
      <div><div class="note" style="margin-top:0"><b>Share of stocks above their average</b>. Below 50% on the 50-day means most stocks are in a short-term downtrend; above 80% is stretched.</div>
        ${lineChart([ln('p20',C.warn,'20-day'), ln('p50',C.accent,'50-day'), ln('p200',C.good,'200-day')], {w:440, h:200, labels, min:0, max:100, hlines:[{y:50, color:C.muted}]})}</div>
    </div>
    <div class="grid" style="grid-template-columns:repeat(auto-fit,minmax(130px,1fr));margin-top:.6rem">${mhTile('Advancers today', H.adv, 'good')}${mhTile('Decliners today', H.dec, 'bad')}${mhTile('Above 20-day', pf(last('p20')))}${mhTile('Above 50-day', pf(last('p50')))}${mhTile('Above 200-day', pf(last('p200')))}</div>
    <div class="note">Counts only the individual stocks on your watchlist (ETFs and funds are left out), using today's list. It describes your own names, so it will not match the NYSE advance/decline line or a market-wide breadth reading.</div></div>`;
}
// v54: market gate, now and over time (the gate that blocks Favorable ratings in a weak market)
function mhGate() {
  const G = P.gate;
  if (!G || !G.on) return '';
  if (!G.ok) return G.mode === 'breadth' ? `<div class="card" style="margin-top:1rem"><h3>Market gate</h3><div class="empty">Gate history did not load (${CFG.benchmark} missing from this run).</div></div>` : `<div class="card" style="margin-top:1rem"><h3>Market gate</h3><div class="note" style="margin:0">Running the legacy rule (<code>market_gate_mode = "legacy"</code>): closed when ${CFG.benchmark}${CFG.regime_both ? ' and ' + CFG.regime_confirm : ''} are rated Unfavorable or in a Weak / Mature/Cooling regime. No history strip for this mode.</div></div>`;
  const N = G.now, n = G.d.length;
  const yn = (v, bad='below', good='above') => v === null || v === undefined ? '<span class="muted">n/a</span>' : v ? `<span class="bad">${bad}</span>` : `<span class="good">${good}</span>`;
  const brd = N.n >= G.min_names;
  let strip = '';
  G.closed.forEach((c, i) => { strip += `<rect x="${i}" y="0" width="1.02" height="10" fill="${c ? C.bad : C.good}" opacity="${c ? .95 : .55}"><title>${G.d[i]}: ${c ? 'CLOSED (' + [G.idx[i] ? 'index under 200-day' : '', G.brd[i] ? 'breadth washed out' : ''].filter(Boolean).join(' + ') + ')' : 'open'}${isNum(G.pct200[i]) ? ' · ' + G.pct200[i] + '% above 200-day, ' + G.pct50[i] + '% above 50-day' : ''}</title></rect>`; });
  let runs = 0; G.closed.forEach((c, i) => { if (c && (i === 0 || !G.closed[i-1])) runs++; });
  let streak = 0; for (let i = n - 1; i >= 0 && G.closed[i] === G.closed[n-1]; i--) streak++;
  return `<div class="card" style="margin-top:1rem"><div class="chart-title"><span><b>Market gate</b> · blocks every Favorable rating while it is closed (Country ETF and Currency funds are exempt)</span><span class="muted">${G.d[0]} → ${G.d[n-1]} · ${G.sessions} sessions</span></div>
    <div class="grid" style="grid-template-columns:repeat(auto-fit,minmax(150px,1fr));margin:.5rem 0 .7rem">
      ${mhTile('Gate now', N.closed ? 'CLOSED' : 'OPEN', N.closed ? 'bad' : 'good')}
      ${mhTile('In this state for', streak + (streak === 1 ? ' session' : ' sessions'))}
      ${mhTile('Closed, share of sessions', fi(G.pct_closed) + '%', G.pct_closed >= 40 ? 'warn' : '')}
      ${mhTile('Closed spells', runs)}
      ${mhTile(CFG.benchmark + ' vs 200-day', yn(N.spy_below))}
      ${CFG.regime_both ? mhTile(CFG.regime_confirm + ' vs 200-day', yn(N.rsp_below)) : ''}
      ${mhTile('Stocks above 200-day', brd ? fi(N.pct200) + '%' : 'n/a', brd && N.pct200 < G.min200 ? 'bad' : '')}
      ${mhTile('Stocks above 50-day', brd ? fi(N.pct50) + '%' : 'n/a', brd && N.pct50 < G.min50 ? 'bad' : '')}
    </div>
    <svg viewBox="0 0 ${n} 10" preserveAspectRatio="none" style="width:100%;height:26px;border-radius:4px;display:block">${strip}</svg>
    <div style="display:flex;justify-content:space-between;font-size:.72rem" class="muted"><span>${G.d[0]}</span><span><span style="color:${C.good}">■</span> open · <span style="color:${C.bad}">■</span> closed · hover a day for the reason</span><span>${G.d[n-1]}</span></div>
    <div class="note">The gate closes when <b>either</b> test fails: (1) the index trend: ${CFG.benchmark}${CFG.regime_both ? ' <b>and</b> ' + CFG.regime_confirm + ' (equal-weight S&amp;P) both close' : ' closes'} under the 200-day EMA; (2) breadth is washed out: fewer than ${G.min200}% of your stocks are above their 200-day EMA <b>and</b> fewer than ${G.min50}% are above their 50-day EMA${brd ? ` (${N.n} stocks counted today)` : ` (not judged today: fewer than ${G.min_names} stocks with a bar on this date)`}. A name in Dormant→Waking with a full squeeze setup is still let through. Settings: <code>market_gate_mode</code>, <code>gate_breadth_200_min</code>, <code>gate_breadth_50_min</code>.</div></div>`;
}

// v52: SPY / QQQ / RSP cards (moved from the old Overview tab)
function mhContext() {
  const cards = (CFG.context || []).map(t => { const r = BY[t]; const H = P.history[t]; if (!r || !H) return '';
    const Hc = sliceH(H, CFG.drawer_bars);
    return `<div class="card acard" data-t="${t}" style="cursor:pointer"><div><div class="t">${t}${cn(t)} ${omBadge(r)} <span class="sub">${r.regime}</span></div>${themeLine(t)}
      <div class="sub">${fp(r.close)} <span class="${signCls(r.ret1)==='g'?'good':'bad'}">${f(r.ret1,2,true)}%</span> · RSI ${f(r.rsi)} · PPO ${f(r.ppo,2,true)} ${arrow(r.sig_x)}</div>
      <div class="chips"><span class="chip ${r.e20>=0?'on':'off'}">EMA20 ${f(r.e20,1,true)}%</span><span class="chip ${r.e50>=0?'on':'off'}">EMA50 ${f(r.e50,1,true)}%</span><span class="chip ${r.e200>=0?'on':'off'}">EMA200 ${f(r.e200,1,true)}%</span></div></div>
      <div>${sparkline(Hc.c, {w:150,h:44,fill:true})}<div class="sub" style="text-align:right">${Hc.d.length}d close</div></div></div>`; }).join('');
  return cards ? `<div class="ctx" style="margin-top:1rem">${cards}</div>` : '';
}
// v52: Breadth, Net Signals, Regime and RSI charts (moved from the old Overview tab)
function mhCharts() {
  const K = P.kpis, Bq = P.breadth || {d:[], pct200:[]};
  const bd = (Bq.d || []).map(md);
  const biasColor = v => v > 10 ? C.good : v < -10 ? C.bad : C.muted;
  const brd = bd.length ? lineChart([{v:Bq.pct200,color:C.accent,fillTo:0,label:'% > EMA200'}],{h:150,min:0,max:100,labels:bd,hlines:[{y:50,color:C.muted}]}) : '<div class="empty">No data</div>';
  return `<div class="grid g2" style="margin-top:1rem">
    <div class="card"><div class="chart-title"><span>Breadth: % of stocks above EMA200 (model, last ${bd.length} sessions)</span><span class="muted">${Bq.n || 0} stocks</span></div>${brd}</div>
    <div class="card"><div class="chart-title"><span>Net Signals distribution (POS − NEG)</span><span class="muted">${ROWS.length} names</span></div>${histogram(ROWS.map(r=>r.bias),{min:-100,max:100,bins:20,colorAt:biasColor,vlines:[{x:0,color:C.text}]})}</div>
    <div class="card"><div class="chart-title"><span>Regime distribution</span><span class="muted">${ROWS.length} names</span></div>${barChart(REGIMES.map(k => ({label:k, v:K.regimes[k]||0, color:regColor(k)})),{h:160})}</div>
    <div class="card"><div class="chart-title"><span>RSI(14) distribution</span><span class="muted">healthy 40–65 shaded</span></div>${histogram(ROWS.map(r=>r.rsi),{min:0,max:100,bins:20,bands:[{from:40,to:65,color:C.accent}],vlines:[{x:70,color:C.warn,label:'70'},{x:80,color:C.bad,label:'80'}]})}</div>
  </div>`;
}
function renderMarket() {
  const host = document.getElementById('market');
  const M = P.market;
  if (!M || !M.ok) { host.innerHTML = `<h2>Market Health</h2><div class="warnbox">Market Health data did not load${M && M.error ? ': ' + esc(M.error) : ''}. The rest of the dashboard is unaffected.</div>${mhGate()}`; return; }
  const X = M.ex_ai || {}, B = M.breadth || {};
  const pc = M.paths ? mhPaths(M) : null;
  const pos = n => ((Math.max(-1, Math.min(1, n)) + 1) / 2 * 100) + '%';
  const sectorRows = (M.sectors || []).map(s => `<div style="margin:.7rem 0"><div style="display:flex;justify-content:space-between;font-size:.84rem"><span class="${s.called ? '' : 'muted'}">${esc(s.name)} <span class="muted" style="font-size:.72rem">${s.symbol}</span></span><span class="${s.latest < 0.15 ? 'bad' : ''}" style="font-variant-numeric:tabular-nums">${mhFc(s.latest)} <span class="muted" style="font-size:.72rem">z ${f(s.z,1,true)}</span></span></div>
      <div style="position:relative;height:8px;border-radius:99px;background:var(--card2);margin-top:.3rem"><span style="position:absolute;left:50%;top:-3px;bottom:-3px;width:1px;background:var(--border)"></span>
      <span title="${M.history_label} average ${mhFc(s.average)}" style="position:absolute;top:50%;left:${pos(s.average)};width:9px;height:9px;border-radius:50%;background:var(--mild);transform:translate(-50%,-50%)"></span>
      <span title="now ${mhFc(s.latest)}" style="position:absolute;top:50%;left:${pos(s.latest)};width:11px;height:11px;border-radius:50%;background:${s.latest < s.average - 0.15 ? 'var(--bad)' : 'var(--text)'};transform:translate(-50%,-50%)"></span></div></div>`).join('');
  const share = v => isNum(v) && B.universe ? (v / B.universe * 100).toFixed(0) + '%' : '—';
  const net = isNum(B.new_highs) && isNum(B.new_lows) ? B.new_highs - B.new_lows : null;
  const breadthHtml = B.ok ? `<div class="grid g3" style="margin-top:.6rem">${mhTile('5-day new highs', B.new_highs)}${mhTile('5-day new lows', B.new_lows)}${mhTile('5-day net', f(net,0,true), net < 0 ? 'bad' : 'good')}</div>
      <div class="grid g3" style="margin-top:.6rem">${mhTile('Above 20-day', share(B.above20))}${mhTile('Above 50-day', share(B.above50))}${mhTile('Above 200-day', share(B.above200))}</div>` : `<div class="empty">Breadth did not load${B.error ? ': ' + esc(B.error) : ''}.</div>`;
  host.innerHTML = `<h2>Market Health <span class="muted" style="font-size:.8rem;font-weight:400">as of ${M.as_of}</span></h2>
    ${M.note ? `<div class="warnbox">${esc(M.note)}</div>` : ''}
    ${pc ? `<div class="card"><div class="chart-title"><span><b>The S&amp;P (SPX) and the market under it</b> · each line starts at 100 · ${pc.from} → ${pc.to} (${pc.sessions} sessions)</span></div>
      <div class="toolbar" id="mh-tb">${MH_RANGES.map(([k,l]) => `<button data-r="${k}" class="${MH_RANGE===k?'on':''}">${l}</button>`).join('')}<button id="mh-iwm" class="${MH_IWM?'on':''}">Small caps (IWM)</button></div>
      ${pc.chart}
      <div class="grid" style="grid-template-columns:repeat(auto-fit,minmax(150px,1fr));margin-top:.6rem">${pc.tiles}</div>
      <div class="note">$SPXXAI is the S&amp;P with ${X.available ? 'the ' + X.names.length + ' large AI stocks (' + X.names.map(n => n.ticker).join(', ') + ') removed' : 'the large AI stocks removed (not available this run)'}. Equal-weight (SPXEW) gives every company the same weight. ${X.available ? `Over the last 3 months those AI stocks, at their S&amp;P weight (${(X.weight*100).toFixed(1)}%), contributed ${(X.contribution63*100).toFixed(1)} points of the S&amp;P's ${mhFp(X.spx63)} move; the rest of the index returned ${mhFp(X.rest63)}.` : ''}</div></div>` : ''}
    ${mhGate()}
    ${mhContext()}
    ${mhBreadthCard(B)}
    ${mhCharts()}
    <div class="grid g2" style="margin-top:1rem">
      <div class="card"><h3>Sectors against the S&amp;P (SPX)</h3>
        <div class="note" style="margin-top:0">${M.window}-session correlation of each sector with the S&amp;P. Scale −1 to +1; left of centre the sector moves against the S&amp;P. <span style="color:var(--mild)">●</span> ${M.history_label} average · <b>●</b> now (red when well below its average). Energy, Staples, Utilities and Health Care are shown brighter.</div>
        ${sectorRows || '<div class="empty">Sector data did not load.</div>'}</div>
      <div>
        <div class="card"><h3>Breadth${B.ok ? ` <span class="muted">${B.universe} stocks</span>` : ''}</h3><div class="note" style="margin-top:0">Individual stocks on your watchlist only; ETFs and funds are left out. New highs / lows are the five-day total of closes at a 52-week high or low. Above 20/50/200-day is the share of those stocks closing above that average.</div>${breadthHtml}</div>
      </div></div>
    <div class="note">Built from public prices (Yahoo Finance); index weights for $SPXXAI come from State Street / iShares holdings. For information only. Apart from the Market gate card, which reports the gate the signals already use, nothing here changes any score, signal or alert.</div>`;
  host.querySelectorAll('#mh-tb button[data-r]').forEach(b => b.onclick = () => { MH_RANGE = b.dataset.r; renderMarket(); });
  const iw = document.getElementById('mh-iwm'); if (iw) iw.onclick = () => { MH_IWM = !MH_IWM; renderMarket(); };
  host.querySelectorAll('.card .pt').forEach(el => el.onclick = () => { showTab('rank'); TABLES['rank-table'].q = el.dataset.k; renderTable('rank-table'); });
}

const TABS = [['market','Market Health'],['changes','Changes'],['ticker','Ticker'],['signals','Signals'],['ppo','PPO'],['themes','Themes'],['tsig','Theme Signals'],['sectors','Sectors'],['sixpack','Six Pack'],['etfs','ETFs'],['bonds','Bonds'],['tear',"Tear's Short List"],['shortlist',"Frank's Short List"],['country','Country ETFs'],['currency','Currency'],['rank','Rankings'],['sqz','Squeeze'],['rotation','Rotation'],['scorecard','Scorecard'],['health','Health'],['guide','Guide']];
function showTab(id) {
  if (id === 'ticker' && !currentTicker) { showTicker(TK_DEFAULT()); return; }
  document.querySelectorAll('main section').forEach(s => s.classList.toggle('active', s.id === id));
  document.querySelectorAll('nav button').forEach(b => b.classList.toggle('active', b.dataset.id === id));
  try { history.replaceState(null, '', '#' + (id === 'ticker' && currentTicker ? 'ticker/' + currentTicker : id)); } catch(e) {}
  window.scrollTo({top:0});
}
function exportTickerHtml(t) {
  // Stand-alone snapshot of the rendered Ticker page: charts are inline SVG, so the file needs
  // no history file, no scripts and no network. Named TICKER_YYYY_MM_DD.html.
  const d = new Date(), p2 = n => String(n).padStart(2, '0');
  const stamp = d.getFullYear() + '_' + p2(d.getMonth()+1) + '_' + p2(d.getDate());
  const sec = document.getElementById('ticker').cloneNode(true);
  sec.querySelectorAll('.toolbar').forEach(e => e.remove());       // navigation / buttons are not part of the snapshot
  sec.classList.add('active');
  sec.querySelectorAll('[onclick]').forEach(e => e.removeAttribute('onclick'));
  // v39: append the Interpretation Guide (copied from the rendered Guide tab) after the Ticker page
  const gsrc = document.getElementById('guide');
  let guideHtml = '';
  if (gsrc) {
    const g = gsrc.cloneNode(true);
    g.removeAttribute('id');
    g.classList.add('active');
    g.querySelectorAll('[onclick]').forEach(e => e.removeAttribute('onclick'));
    guideHtml = '<div class="guide-export" style="margin-top:2rem;padding-top:1rem;border-top:2px solid var(--border)">' +
      '<p class="note" style="margin:0 0 .5rem">Reference: interpretation guide for the scores, regimes and charts shown above.</p>' +
      g.outerHTML + '</div>';
  }
  const css = Array.from(document.querySelectorAll('head style')).map(x => x.textContent).join('\n');
  const html = '<!DOCTYPE html>\n<html lang="en"><head><meta charset="utf-8"/>' +
    '<meta name="viewport" content="width=device-width, initial-scale=1"/>' +
    '<title>' + esc(t) + '_' + stamp + '</title><style>' + css +
    '\nbody{padding:0}main{max-width:1400px;margin:0 auto}tbody tr{cursor:default}section.active{display:block}</style></head><body>' +
    '<main><p class="note" style="margin:.75rem 0">Snapshot of <b>' + esc(t) + '</b> · session ' + esc(P.as_of) +
    ' · dashboard generated ' + esc(P.run_ts) + ' · exported ' + d.getFullYear() + '-' + p2(d.getMonth()+1) + '-' + p2(d.getDate()) +
    ' · static copy (Watchlist Momentum ' + esc(P.version) + ')</p>' +
    '<p class="note" style="margin:0 0 .75rem"><b>For information only. Not Investment Advice. Copyright © Frank Hayes</b></p>' + sec.outerHTML + guideHtml + '</main></body></html>';
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([html], {type:'text/html;charset=utf-8'}));
  a.download = t + '_' + stamp + '.html';
  document.body.appendChild(a); a.click(); a.remove();
  setTimeout(() => URL.revokeObjectURL(a.href), 4000);
}
function showTicker(t) { t = (t||'').toUpperCase(); if (!BY[t]) return; currentTicker = t; renderTicker(t); showTab('ticker'); }
const TK_DEFAULT = () => { const r = ROWS.slice().sort(byBias)[0]; return r ? r.t : TICKERS[0]; };
function init() {
  const K = P.kpis, H = P.health;
  const nChg = P.changes.new_buy.length + P.changes.new_sell.length + P.changes.new_exit.length + P.changes.dropped.length;
  const counts = {ppo:ROWS.filter(r => r.sig_x !== '—').length, signals:K.buy+K.sell+K.exit, sectors:CFG.sectors.filter(x => BY[x.t] && BY[x.t].rec !== 'HOLD').length, sixpack:(CFG.six_pack||[]).filter(x => BY[x.t] && BY[x.t].rec !== 'HOLD').length, etfs:(CFG.etfs||[]).filter(x => BY[x.t] && BY[x.t].rec !== 'HOLD').length, tear:(CFG.tear||[]).filter(x => BY[x.t] && BY[x.t].rec !== 'HOLD').length, shortlist:(CFG.shortlist||[]).filter(x => BY[x.t] && BY[x.t].rec !== 'HOLD').length, country:(CFG.country_etfs||[]).filter(x => BY[x.t] && BY[x.t].rec !== 'HOLD').length, currency:(CFG.currency||[]).filter(x => BY[x.t] && BY[x.t].rec !== 'HOLD').length, changes:nChg, health:H.skipped.length+H.stale.length+H.notes.length, sqz:ROWS.filter(r=>r.sqz_full).length, tsig:TG_ROWS.filter(r => r.sig === 'EARLY ROTATION').length};
  document.getElementById('nav').innerHTML = TABS.map(([id,l],i) => `<button data-id="${id}" onclick="showTab('${id}')">${l}${counts[id]?`<span class="n">${counts[id]}</span>`:''}</button>`).join('');
  document.getElementById('hdr-meta').innerHTML = `Session <b>${P.as_of}</b> · ${K.n} tickers · generated ${esc(P.run_ts)}${H.live_bars && H.live_bars.length ? ' · <span class="badge LIVE">'+H.live_bars.length+' live</span>' : ''}${H.partial_dropped.length?' · <span class="badge INTRADAY">partial bars dropped</span>':''}`;
  document.getElementById('foot').textContent = `Watchlist Momentum ${P.version} · benchmark ${CFG.benchmark} · ${esc(H.source)} · charts are inline SVG (no external resources) · For information only. Not Investment Advice. Copyright © Frank Hayes`;
  document.getElementById('tk-list').innerHTML = TICKERS.map(t => `<option value="${t}"${coName(t) ? ` label="${esc(t + ' — ' + coName(t))}"` : ''}>`).join('');
  if (P.hist_state === 'missing' || P.hist_state === 'stale') document.querySelector('main').insertAdjacentHTML('afterbegin', `<div class="warnbox"><b>${P.hist_state === 'missing' ? 'History file not found.' : 'History file is from a different run.'}</b> Keep the dashboard HTML and its <code>.history.js</code> file in the same folder (they are written together). Charts, sparklines and the Ticker tab need it.</div>`);
  renderMarket(); renderChanges(); renderSignals(); renderPPO(); renderThemes(); renderThemeSignals(); renderSectors(); renderSixPack(); renderEtfs(); renderBonds(); renderTear(); renderShortlist(); renderCountryEtfs(); renderCurrency(); renderRank(); renderSqueeze(); renderRotation(); renderScorecard(); renderHealth(); renderGuide();
  // global click → drawer
  document.body.addEventListener('click', e => { const el = e.target.closest('.tkl,.acard'); if (el && el.dataset.t) { e.stopPropagation(); openDrawer(el.dataset.t); } });
  const jump = document.getElementById('jump');
  jump.addEventListener('change', () => { const t = jump.value.trim().toUpperCase(); if (BY[t]) { openDrawer(t); jump.value=''; } });
  jump.addEventListener('keydown', e => { if (e.key==='Enter') { const t = jump.value.trim().toUpperCase(); if (BY[t]) { (e.shiftKey || document.getElementById('ticker').classList.contains('active')) ? showTicker(t) : openDrawer(t); jump.value=''; } } });
  document.addEventListener('keydown', e => {
    if (e.target.tagName === 'INPUT') { if (e.key==='Escape') e.target.blur(); return; }
    if (e.key === '/') { e.preventDefault(); jump.focus(); }
    else if (e.key === 'Escape') closeDrawer();
    else if (/^[1-9]$/.test(e.key) && TABS[+e.key-1]) showTab(TABS[+e.key-1][0]);
    else if (drawerTicker && (e.key==='ArrowLeft'||e.key==='ArrowRight')) { const i = TICKERS.indexOf(drawerTicker); openDrawer(TICKERS[(i+(e.key==='ArrowRight'?1:-1)+TICKERS.length)%TICKERS.length]); }
    else if (currentTicker && document.getElementById('ticker').classList.contains('active') && (e.key==='ArrowLeft'||e.key==='ArrowRight')) { const i = TICKERS.indexOf(currentTicker); showTicker(TICKERS[(i+(e.key==='ArrowRight'?1:-1)+TICKERS.length)%TICKERS.length]); }
  });
  const h = (location.hash||'').slice(1);
  if (h.startsWith('ticker/')) showTicker(h.slice(7)); else showTab(TABS.some(t => t[0]===h) ? h : 'market');
}
init();
</script>
</body>
</html>
"""


def split_history(payload: dict) -> tuple[dict, dict]:
    """(payload without the per-ticker history, the history itself)."""
    slim = dict(payload)
    hist = slim.pop("history", {}) or {}
    return slim, hist


def build_history_js(history: dict, run_ts: str) -> str:
    """JS file that defines window.__MOMENTUM_HISTORY__ (loaded via <script src>)."""
    body = dumps_js({"run": run_ts, "data": history})
    return "window.__MOMENTUM_HISTORY__=" + body + ";\n"


def build_html(payload: dict, history_src: str | None = None) -> str:
    """history_src=None -> history stays embedded in the HTML (single file).
    history_src='x.history.js' -> history is expected in that sibling file."""
    tag = ""
    if history_src:
        payload, _ = split_history(payload)
        tag = f'<script src="{history_src}"></script>\n'
    js = dumps_js(payload).replace("</", "<\\/")      # never terminate the <script> early
    return (DASHBOARD_TEMPLATE.replace("__VERSION__", VERSION)
            .replace("__HISTORY_TAG__", tag).replace("__PAYLOAD__", js))


# =============================================================================
#  7. SELF-TESTS
# =============================================================================

def _ref_rsi(close: np.ndarray, n: int = 14) -> float:
    """Slow, textbook Wilder RSI for the last bar."""
    d = np.diff(close)
    up, dn = np.maximum(d, 0), np.maximum(-d, 0)
    au, ad = up[:n].mean(), dn[:n].mean()
    for i in range(n, len(d)):
        au = (au * (n - 1) + up[i]) / n
        ad = (ad * (n - 1) + dn[i]) / n
    return 100 - 100 / (1 + au / ad) if ad else 100.0


def _ref_ema(x: np.ndarray, n: int) -> float:
    k = 2 / (n + 1)
    e = x[0]
    for v in x[1:]:
        e = v * k + e * (1 - k)
    return e


def selftest() -> int:
    """Indicator cross-checks, config validation and scoring invariants."""
    fails = 0

    def check(name, cond, detail=""):
        nonlocal fails
        if cond:
            log_ok(name)
        else:
            fails += 1
            log_warn(f"FAIL {name} {detail}")

    cfg = Config()
    px = synthetic_prices(["AAA"], n_bars=400, seed=3)["AAA"]
    c = px["close"]

    # --- indicators vs reference loops
    r_fast = rsi(c, 14).iloc[-1]
    r_ref = _ref_rsi(c.to_numpy(), 14)
    check("RSI(14) matches Wilder reference", abs(r_fast - r_ref) < 0.05, f"{r_fast:.3f} vs {r_ref:.3f}")
    e_fast = ema(c, 20).iloc[-1]
    e_ref = _ref_ema(c.to_numpy(), 20)
    check("EMA(20) matches recursive reference", abs(e_fast - e_ref) / e_ref < 1e-4, f"{e_fast:.4f} vs {e_ref:.4f}")
    y = pd.Series(np.arange(50, dtype=float) * 2.5 + 7)
    check("rolling_slope recovers a known slope", abs(rolling_slope(y, 20).iloc[-1] - 2.5) < 1e-9)
    check("rolling_linreg_last hits the line end", abs(rolling_linreg_last(y, 20).iloc[-1] - y.iloc[-1]) < 1e-9)
    ref_slope = np.polyfit(np.arange(20), c.to_numpy()[-20:], 1)[0]
    check("rolling_slope matches np.polyfit on prices", abs(rolling_slope(c, 20).iloc[-1] - ref_slope) < 1e-6)
    r_acf = np.corrcoef(c.pct_change().to_numpy()[-21:-1], c.pct_change().to_numpy()[-20:])[0, 1]
    check("trend_persistence equals lag-1 autocorrelation", abs(trend_persistence(c, 20).iloc[-1] - r_acf) < 1e-9)
    ad = adx_dmi(px["high"], px["low"], c, 14)
    check("ADX/DMI in range", ad["ADX"].dropna().between(0, 100).all() and ad["DMP"].dropna().between(0, 100).all())
    # Swenlin PMO vs a plain recursive reference
    cv = c.to_numpy(); roc = (cv[1:] / cv[:-1] - 1.0) * 100.0
    s1 = roc[0]; p = 10 * s1; pm = [np.nan]; warm = cfg.pmo_roc_len + cfg.pmo_smooth_len
    pm.append(p)
    for r_ in roc[1:]:
        s1 += (2.0 / cfg.pmo_roc_len) * (r_ - s1)
        p += (2.0 / cfg.pmo_smooth_len) * (10 * s1 - p)
        pm.append(p)
    pm = np.array(pm); pm[:warm] = np.nan
    k = 2.0 / (cfg.pmo_sig_len + 1); sg = pm[warm]
    for v_ in pm[warm + 1:]:
        sg += k * (v_ - sg)
    pmo_df = pmo_block(c, cfg)
    check("Swenlin PMO matches recursive reference", abs(pmo_df["PMO"].iloc[-1] - pm[-1]) < 1e-9 and abs(pmo_df["PMO_Signal"].iloc[-1] - sg) < 1e-9,
          f"{pmo_df['PMO'].iloc[-1]:.6f} vs {pm[-1]:.6f}")
    fr = compute_indicator_frame(px, cfg)
    check("indicator frame has no ±inf", np.isfinite(fr.select_dtypes("number").fillna(0).to_numpy()).all())
    sq = squeeze_block(px, cfg)
    check("squeeze on/off are mutually exclusive", ((sq["Squeeze_On"] + sq["Squeeze_Off"]) <= 1).all())
    check("bars_since counts up from events", bars_since(pd.Series([0, 1, 0, 0, 1, 0])).tolist()[1:] == [0, 1, 2, 0, 1])

    # --- config validation
    try:
        Config(tickers=["A", "a", "B"])
        dup = Config(tickers=["A", "a", "B"])
        check("duplicate tickers de-duplicated case-insensitively", dup.core_tickers[:2] == ["A", "B"] and dup.warnings)
        check("sector + six pack lists merged into the data pull",
              all(t in dup.tickers for t in list(dup.sector_names) + list(dup.six_pack))
              and not any(t in dup.core_tickers for t in list(dup.sector_names) + list(dup.six_pack)))
        check("six pack has no Blend column", len(dup.six_pack) == 6
              and {v[1] for v in dup.six_pack.values()} == {"Growth", "Value"})
        check("ETF list is merged into the pull and kept out of the main list",
              len(dup.etf_tickers) >= 1 and all(t in dup.tickers for t in dup.etf_tickers)
              and not any(t in dup.core_tickers for t in dup.etf_tickers))
        check("Country ETF list is merged into the pull, kept out of the main list, with full fund names",
              len(dup.country_etfs) >= 40 and all(t in dup.tickers for t in dup.country_etfs)
              and not any(t in dup.core_tickers for t in dup.country_etfs)
              and all(isinstance(v, tuple) and len(v) == 2 and len(v[1]) > 10 for v in dup.country_etfs.values()))
        check("Tear's Short List is merged into the pull, de-duplicated, and stays in the main list",
              len(dup.tear_tickers) == 39 and all(t in dup.tickers for t in dup.tear_tickers)
              and all(t in dup.core_tickers or t in dup.etf_tickers for t in dup.tear_tickers))
        check("Shortlist is merged into the pull, de-duplicated, and stays in the main or ETF list",
              len(dup.shortlist_tickers) == len(set(dup.shortlist_tickers)) >= 1 and all(t in dup.tickers for t in dup.shortlist_tickers)
              and all(t in dup.core_tickers or t in dup.etf_tickers or t in dup.country_group or t in dup.sector_names
                      or t in dup.six_pack or t in dup.currency_group for t in dup.shortlist_tickers))
        check("Goldman names are still merged into the pull and de-duplicated",
              len(dup.goldman_tickers) == 17 and all(t in dup.tickers for t in dup.goldman_tickers))
    except Exception as e:
        check("duplicate tickers de-duplicated", False, str(e))
    bad = Config(sell_cross_floor=55, sell_alert_threshold=40)
    check("floor ≥ threshold produces a warning", any("sell_cross_floor" in w for w in bad.warnings))
    check("default sell floor sits below every regime sell threshold (no warning)",
          not any("sell_cross_floor" in w for w in Config().warnings)
          and Config().sell_cross_floor < min(Config().sell_thr_by_regime.values()))
    check("floor equal to the lowest REGIME threshold now warns",
          any("sell_cross_floor" in w for w in Config(sell_cross_floor=35, sell_alert_threshold=40).warnings))
    try:
        Config(regime_lo=60, regime_hi=55)
        check("inverted regime thresholds rejected", False)
    except ValueError:
        check("inverted regime thresholds rejected", True)

    # --- scoring invariants on a synthetic universe
    prices = synthetic_prices(["AAA", "BBB", "CCC", "SPY", "RGTI"], n_bars=500, seed=11)
    health = DataHealth()
    as_of = max(df.index[-1] for df in prices.values())
    frames = prepare_frames(prices, cfg, health, as_of)
    comps = list(cfg.trailing_weights) + list(cfg.emerging_weights)
    dist = build_distribution(frames, comps)
    hist = score_history(frames, cfg, dist, ref_frame=frames.get("SPY"))
    # PMO is informational: dropping its columns must not change any score
    frames_nopmo = {k: v.drop(columns=["PMO", "PMO_Signal"]) for k, v in frames.items()}
    hist_nopmo = score_history(frames_nopmo, cfg, dist, ref_frame=frames_nopmo.get("SPY"))
    check("PMO does not affect scoring",
          hist["Buy_Confidence"].equals(hist_nopmo["Buy_Confidence"])
          and hist["Sell_Confidence"].equals(hist_nopmo["Sell_Confidence"])
          and hist["Recommendation"].equals(hist_nopmo["Recommendation"]))
    check("confidences within 0-100", hist["Buy_Confidence"].between(0, 100).all() and hist["Sell_Confidence"].between(0, 100).all())
    bcols = ["Buy_Component_PPO_Cross", "Buy_Component_RSI", "Buy_Component_EMA",
             "Buy_Component_Persistence", "Buy_Component_Squeeze"]
    nofl = hist["Buy_Floor_Applied"] == 0
    check("buy components stay within the score (floored bars aside)",
          (hist.loc[nofl, bcols].sum(axis=1).clip(upper=100) + 1e-9 >= hist.loc[nofl, "Buy_Confidence"]).all())
    fresh = (hist["PPO_Bars_Since_Neg"] <= cfg.ppo_fresh_bars) & (hist["PPO_Delta"] < 0)
    check("fresh bearish cross still in force respects the sell floor", (hist.loc[fresh, "Sell_Confidence"] >= cfg.sell_cross_floor).all())
    fresh_up = (hist["PPO_Bars_Since_Pos"] <= cfg.ppo_fresh_bars) & (hist["PPO_Delta"] > 0)
    check("v54 fresh bullish cross still in force respects the buy floor, which never reaches a buy threshold",
          (hist.loc[fresh_up, "Buy_Confidence"] >= cfg.buy_cross_floor).all()
          and cfg.buy_cross_floor < min(cfg.buy_thr_by_regime.values())
          and not any("buy_cross_floor" in w for w in cfg.warnings)
          and any("buy_cross_floor" in w for w in Config(buy_cross_floor=35).warnings))
    # v54 symmetry: with the regime weights equal, a bullish bar and its mirror-image bearish bar score the same PPO points
    _sym = pd.DataFrame({"Regime": ["Neutral"] * 2, "Signal_Reliability": [0.5, 0.5], "RSI_14": [50.0, 50.0],
                         "PPO_Delta": [0.4, -0.4], "PPO_Cross_Strength": [0.5, 0.5],
                         "PPO_Hist_Expand_Up": [1, 0], "PPO_Hist_Expand_Dn": [0, 1], "PPO_Above_Zero": [1, 0],
                         "PPO_Bars_Since_Pos": [0, 50], "PPO_Bars_Since_Neg": [50, 0],
                         "PPO_Bars_Since_Zero_Pos": [50, 50], "PPO_Bars_Since_Zero_Neg": [50, 50],
                         "Momentum_Data_OK": [1, 1], "Dollar_Volume_20d": [1e9, 1e9]})
    _old_b, _old_s = dict(BUY_REGIME_W), dict(SELL_REGIME_W)
    BUY_REGIME_W["Neutral"] = SELL_REGIME_W["Neutral"] = (1.0, 1.0, 1.0)
    try:
        _ss = score_frame(_sym, Config())
        _sa = score_frame(_sym, Config(symmetric_scoring=False))
    finally:
        BUY_REGIME_W.update(_old_b); SELL_REGIME_W.update(_old_s)
    check("v54 symmetric scoring: mirror-image bars get the same PPO points on both sides (and did not before)",
          _ss["Buy_Component_PPO_Cross"].iloc[0] == _ss["Sell_Component_PPO_Cross"].iloc[1] > 0
          and _sa["Buy_Component_PPO_Cross"].iloc[0] < _sa["Sell_Component_PPO_Cross"].iloc[1],
          f'{_ss["Buy_Component_PPO_Cross"].iloc[0]} {_ss["Sell_Component_PPO_Cross"].iloc[1]} / {_sa["Buy_Component_PPO_Cross"].iloc[0]} {_sa["Sell_Component_PPO_Cross"].iloc[1]}')
    if cfg.require_ppo_cross_for_alert:
        no_cross = hist["PPO_Bars_Since_Pos"] > cfg.ppo_fresh_bars
        check("no BUY alert without a fresh PPO ↑", int(hist.loc[no_cross, "Buy_Alert"].sum()) == 0)
    ext = hist["RSI_Zone"] == "Extreme"
    check("RSI Extreme keeps Buy below the regime threshold in every regime",
          (hist.loc[ext, "Buy_Confidence"] < hist.loc[ext, "Buy_Threshold"]).all())
    check("BUY needs a positive PPO histogram, SELL a negative one (cross still in force)",
          (hist.loc[hist["Recommendation"] == "BUY", "PPO_Delta"] > 0).all()
          and (hist.loc[hist["Recommendation"] == "SELL", "PPO_Delta"] < 0).all())
    exempt_h = (hist["Regime"] == "Dormant→Waking") & (hist["Squeeze_Setup_Flag"] == 1)
    gated_buys = (hist["Recommendation"] == "BUY") & (hist["Ticker"] != cfg.benchmark) & ~exempt_h
    check("history is gated per bar: no non-exempt BUY below EMA200 or lagging the benchmark",
          not ((hist.loc[gated_buys, "Below_EMA200"] == 1)
               | (hist.loc[gated_buys, "RS_20d"].fillna(0) < cfg.rs_min_excess_for_buy)).any())
    _g = market_gate_series(hist, cfg)
    weak_dates = set(_g.index[_g["closed"]])
    check("history is gated per bar: no non-exempt BUY on a date the market gate is closed",
          len(_g) > 0 and not (gated_buys & pd.to_datetime(hist["Date"]).isin(weak_dates)).any())
    check("v54 small universe falls back to the benchmark anchor (Rank_N = 0)", (hist["Rank_N"] == 0).all())
    check("EXIT only when both alerts fire", ((hist["Recommendation"] != "EXIT") | ((hist["Buy_Alert"] == 1) & (hist["Sell_Alert"] == 1))).all())
    check("no alert without complete data", (hist.loc[hist["Momentum_Data_OK"] == 0, ["Buy_Alert", "Sell_Alert"]].sum().sum() == 0))
    check("squeeze strength reaches 0-100 scale", hist["Squeeze_Setup_Strength"].between(0, 100).all())
    check("regime labels valid", hist["Regime"].isin(REGIMES).all())
    hv = hist["Historical_Vol"].dropna()
    check("reliability floor respected", (hist["Signal_Reliability"].dropna() >= cfg.min_reliability - 1e-9).all())
    check("percentiles within 0-100", hist["Momentum_Pctile"].dropna().between(0, 100).all())
    # young ticker: blend must not be NaN when only Mom_252d is missing
    young = frames["AAA"].iloc[[-1]].copy()
    young["Mom_252d"] = np.nan
    b = blend(young, cfg.trailing_weights, dist)
    check("blend renormalises when a component is missing", np.isfinite(b.iloc[0]))
    # equivalence: scoring the latest panel alone == latest row of the history
    lp = latest_panel(frames)
    lp = lp.reset_index(drop=True)
    lp["Date"] = lp["Last_Bar_Date"]
    lp = add_composites(lp, cfg, dist, ref_frame=frames.get("SPY"))
    lp = squeeze_score_frame(lp, cfg)
    panel_alone = score_frame(lp, cfg).set_index("Ticker")
    last_hist = hist.sort_values("Date").groupby("Ticker").tail(1).set_index("Ticker").loc[panel_alone.index]
    check("panel scoring equals history's last bar", np.allclose(panel_alone["Buy_Confidence"], last_hist["Buy_Confidence"]) and np.allclose(panel_alone["Sell_Confidence"], last_hist["Sell_Confidence"]))
    # payload JSON must be clean
    res = build(cfg, demo=True, tickers=["AAA", "BBB", "CCC", "SPY", "QQQ", "RGTI", "KOID", "DRNZ", "CRCL"], snap_dir=Path("/nonexistent"))
    payload = build_payload(res, cfg, "selftest", None)
    html = build_html(payload)
    check("payload serialises without NaN", "NaN" not in dumps_js(payload))
    check("dashboard HTML assembled", "__PAYLOAD__" not in html and "__HISTORY_TAG__" not in html and len(html) > 50_000)
    slim_html = build_html(payload, history_src="x.history.js")
    hjs = build_history_js(split_history(payload)[1], "selftest")
    check("split mode: HTML is much smaller and references the history file",
          '<script src="x.history.js"></script>' in slim_html and len(html) - len(slim_html) > 0.8 * len(hjs)
          and '"history"' not in slim_html.split("const P =")[1].split("\n")[0])
    check("history JS file is well-formed", hjs.startswith("window.__MOMENTUM_HISTORY__=") and "NaN" not in hjs
          and json.loads(hjs[len("window.__MOMENTUM_HISTORY__="):].rstrip().rstrip(";"))["data"].keys() == payload["history"].keys())
    check("Ticker tab has a stand-alone HTML export (no PDF/print path)",
          "exportTickerHtml" in html and "exportTickerPdf" not in html and "print-ticker" not in html)
    check("Ticker HTML export appends the Interpretation Guide after the Ticker page",
          "guideHtml" in html and "getElementById('guide')" in html and "sec.outerHTML + guideHtml" in html)
    check("stale ticker detected", any(s["ticker"] == "KOID" for s in res["health"].stale))
    check("too-short ticker skipped", any(s["ticker"] == "DRNZ" for s in res["health"].skipped))
    check("short-history ticker cannot alert", res["panel"].loc["CRCL", "Buy_Alert"] == 0 if "CRCL" in res["panel"].index else True)

    # --- themes (v30): primary-only aggregates, bounded scores, secondary display-only
    import tempfile
    tcsv = Path(tempfile.mkdtemp()) / "themes.csv"
    tcsv.write_text("Ticker,Company Name,Theme,Sub Theme,Assignment\n"
                    "AAA,A Co,T1,S1,Primary\nBBB,B Co,T1,S1,Primary\nCCC,C Co,T1,S2,Primary\n"
                    "RGTI,R Co,T2,S3,Primary\nAAA,A Co,T2,S3,Secondary\nBBB,B Co,T3,S9,Secondary\n",
                    encoding="utf-8")
    prim, sec = load_themes(tcsv), load_secondary_themes(tcsv)
    check("primary map ignores secondary rows", prim["AAA"] == ["T1", "S1"] and len(prim) == 4)
    check("secondary map holds only secondary rows", sec.get("AAA") == [["T2", "S3"]] and sec.get("BBB") == [["T3", "S9"]] and "CCC" not in sec)
    panel_t = hist.sort_values("Date").groupby("Ticker").tail(1).set_index("Ticker")
    ts = build_theme_stats(panel_t, hist, prim, cfg, exclude={"SPY"})
    tn = {x["name"]: x for x in ts["themes"]}
    check("theme counts use primary assignments only", tn["T1"]["n"] == 3 and tn["T2"]["n"] == 1 and "T3" not in tn, str({k: v["n"] for k, v in tn.items()}))
    check("small themes are flagged", tn["T2"]["small"] and not tn["T1"]["small"])
    allx = ts["themes"] + ts["subs"]
    check("theme scores and pillars within 0-100", all(0 <= x[k] <= 100 for x in allx for k in ("score", "p_mom", "p_brd", "p_sig", "p_acc") if x[k] is not None))
    check("sub-theme members add up to the theme", sum(x["n"] for x in ts["subs"] if x["theme"] == "T1") == tn["T1"]["n"])
    check("theme history has the requested length", len(tn["T1"]["hist"]) == min(cfg.theme_history_bars, len(ts["dates"])))
    ts_ex = build_theme_stats(panel_t, hist, prim, cfg, exclude={"SPY", "AAA"})
    check("excluded funds are left out of the aggregates", {x["name"]: x["n"] for x in ts_ex["themes"]}["T1"] == 2)
    check("theme weights sum to 1", abs(sum(cfg.theme_weights.values()) - 1.0) < 1e-9)
    payload_ts = build_payload(res, cfg, "selftest", None)
    check("payload carries theme stats and secondary map", "tstats" in payload_ts and "themes2" in payload_ts)
    check("payload carries the Tear list", len(payload_ts["cfg"]["tear"]) == len(cfg.tear_tickers))
    check("payload carries the Shortlist", len(payload_ts["cfg"]["shortlist"]) == len(cfg.shortlist_tickers))

    # --- download retry (v38): a fake Yahoo that drops tickers from the first batch
    fake_px = synthetic_prices(["AAA", "BBB", "CCC", "DDD"], n_bars=200, seed=5)
    seen: dict = {}

    def fake_dl(tickers, period, cfg_, group_by="ticker", threads=True):
        ts = [tickers] if isinstance(tickers, str) else list(tickers)
        parts = {}
        for t in ts:
            seen[t] = seen.get(t, 0) + 1
            if t in fake_px and not (t in ("BBB", "CCC") and seen[t] == 1):   # dropped on first request
                parts[t] = fake_px[t].rename(columns=str.title)
        if not parts:
            return pd.DataFrame()
        if group_by == "column" and len(ts) == 1:
            return parts[ts[0]]
        return pd.concat(parts, axis=1)

    real_dl = globals()["_yf_download"]
    globals()["_yf_download"] = fake_dl
    try:
        rcfg = Config(yf_retry_sleep=0.0, yf_chunk_sleep=0.0, yf_batch_size=3, min_load_bars=60)
        rh = DataHealth()
        got = fetch_prices(["AAA", "BBB", "CCC", "DDD", "ZZZZ"], "2y", rcfg, rh)
    finally:
        globals()["_yf_download"] = real_dl
    check("retry recovers tickers dropped from the first batch", {"AAA", "BBB", "CCC", "DDD"} <= set(got), str(sorted(got)))
    check("a genuinely missing ticker is still reported as skipped",
          "ZZZZ" not in got and [x["ticker"] for x in rh.skipped] == ["ZZZZ"], str(rh.skipped))
    check("retry note recorded on the Health tab", any("retry recovered" in n.lower() for n in rh.notes))

    # --- gates (v41): a gated BUY is Watch + reason; exemptions and idempotence hold
    gp = pd.DataFrame({
        "Recommendation": ["BUY", "BUY", "BUY", "BUY", "HOLD", "HOLD"],
        "Buy_Alert": [1, 1, 1, 1, 0, 0], "Sell_Alert": [0] * 6, "Watch": [""] * 6,
        "Regime": ["Strong", "Strong", "Dormant→Waking", "Strong", "Strong", "Weak"],
        "Squeeze_Setup_Flag": [0, 0, 1, 0, 0, 0],
        "RS_20d": [5.0, -3.0, -3.0, 2.0, -9.0, 1.0],
        "Below_EMA200": [0, 0, 1, 1, 1, 0], "Below_EMA50": [0] * 6, "Momentum_Direction": [1] * 6,
    }, index=["OK", "RS", "EXEMPT", "E200", "PLAIN", "SPY"])
    gc = Config(spy_regime_gate=False)
    _apply_gates(gp, gc)
    check("gate: a clean BUY passes untouched", gp.loc["OK", "Recommendation"] == "BUY" and gp.loc["OK", "Gate_Block"] == "")
    check("gate: RS-blocked BUY becomes HOLD + Watch BUY with a reason",
          gp.loc["RS", "Recommendation"] == "HOLD" and gp.loc["RS", "Watch"] == "BUY" and gp.loc["RS", "Gate_Block"] == "Relative strength")
    check("gate: Dormant→Waking + full squeeze is exempt", gp.loc["EXEMPT", "Recommendation"] == "BUY")
    check("gate: below-EMA200 BUY is blocked and labelled", gp.loc["E200", "Recommendation"] == "HOLD" and gp.loc["E200", "Gate_Block"] == "Below EMA200")
    check("gate: a plain HOLD is not given a block reason", gp.loc["PLAIN", "Gate_Block"] == "" and gp.loc["PLAIN", "Watch"] == "")
    gp2 = gp.copy()
    _apply_gates(gp2, gc)
    check("gate: re-applying the gates changes nothing", gp2["Recommendation"].tolist() == gp["Recommendation"].tolist()
          and gp2["Gate_Block"].tolist() == gp["Gate_Block"].tolist())
    gm = pd.DataFrame({
        "Recommendation": ["HOLD", "BUY"], "Buy_Alert": [0, 1], "Sell_Alert": [0, 0], "Watch": ["", ""],
        "Regime": ["Weak", "Strong"], "Squeeze_Setup_Flag": [0, 0], "RS_20d": [0.0, -2.0],
        "Below_EMA200": [0, 1], "Below_EMA50": [0, 0], "Momentum_Direction": [1, 1],
    }, index=["SPY", "XYZ"])
    _apply_gates(gm, Config())
    check("gate: all applicable reasons are listed together",
          gm.loc["XYZ", "Gate_Block"] == "SPY regime + Relative strength + Below EMA200", gm.loc["XYZ", "Gate_Block"])
    # --- v53: the market-regime gate needs SPY AND RSP to fail
    def _mk(spy_rec, spy_reg, rsp_rec, rsp_reg, with_rsp=True):
        idx = ["SPY"] + (["RSP"] if with_rsp else []) + ["AAA"]
        recs = [spy_rec] + ([rsp_rec] if with_rsp else []) + ["BUY"]
        regs = [spy_reg] + ([rsp_reg] if with_rsp else []) + ["Strong"]
        n = len(idx)
        return pd.DataFrame({"Recommendation": recs, "Buy_Alert": [1 if r == "BUY" else 0 for r in recs],
            "Sell_Alert": [0] * n, "Watch": [""] * n, "Regime": regs, "Squeeze_Setup_Flag": [0] * n,
            "RS_20d": [3.0] * n, "Below_EMA200": [0] * n, "Below_EMA50": [0] * n, "Momentum_Direction": [1] * n}, index=idx)
    g1 = _mk("SELL", "Weak", "HOLD", "Strong"); _apply_gates(g1, Config())
    check("v53 gate: SPY weak but RSP healthy does NOT block", g1.loc["AAA", "Recommendation"] == "BUY" and g1.loc["AAA", "Gate_Block"] == "")
    g2 = _mk("HOLD", "Strong", "SELL", "Weak"); _apply_gates(g2, Config())
    check("v53 gate: RSP weak but SPY healthy does NOT block", g2.loc["AAA", "Recommendation"] == "BUY")
    g3 = _mk("SELL", "Weak", "HOLD", "Mature/Cooling"); _apply_gates(g3, Config())
    check("v53 gate: SPY and RSP both weak blocks", g3.loc["AAA", "Recommendation"] == "HOLD" and g3.loc["AAA", "Gate_Block"] == "SPY regime" and g3.loc["AAA", "Watch"] == "BUY")
    g4 = _mk("SELL", "Weak", "", "", with_rsp=False); _apply_gates(g4, Config())
    check("v53 gate: RSP missing falls back to SPY alone", g4.loc["AAA", "Recommendation"] == "HOLD")
    g5 = _mk("SELL", "Weak", "HOLD", "Strong"); _apply_gates(g5, Config(regime_need_both=False))
    check("v53 gate: regime_need_both=False restores the SPY-only gate", g5.loc["AAA", "Recommendation"] == "HOLD")
    _d = pd.to_datetime(["2026-01-02", "2026-01-05"]).repeat(3)
    hh = pd.DataFrame({"Date": _d, "Ticker": ["SPY", "RSP", "AAA"] * 2,
        "Recommendation": ["SELL", "HOLD", "BUY", "SELL", "SELL", "BUY"],
        "Regime": ["Weak", "Strong", "Strong", "Weak", "Weak", "Strong"], "Buy_Alert": [0, 0, 1, 0, 0, 1], "Sell_Alert": [0] * 6,
        "Watch": [""] * 6, "Squeeze_Setup_Flag": [0] * 6, "RS_20d": [3.0] * 6, "Below_EMA200": [0] * 6, "Below_EMA50": [0] * 6,
        "Momentum_Direction": [1] * 6})
    apply_gates_history(hh, Config(market_gate_mode="legacy"))
    _a = hh[hh["Ticker"] == "AAA"]["Recommendation"].tolist()
    check("v53 gate (history, market_gate_mode='legacy'): blocks only on the bar where SPY and RSP both fail", _a == ["BUY", "HOLD"], str(_a))

    # --- v54: breadth market gate
    def _gh(spy_b, rsp_b, stock_b200, stock_b50):
        """One date per element: SPY / RSP below-EMA200 flags and the share of 40 stocks below each EMA."""
        rows = []
        for k, d in enumerate(pd.bdate_range("2026-02-02", periods=len(spy_b))):
            rows.append({"Date": d, "Ticker": "SPY", "Recommendation": "HOLD", "Below_EMA200": spy_b[k], "Below_EMA50": 0})
            rows.append({"Date": d, "Ticker": "RSP", "Recommendation": "HOLD", "Below_EMA200": rsp_b[k], "Below_EMA50": 0})
            for j in range(40):
                rows.append({"Date": d, "Ticker": f"S{j:02d}", "Recommendation": "BUY" if j == 0 else "HOLD",
                             "Below_EMA200": int(j < stock_b200[k] * 40), "Below_EMA50": int(j < stock_b50[k] * 40)})
        g = pd.DataFrame(rows)
        g["Regime"], g["Buy_Alert"], g["Sell_Alert"], g["Watch"] = "Strong", 0, 0, ""
        g["Squeeze_Setup_Flag"], g["RS_20d"], g["Momentum_Direction"], g["EMA200"] = 0, 3.0, 1, 100.0
        return g
    #            day0 healthy, day1 SPY only, day2 both below, day3 breadth washed out, day4 only the 200-day share is low
    gh = _gh([0, 1, 1, 0, 0], [0, 0, 1, 0, 0], [0.2, 0.2, 0.2, 0.7, 0.7], [0.2, 0.2, 0.2, 0.7, 0.3])
    _stk = [f"S{j:02d}" for j in range(40)]
    _gs = market_gate_series(gh, Config(), _stk)
    check("v54 breadth gate: closed only when SPY and RSP are both under the 200-day, or breadth is washed out on both averages",
          _gs["closed"].tolist() == [False, False, True, True, False] and _gs["idx_weak"].tolist() == [False, False, True, False, False]
          and _gs["brd_weak"].tolist() == [False, False, False, True, False], str(_gs[["idx_weak", "brd_weak", "closed"]].values.tolist()))
    check("v54 breadth gate: with no stock list the index decides alone; SPY alone decides when need_both is off",
          market_gate_series(gh, Config(), None)["closed"].tolist() == [False, False, True, False, False]
          and market_gate_series(gh, Config(regime_need_both=False), None)["closed"].tolist() == [False, True, True, False, False])
    gh2 = gh.copy()
    gh2.loc[gh2["Ticker"] == "S00", "Below_EMA200"] = 0          # S00 itself is above its 200-day on every date
    apply_gates_history(gh2, Config(), _stk)
    _b = gh2[gh2["Ticker"] == "S00"]
    check("v54 breadth gate blocks a Favorable only on closed dates, labelled 'SPY regime'",
          _b["Recommendation"].tolist() == ["BUY", "BUY", "HOLD", "HOLD", "BUY"] and _b["Gate_Block"].tolist() == ["", "", "SPY regime", "SPY regime", ""],
          str(_b["Recommendation"].tolist()))

    # --- v54: trend state (enter on BUY, trailing ATR stop that never falls, exit on stop or on an Unfavorable)
    _td = pd.bdate_range("2026-03-02", periods=7)
    th = pd.DataFrame({"Date": list(_td) * 2, "Ticker": ["AAA"] * 7 + ["BBB"] * 7,
                       "Last_Close": [100, 110, 108, 102, 101, 120, 121] + [50, 51, 52, 53, 54, 55, 56],
                       "ATR_Pct": [2.0] * 14, "Momentum_Data_OK": [1] * 14,
                       "Recommendation": ["BUY", "HOLD", "HOLD", "HOLD", "HOLD", "BUY", "HOLD"] + ["HOLD", "BUY", "HOLD", "SELL", "HOLD", "HOLD", "HOLD"]})
    th = add_trend_state(th.sample(frac=1, random_state=1).reset_index(drop=True), Config()).sort_values(["Ticker", "Date"])
    ta, tb_ = th[th["Ticker"] == "AAA"], th[th["Ticker"] == "BBB"]
    check("v54 trend state: entry on Favorable, stop = highest close - 3 ATR, stop-out on a close under it, re-entry on the next Favorable",
          ta["In_Trend"].tolist() == [1, 1, 1, 0, 0, 1, 1] and ta["Trend_Exit"].tolist() == ["", "", "", "Stop", "", "", ""]
          and np.allclose(ta["Trend_Stop"].iloc[:3], [94.0, 103.4, 103.4]) and abs(ta["Trend_Closed_Ret"].iloc[3] - 2.0) < 1e-9
          and ta["Trend_Days"].iloc[2] == 2 and abs(ta["Trend_Ret_Pct"].iloc[1] - 10.0) < 1e-9 and ta["Trend_Entry_Date"].iloc[6] == "2026-03-09",
          str(ta[["In_Trend", "Trend_Stop", "Trend_Exit"]].values.tolist()))
    check("v54 trend state: an Unfavorable alert closes the trend ('Signal'); position size = risk / (3 x ATR%), capped",
          tb_["In_Trend"].tolist() == [0, 1, 1, 0, 0, 0, 0] and tb_["Trend_Exit"].iloc[3] == "Signal"
          and abs(tb_["Size_Pct"].iloc[0] - 10.0) < 1e-9
          and abs(add_trend_state(pd.DataFrame({"Date": _td[:1], "Ticker": ["X"], "Last_Close": [10.0], "ATR_Pct": [5.0],
                                                "Momentum_Data_OK": [1], "Recommendation": ["HOLD"]}), Config())["Size_Pct"].iloc[0] - 6.7) < 1e-9)
    check("v54 trend state can be switched off", add_trend_state(th.copy(), Config(trend_state=False))["In_Trend"].sum() == 0)

    # --- v54: universe ranking (volatility-adjusted, cross-sectional), scorecard additions, snapshot scorecard
    _names = [f"U{j:02d}" for j in range(36)] + ["SPY", "RSP"]
    _pr = synthetic_prices(_names, n_bars=520, seed=5)
    _uh = DataHealth()
    _fr = prepare_frames(_pr, cfg, _uh, max(d.index[-1] for d in _pr.values()))
    _dist = build_distribution({"SPY": _fr["SPY"]}, comps)
    uhist = score_history(_fr, cfg, _dist, ref_frame=_fr["SPY"], stocks=_names[:36])
    _lastd = uhist[uhist["Date"] == uhist["Date"].max()]
    check("v54 universe ranking: every name is ranked against the others on its date, percentiles spread across 0-100",
          (uhist["Rank_N"] == len(_names)).all() and _lastd["Momentum_Trailing_Pctile"].between(0, 100).all()
          and 35 < _lastd["Momentum_Trailing_Pctile"].mean() < 65 and _lastd["Momentum_Trailing_Pctile"].max() - _lastd["Momentum_Trailing_Pctile"].min() > 40
          and uhist["RS_Rating"].dropna().between(1, 99).all())
    _one = _fr["U00"].copy()
    check("v54 volatility adjustment divides by the name's own volatility (floored), PPO histogram by ATR%",
          "Mom_20d_VA" in _one.columns and "Momentum_Blended_VA" in _one.columns
          and np.allclose((_one["PPO_Delta"] / _one["ATR_Pct"]).dropna().tail(50), _one["PPO_Delta_VA"].dropna().tail(50)))
    _bh = score_history(_fr, Config(pctile_anchor="benchmark"), _dist, ref_frame=_fr["SPY"])
    check("v54 pctile_anchor='benchmark' restores the SPY-history anchor", (_bh["Rank_N"] == 0).all())
    _sc = scorecard(uhist, cfg, "SPY")
    check("v54 scorecard carries gate attribution, score calibration, trend trades and a by-date range",
          [g["gate"] for g in _sc["gates"]][:3] == ["Passed every gate (Favorable)", "Blocked by any gate", "SPY regime"]
          and len(_sc["calib"]) == 2 * (len(cfg.score_buckets) - 1) and "n" in _sc["trend"]
          and all(("nd" in x) for x in _sc["summary"] if x["n"]) and any(("lo" in x) for x in _sc["calib"] if x["n"]))
    _sd = Path(tempfile.mkdtemp())
    _ud = sorted(uhist["Date"].unique())
    _d0, _d1 = pd.Timestamp(_ud[-40]), pd.Timestamp(_ud[-39])
    pd.DataFrame({"Ticker": ["U00", "U01", "U02"], "Recommendation": ["HOLD", "BUY", "SELL"]}).to_csv(_sd / f"Results_{_d0:%Y-%m-%d}.csv", index=False)
    pd.DataFrame({"Ticker": ["U00", "U01", "U02"], "Recommendation": ["BUY", "BUY", "HOLD"]}).to_csv(_sd / f"Results_{_d1:%Y-%m-%d}.csv", index=False)
    _ss2 = snapshot_scorecard(_sd, uhist, cfg, "SPY")
    _px0 = uhist[(uhist["Ticker"] == "U00")].sort_values("Date").set_index("Date")["Last_Close"]
    _exp = (_px0.iloc[_px0.index.get_loc(_d1) + 5] / _px0.loc[_d1] - 1) * 100
    _r5 = next(x for x in _ss2["rows"] if x["side"] == "BUY" and x["h"] == 5)
    check("v54 snapshot scorecard: only NEW signals vs the previous snapshot count, forward return from the snapshot date",
          _ss2["ok"] and _ss2["events"] == {"BUY": 1, "SELL": 0} and _r5["n"] == 1 and abs(_r5["mean"] - round(_exp, 2)) < 0.011, str(_ss2))
    check("v54 snapshot scorecard copes with a missing folder", snapshot_scorecard(Path("/nonexistent"), uhist, cfg, "SPY")["ok"] is False)
    check("fresh-cross window is 3 bars", Config().ppo_fresh_bars == 3)
    check("scored history carries a Gate_Block column", "Gate_Block" in hist.columns)
    check("payload exposes the gate reason and the Health list", "gate" in payload["rows"][0] and "gate_blocked" in payload["health"])
    check("Guide has a Gates section and the Signals tab a Blocked-by column",
          "function gateGuide" in html and "gateGuide()" in html and "label:'Blocked by'" in html)

    # --- currency group (v42)
    cc = Config()
    check("currency group = 8 funds + UUP, merged into the pull, kept out of the main list",
          len(cc.currency_group) == 9 and "UUP" in cc.currency_group and all(t in cc.tickers for t in cc.currency_group)
          and not any(t in cc.core_tickers for t in cc.currency_group))
    gcur = pd.DataFrame({
        "Recommendation": ["BUY", "BUY", "BUY"], "Buy_Alert": [1, 1, 1], "Sell_Alert": [0] * 3, "Watch": [""] * 3,
        "Regime": ["Strong"] * 3, "Squeeze_Setup_Flag": [0] * 3, "RS_20d": [-4.0, -4.0, -4.0],
        "Below_EMA200": [0, 0, 1], "Below_EMA50": [0] * 3, "Momentum_Direction": [1] * 3,
    }, index=["FXE", "AAA", "FXY"])
    gcur2 = pd.DataFrame({"Recommendation": ["HOLD", "BUY"], "Buy_Alert": [0, 1], "Sell_Alert": [0, 0], "Watch": ["", ""],
        "Regime": ["Weak", "Strong"], "Squeeze_Setup_Flag": [0, 0], "RS_20d": [0.0, 0.0], "Below_EMA200": [0, 0],
        "Below_EMA50": [0, 0], "Momentum_Direction": [1, 1]}, index=["SPY", "FXC"])
    _apply_gates(gcur, cc)
    check("gate: a currency fund is NOT blocked by negative RS vs SPY, a stock is",
          gcur.loc["FXE", "Recommendation"] == "BUY" and gcur.loc["AAA", "Recommendation"] == "HOLD")
    check("gate: a currency fund below EMA200 is still blocked", gcur.loc["FXY", "Recommendation"] == "HOLD" and gcur.loc["FXY", "Gate_Block"] == "Below EMA200")
    _apply_gates(gcur2, cc)
    check("gate: a weak SPY does not block a currency BUY", gcur2.loc["FXC", "Recommendation"] == "BUY")
    fxl = ["FXE", "FXY", "FXB", "FXF", "FXA", "FXC", "FXM", "UUP", "AAA", "BBB", "SPY"]
    res_fx = build(cc, demo=True, tickers=fxl, snap_dir=Path("/nonexistent"))
    pan = res_fx["panel"]
    check("currency tickers are scored", all(t in pan.index for t in ["FXE", "FXY", "UUP"]))
    check("currency anchoring note recorded", any("Currency tab" in n for n in res_fx["health"].notes))
    h_fx = res_fx["hist"]
    cfg_off = Config(currency_own_anchor=False)
    res_off = build(cfg_off, demo=True, tickers=fxl, snap_dir=Path("/nonexistent"))
    a = h_fx[h_fx["Ticker"] == "FXE"]["Momentum_Trailing_Pctile"].dropna()
    b = res_off["hist"][res_off["hist"]["Ticker"] == "FXE"]["Momentum_Trailing_Pctile"].dropna()
    check("group anchoring spreads currency percentiles wider than SPY anchoring", a.std() > b.std(), f"{a.std():.1f} vs {b.std():.1f}")
    ma = h_fx[h_fx["Ticker"] == "AAA"]["Momentum_Trailing_Pctile"].reset_index(drop=True)
    mb = res_off["hist"][res_off["hist"]["Ticker"] == "AAA"]["Momentum_Trailing_Pctile"].reset_index(drop=True)
    check("non-currency percentiles are unaffected by the group anchor", ma.equals(mb))
    pl_fx = build_payload(res_fx, cc, "selftest", None)
    check("payload carries the Currency list and correlations",
          len(pl_fx["cfg"]["currency"]) == 9 and "FXE" in pl_fx["fxcorr"] and "spy" in pl_fx["fxcorr"]["FXE"])
    html_fx = build_html(pl_fx)
    check("dashboard has a Currency tab, renderer and Guide section",
          'id="currency"' in html_fx and "function renderCurrency" in html_fx and "function currencyGuide" in html_fx and "['currency','Currency']" in html_fx)
    check("currency funds are excluded from the Theme aggregates and the not-in-Theme list",
          not any(t in pl_fx["health"]["no_theme"] for t in cc.currency_group))

    # --- country ETFs (v43)
    c3 = Config()
    check("country group is populated and kept out of the main list",
          len(c3.country_group) >= 40 and not any(t in c3.core_tickers for t in c3.country_group))
    fl = liquidity_floor(["EWJ", "FXE", "AAPL"], c3)
    check("liquidity floor: country and currency groups are lower than stocks",
          fl[0] == c3.country_min_dollar_vol < c3.min_dollar_vol and fl[1] == c3.currency_min_dollar_vol and fl[2] == c3.min_dollar_vol)
    gcty = pd.DataFrame({
        "Recommendation": ["BUY", "BUY", "BUY", "BUY"], "Buy_Alert": [1] * 4, "Sell_Alert": [0] * 4, "Watch": [""] * 4,
        "Regime": ["Strong"] * 4, "Squeeze_Setup_Flag": [0] * 4, "RS_20d": [3.0, -3.0, 3.0, 3.0],
        "Below_EMA200": [0, 0, 1, 0], "Below_EMA50": [0] * 4, "Momentum_Direction": [1] * 4,
    }, index=["EWJ", "EWG", "EWZ", "AAA"])
    gspy = pd.DataFrame({"Recommendation": ["HOLD"] + ["BUY"] * 4, "Buy_Alert": [0] + [1] * 4, "Sell_Alert": [0] * 5, "Watch": [""] * 5,
        "Regime": ["Weak"] + ["Strong"] * 4, "Squeeze_Setup_Flag": [0] * 5, "RS_20d": [0.0, 3.0, -3.0, 3.0, 3.0],
        "Below_EMA200": [0, 0, 0, 1, 0], "Below_EMA50": [0] * 5, "Momentum_Direction": [1] * 5}, index=["SPY", "EWJ", "EWG", "EWZ", "AAA"])
    _apply_gates(gspy, c3)
    check("gate: a weak SPY does not block a country BUY, but does block a stock",
          gspy.loc["EWJ", "Recommendation"] == "BUY" and gspy.loc["AAA", "Recommendation"] == "HOLD" and gspy.loc["AAA", "Gate_Block"] == "SPY regime")
    check("gate: a country fund still faces the RS and EMA200 gates",
          gspy.loc["EWG", "Gate_Block"] == "Relative strength" and gspy.loc["EWZ", "Gate_Block"] == "Below EMA200")
    html_c = build_html(payload)
    check("v53 PPO tab has All / Watch Favorable / Watch Unfavorable sub-tabs and split Favorable / Unfavorable filters",
          "id=\"ppo-sub\"" in html_c and "ppo-wf-table" in html_c and "ppo-wu-table" in html_c
          and "FAV:r=>r.rec==='BUY', UNFAV:r=>r.rec==='SELL'" in html_c and "ALERTS:r=>r.rec==='BUY'||r.rec==='SELL'" not in html_c.split("function renderPPO")[1].split("Themes tab")[0])
    check("chart legend has top margin and Trailing is blue / Emerging yellow",
          "T = (series.length > 1 && series.some(s => s.label)) ? 22 : 8" in html_c
          and "{v:H.tr,color:C.accent,label:'Trailing'" in html_c and "{v:H.em,color:'#f2cc0c',label:'Emerging'" in html_c)

    # --- header disclaimer and right-hand axis (v44)
    html_h = build_html(payload)
    check("header carries the disclaimer and copyright, and so do the footer and the Ticker export",
          html_h.count("For information only. Not Investment Advice") >= 3 and html_h.count("Frank Hayes") >= 3
          and '<div class="disc">' in html_h)
    check("line charts repeat the Y labels on the right",
          'x="${w-R+4}"' in html_h and 'text-anchor="start">${tickFmt(v)}' in html_h)

    # --- v47: display-only renames + PPO tab
    check("v47 PPO tab is wired in (section, tab, renderer, payload fields)",
          'id="ppo"' in html_h and "function renderPPO" in html_h and "['ppo','PPO']" in html_h
          and "bz_pos" in payload["rows"][0] and "bz_neg" in payload["rows"][0])
    check("v47 Signal and Trailing/Emerging Momentum labels are present",
          "Watch Favorable" in html_h and "Unfavorable" in html_h and "label:'Trailing/Emerging Momentum'" in html_h
          and "label:'Signal'" in html_h and "label:'Regime'" not in html_h and "label:'Rec'" not in html_h)
    check("v47 left the internal recommendation values untouched",
          set(res["panel"]["Recommendation"].unique()) <= {"BUY", "SELL", "EXIT", "HOLD"})

    # --- v48: display-only changes
    check("v48 volume chart, Net Bias cards, coloured Watch badges and Signal sort are wired in",
          "function volumeChart" in html_h and "vol_rel_hi" in html_h and "watchBadge" in html_h
          and 'class="badge WATCH" title' not in html_h and "Net Bias" in html_h
          and "sortKey: 'rec', sortDir: 1" in html_h and "defaultSort: byBias" not in html_h)
    check("v48 Signal column replaced Overall Momentum in the UI", "label:'Overall Momentum'" not in html_h)
    check("v52 Overview tab is gone; SPY / QQQ / RSP cards and the four charts live on Market Health",
          "['overview'" not in html_h and 'id="overview"' not in html_h and "function renderOverview" not in html_h
          and "mhContext()" in html_h and "mhCharts()" in html_h and CONFIG.context_tickers == ("SPY", "QQQ", "RSP"))
    _lp = {t: 1 for t in ("AAA", "SPY", "QQQ", "RSP", "SMH", "XLK", "EWJ", "FXE")}
    check("v52 breadth counts stocks only (benchmark, index, sector, country and currency funds are left out)",
          breadth_stock_list(CONFIG, list(_lp), _lp, demo=True) == ["AAA"])
    _cl = pd.DataFrame(np.random.default_rng(1).normal(0.0005, 0.01, (300, 60)).cumsum(axis=0) + 100,
                       index=pd.bdate_range(end="2026-10-30", periods=300), columns=[f"S{i}" for i in range(60)])
    _br = _mh_breadth(_cl, 50)
    check("v52 breadth is built from the stock closes alone (no S&P list), with history",
          _br.get("ok") and _br["universe"] == 60 and _br.get("history") and "error" not in _br)
    check("v52 breadth says so when there are too few stocks", not _mh_breadth(_cl.iloc[:, :10], 50)["ok"])

    log("")
    log("ALL SELF-TESTS PASSED" if fails == 0 else f"{fails} SELF-TEST(S) FAILED")
    return 1 if fails else 0


# =============================================================================
#  8. MAIN
# =============================================================================

def parse_args(argv=None):
    ap = argparse.ArgumentParser(description="Unified Momentum · Squeeze · Buy/Sell monitor")
    ap.add_argument("--demo", action="store_true", help="synthetic data, no network")
    ap.add_argument("--selftest", action="store_true", help="run indicator/scoring checks and exit")
    ap.add_argument("--tickers", type=str, help="comma-separated override of the universe")
    ap.add_argument("--out-dir", type=str, help="write dashboard/CSV/snapshots here instead of the configured paths")
    ap.add_argument("--open", action="store_true", help="open the dashboard in the default browser when done")
    ap.add_argument("--keep-partial", action="store_true", help="deprecated: today's live bar is now kept by default; this flag is a no-op (see --eod-only)")
    ap.add_argument("--eod-only", action="store_true", help="ignore the live intraday price while the market is open; wait for each day's confirmed close (old default behavior)")
    ap.add_argument("--universe", choices=["list", "themes", "both"], default=None,
                    help="ticker source: 'list' = the list in the code; 'themes' = all unique tickers in Input_Ticker_List_by_Theme.csv; 'both' = the union of the two")
    ap.add_argument("--inline-history", action="store_true", help="embed the history in the HTML (single big file) instead of the separate .history.js")
    ap.add_argument("--no-snapshot", action="store_true", help="do not write a dated snapshot")
    return ap.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    if args.selftest:
        return selftest()

    cfg = CONFIG
    if args.keep_partial:
        cfg.drop_partial_bar = False   # kept for backward compatibility; this is now the default
    if args.eod_only:
        cfg.drop_partial_bar = True
    tickers = [t.strip().upper() for t in args.tickers.split(",") if t.strip()] if args.tickers else None
    source = args.universe or cfg.universe_source
    if source in ("themes", "both") and tickers is None:
        theme_tickers = load_theme_universe(cfg.themes_csv)
        if theme_tickers:
            cfg.tickers = (list(cfg.core_tickers) + theme_tickers) if source == "both" else theme_tickers
            cfg.validate()      # de-dupe, merge Sector/Six Pack/ETF/Country lists, re-collect warnings
            log_ok(f"Universe  ← {'code list + ' if source == 'both' else ''}Theme file: {len(theme_tickers)} theme tickers")
            cfg.warnings.append(f"Universe source: {'code list + ' if source == 'both' else ''}Theme file ({len(theme_tickers)} theme tickers)")
        else:
            log_warn("Theme universe unavailable - using the ticker list in the code instead")
            cfg.warnings.append("Theme universe requested but could not be read; used the code's ticker list")

    now = datetime.now(LOCAL_TZ)
    run_ts = now.strftime("%A, %B %d, %Y at %I:%M %p %Z")
    log("=" * 70)
    log(f"MOMENTUM UNIFIED {VERSION}" + ("  [DEMO]" if args.demo else ""))
    log("=" * 70)
    for w in cfg.warnings:
        log_warn(f"config: {w}")

    paths = OutputPaths(cfg, Path(args.out_dir) if args.out_dir else None)
    for n in paths.notes:
        log_warn(n)

    res = build(cfg, demo=args.demo, snap_dir=paths.snapshots, tickers=tickers)
    payload = build_payload(res, cfg, run_ts, paths)
    payload["market"] = build_market_health(cfg, demo=args.demo, closes=res.get("breadth_closes"))   # v49/v52: Market Health tab (display only)

    # 1) dashboard first — it is the deliverable
    hjs = None
    if args.inline_history:
        html = build_html(payload)
    else:
        _slim, hist_data = split_history(payload)
        hjs = build_history_js(hist_data, run_ts)
        atomic_write_text(paths.history, hjs, cfg)       # history first, so the HTML never points at nothing
        log_ok(f"History   → {paths.history}  ({len(hjs)/1024:.0f} KB)")
        html = build_html(payload, history_src=paths.history.name)
    atomic_write_text(paths.html, html, cfg)
    log_ok(f"Dashboard → {paths.html}  ({len(html)/1024:.0f} KB)")

    # 1b) extra copies (website, etc.), each with its own history file beside it
    for ep in ([] if args.out_dir else cfg.extra_html):
        ep = Path(ep)
        try:
            if hjs is None:
                atomic_write_text(ep, html, cfg)
            else:
                hp = ep.with_name(ep.stem + ".history.js")
                atomic_write_text(hp, hjs, cfg)
                atomic_write_text(ep, build_html(payload, history_src=hp.name), cfg)
            log_ok(f"Copy      → {ep}")
        except Exception as e:
            log_warn(f"Extra copy not written to {ep} ({e})")

    # 2) CSV + snapshot, each independently guarded
    out_df = res["panel"].reset_index()
    try:
        atomic_write_csv(out_df, paths.csv, cfg)
        log_ok(f"Results   → {paths.csv}")
    except Exception as e:
        log_warn(f"CSV write failed ({e})")
    if not args.no_snapshot:
        try:
            snap = paths.snapshots / f"Results_{res['as_of']}.csv"
            atomic_write_csv(out_df, snap, cfg)
            log_ok(f"Snapshot  → {snap}")
        except Exception as e:
            log_warn(f"Snapshot skipped ({e})")

    if args.open or cfg.open_browser:
        try:
            webbrowser.open(paths.html.resolve().as_uri())
        except Exception:
            pass
    log("")
    log("=" * 70)
    log(f"COMPLETE · {run_ts} · {res['health'].timings.get('total_s', '?')} s")
    log("=" * 70)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception:
        traceback.print_exc()
        sys.exit(1)
