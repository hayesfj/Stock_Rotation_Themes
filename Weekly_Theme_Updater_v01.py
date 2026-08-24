"""
update_market_data.py
─────────────────────
Reads finviz_theme_subtheme_tickers_normalized.csv, fetches fresh market data
from Yahoo Finance for every unique ticker, and writes an updated CSV with:

  • Market Cap          — most-recent market capitalisation in millions (float)
  • Sub Market Cap      — allocated market capitalisation in millions (float):
                            100 % for tickers that appear under only one Sub Theme;
                            60 % of Market Cap when Assignment == "Primary";
                            40 % of Market Cap when Assignment == "Secondary"
  • 1W Price Change %   — adjusted-close fractional change over the last 5
                          trading days (float, 4 decimal places; e.g. 0.0123)
  • 1M Price Change %   — same for 21 trading days
  • 3M Price Change %   — same for 63 trading days

Primary / Secondary assignment
------------------------------
Uses the explicit "Assignment" column from the input CSV.
  - "Primary"   → Sub Market Cap = 0.60 × Market Cap
  - "Secondary" → Sub Market Cap = 0.40 × Market Cap
  - Single-row tickers (no Secondary) receive the full Market Cap.

Price-change convention
-----------------------
Values are stored as decimal fractions, not percent:
  a +1.234 % move is written as 0.0123.

Usage
-----
    pip install yfinance tqdm pandas
    python update_market_data.py                         # uses default paths
    python update_market_data.py --input my_file.csv     # custom input
    python update_market_data.py --output results.csv    # custom output
    python update_market_data.py --workers 10            # more parallel threads

Requirements
------------
    yfinance >= 0.2
    pandas
    tqdm
"""

import argparse
import sys
import time
import warnings
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import pandas as pd
import yfinance as yf
from tqdm import tqdm

warnings.filterwarnings("ignore", category=FutureWarning)

# ──────────────────────────────────────────────────────────────────────────────git 
# Configuration
# ──────────────────────────────────────────────────────────────────────────────

DEFAULT_INPUT  = r"G:\My Drive\Projects\Python\Stocks & Options\Themes\Input_Ticker_List_by_Theme.csv"
DEFAULT_OUTPUT = r"G:\My Drive\Projects\Python\Stocks & Options\Themes\Tickers_Themes_SubThemes.csv"

# Lookback window: must cover 3 months + a buffer for weekends / holidays
HISTORY_PERIOD = "4mo"

# Trading-day offsets (approximate)
OFFSETS = {
    "1W Price Change %":  5,
    "1M Price Change %": 21,
    "3M Price Change %": 63,
}

# Thread count for market-cap fetches (keep ≤ 20 to avoid rate-limits)
DEFAULT_WORKERS = 10

# Pause between market-cap batches (seconds)
BATCH_PAUSE = 1.0


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def market_cap_in_millions(value: float | None) -> float | None:
    """Convert raw market-cap number to millions (float).  Returns None on missing/NaN."""
    if value is None or (isinstance(value, float) and value != value):  # NaN
        return None
    return round(value / 1e6, 4)


def pct_change(series: pd.Series, n_days: int) -> float | None:
    """
    Return the fractional change between the value n_days ago and the last
    available value, rounded to 4 decimal places.
    Example: a +1.234 % move → 0.0123.
    Returns None when there is insufficient history.
    """
    valid = series.dropna()
    if len(valid) < n_days + 1:
        return None
    past    = valid.iloc[-(n_days + 1)]
    current = valid.iloc[-1]
    if past == 0:
        return None
    return round((current - past) / past, 4)


def fetch_market_cap(ticker: str) -> tuple[str, float | None]:
    """Fetch market cap for a single ticker; return (ticker, value_in_millions)."""
    try:
        cap = yf.Ticker(ticker).fast_info.market_cap
        return ticker, market_cap_in_millions(cap)
    except Exception:
        return ticker, None


def allocate_sub_market_cap(df: pd.DataFrame) -> pd.Series:
    """
    Allocate Market Cap to Sub Market Cap using the Assignment column.

    Rules
    -----
    - Assignment == "Primary"   → 0.60 × Market Cap
    - Assignment == "Secondary" → 0.40 × Market Cap
    - Tickers that appear only once (no Secondary row) → full Market Cap
      (even if the single row is labelled Primary).

    Returns a Series aligned with df.index.
    """
    if "Assignment" not in df.columns:
        raise ValueError("Column 'Assignment' is required for Sub Market Cap allocation.")

    # How many rows does this ticker have?
    counts = df.groupby("Ticker")["Ticker"].transform("size")

    mc = df["Market Cap"]
    assignment = df["Assignment"].str.strip().str.title()

    # Start with full market cap (covers single-row tickers)
    sub = mc.copy()

    # Multi-row tickers: apply 60/40 split
    multi = counts >= 2
    sub = sub.mask(multi & (assignment == "Primary"),   mc * 0.60)
    sub = sub.mask(multi & (assignment == "Secondary"), mc * 0.40)

    return sub.round(4)


# ──────────────────────────────────────────────────────────────────────────────
# Core logic
# ──────────────────────────────────────────────────────────────────────────────

def fetch_price_changes(tickers: list[str]) -> pd.DataFrame:
    """
    Download adjusted-close history for all tickers in one batch call and
    compute 1W, 1M, 3M fractional changes.

    Returns a DataFrame indexed by ticker with columns:
        '1W Price Change %', '1M Price Change %', '3M Price Change %'
    """
    print(f"\n📥  Downloading {HISTORY_PERIOD} of price history for "
          f"{len(tickers)} tickers …")

    raw = yf.download(
        tickers,
        period=HISTORY_PERIOD,
        auto_adjust=True,
        progress=True,
        threads=True,
    )

    # yfinance returns a MultiIndex when multiple tickers are requested
    if isinstance(raw.columns, pd.MultiIndex):
        close = raw["Close"]           # shape: (days × tickers)
    else:
        # Single-ticker edge case: raw is already a simple DataFrame
        close = raw[["Close"]].rename(columns={"Close": tickers[0]})

    results = []
    for ticker in tickers:
        row = {"Ticker": ticker}
        if ticker not in close.columns:
            for col in OFFSETS:
                row[col] = None
        else:
            s = close[ticker]
            for col, n in OFFSETS.items():
                row[col] = pct_change(s, n)
        results.append(row)

    return pd.DataFrame(results).set_index("Ticker")


def fetch_market_caps(tickers: list[str], workers: int) -> pd.Series:
    """
    Fetch market cap (in millions) for every ticker using a thread pool.
    Returns a Series indexed by ticker (float or None).
    """
    print(f"\n💰  Fetching market caps for {len(tickers)} tickers "
          f"({workers} threads) …")

    caps: dict[str, float | None] = {}
    batch_size = workers * 5           # process in reasonably-sized groups

    with tqdm(total=len(tickers), unit="ticker") as pbar:
        for i in range(0, len(tickers), batch_size):
            batch = tickers[i : i + batch_size]
            with ThreadPoolExecutor(max_workers=workers) as pool:
                futures = {pool.submit(fetch_market_cap, t): t for t in batch}
                for future in as_completed(futures):
                    tkr, cap_m = future.result()
                    caps[tkr] = cap_m
                    pbar.update(1)
            # Brief pause between batches to be polite to Yahoo's servers
            if i + batch_size < len(tickers):
                time.sleep(BATCH_PAUSE)

    return pd.Series(caps, name="Market Cap")


# ──────────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Update market data in finviz CSV")
    parser.add_argument("--input",   default=DEFAULT_INPUT,
                        help=f"Input CSV path  (default: {DEFAULT_INPUT})")
    parser.add_argument("--output",  default=DEFAULT_OUTPUT,
                        help=f"Output CSV path (default: {DEFAULT_OUTPUT})")
    parser.add_argument("--workers", type=int, default=DEFAULT_WORKERS,
                        help=f"Parallel threads for market-cap fetch "
                             f"(default: {DEFAULT_WORKERS})")
    args = parser.parse_args()

    # ── 1. Read input ─────────────────────────────────────────────────────────
    input_path = Path(args.input)
    if not input_path.exists():
        sys.exit(f"❌  Input file not found: {input_path}")

    print(f"📂  Reading {input_path} …")
    df = pd.read_csv(input_path)

    if "Ticker" not in df.columns:
        sys.exit("❌  Column 'Ticker' not found in the input CSV.")
    if "Assignment" not in df.columns:
        sys.exit("❌  Column 'Assignment' not found in the input CSV.")

    tickers = df["Ticker"].dropna().unique().tolist()
    print(f"    {len(df):,} rows · {len(tickers):,} unique tickers")

    # ── 2. Fetch price-change data ────────────────────────────────────────────
    price_df = fetch_price_changes(tickers)

    # ── 3. Fetch market caps (already in millions) ────────────────────────────
    cap_series = fetch_market_caps(tickers, args.workers)

    # ── 4. Merge into original DataFrame ─────────────────────────────────────
    print("\n🔗  Merging results into original data …")

    # Drop old versions of the target columns if they already exist
    target_cols = ["Market Cap", "Sub Market Cap"] + list(OFFSETS.keys())
    df.drop(columns=[c for c in target_cols if c in df.columns],
            inplace=True, errors="ignore")

    # Map market cap (float, millions)
    df["Market Cap"] = df["Ticker"].map(cap_series)

    # Map price changes (float, 4 d.p. fractional)
    for col in OFFSETS:
        df[col] = df["Ticker"].map(price_df[col])

    # ── 5. Allocate Sub Market Cap (60 % Primary / 40 % Secondary) ────────────
    df["Sub Market Cap"] = allocate_sub_market_cap(df)

    # Ensure consistent numeric dtypes (NaN stays NaN)
    numeric_cols = ["Market Cap", "Sub Market Cap"] + list(OFFSETS.keys())
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # ── 6. Save ───────────────────────────────────────────────────────────────
    output_path = Path(args.output)
    df.to_csv(output_path, index=False)
    print(f"\n✅  Saved {len(df):,} rows → {output_path}")

    # ── 7. Quick sanity summary ───────────────────────────────────────────────
    total_rows = len(df)
    total_tickers = len(tickers)
    missing_cap = df["Market Cap"].isna().sum()
    missing_sub = df["Sub Market Cap"].isna().sum()
    missing_1w  = df["1W Price Change %"].isna().sum()
    missing_3m  = df["3M Price Change %"].isna().sum()

    print("\n📊  Coverage summary:")
    print(f"    Market Cap          — {total_tickers - (df.groupby('Ticker')['Market Cap'].first().isna().sum())}/{total_tickers} tickers populated")
    print(f"    Sub Market Cap      — {total_rows - missing_sub}/{total_rows} rows populated")
    print(f"    1W Price Change %   — {total_tickers - (df.groupby('Ticker')['1W Price Change %'].first().isna().sum())}/{total_tickers} tickers populated")
    print(f"    3M Price Change %   — {total_tickers - (df.groupby('Ticker')['3M Price Change %'].first().isna().sum())}/{total_tickers} tickers populated")

    # Preview
    preview_cols = [c for c in ["Ticker", "Theme", "Sub Theme", "Assignment",
                                "Market Cap", "Sub Market Cap",
                                "1W Price Change %", "1M Price Change %",
                                "3M Price Change %"] if c in df.columns]
    print("\n🔍  Sample output (first 8 rows):")
    print(df[preview_cols].head(8).to_string(index=False))


if __name__ == "__main__":
    main()
