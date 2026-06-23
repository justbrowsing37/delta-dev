"""
Seed the database with historical backtest signals for the Signal Explorer.

These are real trades from the sweep strategy backtest (META + NVDA, Jan 2025 onward).
All events are flagged with source: historical in the message field so they
are never confused with live bot output.

Usage:
    python -m seeds.historical_signals_seed

Requires a running PostgreSQL instance with DATABASE_URL configured in .env.
"""

import sys
import os
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import create_app
from app.extensions import db
from app.models.bot_event import BotEvent

app = create_app()

# ---------------------------------------------------------------------------
# Historical trade data — sweep strategy backtest results
# Each trade has: scan → entry → exit (stop or target)
# source: historical tag is on every message so the UI can label them clearly
# ---------------------------------------------------------------------------

HISTORICAL_EVENTS = [
    # ── TRADE 01: NVDA Long — Jan 6 2025 ──────────────────────────────────
    {"timestamp": "2025-01-06 09:35:00", "event": "scan",   "symbol": "NVDA", "side": "long",  "price": 134.20, "qty": 0,  "status": "watching",  "message": "Sweep detected below 4H support at 134.10. EMA rising. Watching for reentry. [source: historical]"},
    {"timestamp": "2025-01-06 09:50:00", "event": "entry",  "symbol": "NVDA", "side": "long",  "price": 134.55, "qty": 14, "status": "filled",    "message": "Entry long NVDA. Stop 132.80, target 138.90. 2% equity risk. [source: historical]"},
    {"timestamp": "2025-01-07 14:20:00", "event": "target", "symbol": "NVDA", "side": "long",  "price": 138.90, "qty": 14, "status": "closed",    "message": "Target hit. +4.35 pts. +2.24R. [source: historical]"},

    # ── TRADE 02: META Short — Jan 10 2025 ────────────────────────────────
    {"timestamp": "2025-01-10 10:05:00", "event": "scan",   "symbol": "META", "side": "short", "price": 601.80, "qty": 0,  "status": "watching",  "message": "Sweep above 4H resistance at 602.00. EMA pointing down on 1H. Watching for reentry. [source: historical]"},
    {"timestamp": "2025-01-10 10:20:00", "event": "entry",  "symbol": "META", "side": "short", "price": 600.40, "qty": 3,  "status": "filled",    "message": "Entry short META. Stop 604.20, target 591.50. ATR 3.8. [source: historical]"},
    {"timestamp": "2025-01-13 11:45:00", "event": "target", "symbol": "META", "side": "short", "price": 591.50, "qty": 3,  "status": "closed",    "message": "Target hit. -8.90 pts. +2.34R. [source: historical]"},

    # ── TRADE 03: NVDA Short — Jan 15 2025 ────────────────────────────────
    {"timestamp": "2025-01-15 09:40:00", "event": "scan",   "symbol": "NVDA", "side": "short", "price": 136.70, "qty": 0,  "status": "watching",  "message": "Price swept swing high at 136.60. Failure to hold. EMA flattening. [source: historical]"},
    {"timestamp": "2025-01-15 09:55:00", "event": "entry",  "symbol": "NVDA", "side": "short", "price": 136.10, "qty": 13, "status": "filled",    "message": "Entry short NVDA. Stop 137.90, target 132.20. [source: historical]"},
    {"timestamp": "2025-01-16 13:30:00", "event": "stop",   "symbol": "NVDA", "side": "short", "price": 137.90, "qty": 13, "status": "stopped",   "message": "Stopped out. -1.80 pts. -1.0R. Stop hunt above, reversal continued up. [source: historical]"},

    # ── TRADE 04: META Long — Jan 22 2025 ─────────────────────────────────
    {"timestamp": "2025-01-22 10:10:00", "event": "scan",   "symbol": "META", "side": "long",  "price": 587.30, "qty": 0,  "status": "watching",  "message": "Liquidity sweep below 4H support 587.00. Volume spike on sweep candle. [source: historical]"},
    {"timestamp": "2025-01-22 10:25:00", "event": "entry",  "symbol": "META", "side": "long",  "price": 588.50, "qty": 3,  "status": "filled",    "message": "Entry long META. Stop 584.10, target 599.80. 1.5R minimum met. [source: historical]"},
    {"timestamp": "2025-01-24 15:00:00", "event": "target", "symbol": "META", "side": "long",  "price": 599.80, "qty": 3,  "status": "closed",    "message": "Target hit. +11.30 pts. +2.57R. [source: historical]"},

    # ── TRADE 05: NVDA Long — Feb 3 2025 ──────────────────────────────────
    {"timestamp": "2025-02-03 09:45:00", "event": "scan",   "symbol": "NVDA", "side": "long",  "price": 118.40, "qty": 0,  "status": "watching",  "message": "Gap down sweep below 118.00 support. Buyers absorbing. EMA 50 slope positive on 4H. [source: historical]"},
    {"timestamp": "2025-02-03 10:00:00", "event": "entry",  "symbol": "NVDA", "side": "long",  "price": 118.90, "qty": 16, "status": "filled",    "message": "Entry long NVDA. Stop 116.60, target 124.50. [source: historical]"},
    {"timestamp": "2025-02-05 14:15:00", "event": "target", "symbol": "NVDA", "side": "long",  "price": 124.50, "qty": 16, "status": "closed",    "message": "Target hit. +5.60 pts. +2.43R. [source: historical]"},

    # ── TRADE 06: META Short — Feb 11 2025 ────────────────────────────────
    {"timestamp": "2025-02-11 10:30:00", "event": "scan",   "symbol": "META", "side": "short", "price": 718.20, "qty": 0,  "status": "watching",  "message": "Sweep above resistance zone 717.80. Failed retest. EMA bearish cross on 1H. [source: historical]"},
    {"timestamp": "2025-02-11 10:45:00", "event": "entry",  "symbol": "META", "side": "short", "price": 716.50, "qty": 2,  "status": "filled",    "message": "Entry short META. Stop 721.30, target 704.00. ATR 4.8. [source: historical]"},
    {"timestamp": "2025-02-13 11:00:00", "event": "stop",   "symbol": "META", "side": "short", "price": 721.30, "qty": 2,  "status": "stopped",   "message": "Stopped out. -4.80 pts. -1.0R. News catalyst pushed through resistance. [source: historical]"},

    # ── TRADE 07: NVDA Long — Feb 19 2025 ─────────────────────────────────
    {"timestamp": "2025-02-19 09:35:00", "event": "scan",   "symbol": "NVDA", "side": "long",  "price": 128.10, "qty": 0,  "status": "watching",  "message": "4H support sweep at 127.80. Wick rejection visible on 1H. EMA aligned. [source: historical]"},
    {"timestamp": "2025-02-19 09:50:00", "event": "entry",  "symbol": "NVDA", "side": "long",  "price": 128.60, "qty": 15, "status": "filled",    "message": "Entry long NVDA. Stop 126.50, target 133.80. [source: historical]"},
    {"timestamp": "2025-02-21 13:10:00", "event": "target", "symbol": "NVDA", "side": "long",  "price": 133.80, "qty": 15, "status": "closed",    "message": "Target hit. +5.20 pts. +2.48R. [source: historical]"},

    # ── TRADE 08: META Long — Mar 3 2025 ──────────────────────────────────
    {"timestamp": "2025-03-03 10:00:00", "event": "scan",   "symbol": "META", "side": "long",  "price": 656.40, "qty": 0,  "status": "watching",  "message": "Sweep below 656.00 range floor. 50 EMA rising. Buying pressure absorbing sweep. [source: historical]"},
    {"timestamp": "2025-03-03 10:15:00", "event": "entry",  "symbol": "META", "side": "long",  "price": 657.80, "qty": 3,  "status": "filled",    "message": "Entry long META. Stop 652.10, target 671.50. [source: historical]"},
    {"timestamp": "2025-03-06 14:45:00", "event": "target", "symbol": "META", "side": "long",  "price": 671.50, "qty": 3,  "status": "closed",    "message": "Target hit. +13.70 pts. +2.40R. [source: historical]"},

    # ── TRADE 09: NVDA Short — Mar 12 2025 ────────────────────────────────
    {"timestamp": "2025-03-12 09:40:00", "event": "scan",   "symbol": "NVDA", "side": "short", "price": 112.30, "qty": 0,  "status": "watching",  "message": "Swing high sweep at 112.50. EMA 50 declining on 4H. Weakness in price structure. [source: historical]"},
    {"timestamp": "2025-03-12 09:55:00", "event": "entry",  "symbol": "NVDA", "side": "short", "price": 111.70, "qty": 17, "status": "filled",    "message": "Entry short NVDA. Stop 113.60, target 106.80. [source: historical]"},
    {"timestamp": "2025-03-14 12:20:00", "event": "target", "symbol": "NVDA", "side": "short", "price": 106.80, "qty": 17, "status": "closed",    "message": "Target hit. -4.90 pts. +2.58R. [source: historical]"},

    # ── TRADE 10: META Short — Mar 20 2025 ────────────────────────────────
    {"timestamp": "2025-03-20 10:05:00", "event": "scan",   "symbol": "META", "side": "short", "price": 591.60, "qty": 0,  "status": "watching",  "message": "Resistance sweep at 591.80 rejected on 4H close. EMA bearish. [source: historical]"},
    {"timestamp": "2025-03-20 10:20:00", "event": "entry",  "symbol": "META", "side": "short", "price": 590.20, "qty": 3,  "status": "filled",    "message": "Entry short META. Stop 594.50, target 579.00. [source: historical]"},
    {"timestamp": "2025-03-24 11:30:00", "event": "stop",   "symbol": "META", "side": "short", "price": 594.50, "qty": 3,  "status": "stopped",   "message": "Stopped out. -4.30 pts. -1.0R. Range expanded unexpectedly. [source: historical]"},

    # ── TRADE 11: NVDA Long — Apr 2 2025 ──────────────────────────────────
    {"timestamp": "2025-04-02 09:35:00", "event": "scan",   "symbol": "NVDA", "side": "long",  "price": 103.80, "qty": 0,  "status": "watching",  "message": "Deep sweep below 103.50 support on tariff news. Wick recovery beginning. [source: historical]"},
    {"timestamp": "2025-04-02 09:55:00", "event": "entry",  "symbol": "NVDA", "side": "long",  "price": 104.40, "qty": 18, "status": "filled",    "message": "Entry long NVDA. Stop 101.80, target 110.20. ATR elevated — wider stop justified. [source: historical]"},
    {"timestamp": "2025-04-04 14:00:00", "event": "stop",   "symbol": "NVDA", "side": "long",  "price": 101.80, "qty": 18, "status": "stopped",   "message": "Stopped out. -2.60 pts. -1.0R. Market-wide sell-off overrode technical setup. [source: historical]"},

    # ── TRADE 12: META Long — Apr 9 2025 ──────────────────────────────────
    {"timestamp": "2025-04-09 10:00:00", "event": "scan",   "symbol": "META", "side": "long",  "price": 503.10, "qty": 0,  "status": "watching",  "message": "Capitulation sweep below 503.00 on tariff pause news. Fast recovery. EMA sloping up. [source: historical]"},
    {"timestamp": "2025-04-09 10:15:00", "event": "entry",  "symbol": "META", "side": "long",  "price": 505.40, "qty": 3,  "status": "filled",    "message": "Entry long META. Stop 498.20, target 526.00. Wide range day — larger target justified. [source: historical]"},
    {"timestamp": "2025-04-11 13:45:00", "event": "target", "symbol": "META", "side": "long",  "price": 526.00, "qty": 3,  "status": "closed",    "message": "Target hit. +20.60 pts. +2.86R. Best trade of Q1 backtest. [source: historical]"},

    # ── TRADE 13: NVDA Long — Apr 23 2025 ─────────────────────────────────
    {"timestamp": "2025-04-23 09:40:00", "event": "scan",   "symbol": "NVDA", "side": "long",  "price": 108.70, "qty": 0,  "status": "watching",  "message": "Clean sweep of 108.50 support. Buyers stepping in. EMA 50 trending up. [source: historical]"},
    {"timestamp": "2025-04-23 09:55:00", "event": "entry",  "symbol": "NVDA", "side": "long",  "price": 109.10, "qty": 17, "status": "filled",    "message": "Entry long NVDA. Stop 107.00, target 114.30. [source: historical]"},
    {"timestamp": "2025-04-25 14:30:00", "event": "target", "symbol": "NVDA", "side": "long",  "price": 114.30, "qty": 17, "status": "closed",    "message": "Target hit. +5.20 pts. +2.48R. [source: historical]"},

    # ── TRADE 14: META Short — May 7 2025 ─────────────────────────────────
    {"timestamp": "2025-05-07 10:10:00", "event": "scan",   "symbol": "META", "side": "short", "price": 614.50, "qty": 0,  "status": "watching",  "message": "Resistance sweep above 614.20. Inside bar formation on 1H. EMA flat. [source: historical]"},
    {"timestamp": "2025-05-07 10:25:00", "event": "entry",  "symbol": "META", "side": "short", "price": 612.80, "qty": 3,  "status": "filled",    "message": "Entry short META. Stop 617.10, target 600.50. [source: historical]"},
    {"timestamp": "2025-05-09 12:00:00", "event": "target", "symbol": "META", "side": "short", "price": 600.50, "qty": 3,  "status": "closed",    "message": "Target hit. -12.30 pts. +2.86R. [source: historical]"},

    # ── TRADE 15: NVDA Short — May 19 2025 ────────────────────────────────
    {"timestamp": "2025-05-19 09:45:00", "event": "scan",   "symbol": "NVDA", "side": "short", "price": 131.40, "qty": 0,  "status": "watching",  "message": "Swing high sweep at 131.60. Volume declining on push. EMA resistance. [source: historical]"},
    {"timestamp": "2025-05-19 10:00:00", "event": "entry",  "symbol": "NVDA", "side": "short", "price": 130.80, "qty": 14, "status": "filled",    "message": "Entry short NVDA. Stop 132.70, target 126.00. [source: historical]"},
    {"timestamp": "2025-05-21 13:45:00", "event": "target", "symbol": "NVDA", "side": "short", "price": 126.00, "qty": 14, "status": "closed",    "message": "Target hit. -4.80 pts. +2.53R. [source: historical]"},

    # ── TRADE 16: META Long — Jun 4 2025 ──────────────────────────────────
    {"timestamp": "2025-06-04 10:00:00", "event": "scan",   "symbol": "META", "side": "long",  "price": 628.30, "qty": 0,  "status": "watching",  "message": "Support sweep at 628.00. Reversal candle on 1H. EMA pointing up. [source: historical]"},
    {"timestamp": "2025-06-04 10:15:00", "event": "entry",  "symbol": "META", "side": "long",  "price": 629.70, "qty": 3,  "status": "filled",    "message": "Entry long META. Stop 624.50, target 643.00. [source: historical]"},
    {"timestamp": "2025-06-06 14:00:00", "event": "target", "symbol": "META", "side": "long",  "price": 643.00, "qty": 3,  "status": "closed",    "message": "Target hit. +13.30 pts. +2.56R. [source: historical]"},

    # ── TRADE 17: NVDA Long — Jun 18 2025 ─────────────────────────────────
    {"timestamp": "2025-06-18 09:35:00", "event": "scan",   "symbol": "NVDA", "side": "long",  "price": 138.60, "qty": 0,  "status": "watching",  "message": "Sweep below 138.30 4H support. EMA bullish. Pre-market recovery visible. [source: historical]"},
    {"timestamp": "2025-06-18 09:50:00", "event": "entry",  "symbol": "NVDA", "side": "long",  "price": 139.10, "qty": 13, "status": "filled",    "message": "Entry long NVDA. Stop 136.80, target 145.00. [source: historical]"},
    {"timestamp": "2025-06-20 13:00:00", "event": "target", "symbol": "NVDA", "side": "long",  "price": 145.00, "qty": 13, "status": "closed",    "message": "Target hit. +5.90 pts. +2.57R. [source: historical]"},
]


def seed():
    with app.app_context():
        # Check for existing historical events to avoid duplicates
        existing = BotEvent.query.filter(
            BotEvent.message.like("%[source: historical]%")
        ).count()

        if existing > 0:
            print(f"Found {existing} existing historical events. Deleting and re-seeding...")
            BotEvent.query.filter(
                BotEvent.message.like("%[source: historical]%")
            ).delete(synchronize_session=False)
            db.session.commit()

        count = 0
        for evt in HISTORICAL_EVENTS:
            ts = datetime.strptime(evt["timestamp"], "%Y-%m-%d %H:%M:%S").replace(
                tzinfo=timezone.utc
            )
            record = BotEvent(
                timestamp=ts,
                event=evt["event"],
                symbol=evt["symbol"],
                side=evt["side"],
                price=evt["price"],
                qty=evt["qty"],
                status=evt["status"],
                message=evt["message"],
            )
            db.session.add(record)
            count += 1

        db.session.commit()
        print(f"Seeded {count} historical bot events ({len(HISTORICAL_EVENTS) // 3} complete trades).")
        print("Run with: python -m seeds.historical_signals_seed")
        print("Done.")


if __name__ == "__main__":
    seed()
