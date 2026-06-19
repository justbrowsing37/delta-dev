# sweep_runner.py
import pandas as pd
from sweep_strategy import (
    build_4h_from_1h, calc_atr, get_4h_range,
    find_swing_high, find_swing_low,
    check_flip_confirmation, size_position,
    _calc_sl, _calc_tp, Position
)
from sweep_config import (
    SLIPPAGE, VOL_WINDOW, SWING_LOOKBACK
)


class TradeTracker:
    def __init__(self, equity: float):
        self.equity = equity
        self.position: Optional[dict] = None
        self.retest: Optional[dict] = None
        self.trades = []

    def process_bar(self, bar, prev_bar, ts, h4_high, h4_low, atr, history):
        price = float(bar["Close"])
        if self.position is None:
            return self._check_new_entry(bar, prev_bar, ts, price, h4_high, h4_low, atr, history)
        return self._manage_position(bar, prev_bar, ts, price, h4_high, h4_low, atr)

    def _check_new_entry(self, bar, prev_bar, ts, price, h4_high, h4_low, atr, history):
        prev_close = float(prev_bar["Close"])
        swept_high = prev_close > h4_high and price <= h4_high
        swept_low = prev_close < h4_low and price >= h4_low
        if not swept_high and not swept_low:
            return None

        side = "short" if swept_high else "long"
        entry = price * (1 - SLIPPAGE if side == "short" else 1 + SLIPPAGE)
        sl = _calc_sl(side, entry, history, atr)
        tp = _calc_tp(side, entry, sl, h4_high, h4_low)
        qty, _ = size_position(self.equity, entry, sl)
        return {
            "action": "entry", "side": side, "price": entry, "qty": qty,
            "sl": sl, "tp": tp, "h4_high": h4_high, "h4_low": h4_low,
            "ts": ts
        }

    def _manage_position(self, bar, prev_bar, ts, price, h4_high, h4_low, atr=None):
        side = self.position["side"]
        if side == "short":
            hit_sl = bar["High"] >= self.position["sl"]
            hit_tp = bar["Low"] <= self.position["tp"]
            rebuild = bar["Close"] > h4_high and prev_bar["Close"] > h4_high
        else:
            hit_sl = bar["Low"] <= self.position["sl"]
            hit_tp = bar["High"] >= self.position["tp"]
            rebuild = bar["Close"] < h4_low and prev_bar["Close"] < h4_low

        if hit_sl or hit_tp or rebuild:
            exit_px = self.position["sl"] if hit_sl else (self.position["tp"] if hit_tp else price)
            pnl = (exit_px - self.position["entry"]) * self.position["qty"] if side == "long" \
                else (self.position["entry"] - exit_px) * self.position["qty"]
            self.equity += pnl
            reason = "stop" if hit_sl else ("target" if hit_tp else "rebuild_exit")
            self.trades.append(dict(
                entry=self.position["entry"], exit=exit_px,
                qty=self.position["qty"], pnl=pnl, reason=reason,
                entry_time=self.position["ts"], exit_time=ts
            ))
            self.position = None

            if rebuild:
                flip_side = "long" if side == "short" else "short"
                flip_dir = "up" if flip_side == "long" else "down"
                atr = float(calc_atr(bar.to_frame().T).iloc[-1]) if atr is None else atr
                conf = check_flip_confirmation(bar.to_frame().T, flip_dir)
                if conf == "strong":
                    entry = price * (1 + SLIPPAGE if flip_side == "long" else 1 - SLIPPAGE)
                    sl = _calc_sl(flip_side, entry, bar.to_frame().T, atr)
                    tp = _calc_tp(flip_side, entry, sl, h4_high, h4_low)
                    qty, _ = size_position(self.equity, entry, sl)
                    self.position = dict(side=flip_side, entry=entry, qty=qty, sl=sl, tp=tp, ts=ts)
                elif conf == "weak":
                    self.retest = dict(side=flip_side, level=h4_high if flip_side == "long" else h4_low)
            return {"action": "exit", "pnl": pnl, "reason": reason}
        return None