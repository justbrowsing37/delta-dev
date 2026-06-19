# sweep_csv.py
import csv
import logging
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

CSV_PATH = Path(__file__).parent / "data" / "bot_events.csv"
FIELDS = ["timestamp", "event", "symbol", "side", "price", "qty", "status", "message"]

log = logging.getLogger(__name__)

try:
    from app.extensions import db
    from app.models.bot_event import BotEvent
    _db_available = True
except ImportError:
    _db_available = False


def _ensure_file():
    CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not CSV_PATH.exists():
        with open(CSV_PATH, "w", newline="") as f:
            csv.writer(f).writerow(FIELDS)


def log_event(event, symbol="", side="", price="", qty="", status="", message=""):
    now = datetime.now(ZoneInfo("America/New_York"))

    try:
        _ensure_file()
        ts = now.strftime("%Y-%m-%d %H:%M:%S %Z")
        with open(CSV_PATH, "a", newline="") as f:
            csv.writer(f).writerow([ts, event, symbol, side, price, qty, status, message])
    except Exception as e:
        log.warning(f"CSV log_event failed: {e}")

    if _db_available:
        try:
            row = BotEvent(
                timestamp=now,
                event=event,
                symbol=symbol,
                side=side,
                price=float(price) if price else None,
                qty=int(qty) if qty else None,
                status=status,
                message=message,
            )
            db.session.add(row)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            log.warning(f"DB write failed (CSV only): {e}")
