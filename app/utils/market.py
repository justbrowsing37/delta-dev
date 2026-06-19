from zoneinfo import ZoneInfo
from datetime import datetime, timezone

from app.extensions import db
from app.models.bot_event import BotEvent

TIMEZONE = ZoneInfo("America/New_York")
SYMBOLS = ["NVDA", "META"]
PAPER = True


def now_et():
    return datetime.now(TIMEZONE)


def market_open_state(now):
    return (
        now.weekday() < 5
        and now.time() >= datetime.strptime("09:30", "%H:%M").time()
        and now.time() <= datetime.strptime("16:00", "%H:%M").time()
    )


def compute_health(rows):
    now = datetime.now(timezone.utc)
    if not rows:
        return "critical", "No events yet"

    last = rows[0]
    ts = last.timestamp
    if ts and ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    age = (now - ts).total_seconds() if ts else float("inf")

    recent_error = None
    for r in rows:
        if r.event == "error":
            recent_error = r
            break

    if recent_error:
        rts = recent_error.timestamp
        if rts and rts.tzinfo is None:
            rts = rts.replace(tzinfo=timezone.utc)
        if rts and (now - rts).total_seconds() <= 300:
            return "critical", "Recent error event"

    if market_open_state(datetime.now(TIMEZONE)):
        if age <= 90:
            return "healthy", "Fresh event flow"
        if age <= 180:
            return "warning", "Event stream slowing"
        return "critical", "Stale during market hours"

    return "healthy", "Market closed"
