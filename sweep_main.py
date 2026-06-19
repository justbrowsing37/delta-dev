# sweep_main.py
"""
Live trading loop for the 4H Liquidity Sweep Bot.
Run: python sweep_main.py
"""
import time
from datetime import datetime, timezone
from datetime import time as dt_time
from zoneinfo import ZoneInfo
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from sweep_config import (
    API_KEY, SECRET_KEY, PAPER, UNIVERSE,
    LOOP_INTERVAL_SEC, RANGE_LOOKBACK_DAYS, ENTRY_LOOKBACK_DAYS,
    MAX_DAILY_LOSS, MAX_CONSECUTIVE_LOSSES
)
from sweep_data import get_5min_bars, get_1h_bars
from sweep_strategy import get_signal, build_4h_from_1h, Position
from sweep_state import load_positions, save_positions
from bot_logger import get_logger
from sweep_csv import log_event

log           = get_logger(__name__)
client       = TradingClient(API_KEY, SECRET_KEY, paper=PAPER)
positions   = load_positions()
daily_pnl    = 0.0
consecutive_losses = 0
last_date    = None


def get_equity() -> float:
    return float(client.get_account().equity)


def get_buying_power() -> float:
    return float(client.get_account().buying_power)


def check_circuit_breaker(action: str, pnl: float = 0.0) -> bool:
    global daily_pnl, consecutive_losses, last_date
    now = datetime.now(timezone.utc)

    if last_date is None or now.date() != last_date:
        daily_pnl = 0.0
        consecutive_losses = 0
        last_date = now.date()

    if action in ("exit", "flip_strong", "flip_weak"):
        if pnl < 0:
            consecutive_losses += 1
        else:
            consecutive_losses = 0

    if action != "hold":
        daily_pnl += pnl

    if daily_pnl < -get_equity() * MAX_DAILY_LOSS:
        log.critical(f"CIRCUIT BREAKER: Daily loss ${daily_pnl:.2f} exceeds {MAX_DAILY_LOSS*100}%")
        return True

    if consecutive_losses >= MAX_CONSECUTIVE_LOSSES:
        log.critical(f"CIRCUIT BREAKER: {consecutive_losses} consecutive losses")
        return True

    return False


def _estimate_pnl(pos: Position, exit_price: float) -> float:
    if pos.side == "long":
        return (exit_price - pos.entry) * pos.qty
    else:
        return (pos.entry - exit_price) * pos.qty


def has_sufficient_buying_power(qty: int, price: float) -> bool:
    required = qty * price
    return get_buying_power() >= required


def place_order(symbol, side, qty):
    req = MarketOrderRequest(
        symbol=symbol, qty=qty,
        side=OrderSide.BUY if side == "long" else OrderSide.SELL,
        time_in_force=TimeInForce.DAY,
    )
    client.submit_order(req)
    log.info(f"ORDER {symbol} {side.upper()} qty={qty}")


def close_position(symbol, qty, side):
    req = MarketOrderRequest(
        symbol=symbol, qty=qty,
        side=OrderSide.SELL if side == "long" else OrderSide.BUY,
        time_in_force=TimeInForce.DAY,
    )
    client.submit_order(req)
    log.info(f"CLOSE {symbol} qty={qty}")


def run():
    log.info("=== 4H Sweep Bot Starting ===")
    log.info(f"Universe: {UNIVERSE} | Paper: {PAPER}")

    while True:
        try:
            now_et = datetime.now(ZoneInfo("America/New_York"))
            if now_et.weekday() >= 5 or not (dt_time(9, 30) <= now_et.time() < dt_time(16, 0)):
                log.info(f"Outside market hours ({now_et.strftime('%Y-%m-%d %H:%M:%S %Z')}) — sleeping 60s")
                time.sleep(60)
                continue

            equity = get_equity()
            log.info(f"Scanning {len(UNIVERSE)} symbols | Equity: ${equity:,.2f}")

            for symbol in UNIVERSE:
                try:
                    df_1h = get_1h_bars(symbol, RANGE_LOOKBACK_DAYS)
                    df_4h = build_4h_from_1h(df_1h)
                    df_5m = get_5min_bars(symbol, ENTRY_LOOKBACK_DAYS)
                    pos   = positions.get(symbol)
                    sig   = get_signal(df_5m, df_4h, equity, pos)
                    action = sig["action"]

                    if action == "hold":
                        log.info(f"{symbol} | HOLD | side={pos.side if pos else 'none'}")
                        log_event("scan", symbol=symbol, side=pos.side if pos else "none",
                                  status="hold", message="no setup")

                    elif action == "entry":
                        if not has_sufficient_buying_power(sig["qty"], sig["price"]):
                            log.warning(f"Skipping {symbol} — insufficient buying power")
                            log_event("skip", symbol=symbol, side=sig["side"],
                                      price=sig["price"], qty=sig["qty"],
                                      status="insufficient_bp")
                            continue
                        log.info(f"ENTRY {symbol} {sig['side'].upper()} @ ${sig['price']:.2f} | Qty:{sig['qty']} | SL:${sig['sl']:.2f} | TP:${sig['tp']:.2f}")
                        log_event("order_submitted", symbol=symbol, side=sig["side"],
                                  price=sig["price"], qty=sig["qty"], status="pending")
                        place_order(symbol, sig["side"], sig["qty"])
                        positions[symbol] = Position(
                            symbol=symbol, side=sig["side"], entry=sig["price"],
                            qty=sig["qty"], sl=sig["sl"], tp=sig["tp"],
                            h4_high=sig["h4_high"], h4_low=sig["h4_low"]
                        )
                        save_positions(positions)
                        log_event("position_opened", symbol=symbol, side=sig["side"],
                                  price=sig["price"], qty=sig["qty"], status="filled")

                    elif action == "exit":
                        pnl_est = _estimate_pnl(pos, sig["price"])
                        log.info(f"EXIT {symbol} @ ${sig['price']:.2f} | {sig['reason']} | PnL≈${pnl_est:.2f}")
                        close_position(symbol, pos.qty, pos.side)
                        log_event("exit", symbol=symbol, side=pos.side,
                                  price=sig["price"], qty=pos.qty,
                                  status="closed", message=sig.get("reason", ""))
                        del positions[symbol]
                        save_positions(positions)
                        if check_circuit_breaker("exit", pnl_est):
                            log.critical("Circuit breaker triggered — halting all trading.")
                            return

                    elif action == "flip_strong":
                        pnl_est = _estimate_pnl(pos, sig["price"])
                        if check_circuit_breaker("flip_strong", pnl_est):
                            log.critical("Circuit breaker triggered — halting all trading.")
                            return
                        if not has_sufficient_buying_power(sig["qty"], sig["price"]):
                            log.warning(f"Skipping flip for {symbol} — insufficient buying power")
                            log_event("skip", symbol=symbol, side=sig["side"],
                                      price=sig["price"], qty=sig["qty"],
                                      status="insufficient_bp", message="flip_strong")
                            continue
                        log.info(f"FLIP→{sig['side'].upper()} {symbol} @ ${sig['price']:.2f} [strong]")
                        close_position(symbol, pos.qty, pos.side)
                        log_event("exit", symbol=symbol, side=pos.side,
                                  price=sig["price"], qty=pos.qty,
                                  status="closed", message="flip_strong")
                        place_order(symbol, sig["side"], sig["qty"])
                        positions[symbol] = Position(
                            symbol=symbol, side=sig["side"], entry=sig["price"],
                            qty=sig["qty"], sl=sig["sl"], tp=sig["tp"],
                            h4_high=sig["h4_high"], h4_low=sig["h4_low"]
                        )
                        save_positions(positions)
                        log_event("position_opened", symbol=symbol, side=sig["side"],
                                  price=sig["price"], qty=sig["qty"],
                                  status="filled", message="flip_strong")

                    elif action == "flip_weak":
                        pnl_est = _estimate_pnl(pos, sig["price"])
                        if check_circuit_breaker("flip_weak", pnl_est):
                            log.critical("Circuit breaker triggered — halting all trading.")
                            return
                        log.info(f"FLIP_WEAK {symbol} — flat, waiting retest @ ${sig['retest_level']:.2f}")
                        close_position(symbol, pos.qty, pos.side)
                        log_event("exit", symbol=symbol, side=pos.side,
                                  price=sig.get("retest_level", ""), qty=pos.qty,
                                  status="closed", message="flip_weak")
                        positions[symbol] = Position(
                            symbol=symbol, side=sig["side"], entry=0, qty=0, sl=0, tp=0,
                            h4_high=pos.h4_high, h4_low=pos.h4_low,
                            retest_mode=True, retest_level=sig["retest_level"],
                            retest_dir=sig["side"]
                        )
                        save_positions(positions)

                    elif action == "retest_entry":
                        if not has_sufficient_buying_power(sig["qty"], sig["price"]):
                            log.warning(f"Skipping retest entry for {symbol} — insufficient buying power")
                            log_event("skip", symbol=symbol, side=sig["side"],
                                      price=sig["price"], qty=sig["qty"],
                                      status="insufficient_bp", message="retest_entry")
                            continue
                        log.info(f"RETEST ENTRY {symbol} {sig['side'].upper()} @ ${sig['price']:.2f}")
                        log_event("order_submitted", symbol=symbol, side=sig["side"],
                                  price=sig["price"], qty=sig["qty"], status="pending", message="retest")
                        place_order(symbol, sig["side"], sig["qty"])
                        positions[symbol] = Position(
                            symbol=symbol, side=sig["side"], entry=sig["price"],
                            qty=sig["qty"], sl=sig["sl"], tp=sig["tp"],
                            h4_high=sig["h4_high"], h4_low=sig["h4_low"]
                        )
                        save_positions(positions)
                        log_event("position_opened", symbol=symbol, side=sig["side"],
                                  price=sig["price"], qty=sig["qty"],
                                  status="filled", message="retest")

                except Exception as e:
                    log.error(f"Loop error {symbol}: {e}")
                    log_event("error", symbol=symbol, status="error", message=str(e))

            for pos in positions.values():
                value = pos.entry * pos.qty
                log_event("position", symbol=pos.symbol, side=pos.side,
                          price=pos.entry, qty=pos.qty, status="active",
                          message=f"value={value:.2f}")

            time.sleep(LOOP_INTERVAL_SEC)

        except KeyboardInterrupt:
            log.info("Bot stopped.")
            break
        except Exception as e:
            log.error(f"Main loop error: {e}")
            log_event("error", status="error", message=str(e))
            time.sleep(10)


if __name__ == "__main__":
    run()
