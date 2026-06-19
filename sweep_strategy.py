# sweep_strategy.py  (v2 — ATR-capped stops)
"""
4H Liquidity Sweep / Stop Hunt Reversal Strategy.

Key fix: stop-loss = min(swing point, entry ± 1.5×ATR14)
This prevents >2×ATR stops that caused the 25% win-rate problem.
"""
import pandas as pd
import numpy as np
from dataclasses import dataclass
from typing import Optional
from sweep_config import (
    MIN_RR, MAX_POSITION_RISK, EQUITY_RISK_PER_TRADE,
    SWING_LOOKBACK, VOL_WINDOW, FLIP_VOL_MULT,
    STOP_ATR_MULT
)


@dataclass
class Position:
    symbol:       str
    side:         str
    entry:        float
    qty:          int
    sl:           float
    tp:           float
    h4_high:      float
    h4_low:       float
    retest_mode:  bool = False
    retest_level: Optional[float] = None
    retest_dir:   Optional[str] = None


def calc_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    tr = pd.concat([
        df["High"] - df["Low"],
        (df["High"] - df["Close"].shift(1)).abs(),
        (df["Low"]  - df["Close"].shift(1)).abs(),
        ], axis=1).max(axis=1)
    return tr.rolling(period).mean()

def calc_ema(df: pd.DataFrame, period: int = 50) -> pd.Series:
    return df["Close"].ewm(span=period, adjust=False).mean()


def build_4h_from_1h(df_1h: pd.DataFrame) -> pd.DataFrame:
    df = df_1h.copy()
    df.index = pd.to_datetime(df.index, utc=True)
    return df.resample("4h").agg({
        "Open": "first", "High": "max",
        "Low": "min", "Close": "last", "Volume": "sum"
    }).dropna()


def get_4h_range(df_4h: pd.DataFrame, ts: pd.Timestamp):
    prev = df_4h[df_4h.index < ts]
    if prev.empty:
        return None, None
    last = prev.iloc[-1]
    return float(last["High"]), float(last["Low"])


def find_swing_high(df: pd.DataFrame, lookback: int = SWING_LOOKBACK) -> float:
    highs = df["High"].values[-lookback:]
    for i in range(len(highs) - 2, 0, -1):
        if highs[i] > highs[i - 1] and highs[i] > highs[i + 1]:
            return float(highs[i])
    return float(df["High"].iloc[-lookback:].max())


def find_swing_low(df: pd.DataFrame, lookback: int = SWING_LOOKBACK) -> float:
    lows = df["Low"].values[-lookback:]
    for i in range(len(lows) - 2, 0, -1):
        if lows[i] < lows[i - 1] and lows[i] < lows[i + 1]:
            return float(lows[i])
    return float(df["Low"].iloc[-lookback:].min())


def _calc_sl(side: str, entry: float, history: pd.DataFrame, atr: float) -> float:
    atr_stop = atr * STOP_ATR_MULT
    if side == "short":
        swing  = find_swing_high(history)
        sl_atr = entry + atr_stop
        raw_sl = min(swing, sl_atr)
        return max(raw_sl, entry + 0.01)
    else:
        swing  = find_swing_low(history)
        sl_atr = entry - atr_stop
        raw_sl = max(swing, sl_atr)
        return min(raw_sl, entry - 0.01)


def _calc_tp(side: str, entry: float, sl: float, h4_high: float, h4_low: float) -> float:
    risk = abs(entry - sl)
    if side == "short":
        natural_tp = h4_low
        min_tp     = entry - MIN_RR * risk
        return min(natural_tp, min_tp)
    else:
        natural_tp = h4_high
        min_tp     = entry + MIN_RR * risk
        return max(natural_tp, min_tp)


def size_position(equity: float, entry: float, sl: float):
    sl_dist = abs(entry - sl)

    min_stop_dist = max(entry * 0.003, 0.25)   # at least 0.3% of price or $0.25
    max_stop_dist = entry * MAX_POSITION_RISK

    if sl_dist <= 0:
        sl_dist = min_stop_dist

    sl_dist = max(sl_dist, min_stop_dist)
    sl_dist = min(sl_dist, max_stop_dist)

    risk_amt = equity * EQUITY_RISK_PER_TRADE
    raw_qty = int(risk_amt / sl_dist)

    max_notional = equity * 1.0   # no leverage in backtest
    max_qty_by_notional = max(1, int(max_notional / entry))

    qty = max(1, min(raw_qty, max_qty_by_notional))
    return qty, sl_dist


def check_flip_confirmation(df: pd.DataFrame, direction: str) -> str:
    if len(df) < VOL_WINDOW + 3:
        return "none"
    recent  = df.iloc[-3:]
    last    = df.iloc[-1]
    avg_vol = df["Volume"].iloc[-(VOL_WINDOW + 3):-3].mean()

    cond1 = bool((recent["Close"].diff().dropna() > 0).all()) if direction == "up" \
        else bool((recent["Close"].diff().dropna() < 0).all())

    body  = abs(last["Close"] - last["Open"])
    rng   = last["High"] - last["Low"]
    cond2 = bool((body / rng) > 0.60) if rng > 0 else False
    cond3 = bool(last["Volume"] > FLIP_VOL_MULT * avg_vol)

    score = sum([cond1, cond2, cond3])
    if score == 3:
        return "strong"
    if score >= 2:
        return "weak"
    return "none"


def get_signal(df_5m, df_4h, equity, position, slippage=0.0005):
    if len(df_5m) < VOL_WINDOW + SWING_LOOKBACK + 5:
        return {"action": "hold", "reason": "insufficient_data"}

    bar      = df_5m.iloc[-1]
    prev_bar = df_5m.iloc[-2]
    price    = float(bar["Close"])
    ts       = df_5m.index[-1]
    atr      = float(calc_atr(df_5m).iloc[-1])

    h4_high, h4_low = get_4h_range(df_4h, ts)
    if h4_high is None:
        return {"action": "hold", "reason": "no_4h_range"}

    if position is not None:
        if position.retest_mode and position.retest_level and position.retest_dir:
            level   = position.retest_level
            side    = position.retest_dir
            touched = bar["Low"] <= level <= bar["High"]
            failed  = (price < level * 0.995) if side == "long" else (price > level * 1.005)

            if touched:
                entry = price * (1 + slippage if side == "long" else 1 - slippage)
                sl    = _calc_sl(side, entry, df_5m, atr)
                tp    = _calc_tp(side, entry, sl, h4_high, h4_low)
                qty, _ = size_position(equity, entry, sl)
                return {
                    "action": "retest_entry", "side": side, "price": entry,
                    "qty": qty, "sl": sl, "tp": tp,
                    "h4_high": h4_high, "h4_low": h4_low,
                    "reason": "retest_held"
                }

            if failed:
                return {
                    "action": "exit", "side": None, "price": price,
                    "qty": position.qty, "reason": "retest_failed"
                }

            return {"action": "hold", "reason": "retest_waiting"}

        side = position.side
        if side == "short":
            hit_sl  = bar["High"] >= position.sl
            hit_tp  = bar["Low"]  <= position.tp
            rebuild = bar["Close"] > h4_high and prev_bar["Close"] > h4_high
        else:
            hit_sl  = bar["Low"]  <= position.sl
            hit_tp  = bar["High"] >= position.tp
            rebuild = bar["Close"] < h4_low and prev_bar["Close"] < h4_low

        if hit_sl:
            return {"action": "exit", "side": None, "price": position.sl,
                    "qty": position.qty, "reason": "stop"}

        if hit_tp:
            return {"action": "exit", "side": None, "price": position.tp,
                    "qty": position.qty, "reason": "target"}

        if rebuild:
            flip_side = "long" if side == "short" else "short"
            flip_dir  = "up" if side == "short" else "down"
            conf      = check_flip_confirmation(df_5m, flip_dir)

            if conf == "strong":
                entry  = price * (1 + slippage if flip_side == "long" else 1 - slippage)
                sl     = _calc_sl(flip_side, entry, df_5m, atr)
                tp     = _calc_tp(flip_side, entry, sl, h4_high, h4_low)
                qty, _ = size_position(equity, entry, sl)
                return {
                    "action": "flip_strong", "side": flip_side, "price": entry,
                    "qty": qty, "sl": sl, "tp": tp,
                    "h4_high": h4_high, "h4_low": h4_low,
                    "reason": "trend_rebuild_strong_flip"
                }

            elif conf == "weak":
                retest_level = h4_high if flip_side == "long" else h4_low
                return {
                    "action": "flip_weak", "side": flip_side, "price": price,
                    "qty": 0, "retest_level": retest_level,
                    "reason": "trend_rebuild_weak_wait_retest"
                }

            else:
                return {
                    "action": "exit", "side": None, "price": price,
                    "qty": position.qty, "reason": "trend_rebuild_no_flip"
                }

        return {"action": "hold", "reason": "in_trade"}

    prev_close = float(prev_bar["Close"])
    swept_high = prev_close > h4_high and price <= h4_high
    swept_low  = prev_close < h4_low and price >= h4_low

    if not swept_high and not swept_low:
        return {"action": "hold", "reason": "no_sweep"}

    from sweep_config import USE_TREND_FILTER, TREND_EMA_PERIOD
    if USE_TREND_FILTER:
        ema = float(calc_ema(df_5m, TREND_EMA_PERIOD).iloc[-1])
        above_ema = price > ema
        if swept_high and above_ema:
            return {"action": "hold", "reason": "trend_filter_blocked_short"}
        if swept_low and not above_ema:
            return {"action": "hold", "reason": "trend_filter_blocked_long"}

    side  = "short" if swept_high else "long"
    entry = price * (1 - slippage if side == "short" else 1 + slippage)
    sl    = _calc_sl(side, entry, df_5m, atr)
    tp    = _calc_tp(side, entry, sl, h4_high, h4_low)
    qty, _ = size_position(equity, entry, sl)

    return {
        "action": "entry", "side": side, "price": entry, "qty": qty,
        "sl": sl, "tp": tp,
        "h4_high": h4_high, "h4_low": h4_low,
        "reason": "sweep_reentry"
    }