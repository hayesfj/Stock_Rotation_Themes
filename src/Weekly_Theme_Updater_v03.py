"""
Weekly_Theme_Updater_v03.py
───────────────────────────
Reads the Input_Ticker_List_by_Theme.csv, fetches fresh market data from
Yahoo Finance for every unique ticker, and writes an updated CSV with:

  • Market Cap          — most-recent market capitalisation in millions (float)
  • Sub Market Cap      — allocated market capitalisation in millions (float):
                            100 % for tickers under only one Sub Theme;
                            60 % of Market Cap when Assignment == "Primary";
                            40 % of Market Cap when Assignment == "Secondary"
  • 1W / 1M / 3M Price Change %  — adjusted-close fractional changes
                            (float, 4 dp; a +1.234 % move → 0.0123)

EVOLUTION
─────────
v01  left ~55 % of Market Cap cells blank: it fetched cap one ticker at a time
     via `yf.Ticker(t).fast_info.market_cap` across 10 threads. That per-ticker
     hammering trips Yahoo's rate limiter, and fast_info returns None (not an
     exception) when throttled, so failures were silent.
v02  fixed reliability with a curl_cffi session, retry/backoff, a per-ticker
     fallback chain, symbol normalisation, caching, and honest diagnostics —
     but was still up to ~1,400 requests for the cap phase.
v03  (this file) adds the BATCHED path as the primary cap source:

       Yahoo's /v7/finance/quote endpoint returns `marketCap` for ~100 symbols
       in ONE authenticated request. For ~1,400 tickers that's ~14 requests
       instead of ~1,400 — the same "one bulk call" trick that makes price
       history reliable. yfinance's own YfData handles the cookie+crumb
       handshake, so we reuse its authenticated session.

     Cap resolution order in v03:
       1. Batched /v7/quote in chunks of 100      (fast, ~14 requests total)
       2. shares × last close, locally            (for symbols the batch omits)
       3. v02 per-ticker fallback chain           (mops up remaining stragglers)

     Everything else from v02 is retained: curl_cffi session, symbol
     normalisation (BF.B → BF-B), on-disk cap cache, and rate-limited-vs-missing
     reporting. The price-change path (single yf.download) is unchanged.

Usage
─────
    pip install "yfinance>=0.2.40" curl_cffi tqdm pandas
    python Weekly_Theme_Updater_v03.py
    python Weekly_Theme_Updater_v03.py --input my_file.csv --output out.csv
    python Weekly_Theme_Updater_v03.py --workers 4
    python Weekly_Theme_Updater_v03.py --no-cache        # ignore cap cache
    python Weekly_Theme_Updater_v03.py --no-batch        # skip /v7 batch, use v02 path
    python Weekly_Theme_Updater_v03.py --chunk 100       # symbols per batch request
"""

import argparse
import json
import random
import sys
import time
import warnings
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

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

# YfData carries Yahoo's cookie+crumb handshake; we reuse it for the batched
# /v7/finance/quote endpoint. If unavailable (older/newer yfinance), v03 simply
# skips the batch path and behaves like v02.
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

HISTORY_PERIOD = "4mo"

OFFSETS = {
    "1W Price Change %":  5,
    "1M Price Change %": 21,
    "3M Price Change %": 63,
}

# 4 threads (not 10) is far gentler on Yahoo's quote endpoint and still fast.
DEFAULT_WORKERS = 4
BATCH_PAUSE     = 1.0     # pause between market-cap batches (seconds)
MAX_RETRIES     = 4       # per-ticker retry attempts on rate-limit
RETRY_BASE      = 2.0     # exponential backoff base (seconds)

# Batched /v7/finance/quote settings
QUOTE_URL          = "https://query2.finance.yahoo.com/v7/finance/quote"
DEFAULT_CHUNK      = 100   # symbols per batched request (Yahoo tolerates ~100)
QUOTE_CHUNK_PAUSE  = 0.4   # polite pause between chunk requests (seconds)
QUOTE_MAX_RETRIES  = 3     # retries per chunk on failure/throttle


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


def market_cap_in_millions(value) -> float | None:
    if value is None or (isinstance(value, float) and value != value):   # NaN
        return None
    try:
        return round(float(value) / 1e6, 4)
    except (TypeError, ValueError):
        return None


def pct_change(series: pd.Series, n_days: int) -> float | None:
    valid = series.dropna()
    if len(valid) < n_days + 1:
        return None
    past    = valid.iloc[-(n_days + 1)]
    current = valid.iloc[-1]
    if past == 0:
        return None
    return round((current - past) / past, 4)


# ──────────────────────────────────────────────────────────────────────────────
# BATCHED market-cap fetch — /v7/finance/quote (v03 primary path)
# ──────────────────────────────────────────────────────────────────────────────

def _chunks(seq: list, size: int):
    for i in range(0, len(seq), size):
        yield seq[i : i + size]


def fetch_caps_batched(tickers: list[str], session, chunk_size: int) -> dict[str, float]:
    """
    Fetch market caps for many tickers using Yahoo's /v7/finance/quote endpoint,
    ~`chunk_size` symbols per request. Returns {original_ticker: cap_in_millions}
    for whatever the batch resolved. Symbols the batch omits are simply absent
    from the returned dict (the caller falls back for those).

    Reuses yfinance's YfData so the cookie+crumb handshake is handled for us.
    Never manually adds 'crumb' to params — YfData injects it.
    """
    if YfData is None:
        print("    ⚠️  yfinance.data.YfData unavailable — skipping batch path.")
        return {}

    try:
        yfd = YfData(session=session)
    except Exception as e:
        print(f"    ⚠️  Could not init YfData ({e}) — skipping batch path.")
        return {}

    # Map Yahoo symbols back to the caller's original symbols.
    y2orig = {to_yahoo_symbol(t): t for t in tickers}
    ysyms  = list(y2orig.keys())

    out: dict[str, float] = {}
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
                    ysym = q.get("symbol")
                    cap  = q.get("marketCap")
                    orig = y2orig.get(ysym)
                    cap_m = market_cap_in_millions(cap)
                    if orig is not None and cap_m is not None:
                        out[orig] = cap_m
                break  # chunk succeeded (even if some symbols had no cap)
            except YFRateLimitError:
                time.sleep(RETRY_BASE * (2 ** attempt) + random.uniform(0, 1.0))
            except Exception:
                # crumb hiccup / transient network — brief backoff then retry
                time.sleep(1.0 * (attempt + 1) + random.uniform(0, 0.5))
        time.sleep(QUOTE_CHUNK_PAUSE)

    print(f"    ✔️  Batch resolved {len(out)}/{len(tickers)} caps.")
    return out


# ──────────────────────────────────────────────────────────────────────────────
# Robust per-ticker market-cap fetch (v02 fallback path)
# ──────────────────────────────────────────────────────────────────────────────

def _raw_cap_from_ticker(tk: "yf.Ticker", last_close: float | None) -> float | None:
    """Fallback chain. Returns raw market cap (NOT millions) or None."""
    # 1) fast_info.marketCap — cheapest, usually correct
    try:
        cap = tk.fast_info.get("marketCap")
        if cap:
            return cap
    except YFRateLimitError:
        raise
    except Exception:
        pass

    # 2) shares × last close — reuses price already downloaded in bulk;
    #    needs only 'shares' from the (throttle-prone) quote, but survives
    #    when marketCap itself is momentarily absent.
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

    # 3) .info['marketCap'] — different (quoteSummary) endpoint, second chance
    try:
        cap = tk.info.get("marketCap")
        if cap:
            return cap
    except YFRateLimitError:
        raise
    except Exception:
        pass

    return None


def fetch_one_cap(orig_ticker: str, session, last_close: float | None):
    """
    Fetch cap for one original-symbol ticker with retry/backoff.
    Returns (orig_ticker, cap_in_millions_or_None, status)
    status ∈ {'ok', 'missing', 'rate_limited'}
    """
    ysym = to_yahoo_symbol(orig_ticker)
    for attempt in range(MAX_RETRIES):
        try:
            tk = yf.Ticker(ysym, session=session) if session else yf.Ticker(ysym)
            raw = _raw_cap_from_ticker(tk, last_close)
            cap_m = market_cap_in_millions(raw)
            return orig_ticker, cap_m, ("ok" if cap_m is not None else "missing")
        except YFRateLimitError:
            # exponential backoff with jitter, then retry this ticker
            time.sleep(RETRY_BASE * (2 ** attempt) + random.uniform(0, 1.0))
        except Exception:
            return orig_ticker, None, "missing"
    return orig_ticker, None, "rate_limited"


def fetch_market_caps(tickers: list[str], workers: int,
                      last_close: dict[str, float] | None = None) -> pd.Series:
    """Fetch market cap (millions) for every ticker. Series indexed by ORIGINAL ticker."""
    last_close = last_close or {}
    print(f"\n💰  Fetching market caps for {len(tickers)} tickers ({workers} threads) …")

    session = make_session()
    if session is None:
        print("    ⚠️  curl_cffi unavailable — falling back to default session "
              "(more likely to be rate-limited). `pip install curl_cffi` recommended.")

    caps: dict[str, float | None] = {}
    rate_limited: list[str] = []
    batch_size = max(workers * 4, 8)

    with tqdm(total=len(tickers), unit="ticker") as pbar:
        for i in range(0, len(tickers), batch_size):
            batch = tickers[i : i + batch_size]
            with ThreadPoolExecutor(max_workers=workers) as pool:
                futures = {
                    pool.submit(fetch_one_cap, t, session, last_close.get(t)): t
                    for t in batch
                }
                for fut in as_completed(futures):
                    tkr, cap_m, status = fut.result()
                    caps[tkr] = cap_m
                    if status == "rate_limited":
                        rate_limited.append(tkr)
                    pbar.update(1)
            if i + batch_size < len(tickers):
                time.sleep(BATCH_PAUSE)

    # ── Sequential straggler sweep: retry rate-limited names slowly ──────────
    if rate_limited:
        print(f"\n🔁  Re-trying {len(rate_limited)} rate-limited tickers "
              f"sequentially (slower, higher success) …")
        for tkr in tqdm(rate_limited, unit="ticker"):
            _, cap_m, _ = fetch_one_cap(tkr, session, last_close.get(tkr))
            if cap_m is not None:
                caps[tkr] = cap_m
            time.sleep(1.0 + random.uniform(0, 0.5))

    return pd.Series(caps, name="Market Cap")


# ──────────────────────────────────────────────────────────────────────────────
# Price changes (unchanged from v01 — this path works)
# ──────────────────────────────────────────────────────────────────────────────

def fetch_price_changes(tickers: list[str]):
    """
    Bulk-download adjusted close, compute 1W/1M/3M changes.
    Returns (price_df indexed by original ticker, last_close dict).
    """
    ysyms = [to_yahoo_symbol(t) for t in tickers]
    y2orig = dict(zip(ysyms, tickers))

    print(f"\n📥  Downloading {HISTORY_PERIOD} of price history for "
          f"{len(ysyms)} tickers …")

    raw = yf.download(ysyms, period=HISTORY_PERIOD, auto_adjust=True,
                      progress=True, threads=True)

    if isinstance(raw.columns, pd.MultiIndex):
        close = raw["Close"]
    else:
        close = raw[["Close"]].rename(columns={"Close": ysyms[0]})

    results, last_close = [], {}
    for ysym in ysyms:
        orig = y2orig[ysym]
        row = {"Ticker": orig}
        if ysym not in close.columns:
            for col in OFFSETS:
                row[col] = None
        else:
            s = close[ysym]
            for col, n in OFFSETS.items():
                row[col] = pct_change(s, n)
            valid = s.dropna()
            if len(valid):
                last_close[orig] = float(valid.iloc[-1])
        results.append(row)

    return pd.DataFrame(results).set_index("Ticker"), last_close


# ──────────────────────────────────────────────────────────────────────────────
# Sub-market-cap allocation (unchanged)
# ──────────────────────────────────────────────────────────────────────────────

def allocate_sub_market_cap(df: pd.DataFrame) -> pd.Series:
    if "Assignment" not in df.columns:
        raise ValueError("Column 'Assignment' is required for Sub Market Cap allocation.")
    counts = df.groupby("Ticker")["Ticker"].transform("size")
    mc = df["Market Cap"]
    assignment = df["Assignment"].astype(str).str.strip().str.title()
    sub = mc.copy()
    multi = counts >= 2
    sub = sub.mask(multi & (assignment == "Primary"),   mc * 0.60)
    sub = sub.mask(multi & (assignment == "Secondary"), mc * 0.40)
    return sub.round(4)


# ──────────────────────────────────────────────────────────────────────────────
# Cache
# ──────────────────────────────────────────────────────────────────────────────

def load_cache(path: Path) -> dict:
    if path.exists():
        try:
            return json.loads(path.read_text())
        except Exception:
            return {}
    return {}


def save_cache(path: Path, caps: pd.Series):
    try:
        data = {k: v for k, v in caps.items() if v is not None}
        path.write_text(json.dumps(data))
    except Exception:
        pass


# ──────────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Update market data (v03, batched caps)")
    parser.add_argument("--input",   default=DEFAULT_INPUT)
    parser.add_argument("--output",  default=DEFAULT_OUTPUT)
    parser.add_argument("--workers", type=int, default=DEFAULT_WORKERS)
    parser.add_argument("--chunk",   type=int, default=DEFAULT_CHUNK,
                        help="Symbols per batched /v7/quote request (default 100).")
    parser.add_argument("--no-batch", action="store_true",
                        help="Skip the batched /v7/quote path; use the v02 per-ticker path only.")
    parser.add_argument("--no-cache", action="store_true",
                        help="Ignore the market-cap cache and refetch everything.")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        sys.exit(f"❌  Input file not found: {input_path}")

    print(f"📂  Reading {input_path} …")
    df = pd.read_csv(input_path)
    for col in ("Ticker", "Assignment"):
        if col not in df.columns:
            sys.exit(f"❌  Column '{col}' not found in the input CSV.")

    tickers = df["Ticker"].dropna().unique().tolist()
    print(f"    {len(df):,} rows · {len(tickers):,} unique tickers")

    # 1. Price changes (also gives us last_close for the cap fallback)
    price_df, last_close = fetch_price_changes(tickers)

    # 2. Market caps — cache → batched /v7/quote → per-ticker fallback
    cache_path = Path(args.output).with_suffix(".capcache.json")
    cached = {} if args.no_cache else load_cache(cache_path)
    to_fetch = [t for t in tickers if t not in cached]
    print(f"    cache: {len(cached)} cached · {len(to_fetch)} to fetch")

    resolved: dict[str, float] = {}

    # 2a. Batched primary path (~14 requests for ~1,400 tickers)
    if to_fetch and not args.no_batch:
        session = make_session()
        resolved.update(fetch_caps_batched(to_fetch, session, args.chunk))

    # 2b. Per-ticker fallback ONLY for whatever the batch didn't resolve
    still_missing = [t for t in to_fetch if t not in resolved]
    if still_missing:
        print(f"\n↩️  {len(still_missing)} tickers unresolved by batch — "
              f"using per-ticker fallback …")
        fb = fetch_market_caps(still_missing, args.workers, last_close)
        for t, v in fb.items():
            if v is not None:
                resolved[t] = v

    fetched = pd.Series(resolved, name="Market Cap")
    cap_series = pd.concat([pd.Series(cached, name="Market Cap"), fetched])
    cap_series = cap_series[~cap_series.index.duplicated(keep="last")]
    if not args.no_cache:
        save_cache(cache_path, cap_series)

    # 3. Merge
    print("\n🔗  Merging results into original data …")
    target_cols = ["Market Cap", "Sub Market Cap"] + list(OFFSETS.keys())
    df.drop(columns=[c for c in target_cols if c in df.columns],
            inplace=True, errors="ignore")

    df["Market Cap"] = df["Ticker"].map(cap_series)
    for col in OFFSETS:
        df[col] = df["Ticker"].map(price_df[col])

    # 4. Sub market cap
    df["Sub Market Cap"] = allocate_sub_market_cap(df)

    numeric_cols = ["Market Cap", "Sub Market Cap"] + list(OFFSETS.keys())
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # 5. Save
    output_path = Path(args.output)
    df.to_csv(output_path, index=False)
    print(f"\n✅  Saved {len(df):,} rows → {output_path}")

    # 6. Coverage summary
    tcap = df.groupby("Ticker")["Market Cap"].first()
    missing_caps = tcap[tcap.isna()].index.tolist()
    print("\n📊  Coverage summary:")
    print(f"    Market Cap        — {len(tickers) - len(missing_caps)}/{len(tickers)} tickers populated")
    print(f"    Sub Market Cap    — {len(df) - df['Sub Market Cap'].isna().sum()}/{len(df)} rows populated")
    print(f"    1W Price Change % — {len(tickers) - df.groupby('Ticker')['1W Price Change %'].first().isna().sum()}/{len(tickers)} tickers")
    print(f"    3M Price Change % — {len(tickers) - df.groupby('Ticker')['3M Price Change %'].first().isna().sum()}/{len(tickers)} tickers")
    if missing_caps:
        print(f"\n    ⚠️  {len(missing_caps)} tickers still without a cap "
              f"(likely delisted / non-US / genuinely unavailable):")
        print(f"       {', '.join(missing_caps[:40])}"
              + (" …" if len(missing_caps) > 40 else ""))
        print("       Re-running will retry ONLY these (cache keeps the rest).")


if __name__ == "__main__":
    main()
