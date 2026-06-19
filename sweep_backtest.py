# sweep_backtest.py  (v2 — ATR-capped stops)
"""
Backtest the 4H Liquidity Sweep strategy.
Usage: python sweep_backtest.py --start 2024-06-01 --end 2026-04-01 --equity 5000
"""
import argparse, json, warnings
import pandas as pd
import numpy as np
import yfinance as yf
warnings.filterwarnings("ignore")

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from sweep_strategy import (
    build_4h_from_1h, get_4h_range, calc_atr,
    find_swing_high, find_swing_low,
    check_flip_confirmation, size_position,
    _calc_sl, _calc_tp
)
from sweep_config import (
    UNIVERSE, SLIPPAGE, VOL_WINDOW, SWING_LOOKBACK
)


def download_data(symbols, start, end):
    data = {}
    print(f"Downloading 1H data for {len(symbols)} symbols...")
    for sym in symbols:
        df = yf.download(sym, start=start, end=end, interval="1h",
                         auto_adjust=True, progress=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df.index = pd.to_datetime(df.index, utc=True)
        data[sym] = df
        print(f"  ✓ {sym}: {len(df)} bars")
    return data


def run_backtest(symbol, df_1h, equity):
    df_4h     = build_4h_from_1h(df_1h)
    df        = df_1h.copy()
    df["atr"] = calc_atr(df)
    trades    = []
    cur_eq    = equity
    position  = None
    retest    = None
    pending_entry = None
    min_idx   = VOL_WINDOW + SWING_LOOKBACK + 5

    for i in range(min_idx, len(df)):
        bar      = df.iloc[i]
        prev_bar = df.iloc[i - 1]
        ts       = df.index[i]
        price    = float(bar["Close"])
        atr      = float(bar["atr"])
        if np.isnan(atr):
            continue

        h4_high, h4_low = get_4h_range(df_4h, ts)
        if h4_high is None:
            continue

        history = df.iloc[max(0, i - 40):i]

        # Execute pending sweep entry at this bar's open (fixes lookahead bias)
        if pending_entry is not None and position is None:
            side   = pending_entry["side"]
            entry  = float(bar["Open"]) * (1 - SLIPPAGE if side == "short" else 1 + SLIPPAGE)
            ph4_h  = pending_entry["h4_high"]
            ph4_l  = pending_entry["h4_low"]
            sl     = _calc_sl(side, entry, history, atr)
            tp     = _calc_tp(side, entry, sl, ph4_h, ph4_l)
            qty, _ = size_position(cur_eq, entry, sl)
            position = dict(side=side, entry=entry, qty=qty, sl=sl, tp=tp,
                            ts=ts, h4_high=ph4_h, h4_low=ph4_l)
            pending_entry = None

        # ── retest management ────────────────────────────────────────────────
        if retest is not None:
            level, side = retest["level"], retest["side"]
            touched = bar["Low"] <= level <= bar["High"]
            failed  = (price < level * 0.995) if side == "long" else (price > level * 1.005)

            if touched and position is None:
                entry  = price * (1 + SLIPPAGE if side == "long" else 1 - SLIPPAGE)
                sl     = _calc_sl(side, entry, history, atr)
                tp     = _calc_tp(side, entry, sl, h4_high, h4_low)
                qty, _ = size_position(cur_eq, entry, sl)
                position = dict(side=side, entry=entry, qty=qty, sl=sl, tp=tp,
                                ts=ts, h4_high=h4_high, h4_low=h4_low)
                retest = None
                continue

            if failed:
                retest = None
            continue

        # ── manage open position ─────────────────────────────────────────────
        if position is not None:
            side = position["side"]
            if side == "short":
                hit_sl  = bar["High"] >= position["sl"]
                hit_tp  = bar["Low"]  <= position["tp"]
                rebuild = bar["Close"] > h4_high and prev_bar["Close"] > h4_high
            else:
                hit_sl  = bar["Low"]  <= position["sl"]
                hit_tp  = bar["High"] >= position["tp"]
                rebuild = bar["Close"] < h4_low and prev_bar["Close"] < h4_low

            if hit_sl or hit_tp or rebuild:
                exit_px = position["sl"] if hit_sl else (position["tp"] if hit_tp else price)
                pnl = (exit_px - position["entry"]) * position["qty"] if side == "long" \
                    else (position["entry"] - exit_px) * position["qty"]
                cur_eq += pnl
                reason  = "stop" if hit_sl else ("target" if hit_tp else "rebuild_exit")
                trades.append(dict(
                    symbol=symbol, side=side,
                    entry=position["entry"], exit=exit_px,
                    qty=position["qty"], pnl=round(pnl, 2),
                    reason=reason,
                    entry_time=position["ts"], exit_time=ts
                ))
                flip_side = "long" if side == "short" else "short"
                position  = None

                if rebuild:
                    flip_dir = "up" if flip_side == "long" else "down"
                    conf     = check_flip_confirmation(history, flip_dir)
                    if conf == "strong":
                        entry  = price * (1 + SLIPPAGE if flip_side == "long" else 1 - SLIPPAGE)
                        sl     = _calc_sl(flip_side, entry, history, atr)
                        tp     = _calc_tp(flip_side, entry, sl, h4_high, h4_low)
                        qty, _ = size_position(cur_eq, entry, sl)
                        position = dict(side=flip_side, entry=entry, qty=qty, sl=sl, tp=tp,
                                        ts=ts, h4_high=h4_high, h4_low=h4_low)
                    elif conf == "weak":
                        retest = dict(
                            side=flip_side,
                            level=h4_high if flip_side == "long" else h4_low
                        )
            continue

        # ── new sweep entry ──────────────────────────────────────────────────
        prev_close = float(prev_bar["Close"])
        swept_high = prev_close > h4_high and price <= h4_high
        swept_low  = prev_close < h4_low  and price >= h4_low
        if not swept_high and not swept_low:
            continue

        from sweep_config import USE_TREND_FILTER, TREND_EMA_PERIOD
        if USE_TREND_FILTER:
            from sweep_strategy import calc_ema
            ema       = float(calc_ema(history, TREND_EMA_PERIOD).iloc[-1])
            above_ema = price > ema
            if swept_high and above_ema:
                continue
            if swept_low and not above_ema:
                continue

        pending_entry = {
            "side":    "short" if swept_high else "long",
            "h4_high": h4_high,
            "h4_low":  h4_low,
        }

    return trades, cur_eq


def print_results(all_trades, start_equity, months, verbose_trades=True):
    df = pd.DataFrame(all_trades)
    if df.empty:
        print("No trades generated.")
        return

    # ── Print every trade ────────────────────────────────────────────────────
    if verbose_trades:
        print("=" * 75)
        print("TRADE LOG")
        print("=" * 75)
        print(f"  {'#':>4}  {'Sym':<5} {'Side':<6} {'Entry':>8} {'Exit':>8} "
              f"{'Qty':>4}  {'P&L':>8}  {'Reason':<22} {'Entry Time'}")
        print("-" * 75)
        for i, row in df.iterrows():
            pnl_str = f"${row['pnl']:+.2f}"
            marker  = "✓" if row["pnl"] > 0 else "✗"
            print(f"  {i+1:>4}  {row['symbol']:<5} {row['side']:<6} "
                  f"{row['entry']:>8.2f} {row['exit']:>8.2f} "
                  f"{int(row['qty']):>4}  {pnl_str:>8}  "
                  f"{row['reason']:<22} {str(row['entry_time'])[:16]}  {marker}")
        print("=" * 75)
        print()

    df["pnl"] = df["pnl"].astype(float)
    total_pnl  = df["pnl"].sum()
    final_eq   = start_equity + total_pnl
    wins       = df[df["pnl"] > 0]
    losses     = df[df["pnl"] <= 0]
    win_rate   = len(wins) / len(df) * 100
    pf         = wins["pnl"].sum() / abs(losses["pnl"].sum()) if len(losses) else 0
    ret_pct    = total_pnl / start_equity * 100
    monthly    = ret_pct / months

    eq_curve = [start_equity]
    for p in df["pnl"]:
        eq_curve.append(eq_curve[-1] + p)
    peak = start_equity
    max_dd = 0
    for e in eq_curve:
        peak   = max(peak, e)
        max_dd = min(max_dd, (e - peak) / peak * 100)

    print("=" * 60)
    print("4H SWEEP BACKTEST RESULTS")
    print("=" * 60)
    print(f"Total trades:   {len(df)}")
    print(f"Win rate:       {win_rate:.1f}%")
    print(f"Avg win:        ${wins['pnl'].mean():.2f}")
    print(f"Avg loss:       ${losses['pnl'].mean():.2f}")
    print(f"Profit factor:  {pf:.2f}")
    print(f"Total P&L:      ${total_pnl:.2f}")
    print(f"Final equity:   ${final_eq:.2f}")
    print(f"Return:         {ret_pct:+.1f}%")
    print(f"Monthly return: {monthly:+.2f}%")
    print(f"Max drawdown:   {max_dd:.1f}%")
    print()
    print("Exit breakdown:")
    for reason, grp in df.groupby("reason"):
        wr = (grp["pnl"] > 0).mean() * 100
        print(f"  {reason:22s}: {len(grp):3d} | WR:{wr:5.1f}% | P&L:${grp['pnl'].sum():8.2f}")
    print()
    print("Per-symbol breakdown:")
    for sym, grp in df.groupby("symbol"):
        wr = (grp["pnl"] > 0).mean() * 100
        print(f"  {sym:6s}: {len(grp):3d} trades | WR:{wr:5.1f}% | P&L:${grp['pnl'].sum():8.2f}")

    df.to_csv("sweep_backtest_trades.csv", index=False)
    pd.DataFrame({"equity": eq_curve}).to_csv("sweep_backtest_equity.csv", index=False)
    with open("sweep_backtest_summary.json", "w") as f:
        json.dump(dict(
            total_trades=len(df), win_rate=round(win_rate, 2),
            profit_factor=round(pf, 2), total_pnl=round(total_pnl, 2),
            final_equity=round(final_eq, 2),
            monthly_return=round(monthly, 2),
            max_drawdown=round(max_dd, 2)
        ), f, indent=2)
    print("\nSaved: sweep_backtest_trades.csv, sweep_backtest_equity.csv, sweep_backtest_summary.json")


if __name__ == "__main__":
    from dateutil.relativedelta import relativedelta
    from datetime import datetime

    parser = argparse.ArgumentParser(description="4H Sweep Backtest v2")
    parser.add_argument("--start",  default="2024-06-01")
    parser.add_argument("--end",    default="2026-04-01")
    parser.add_argument("--equity", type=float, default=5000)
    args = parser.parse_args()

    d1     = datetime.strptime(args.start, "%Y-%m-%d")
    d2     = datetime.strptime(args.end,   "%Y-%m-%d")
    rd     = relativedelta(d2, d1)
    months = rd.months + rd.years * 12

    data   = download_data(UNIVERSE, args.start, args.end)

    print(f"\n=== Starting Backtest ===")
    print(f"Equity: ${args.equity:.2f} | Symbols: {UNIVERSE}\n")

    all_trades = []
    eq_per_sym = args.equity / len(UNIVERSE)
    for sym in UNIVERSE:
        trades, _ = run_backtest(sym, data[sym], eq_per_sym)
        all_trades.extend(trades)

    print_results(all_trades, args.equity, months)