# sweep_data.py
import time
import pandas as pd
from datetime import datetime, timedelta, timezone
from alpaca.data.enums import DataFeed
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
from sweep_config import API_KEY, SECRET_KEY
from bot_logger import get_logger

log         = get_logger(__name__)
data_client = StockHistoricalDataClient(API_KEY, SECRET_KEY)

MAX_RETRIES = 3
RETRY_BASE_DELAY = 1.0


def _fetch_with_retry(symbols, timeframe, start, end):
    last_error = None
    for attempt in range(MAX_RETRIES):
        try:
            return _fetch(symbols, timeframe, start, end)
        except Exception as e:
            last_error = e
            if attempt < MAX_RETRIES - 1:
                delay = RETRY_BASE_DELAY * (2 ** attempt)
                log.warning(f"Fetch failed (attempt {attempt + 1}/{MAX_RETRIES}), retrying in {delay}s: {e}")
                time.sleep(delay)
    raise last_error


def _fetch(symbols, timeframe, start, end):
    req  = StockBarsRequest(
        symbol_or_symbols=symbols, timeframe=timeframe,
        start=start, end=end, feed=DataFeed.IEX,
    )
    bars = data_client.get_stock_bars(req)
    df   = bars.df.sort_index()
    df.columns = [c.capitalize() for c in df.columns]
    return df


def get_5min_bars(symbol: str, lookback_days: int = 5) -> pd.DataFrame:
    end   = datetime.now(timezone.utc)
    start = end - timedelta(days=lookback_days)
    df    = _fetch_with_retry(symbol, TimeFrame(5, TimeFrameUnit.Minute), start, end)
    if isinstance(df.index, pd.MultiIndex):
        df = df.xs(symbol, level="symbol")
    return df.sort_index()


def get_1h_bars(symbol: str, lookback_days: int = 10) -> pd.DataFrame:
    end   = datetime.now(timezone.utc)
    start = end - timedelta(days=lookback_days)
    df    = _fetch_with_retry(symbol, TimeFrame.Hour, start, end)
    if isinstance(df.index, pd.MultiIndex):
        df = df.xs(symbol, level="symbol")
    return df.sort_index()
