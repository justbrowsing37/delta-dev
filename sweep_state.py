# sweep_state.py
import json
import logging
from pathlib import Path
from datetime import datetime, timezone
from sweep_strategy import Position

log = logging.getLogger(__name__)
STATE_FILE = Path(__file__).parent / "positions.json"


def load_positions() -> dict[str, Position]:
    if not STATE_FILE.exists():
        return {}
    try:
        with open(STATE_FILE) as f:
            data = json.load(f)
        positions = {}
        for sym, p in data.items():
            positions[sym] = Position(
                symbol=sym,
                side=p["side"],
                entry=p["entry"],
                qty=p["qty"],
                sl=p["sl"],
                tp=p["tp"],
                h4_high=p["h4_high"],
                h4_low=p["h4_low"],
                retest_mode=p.get("retest_mode", False),
                retest_level=p.get("retest_level"),
                retest_dir=p.get("retest_dir"),
            )
        return positions
    except Exception as e:
        log.warning("Failed to load positions: %s", e)
        return {}


def save_positions(positions: dict[str, Position]) -> None:
    data = {}
    for sym, p in positions.items():
        data[sym] = {
            "side": p.side,
            "entry": p.entry,
            "qty": p.qty,
            "sl": p.sl,
            "tp": p.tp,
            "h4_high": p.h4_high,
            "h4_low": p.h4_low,
            "retest_mode": p.retest_mode,
            "retest_level": p.retest_level,
            "retest_dir": p.retest_dir,
        }
    STATE_FILE.write_text(json.dumps(data, indent=2))


def clear_positions() -> None:
    if STATE_FILE.exists():
        STATE_FILE.unlink()