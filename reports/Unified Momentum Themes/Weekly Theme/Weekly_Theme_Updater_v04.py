"""
Weekly_Theme_Updater_v04.py
───────────────────────────
Reads Input_Ticker_List_by_Theme.csv, fetches fresh market data from Yahoo
Finance for every unique ticker, and writes:

  1. Tickers_Themes_SubThemes.csv        — per-row ticker detail (v03 columns
                                            plus returns provenance + technicals)
  2. Theme_Summary_<date>.csv            — theme-level aggregates
  3. SubTheme_Summary_<date>.csv         — sub-theme-level aggregates
  4. PPO_Candidates_<date>.csv           — weekly-trend-intact + daily-PPO-reset screen
  5. run_manifest_<date>.json            — as-of date, coverage, failures, universe diff
  6. dated archive copies of (1)

WHAT CHANGED FROM v03
─────────────────────
v03 shipped correct plumbing with four defects that silently corrupted output:

  (a) THE CACHE NEVER EXPIRED. `to_fetch` was `[t for t in tickers if t not in
      cached]`, and every resolved cap was rewritten to the cache each run. Once
      a ticker was cached it was never refetched, so market caps froze at
      whatever date the cache was first written while prices kept updating.
      Empirically: 1,394 of 1,394 caps were byte-identical week over week.
      → v04 timestamps every cache entry and refetches anything older than
        --cache-ttl days (default 6). v1 flat caches are treated as expired.

  (b) LOOKBACKS WERE POSITIONAL. `pct_change` did series.dropna() then
      .iloc[-(n+1)], so a ticker with halts or thin trading measured a different
      calendar window than its peers under the same column heading, and a
      ticker that stopped printing prices reported a stale close as "current"
      with no flag.
      → v04 anchors every window to the LAST COMMON TRADING DATE and uses a
        date-based asof lookback (7 / 31 / 93 calendar days). Any symbol whose
        own last bar is more than --staleness-days behind the market is marked
        Stale and its returns are nulled rather than silently wrong.

  (c) DOWNLOAD FAILURES WERE SILENT. yf.download drops symbols it cannot
      resolve; v03 turned that into None and moved on.
      → v04 records every unresolved / stale / partial symbol in the manifest
        and prints them at the end.

  (d) NO AS-OF DATE. Nothing in the output said what date the data described.
      → v04 stamps the as-of date into the manifest, the summary filenames, and
        a "Data As Of" column.

v04 also adds the analytics the rotation framework actually needs, which v03
never produced (forcing the weekly report to *infer* PPO and trend structure
from 1W/1M/3M returns):

  • DUAL WEIGHTING. Every theme and sub-theme is reported cap-weighted AND
    equal-weighted, with breadth, top-3 weight share, effective N (1/HHI) and a
    Distortion figure (cap-wtd minus equal-wtd). Cap-weighting alone produces
    false signals in concentrated themes — e.g. Energy-Traditional printed
    -2.33% cap-weighted while the median constituent was flat (+0.06% equal-
    weighted), driven entirely by two mega-caps.
  • TICKER COLLAPSE. A ticker listed in two sub-themes of the SAME theme
    entered the theme average twice under v03, distorting breadth and
    equal-weight. v04 collapses to one row per (level, ticker) before
    aggregating; cap-weighted results are unchanged, breadth is corrected.
  • OPTIONAL WEIGHT CAP (--weight-cap) so a single mega-cap cannot define a
    small theme (PLTR was the largest weight in Defense & Aerospace).
  • TECHNICALS: 30-week EMA position and slope, weekly PPO + histogram
    direction, daily PPO + distance from zero + turn, relative strength vs the
    benchmark, and a 20d/60d dollar-volume accumulation proxy.
  • DOWN-DAY TEST: capture ratio and green-rate measured on the benchmark's
    actual down sessions over the trailing window, instead of using 1W breadth
    as a proxy for selloff resilience.
  • NUMERIC ROTATION SCREEN: each theme is classified EARLY ROTATION / MATURE
    LEADERSHIP / FAILED ROTATION / MIXED by explicit thresholds, so week-over-
    week upgrades and downgrades are reproducible rather than narrative.
  • ARCHIVING: the previous stable output is rotated to *_Last_Week.csv
    automatically and a dated snapshot is kept.

Generalisation note: v03's Sub Market Cap allocation hard-coded 60/40 and
assumed at most one Primary and one Secondary. v04 keeps 60% for Primary but
splits the remaining 40% evenly across however many Secondary rows exist, so a
ticker's allocations always sum to exactly its market cap.

Usage
─────
    pip install "yfinance>=0.2.40" curl_cffi tqdm pandas numpy
    python Weekly_Theme_Updater_v04.py
    python Weekly_Theme_Updater_v04.py --input my.csv --output out.csv
    python Weekly_Theme_Updater_v04.py --cache-ttl 0        # force cap refresh
    python Weekly_Theme_Updater_v04.py --weight-cap 0.15    # cap any name at 15%
    python Weekly_Theme_Updater_v04.py --no-technicals      # returns only, faster
    python Weekly_Theme_Updater_v04.py --start-weights      # weight by period-start cap
"""

import argparse
import json
import math
import random
import shutil
import sys
import time
import warnings
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf
from tqdm import tqdm

try:
    from yfinance.exceptions import YFRateLimitError
except Exception:                       # older yfinance
    class YFRateLimitError(Exception):
        pass

try:
    from curl_cffi import requests as _cffi_requests
except Exception:
    _cffi_requests = None

try:
    from yfinance.data import YfData
except Exception:
    YfData = None

warnings.filterwarnings("ignore", category=FutureWarning)

# ──────────────────────────────────────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────────────────────────────────────

DEFAULT_INPUT  = r"G:\My Drive\Projects\Python\Stocks & Options\Themes\data\Input_Ticker_List_by_Theme.csv"
DEFAULT_OUTPUT = r"G:\My Drive\Projects\Python\Stocks & Options\Themes\data\Tickers_Themes_SubThemes.csv"

# 2 years of daily bars: enough for a 30-week EMA (~150 weekly bars available)
# and for daily PPO warm-up. Still one bulk request.
HISTORY_PERIOD = "1y"
BENCHMARK      = "SPY"

# Calendar-day lookbacks, anchored to the last common trading date.
# v03 used trading-day counts (5/21/63) applied per-ticker, which drifted.
OFFSETS_DAYS = {
    "1W Price Change %":   7,
    "1M Price Change %":  31,
    "3M Price Change %":  93,
}

# A symbol whose own last bar is more than this many calendar days behind the
# market's last bar is treated as stale; its returns are nulled and flagged.
STALENESS_DAYS = 6

DEFAULT_WORKERS   = 4
BATCH_PAUSE       = 1.0
MAX_RETRIES       = 4
RETRY_BASE        = 2.0

QUOTE_URL         = "https://query2.finance.yahoo.com/v7/finance/quote"
DEFAULT_CHUNK     = 100
QUOTE_CHUNK_PAUSE = 0.4
QUOTE_MAX_RETRIES = 3

DEFAULT_CACHE_TTL_DAYS = 6      # < 7 so a weekly run always refreshes caps
CACHE_FORMAT           = 2

# Technical parameters
EMA_WEEKS        = 30           # 30-week EMA on weekly closes
PPO_FAST         = 12
PPO_SLOW         = 26
PPO_SIGNAL       = 9
PPO_ZERO_BAND    = 1.0          # |daily PPO| <= this counts as "reset to zero"
RS_LOOKBACK_DAYS = 31           # relative-strength change window
VOL_SHORT        = 20
VOL_LONG         = 60
DOWN_DAY_WINDOW  = 15           # trailing sessions searched for benchmark down days

# Rotation screen thresholds (all in percent unless noted)
SCREEN = {
    "early_min_1w":        1.5,   # 1W must be meaningfully positive
    "early_1m_floor":     -6.0,   # 1M base must be mediocre, not strong...
    "early_1m_ceiling":    6.0,   # ...and not already extended
    "early_min_breadth":  55.0,
    "early_max_distort":   1.5,   # cap-wtd minus equal-wtd, in pp
    "early_min_3m":      -12.0,   # not in structural decline
    "mature_min_1m":      12.0,
    "mature_min_3m":      15.0,
    "failed_max_1w":      -1.0,
    "failed_max_breadth": 40.0,
}

MIN_CONSTITUENTS = 4            # sub-themes below this are flagged, not cited


# ──────────────────────────────────────────────────────────────────────────────
# Session / symbol helpers
# ──────────────────────────────────────────────────────────────────────────────

def make_session():
    """Browser-impersonating session — this alone removes most 429s."""
    if _cffi_requests is None:
        return None
    try:
        return _cffi_requests.Session(impersonate="chrome")
    except Exception:
        return None


def to_yahoo_symbol(sym: str) -> str:
    """Yahoo uses '-' where tickers use '.' (BF.B → BF-B, MOG.A → MOG-A)."""
    return str(sym).strip().upper().replace(".", "-")


def market_cap_in_millions(value):
    if value is None or (isinstance(value, float) and value != value):
        return None
    try:
        return round(float(value) / 1e6, 4)
    except (TypeError, ValueError):
        return None


def _safe_round(x, nd=4):
    if x is None:
        return None
    try:
        if isinstance(x, float) and (math.isnan(x) or math.isinf(x)):
            return None
        return round(float(x), nd)
    except (TypeError, ValueError):
        return None


# ──────────────────────────────────────────────────────────────────────────────
# Market-cap cache — v04 timestamps entries so they actually expire
# ──────────────────────────────────────────────────────────────────────────────

def load_cache(path: Path, ttl_days: int):
    """
    Returns (fresh_caps: dict[str, float], n_expired: int).

    v1 caches were a flat {ticker: cap} dict with no timestamps. There is no way
    to know how old those values are, so they are treated as expired — which is
    exactly the bug this fixes.
    """
    if not path.exists() or ttl_days < 0:
        return {}, 0
    try:
        blob = json.loads(path.read_text())
    except Exception:
        return {}, 0

    if not isinstance(blob, dict):
        return {}, 0

    if blob.get("_format") != CACHE_FORMAT:
        n = len(blob) if isinstance(blob, dict) else 0
        print(f"    ℹ️  Legacy (untimestamped) cap cache found with {n} entries — "
              f"treating all as expired.")
        return {}, n

    today = date.today()
    fresh, expired = {}, 0
    for tkr, rec in (blob.get("caps") or {}).items():
        try:
            cap = float(rec["cap"])
            ts = datetime.strptime(rec["ts"], "%Y-%m-%d").date()
        except Exception:
            expired += 1
            continue
        if (today - ts).days <= ttl_days:
            fresh[tkr] = cap
        else:
            expired += 1
    return fresh, expired


def save_cache(path: Path, caps: dict, stamps: dict):
    """Persist caps with a per-entry fetch date."""
    today = date.today().isoformat()
    payload = {
        "_format": CACHE_FORMAT,
        "_written": today,
        "caps": {
            k: {"cap": float(v), "ts": stamps.get(k, today)}
            for k, v in caps.items() if v is not None
        },
    }
    try:
        path.write_text(json.dumps(payload))
    except Exception as e:
        print(f"    ⚠️  Could not write cap cache: {e}")


# ──────────────────────────────────────────────────────────────────────────────
# Batched market-cap fetch — /v7/finance/quote
# ──────────────────────────────────────────────────────────────────────────────

def _chunks(seq, size):
    for i in range(0, len(seq), size):
        yield seq[i:i + size]


def fetch_caps_batched(tickers, session, chunk_size):
    """~chunk_size symbols per request. Returns {original_ticker: cap_millions}."""
    if YfData is None:
        print("    ⚠️  yfinance.data.YfData unavailable — skipping batch path.")
        return {}
    try:
        yfd = YfData(session=session)
    except Exception as e:
        print(f"    ⚠️  Could not init YfData ({e}) — skipping batch path.")
        return {}

    y2orig = {to_yahoo_symbol(t): t for t in tickers}
    ysyms = list(y2orig.keys())
    out = {}
    chunk_list = list(_chunks(ysyms, chunk_size))
    print(f"\n🚀  Batched cap fetch: {len(ysyms)} tickers in {len(chunk_list)} "
          f"requests (~{chunk_size}/request) …")

    for chunk in tqdm(chunk_list, unit="chunk"):
        params = {"symbols": ",".join(chunk)}
        for attempt in range(QUOTE_MAX_RETRIES):
            try:
                data = yfd.get_raw_json(QUOTE_URL, params=params)
                results = (data or {}).get("quoteResponse", {}).get("result", []) or []
                for q in results:
                    orig = y2orig.get(q.get("symbol"))
                    cap_m = market_cap_in_millions(q.get("marketCap"))
                    if orig is not None and cap_m is not None:
                        out[orig] = cap_m
                break
            except YFRateLimitError:
                time.sleep(RETRY_BASE * (2 ** attempt) + random.uniform(0, 1.0))
            except Exception:
                time.sleep(1.0 * (attempt + 1) + random.uniform(0, 0.5))
        time.sleep(QUOTE_CHUNK_PAUSE)

    print(f"    ✔️  Batch resolved {len(out)}/{len(tickers)} caps.")
    return out


# ──────────────────────────────────────────────────────────────────────────────
# Per-ticker market-cap fallback
# ──────────────────────────────────────────────────────────────────────────────

def _raw_cap_from_ticker(tk, last_close):
    try:
        cap = tk.fast_info.get("marketCap")
        if cap:
            return cap
    except YFRateLimitError:
        raise
    except Exception:
        pass
    try:
        shares = tk.fast_info.get("shares")
        px = None
        try:
            px = tk.fast_info.get("lastPrice")
        except Exception:
            px = None
        if not px:
            px = last_close
        if shares and px:
            return float(shares) * float(px)
    except YFRateLimitError:
        raise
    except Exception:
        pass
    try:
        cap = tk.info.get("marketCap")
        if cap:
            return cap
    except YFRateLimitError:
        raise
    except Exception:
        pass
    return None


def fetch_one_cap(orig_ticker, session, last_close):
    ysym = to_yahoo_symbol(orig_ticker)
    for attempt in range(MAX_RETRIES):
        try:
            tk = yf.Ticker(ysym, session=session) if session else yf.Ticker(ysym)
            cap_m = market_cap_in_millions(_raw_cap_from_ticker(tk, last_close))
            return orig_ticker, cap_m, ("ok" if cap_m is not None else "missing")
        except YFRateLimitError:
            time.sleep(RETRY_BASE * (2 ** attempt) + random.uniform(0, 1.0))
        except Exception:
            return orig_ticker, None, "missing"
    return orig_ticker, None, "rate_limited"


def fetch_market_caps(tickers, workers, last_close=None):
    last_close = last_close or {}
    print(f"\n💰  Per-ticker cap fallback for {len(tickers)} tickers "
          f"({workers} threads) …")
    session = make_session()
    if session is None:
        print("    ⚠️  curl_cffi unavailable — `pip install curl_cffi` recommended.")

    caps, rate_limited = {}, []
    batch_size = max(workers * 4, 8)

    with tqdm(total=len(tickers), unit="ticker") as pbar:
        for i in range(0, len(tickers), batch_size):
            batch = tickers[i:i + batch_size]
            with ThreadPoolExecutor(max_workers=workers) as pool:
                futures = {pool.submit(fetch_one_cap, t, session, last_close.get(t)): t
                           for t in batch}
                for fut in as_completed(futures):
                    tkr, cap_m, status = fut.result()
                    caps[tkr] = cap_m
                    if status == "rate_limited":
                        rate_limited.append(tkr)
                    pbar.update(1)
            if i + batch_size < len(tickers):
                time.sleep(BATCH_PAUSE)

    if rate_limited:
        print(f"\n🔁  Re-trying {len(rate_limited)} rate-limited tickers sequentially …")
        for tkr in tqdm(rate_limited, unit="ticker"):
            _, cap_m, _ = fetch_one_cap(tkr, session, last_close.get(tkr))
            if cap_m is not None:
                caps[tkr] = cap_m
            time.sleep(1.0 + random.uniform(0, 0.5))

    return pd.Series(caps, name="Market Cap")


# ──────────────────────────────────────────────────────────────────────────────
# Price history
# ──────────────────────────────────────────────────────────────────────────────

def _extract_field(raw, field):
    """
    Pull one OHLCV field out of a yf.download result. yfinance has shipped both
    (field, symbol) and (symbol, field) MultiIndex orderings; handle either, and
    the single-symbol flat-column case.
    """
    if raw is None or len(raw) == 0:
        return None
    if isinstance(raw.columns, pd.MultiIndex):
        lvl0 = raw.columns.get_level_values(0)
        lvl1 = raw.columns.get_level_values(1)
        if field in set(lvl0):
            return raw.xs(field, axis=1, level=0)
        if field in set(lvl1):
            return raw.xs(field, axis=1, level=1)
        return None
    if field in raw.columns:
        return raw[[field]]
    return None


def fetch_price_history(ysyms, period, benchmark):
    """Bulk-download daily bars once. Returns (close_df, volume_df)."""
    want = list(dict.fromkeys(ysyms + [benchmark]))
    print(f"\n📥  Downloading {period} of daily history for {len(want)} symbols "
          f"(incl. benchmark {benchmark}) …")

    raw = yf.download(want, period=period, auto_adjust=True,
                      progress=True, threads=True, group_by="column")

    close = _extract_field(raw, "Close")
    volume = _extract_field(raw, "Volume")

    if close is None:
        raise SystemExit("❌  Could not extract Close prices from the download.")

    if not isinstance(raw.columns, pd.MultiIndex) and len(want) == 1:
        close.columns = want
        if volume is not None:
            volume.columns = want

    close = close.sort_index()
    if volume is not None:
        volume = volume.reindex(columns=close.columns).sort_index()

    close.index = pd.to_datetime(close.index)
    if volume is not None:
        volume.index = pd.to_datetime(volume.index)

    missing = [s for s in want if s not in close.columns]
    if missing:
        print(f"    ⚠️  {len(missing)} symbols returned no price column at all.")
    return close, volume


def compute_returns(close, ysym_to_orig, staleness_days):
    """
    Date-anchored returns. Every window is measured from the LAST COMMON TRADING
    DATE back a fixed number of calendar days, using the last available close at
    or before that date. Symbols whose own last bar lags the market are flagged
    Stale and nulled instead of quietly reporting a shifted window.
    """
    if len(close.index) == 0:
        raise SystemExit("❌  Empty price history.")
    market_last = close.index.max()
    print(f"\n📐  Computing date-anchored returns · market last bar = "
          f"{market_last.date()}")

    rows, last_close, status = [], {}, {}
    for ysym in tqdm(list(close.columns), unit="symbol"):
        orig = ysym_to_orig.get(ysym)
        if orig is None:
            continue
        row = {"Ticker": orig}
        valid = close[ysym].dropna()

        if len(valid) < 2:
            for col in OFFSETS_DAYS:
                row[col] = None
            row["Last Bar Date"] = None
            row["Stale"] = True
            status[orig] = "no_data"
            rows.append(row)
            continue

        sym_last = valid.index[-1]
        lag = (market_last - sym_last).days
        stale = lag > staleness_days
        row["Last Bar Date"] = sym_last.date().isoformat()
        row["Stale"] = bool(stale)
        last_close[orig] = float(valid.iloc[-1])

        if stale:
            for col in OFFSETS_DAYS:
                row[col] = None
            status[orig] = f"stale_{lag}d"
        else:
            cur = float(valid.iloc[-1])
            partial = False
            for col, days in OFFSETS_DAYS.items():
                base = valid.asof(market_last - pd.Timedelta(days=days))
                if base is None or pd.isna(base) or float(base) == 0.0:
                    row[col] = None
                    partial = True
                else:
                    row[col] = _safe_round((cur - float(base)) / float(base), 4)
            status[orig] = "partial" if partial else "ok"
        rows.append(row)

    df = pd.DataFrame(rows).set_index("Ticker")
    return df, last_close, status, market_last


# ──────────────────────────────────────────────────────────────────────────────
# Technicals — the layer v03 never produced
# ──────────────────────────────────────────────────────────────────────────────

def _ppo(series, fast=PPO_FAST, slow=PPO_SLOW, signal=PPO_SIGNAL):
    """Percentage Price Oscillator + signal + histogram."""
    ef = series.ewm(span=fast, adjust=False).mean()
    es = series.ewm(span=slow, adjust=False).mean()
    ppo = (ef - es) / es.replace(0, np.nan) * 100.0
    sig = ppo.ewm(span=signal, adjust=False).mean()
    return ppo, sig, ppo - sig


def compute_technicals(close, volume, ysym_to_orig, benchmark, down_day_window,
                       stale=None):
    """
    Per-ticker weekly trend structure, daily momentum, relative strength,
    a volume accumulation proxy, and down-day behaviour measured on the
    benchmark's actual negative sessions.

    Symbols flagged stale by compute_returns are skipped: an EMA or PPO reading
    taken from bars that stopped weeks ago is worse than no reading at all.
    """
    stale = stale or set()
    print("\n📈  Computing weekly trend, PPO, relative strength and down-day stats …")

    if benchmark not in close.columns:
        print(f"    ⚠️  Benchmark {benchmark} missing — RS and down-day stats skipped.")
        bench = None
        down_days = pd.DatetimeIndex([])
    else:
        bench = close[benchmark].dropna()
        bench_ret = bench.pct_change()
        recent = bench_ret.tail(down_day_window)
        down_days = recent[recent < 0].index
        print(f"    Benchmark down days in last {down_day_window} sessions: "
              f"{len(down_days)}")

    daily_ret = close.pct_change()
    weekly = close.resample("W-FRI").last()

    rows = []
    for ysym in tqdm(list(close.columns), unit="symbol"):
        orig = ysym_to_orig.get(ysym)
        if orig is None or orig in stale:
            continue
        rec = {"Ticker": orig}

        w = weekly[ysym].dropna()
        d = close[ysym].dropna()

        # ── Weekly trend structure ───────────────────────────────────────────
        if len(w) >= EMA_WEEKS + 5:
            ema = w.ewm(span=EMA_WEEKS, adjust=False).mean()
            last_px, last_ema = float(w.iloc[-1]), float(ema.iloc[-1])
            rec["Pct vs 30W EMA"] = _safe_round((last_px - last_ema) / last_ema * 100, 2)
            rec["Above 30W EMA"] = bool(last_px > last_ema)
            rec["30W EMA Rising"] = bool(float(ema.iloc[-1]) > float(ema.iloc[-5]))
            wppo, _, whist = _ppo(w)
            rec["Weekly PPO"] = _safe_round(wppo.iloc[-1], 3)
            rec["Weekly PPO Hist"] = _safe_round(whist.iloc[-1], 3)
            if len(whist.dropna()) >= 3:
                rec["Weekly Hist Improving"] = bool(
                    float(whist.iloc[-1]) > float(whist.iloc[-2]))
            else:
                rec["Weekly Hist Improving"] = None
        else:
            for k in ("Pct vs 30W EMA", "Above 30W EMA", "30W EMA Rising",
                      "Weekly PPO", "Weekly PPO Hist", "Weekly Hist Improving"):
                rec[k] = None

        # ── Daily momentum ───────────────────────────────────────────────────
        if len(d) >= PPO_SLOW + PPO_SIGNAL + 5:
            dppo, dsig, dhist = _ppo(d)
            rec["Daily PPO"] = _safe_round(dppo.iloc[-1], 3)
            rec["Daily PPO Hist"] = _safe_round(dhist.iloc[-1], 3)
            rec["Daily PPO Near Zero"] = bool(abs(float(dppo.iloc[-1])) <= PPO_ZERO_BAND)
            rec["Daily PPO Turning Up"] = bool(float(dhist.iloc[-1]) > float(dhist.iloc[-2]))
            rec["Daily PPO Above Signal"] = bool(float(dppo.iloc[-1]) > float(dsig.iloc[-1]))
        else:
            for k in ("Daily PPO", "Daily PPO Hist", "Daily PPO Near Zero",
                      "Daily PPO Turning Up", "Daily PPO Above Signal"):
                rec[k] = None

        # ── Relative strength vs benchmark ───────────────────────────────────
        rec["RS 1M Change %"] = None
        rec["RS Improving"] = None
        if bench is not None and len(d) > 5 and ysym != benchmark:
            rs = (d / bench.reindex(d.index)).dropna()
            if len(rs) > 5:
                anchor = rs.asof(rs.index[-1] - pd.Timedelta(days=RS_LOOKBACK_DAYS))
                if anchor is not None and not pd.isna(anchor) and float(anchor) != 0:
                    chg = (float(rs.iloc[-1]) - float(anchor)) / float(anchor) * 100
                    rec["RS 1M Change %"] = _safe_round(chg, 2)
                    rec["RS Improving"] = bool(chg > 0)

        # ── Volume accumulation proxy ────────────────────────────────────────
        rec["Vol Ratio 20/60"] = None
        if volume is not None and ysym in volume.columns:
            dv = (close[ysym] * volume[ysym]).dropna()
            if len(dv) >= VOL_LONG:
                short = float(dv.tail(VOL_SHORT).mean())
                long_ = float(dv.tail(VOL_LONG).mean())
                if long_ > 0:
                    rec["Vol Ratio 20/60"] = _safe_round(short / long_, 2)

        # ── Down-day behaviour ───────────────────────────────────────────────
        rec["Down Day Capture"] = None
        rec["Down Day Green Rate %"] = None
        if len(down_days) > 0 and ysym in daily_ret.columns:
            r = daily_ret[ysym].reindex(down_days).dropna()
            if len(r) >= max(2, len(down_days) // 2):
                b = daily_ret[benchmark].reindex(r.index)
                bsum = float(b.sum())
                if abs(bsum) > 1e-6:
                    # <1 means it fell less than the market; <0 means it rose.
                    rec["Down Day Capture"] = _safe_round(float(r.sum()) / bsum, 2)
                rec["Down Day Green Rate %"] = _safe_round((r > 0).mean() * 100, 1)

        rows.append(rec)

    return pd.DataFrame(rows).set_index("Ticker")


# ──────────────────────────────────────────────────────────────────────────────
# Sub-market-cap allocation (generalised)
# ──────────────────────────────────────────────────────────────────────────────

def allocate_sub_market_cap(df):
    """
    100% when a ticker sits under a single sub-theme.
    Otherwise 60% to the Primary row and the remaining 40% split evenly across
    however many Secondary rows exist. v03 hard-coded 40% to each Secondary,
    which over-allocated any ticker carrying more than one Secondary tag.
    """
    if "Assignment" not in df.columns:
        raise ValueError("Column 'Assignment' is required for Sub Market Cap allocation.")

    assignment = df["Assignment"].astype(str).str.strip().str.title()
    counts = df.groupby("Ticker")["Ticker"].transform("size")
    n_secondary = (assignment.eq("Secondary")
                   .groupby(df["Ticker"]).transform("sum")
                   .replace(0, np.nan))

    mc = pd.to_numeric(df["Market Cap"], errors="coerce")
    sub = mc.copy()
    multi = counts >= 2
    sub = sub.mask(multi & assignment.eq("Primary"), mc * 0.60)
    sub = sub.mask(multi & assignment.eq("Secondary"), mc * 0.40 / n_secondary)
    return sub.round(4)


# ──────────────────────────────────────────────────────────────────────────────
# Aggregation
# ──────────────────────────────────────────────────────────────────────────────

def _apply_weight_cap(weights: pd.Series, cap_pct: float) -> pd.Series:
    """Iteratively cap each weight at cap_pct of the total, redistributing pro-rata."""
    w = weights.astype(float).copy()
    total = w.sum()
    if total <= 0 or cap_pct is None or cap_pct >= 1.0:
        return w
    for _ in range(25):
        total = w.sum()
        limit = total * cap_pct
        over = w > limit + 1e-9
        if not over.any():
            break
        excess = (w[over] - limit).sum()
        w[over] = limit
        under = ~over
        under_total = w[under].sum()
        if under_total <= 0:
            break
        w[under] = w[under] + excess * (w[under] / under_total)
    return w


def _weighted(values: pd.Series, weights: pd.Series):
    m = values.notna() & weights.notna() & (weights > 0)
    if not m.any():
        return None
    return float((values[m] * weights[m]).sum() / weights[m].sum())


def collapse_to_level(df, level_cols):
    """
    One row per (level, ticker). A ticker tagged into two sub-themes of the same
    theme entered v03's theme average twice, inflating its breadth and equal-
    weight contribution; summing its allocations first fixes that without
    changing the cap-weighted result.
    """
    agg = {"Weight": ("Sub Market Cap", "sum")}
    g = df.groupby(level_cols + ["Ticker"], as_index=False, dropna=False).agg(**agg)
    per_ticker_cols = [c for c in df.columns
                       if c not in ("Theme", "Sub Theme", "Assignment",
                                    "Sub Market Cap", "Ticker")]
    first = df.groupby("Ticker", as_index=True)[per_ticker_cols].first()
    return g.join(first, on="Ticker")


def summarise(df, level_cols, weight_cap=None, start_weights=False):
    """Cap-weighted and equal-weighted aggregates with concentration diagnostics."""
    collapsed = collapse_to_level(df, level_cols)
    out = []

    for keys, d in collapsed.groupby(level_cols, dropna=False):
        keys = keys if isinstance(keys, tuple) else (keys,)
        rec = dict(zip(level_cols, keys))
        w_raw = d["Weight"].astype(float)
        w = _apply_weight_cap(w_raw, weight_cap) if weight_cap else w_raw

        rec["Constituents"] = int(d["Ticker"].nunique())
        rec["Theme Cap ($M)"] = _safe_round(float(w_raw.sum()), 1)

        for col, short in (("1W Price Change %", "1W"),
                           ("1M Price Change %", "1M"),
                           ("3M Price Change %", "3M")):
            vals = pd.to_numeric(d[col], errors="coerce")
            ww = w
            if start_weights:
                # Approximate beginning-of-period cap: end cap / (1 + return).
                ww = (w / (1.0 + vals.fillna(0.0))).replace([np.inf, -np.inf], np.nan)
            cw = _weighted(vals, ww)
            ew = vals.mean()
            rec[f"CapWtd {short} %"] = _safe_round(None if cw is None else cw * 100, 2)
            rec[f"EqWtd {short} %"] = _safe_round(None if pd.isna(ew) else ew * 100, 2)

        v1w = pd.to_numeric(d["1W Price Change %"], errors="coerce")
        n_valid = int(v1w.notna().sum())
        rec["Breadth 1W %"] = _safe_round((v1w > 0).sum() / n_valid * 100, 1) if n_valid else None
        rec["Coverage %"] = _safe_round(n_valid / len(d) * 100, 1) if len(d) else None

        tot = float(w_raw.sum())
        if tot > 0:
            shares = (w_raw / tot).sort_values(ascending=False)
            rec["Top3 Weight %"] = _safe_round(float(shares.head(3).sum()) * 100, 1)
            hhi = float((shares ** 2).sum())
            rec["Effective N"] = _safe_round(1.0 / hhi, 1) if hhi > 0 else None
            rec["Top Name"] = str(d.loc[w_raw.idxmax(), "Ticker"])
        else:
            rec["Top3 Weight %"] = rec["Effective N"] = rec["Top Name"] = None

        cw1, ew1 = rec["CapWtd 1W %"], rec["EqWtd 1W %"]
        rec["Distortion pp"] = _safe_round(cw1 - ew1, 2) if (cw1 is not None and ew1 is not None) else None
        rec["Mega Cap Distorted"] = (
            bool(abs(rec["Distortion pp"]) > SCREEN["early_max_distort"])
            if rec["Distortion pp"] is not None else None)

        for src, dst in (("Down Day Capture", "Down Day Capture"),
                         ("Vol Ratio 20/60", "Vol Ratio 20/60")):
            if src in d.columns:
                rec[dst] = _safe_round(_weighted(pd.to_numeric(d[src], errors="coerce"), w), 2)

        if "Above 30W EMA" in d.columns:
            s = d["Above 30W EMA"].dropna()
            rec["Pct Above 30W EMA"] = _safe_round(s.astype(bool).mean() * 100, 1) if len(s) else None

        # Acceleration: weekly pace vs the average weekly pace of the month.
        if rec["CapWtd 1W %"] is not None and rec["CapWtd 1M %"] is not None:
            rec["Acceleration pp"] = _safe_round(
                rec["CapWtd 1W %"] - rec["CapWtd 1M %"] / 4.3, 2)
        else:
            rec["Acceleration pp"] = None

        rec["Signal"] = classify(rec)
        out.append(rec)

    sort_key = "CapWtd 1W %"
    res = pd.DataFrame(out)
    if sort_key in res.columns:
        res = res.sort_values(sort_key, ascending=False, na_position="last")
    return res.reset_index(drop=True)


def classify(rec):
    """
    Explicit numeric rotation screen. The point is reproducibility: the same
    inputs must produce the same upgrade/downgrade every week, so the report's
    change log is mechanical rather than narrative.
    """
    w1, m1, m3 = rec.get("CapWtd 1W %"), rec.get("CapWtd 1M %"), rec.get("CapWtd 3M %")
    e1 = rec.get("EqWtd 1W %")
    breadth = rec.get("Breadth 1W %")
    distort = rec.get("Distortion pp")
    if w1 is None or m1 is None:
        return "INSUFFICIENT DATA"

    s = SCREEN
    if (w1 <= s["failed_max_1w"]) or (breadth is not None and breadth <= s["failed_max_breadth"]):
        return "FAILED ROTATION"

    early = (
        w1 >= s["early_min_1w"]
        and s["early_1m_floor"] <= m1 <= s["early_1m_ceiling"]
        and w1 > (m1 / 4.3)
        and (breadth is None or breadth >= s["early_min_breadth"])
        and (distort is None or abs(distort) <= s["early_max_distort"])
        and (m3 is None or m3 >= s["early_min_3m"])
        # the equal-weighted move must also be positive: no signal that exists
        # only in the cap-weighted number
        and (e1 is None or e1 > 0)
    )
    if early:
        return "EARLY ROTATION"

    if (m1 >= s["mature_min_1m"]) or (m3 is not None and m3 >= s["mature_min_3m"] and w1 > 0):
        return "MATURE LEADERSHIP"
    return "MIXED / CONSOLIDATING"


# ──────────────────────────────────────────────────────────────────────────────
# PPO reset screen
# ──────────────────────────────────────────────────────────────────────────────

def ppo_candidates(df):
    """
    'Weekly trend intact + daily PPO reset + improving relative strength.'
    v03 shipped none of these fields, so prior reports inferred the setup from
    1W/1M/3M returns. This measures it.
    """
    needed = ["Above 30W EMA", "30W EMA Rising", "Daily PPO", "Daily PPO Near Zero",
              "Daily PPO Turning Up", "RS 1M Change %"]
    if not all(c in df.columns for c in needed):
        return pd.DataFrame()

    t = (df.sort_values("Sub Market Cap", ascending=False)
           .drop_duplicates(subset="Ticker", keep="first")
           .copy())

    weekly_ok = t["Above 30W EMA"].fillna(False).astype(bool) & \
                t["30W EMA Rising"].fillna(False).astype(bool)
    reset = t["Daily PPO Near Zero"].fillna(False).astype(bool)
    turning = t["Daily PPO Turning Up"].fillna(False).astype(bool)
    rs_ok = pd.to_numeric(t["RS 1M Change %"], errors="coerce") > 0
    hist_ok = t.get("Weekly Hist Improving", pd.Series(False, index=t.index)) \
               .fillna(False).astype(bool)
    accum = pd.to_numeric(t.get("Vol Ratio 20/60"), errors="coerce").fillna(0) >= 1.0

    t["Setup"] = None

    # High conviction requires the full stack from the framework: price above a
    # rising 30W EMA, weekly histogram improving, daily PPO reset to zero and
    # turning up, and relative strength already improving.
    t.loc[weekly_ok & hist_ok & reset & turning & rs_ok, "Setup"] = "HIGH CONVICTION"
    t.loc[t["Setup"].isna() & weekly_ok & reset & (rs_ok | hist_ok), "Setup"] = "WATCHLIST"
    t.loc[t["Setup"].isna() & weekly_ok & (reset | turning) & accum, "Setup"] = "WATCHLIST"

    cols = ["Ticker", "Company Name", "Theme", "Sub Theme", "Setup", "Market Cap",
            "1W Price Change %", "1M Price Change %", "3M Price Change %",
            "Pct vs 30W EMA", "Weekly PPO Hist", "Weekly Hist Improving",
            "Daily PPO", "Daily PPO Hist", "Daily PPO Turning Up",
            "RS 1M Change %", "Vol Ratio 20/60", "Down Day Capture"]
    cols = [c for c in cols if c in t.columns]
    out = t[t["Setup"].notna()][cols].copy()
    order = {"HIGH CONVICTION": 0, "WATCHLIST": 1}
    out["_o"] = out["Setup"].map(order)
    return (out.sort_values(["_o", "Market Cap"], ascending=[True, False])
               .drop(columns="_o").reset_index(drop=True))


# ──────────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────────

def main():
    p = argparse.ArgumentParser(description="Weekly theme data updater (v04)")
    p.add_argument("--input", default=DEFAULT_INPUT)
    p.add_argument("--output", default=DEFAULT_OUTPUT)
    p.add_argument("--outdir", default=None,
                   help="Directory for summary/manifest files (default: output's folder).")
    p.add_argument("--workers", type=int, default=DEFAULT_WORKERS)
    p.add_argument("--chunk", type=int, default=DEFAULT_CHUNK)
    p.add_argument("--period", default=HISTORY_PERIOD,
                   help="Daily history period (default 2y; needs >=1y for the 30W EMA).")
    p.add_argument("--benchmark", default=BENCHMARK)
    p.add_argument("--cache-ttl", type=int, default=DEFAULT_CACHE_TTL_DAYS,
                   help="Refetch caps older than N days (default 6). 0 means only entries fetched today count as fresh; use --no-cache to force a full refetch.")
    p.add_argument("--staleness-days", type=int, default=STALENESS_DAYS)
    p.add_argument("--down-days", type=int, default=DOWN_DAY_WINDOW)
    p.add_argument("--weight-cap", type=float, default=None,
                   help="Cap any single name at this share of a theme, e.g. 0.15.")
    p.add_argument("--min-constituents", type=int, default=MIN_CONSTITUENTS)
    p.add_argument("--start-weights", action="store_true",
                   help="Weight each window by approximate period-START cap.")
    p.add_argument("--no-batch", action="store_true")
    p.add_argument("--no-cache", action="store_true")
    p.add_argument("--no-technicals", action="store_true")
    p.add_argument("--no-rotate", action="store_true",
                   help="Do not copy the existing output to *_Last_Week.csv.")
    args = p.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        sys.exit(f"❌  Input file not found: {input_path}")

    output_path = Path(args.output)
    outdir = Path(args.outdir) if args.outdir else output_path.parent
    outdir.mkdir(parents=True, exist_ok=True)

    print(f"📂  Reading {input_path} …")
    df = pd.read_csv(input_path)
    for col in ("Ticker", "Assignment", "Theme", "Sub Theme"):
        if col not in df.columns:
            sys.exit(f"❌  Column '{col}' not found in the input CSV.")
    df["Ticker"] = df["Ticker"].astype(str).str.strip()

    tickers = df["Ticker"].dropna().unique().tolist()
    print(f"    {len(df):,} rows · {len(tickers):,} unique tickers · "
          f"{df['Theme'].nunique()} themes · {df['Sub Theme'].nunique()} sub-themes")

    # Universe diff vs the previous stable output, so dropped names are visible.
    prev_tickers = set()
    if output_path.exists():
        try:
            prev_tickers = set(pd.read_csv(output_path)["Ticker"].astype(str).str.strip())
        except Exception:
            pass
    added = sorted(set(tickers) - prev_tickers) if prev_tickers else []
    dropped = sorted(prev_tickers - set(tickers)) if prev_tickers else []

    ysyms = [to_yahoo_symbol(t) for t in tickers]
    ysym_to_orig = dict(zip(ysyms, tickers))

    # ── 1. Prices ────────────────────────────────────────────────────────────
    close, volume = fetch_price_history(ysyms, args.period, args.benchmark)
    price_df, last_close, status, market_last = compute_returns(
        close, ysym_to_orig, args.staleness_days)
    as_of = market_last.date().isoformat()

    # ── 2. Technicals ────────────────────────────────────────────────────────
    stale_set = {t for t, s in status.items()
                 if str(s).startswith("stale") or s == "no_data"}
    if args.no_technicals:
        tech_df = pd.DataFrame(index=pd.Index([], name="Ticker"))
    else:
        tech_df = compute_technicals(close, volume, ysym_to_orig,
                                     args.benchmark, args.down_days,
                                     stale=stale_set)

    # ── 3. Market caps: fresh cache → batched quote → per-ticker fallback ────
    cache_path = output_path.with_suffix(".capcache.json")
    ttl = -1 if args.no_cache else args.cache_ttl
    cached, n_expired = ({}, 0) if args.no_cache else load_cache(cache_path, ttl)
    to_fetch = [t for t in tickers if t not in cached]
    print(f"\n💾  Cap cache: {len(cached)} fresh (≤{args.cache_ttl}d) · "
          f"{n_expired} expired · {len(to_fetch)} to fetch")

    resolved, stamps = {}, {}
    today_iso = date.today().isoformat()
    if to_fetch and not args.no_batch:
        resolved.update(fetch_caps_batched(to_fetch, make_session(), args.chunk))
    still_missing = [t for t in to_fetch if t not in resolved]
    if still_missing:
        print(f"\n↩️  {len(still_missing)} tickers unresolved by batch — falling back …")
        fb = fetch_market_caps(still_missing, args.workers, last_close)
        for t, v in fb.items():
            if v is not None:
                resolved[t] = v
    for t in resolved:
        stamps[t] = today_iso

    cap_series = pd.concat([pd.Series(cached, dtype="float64"),
                            pd.Series(resolved, dtype="float64")])
    cap_series = cap_series[~cap_series.index.duplicated(keep="last")]
    cap_series.name = "Market Cap"
    if not args.no_cache:
        # Preserve original timestamps for entries that came from the cache.
        try:
            old = json.loads(cache_path.read_text()) if cache_path.exists() else {}
            for k, v in (old.get("caps") or {}).items():
                stamps.setdefault(k, v.get("ts", today_iso))
        except Exception:
            pass
        save_cache(cache_path, cap_series.to_dict(), stamps)

    # ── 4. Merge ─────────────────────────────────────────────────────────────
    print("\n🔗  Merging results …")
    generated = (["Market Cap", "Sub Market Cap", "Data As Of", "Last Bar Date", "Stale",
                  "Return Status"] + list(OFFSETS_DAYS) + list(tech_df.columns))
    df.drop(columns=[c for c in generated if c in df.columns], inplace=True, errors="ignore")

    df["Market Cap"] = df["Ticker"].map(cap_series)
    for col in list(OFFSETS_DAYS) + ["Last Bar Date", "Stale"]:
        if col in price_df.columns:
            df[col] = df["Ticker"].map(price_df[col])
    df["Return Status"] = df["Ticker"].map(status)
    for col in tech_df.columns:
        df[col] = df["Ticker"].map(tech_df[col])

    df["Sub Market Cap"] = allocate_sub_market_cap(df)
    df["Data As Of"] = as_of

    for col in ["Market Cap", "Sub Market Cap"] + list(OFFSETS_DAYS):
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Column order: v03 layout first so downstream consumers keep working.
    lead = ["Ticker", "Company Name", "Theme", "Sub Theme", "Assignment",
            "Market Cap"] + list(OFFSETS_DAYS) + ["Sub Market Cap"]
    lead = [c for c in lead if c in df.columns]
    df = df[lead + [c for c in df.columns if c not in lead]]

    # ── 5. Write detail + rotate previous ────────────────────────────────────
    if output_path.exists() and not args.no_rotate:
        lastweek = output_path.with_name(output_path.stem + "_Last_Week.csv")
        try:
            shutil.copy2(output_path, lastweek)
            print(f"    ↪️  Previous output rotated to {lastweek.name}")
        except Exception as e:
            print(f"    ⚠️  Could not rotate previous output: {e}")

    df.to_csv(output_path, index=False)
    archive = outdir / f"{output_path.stem}_{as_of}.csv"
    df.to_csv(archive, index=False)
    print(f"\n✅  Saved {len(df):,} rows → {output_path}")
    print(f"    Archived snapshot → {archive.name}")

    # ── 6. Summaries ─────────────────────────────────────────────────────────
    print("\n📊  Building theme and sub-theme summaries …")
    theme_sum = summarise(df, ["Theme"], args.weight_cap, args.start_weights)
    sub_sum = summarise(df, ["Theme", "Sub Theme"], args.weight_cap, args.start_weights)
    sub_sum["Below Min Constituents"] = sub_sum["Constituents"] < args.min_constituents

    theme_path = outdir / f"Theme_Summary_{as_of}.csv"
    sub_path = outdir / f"SubTheme_Summary_{as_of}.csv"
    theme_sum.to_csv(theme_path, index=False)
    sub_sum.to_csv(sub_path, index=False)
    print(f"    → {theme_path.name} ({len(theme_sum)} themes)")
    print(f"    → {sub_path.name} ({len(sub_sum)} sub-themes, "
          f"{int(sub_sum['Below Min Constituents'].sum())} below the {args.min_constituents}-name floor)")

    cands = ppo_candidates(df)
    cand_path = outdir / f"PPO_Candidates_{as_of}.csv"
    if len(cands):
        cands.to_csv(cand_path, index=False)
        hi = int((cands["Setup"] == "HIGH CONVICTION").sum())
        print(f"    → {cand_path.name} ({hi} high conviction, "
              f"{len(cands) - hi} watchlist)")
    else:
        print("    → no PPO candidates (technicals disabled or insufficient history)")

    # ── 7. Manifest ──────────────────────────────────────────────────────────
    status_counts = pd.Series(status).value_counts().to_dict()
    no_cap = sorted(df.loc[df["Market Cap"].isna(), "Ticker"].unique().tolist())
    stale = sorted([t for t, s in status.items() if str(s).startswith("stale")])
    nodata = sorted([t for t, s in status.items() if s == "no_data"])
    partial = sorted([t for t, s in status.items() if s == "partial"])

    manifest = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "data_as_of": as_of,
        "benchmark": args.benchmark,
        "history_period": args.period,
        "lookback_calendar_days": OFFSETS_DAYS,
        "weight_cap": args.weight_cap,
        "start_weights": bool(args.start_weights),
        "universe": {
            "rows": int(len(df)),
            "tickers": int(df["Ticker"].nunique()),
            "themes": int(df["Theme"].nunique()),
            "sub_themes": int(df["Sub Theme"].nunique()),
            "added_vs_previous": added,
            "dropped_vs_previous": dropped,
        },
        "coverage": {
            "market_cap": int(df["Market Cap"].notna().groupby(df["Ticker"]).any().sum()),
            "return_status_counts": {str(k): int(v) for k, v in status_counts.items()},
        },
        "failures": {
            "no_market_cap": no_cap,
            "no_price_data": nodata,
            "stale_symbols": stale,
            "partial_history": partial,
        },
        "outputs": {
            "detail": str(output_path),
            "archive": str(archive),
            "theme_summary": str(theme_path),
            "subtheme_summary": str(sub_path),
            "ppo_candidates": str(cand_path) if len(cands) else None,
        },
    }
    manifest_path = outdir / f"run_manifest_{as_of}.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))
    print(f"    → {manifest_path.name}")

    # ── 8. Console summary ───────────────────────────────────────────────────
    print("\n📋  Coverage")
    print(f"    Data as of        — {as_of}")
    print(f"    Market Cap        — {manifest['coverage']['market_cap']}/{len(tickers)} tickers")
    print(f"    Return status     — {status_counts}")
    for label, lst in (("no price data", nodata), ("stale", stale),
                       ("partial history", partial), ("no market cap", no_cap)):
        if lst:
            print(f"    ⚠️  {len(lst)} {label}: {', '.join(lst[:30])}"
                  + (" …" if len(lst) > 30 else ""))
    if dropped or added:
        print(f"    Universe diff     — +{len(added)} / -{len(dropped)} vs previous run")
        if dropped:
            print(f"       dropped: {', '.join(dropped[:20])}")

    flagged = theme_sum[theme_sum["Mega Cap Distorted"] == True]  # noqa: E712
    if len(flagged):
        print(f"\n⚠️  {len(flagged)} themes are mega-cap distorted "
              f"(|cap-wtd − equal-wtd| > {SCREEN['early_max_distort']}pp). "
              f"Use the equal-weighted read for rotation calls:")
        for _, r in flagged.iterrows():
            print(f"       {r['Theme']:<38} cap {r['CapWtd 1W %']:>6}%  "
                  f"eq {r['EqWtd 1W %']:>6}%  top {r['Top Name']}  "
                  f"effN {r['Effective N']}")

    early = theme_sum[theme_sum["Signal"] == "EARLY ROTATION"]
    if len(early):
        print("\n🎯  Themes passing the EARLY ROTATION screen:")
        for _, r in early.iterrows():
            print(f"       {r['Theme']:<38} 1W {r['CapWtd 1W %']:>6}%  "
                  f"1M {r['CapWtd 1M %']:>6}%  breadth {r['Breadth 1W %']}%")
    else:
        print("\n🎯  No themes passed the EARLY ROTATION screen this week.")


if __name__ == "__main__":
    main()
