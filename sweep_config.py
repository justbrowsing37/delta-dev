# sweep_config.py
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY    = os.getenv("ALPACA_API_KEY")
SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")

BASE_URL   = "https://paper-api.alpaca.markets"
PAPER      = True

UNIVERSE = ["NVDA", "META", "AMD", "AAPL", "TSLA", "XOM", "SPY"]

EQUITY_RISK_PER_TRADE = 0.03
MAX_POSITION_RISK     = 0.1
MIN_RR                = 1.5
SLIPPAGE              = 0.0005
STOP_ATR_MULT         = 2.0

SWING_LOOKBACK        = 20
VOL_WINDOW            = 20
FLIP_VOL_MULT         = 1.2

RANGE_LOOKBACK_DAYS   = 10
ENTRY_LOOKBACK_DAYS   = 5
LOOP_INTERVAL_SEC     = 30

MAX_DAILY_LOSS        = 0.05
MAX_CONSECUTIVE_LOSSES = 3

USE_TREND_FILTER   = True
TREND_EMA_PERIOD   = 50

