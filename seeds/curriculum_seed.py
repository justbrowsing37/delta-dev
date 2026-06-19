"""
Seed the database with the Delta Core curriculum:
5 modules (0–4), 22 lessons total.

Usage:
    python -m seeds.curriculum_seed

Requires a running PostgreSQL instance with the DATABASE_URL configured in .env.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import create_app
from app.extensions import db
from app.models.module import Module
from app.models.lesson import Lesson

app = create_app()

MODULES = [
    {
        "title": "What is the Market?",
        "slug": "what-is-the-market",
        "description": "No assumed knowledge. Start here if you have never traded before.",
        "icon": "bank",
        "sort_order": 0,
        "lessons": [
            {
                "title": "What is a stock?",
                "slug": "what-is-a-stock",
                "sort_order": 0,
                "estimated_minutes": 3,
                "concept_tags": ["stock", "equity", "basics"],
                "content": """
<h2>A piece of ownership</h2>
<p>A stock is a small slice of ownership in a company. When you buy one share of Apple, you own a tiny fraction of Apple — its buildings, its patents, its cash, its future profits.</p>
<p>Companies sell shares to raise money (called <strong>raising capital</strong>). Investors buy shares hoping the company grows, which makes each slice worth more over time.</p>
<div class="key-takeaway">
  <strong>Key takeaway:</strong> A stock = a piece of a company. When the company earns more, the piece tends to be worth more.
</div>
""",
            },
            {
                "title": "What does it mean to own a share?",
                "slug": "what-does-it-mean-to-own-a-share",
                "sort_order": 1,
                "estimated_minutes": 3,
                "concept_tags": ["ownership", "shareholder", "basics"],
                "content": """
<h2>Rights and risks</h2>
<p>Owning a share gives you certain rights: a vote at shareholder meetings, a claim on a portion of profits (dividends), and the ability to sell your slice to someone else.</p>
<p>It also means you share the risk. If the company loses value, your share loses value. You are not personally on the hook for the company's debts, but your investment can go to zero.</p>
<div class="key-takeaway">
  <strong>Key takeaway:</strong> Ownership = upside potential + downside risk. You can lose your entire investment if the company fails.
</div>
""",
            },
            {
                "title": "How does a stock exchange work?",
                "slug": "how-does-a-stock-exchange-work",
                "sort_order": 2,
                "estimated_minutes": 4,
                "concept_tags": ["exchange", "market", "order"],
                "content": """
<h2>The marketplace for shares</h2>
<p>A stock exchange (like NYSE or Nasdaq) is a central marketplace where buyers and sellers meet. When you place an order to buy Apple, your broker sends that order to the exchange, which matches you with someone selling.</p>
<p>Exchanges provide <strong>liquidity</strong> — the ability to buy or sell quickly at a fair price. Without exchanges, you would need to find a buyer for your shares yourself.</p>
<p>Most modern exchanges are fully electronic. Matching engines pair buy orders with sell orders in milliseconds.</p>
<div class="key-takeaway">
  <strong>Key takeaway:</strong> An exchange is a central matching point. Buyers meet sellers, and the current price is whatever the last trade happened at.
</div>
""",
            },
            {
                "title": "What moves a stock price?",
                "slug": "what-moves-a-stock-price",
                "sort_order": 3,
                "estimated_minutes": 4,
                "concept_tags": ["price", "supply-demand", "volatility"],
                "content": """
<h2>Supply and demand, every second</h2>
<p>A stock price moves because supply and demand shift. If more people want to buy than sell, the price goes up. If more people want to sell than buy, the price goes down.</p>
<p>What drives supply and demand? Company earnings, news events, economic data, investor sentiment, and sometimes just algorithms reacting to each other.</p>
<p>Price moves in <strong>ticks</strong> — tiny increments — and over time those ticks form the patterns traders study.</p>
<div class="key-takeaway">
  <strong>Key takeaway:</strong> Price is a real-time auction. Every tick represents a transaction between a buyer and a seller who disagree on value.
</div>
""",
            },
            {
                "title": "Bulls, bears, and market sentiment",
                "slug": "bulls-bears-and-market-sentiment",
                "sort_order": 4,
                "estimated_minutes": 3,
                "concept_tags": ["bullish", "bearish", "sentiment"],
                "content": """
<h2>The two tribes</h2>
<p><strong>Bulls</strong> expect prices to rise. They buy, hoping to sell later at a higher price. <strong>Bears</strong> expect prices to fall. They sell (or short-sell), hoping to buy back later at a lower price.</p>
<p>Market <strong>sentiment</strong> is the overall mood — are most participants bullish or bearish right now? Sentiment can shift quickly on news, and extreme sentiment often signals a turning point.</p>
<div class="key-takeaway">
  <strong>Key takeaway:</strong> Markets are driven by the tug-of-war between bulls and bears. Sentiment tells you who is in control.
</div>
""",
            },
        ],
    },
    {
        "title": "Reading the Market",
        "slug": "reading-the-market",
        "description": "Learn how to read a price chart and understand what the market is telling you.",
        "icon": "chart",
        "sort_order": 1,
        "lessons": [
            {
                "title": "How to read a price chart",
                "slug": "how-to-read-a-price-chart",
                "sort_order": 0,
                "estimated_minutes": 4,
                "concept_tags": ["chart", "candlestick", "timeframe"],
                "content": """
<h2>Candlesticks tell the story</h2>
<p>A price chart plots time on the horizontal axis and price on the vertical axis. Each <strong>candlestick</strong> shows four data points: open, high, low, and close for that time period.</p>
<p>A green candle means price closed higher than it opened. A red candle means price closed lower. The <strong>wicks</strong> (thin lines above and below the body) show the high and low price reached.</p>
<p>Different <strong>timeframes</strong> show different detail: 1-minute candles for fine-grained moves, daily candles for the big picture.</p>
<div class="key-takeaway">
  <strong>Key takeaway:</strong> Every candle is a fight between buyers and sellers. The size and color tell you who won that round.
</div>
""",
            },
            {
                "title": "What is a trading range?",
                "slug": "what-is-a-trading-range",
                "sort_order": 1,
                "estimated_minutes": 3,
                "concept_tags": ["range", "consolidation", "boundary"],
                "content": """
<h2>Price taking a breather</h2>
<p>A <strong>trading range</strong> is when price moves sideways between two horizontal levels — a support floor and a resistance ceiling. Price bounces between them like a ball in a room.</p>
<p>Ranges form when buyers and sellers are balanced. Neither side has enough force to break out. The range contains the price until one side wins.</p>
<p>Most breakouts from ranges fail (they are <strong>fakeouts</strong>). That is a key insight for the sweep strategy.</p>
<div class="key-takeaway">
  <strong>Key takeaway:</strong> A range is a tug-of-war. Price respects the boundaries until it doesn't — and that moment is where opportunity lives.
</div>
""",
            },
            {
                "title": "Support and resistance",
                "slug": "support-and-resistance",
                "sort_order": 2,
                "estimated_minutes": 3,
                "concept_tags": ["support", "resistance", "level"],
                "content": """
<h2>The floor and ceiling</h2>
<p><strong>Support</strong> is a price level where buying pressure is strong enough to stop price from falling further. <strong>Resistance</strong> is where selling pressure stops price from rising.</p>
<p>These levels form because traders remember them. If a stock bounced at $100 three times, traders will place buy orders near $100 again — creating support.</p>
<p>When support breaks, it often becomes resistance, and vice versa. This role reversal is one of the most reliable patterns in technical analysis.</p>
<div class="key-takeaway">
  <strong>Key takeaway:</strong> Support and resistance are self-fulfilling because traders act on them. Broken support becomes resistance.
</div>
""",
            },
            {
                "title": "Breakouts vs fakeouts",
                "slug": "breakouts-vs-fakeouts",
                "sort_order": 3,
                "estimated_minutes": 3,
                "concept_tags": ["breakout", "fakeout", "trap"],
                "content": """
<h2>Not all breakouts are real</h2>
<p>A <strong>breakout</strong> is when price moves beyond a support or resistance level. A <strong>fakeout</strong> is when price breaks the level briefly, then reverses back inside the range.</p>
<p>Fakeouts trap traders who chased the breakout. They buy at resistance (expecting a breakout higher), only for price to reverse and fall. These trapped traders are forced to sell at a loss, which fuels the move in the opposite direction.</p>
<p>The sweep strategy is built on identifying these fakeouts and trading the reversal.</p>
<div class="key-takeaway">
  <strong>Key takeaway:</strong> Fakeouts are traps. The sweep strategy waits for the trap to spring, then trades the reversal.
</div>
""",
            },
        ],
    },
    {
        "title": "How Big Money Moves",
        "slug": "how-big-money-moves",
        "description": "Understand how institutions think and why retail traders often lose.",
        "icon": "globe",
        "sort_order": 2,
        "lessons": [
            {
                "title": "Retail traders vs institutional traders",
                "slug": "retail-vs-institutional-traders",
                "sort_order": 0,
                "estimated_minutes": 3,
                "concept_tags": ["retail", "institutional", "smart-money"],
                "content": """
<h2>Two different games</h2>
<p><strong>Retail traders</strong> are individuals trading with their own money — usually small amounts, limited tools, and emotional decision-making. <strong>Institutional traders</strong> manage large funds, use algorithms, and have access to better data and execution.</p>
<p>Institutions do not trade like retail. They need large positions, so they cannot buy all at once without moving price against themselves. They accumulate slowly, often during quiet periods, and they use liquidity sweeps to fill their orders.</p>
<p>Understanding how institutions think is the key to reading what is really happening in the market.</p>
<div class="key-takeaway">
  <strong>Key takeaway:</strong> Retail trades with emotion. Institutions trade with strategy. Learn to see what the institutions are doing.
</div>
""",
            },
            {
                "title": "What is liquidity?",
                "slug": "what-is-liquidity",
                "sort_order": 1,
                "estimated_minutes": 3,
                "concept_tags": ["liquidity", "order-book", "depth"],
                "content": """
<h2>Fuel for big moves</h2>
<p><strong>Liquidity</strong> is the pool of orders waiting to be filled — buy orders below price and sell orders above price. The more orders waiting, the deeper the liquidity.</p>
<p>Institutions need liquidity to enter and exit large positions. They look for areas where many stop-loss orders cluster, because those orders represent guaranteed volume.</p>
<p>Where is liquidity concentrated? Above recent highs (where short sellers put stops) and below recent lows (where long traders put stops). These are the zones the price gets <strong>swept</strong> to.</p>
<div class="key-takeaway">
  <strong>Key takeaway:</strong> Liquidity is the fuel. Institutions drive price toward clustered stops to fill their own orders.
</div>
""",
            },
            {
                "title": "Why stop hunts happen",
                "slug": "why-stop-hunts-happen",
                "sort_order": 2,
                "estimated_minutes": 4,
                "concept_tags": ["stop-hunt", "stop-loss", "liquidity-grab"],
                "content": """
<h2>Triggering the traps</h2>
<p>A <strong>stop hunt</strong> occurs when price moves sharply past a key level, triggering a wave of stop-loss orders, then reverses. The sharp move is driven by the cascade of stops being hit.</p>
<p>Institutions know where retail stop-loss orders cluster — just below support levels (where long traders place stops) and just above resistance levels (where short traders place stops).</p>
<p>By pushing price through these levels, institutions trigger the stops, which provides the liquidity they need to fill their own larger orders at a better price.</p>
<div class="key-takeaway">
  <strong>Key takeaway:</strong> A stop hunt is not random. It is a deliberate move to collect liquidity. The reversal that follows is the real move.
</div>
""",
            },
            {
                "title": "Liquidity sweeps explained",
                "slug": "liquidity-sweeps-explained",
                "sort_order": 3,
                "estimated_minutes": 4,
                "concept_tags": ["sweep", "liquidity", "reversal"],
                "content": """
<h2>The sweep pattern</h2>
<p>A <strong>liquidity sweep</strong> is the specific pattern: price pushes beyond a key level (often a recent high or low), triggers the stops clustered there, and immediately reverses direction. The sweep is the move out, the reversal is the real move.</p>
<p>Delta One's engine detects these sweeps on the 4-hour timeframe. When price sweeps a level and fails to hold, the breakout was a trap. The strategy looks for a reversal trade in the opposite direction.</p>
<p>Not every sweep leads to a reversal. The strategy uses additional confluences — the 50 EMA trend filter, swing structure confirmation, and ATR-based risk — to filter out false signals.</p>
<div class="key-takeaway">
  <strong>Key takeaway:</strong> A sweep + failure to hold = trap. The reversal is the opportunity. Confluences confirm it.
</div>
""",
            },
            {
                "title": "Reading the 4H range",
                "slug": "reading-the-4h-range",
                "sort_order": 4,
                "estimated_minutes": 3,
                "concept_tags": ["4h-range", "timeframe", "structure"],
                "content": """
<h2>The big picture</h2>
<p>Delta One builds its range structure from 1-hour data and projects it onto the 4-hour chart. This gives a higher-level view of where support and resistance are forming.</p>
<p>The 4-hour range tells you the <strong>battlefield</strong> — where the major liquidity pools are and where sweeps are likely to occur. It filters out the noise of smaller timeframes.</p>
<p>When price approaches the edge of the 4-hour range, watch for a sweep. When it sweeps and reverses, the 4-hour range provides the target for the move back to the opposite side.</p>
<div class="key-takeaway">
  <strong>Key takeaway:</strong> The 4H range is your map. It shows you where the liquidity is and where to expect sweeps.
</div>
""",
            },
        ],
    },
    {
        "title": "The Sweep Strategy",
        "slug": "the-sweep-strategy",
        "description": "Understand exactly what Delta One detects and why it trades the way it does.",
        "icon": "target",
        "sort_order": 3,
        "lessons": [
            {
                "title": "What Delta One looks for",
                "slug": "what-delta-one-looks-for",
                "sort_order": 0,
                "estimated_minutes": 4,
                "concept_tags": ["delta-one", "scan", "detection"],
                "content": """
<h2>Scanning for the setup</h2>
<p>Delta One continuously scans NVDA, META, and other equities in its universe. It looks for three conditions aligning:</p>
<ol>
  <li><strong>4H range structure</strong> — A clear support and resistance level built from 1-hour data</li>
  <li><strong>5-minute breakout + reentry</strong> — Price sweeps the range edge and the candle closes back inside</li>
  <li><strong>50 EMA trend filter</strong> — The trend must confirm the reversal direction (no counter-trend entries)</li>
</ol>
<p>When all three align, the engine generates a signal. It does not predict — it reacts to what the market has already done.</p>
<div class="key-takeaway">
  <strong>Key takeaway:</strong> Delta One does not guess. It waits for the market to show its hand — then acts.
</div>
""",
            },
            {
                "title": "Entry conditions",
                "slug": "entry-conditions",
                "sort_order": 1,
                "estimated_minutes": 4,
                "concept_tags": ["entry", "signal", "execution"],
                "content": """
<h2>When the trigger fires</h2>
<p>Once a sweep is detected, the engine checks entry conditions before placing a trade:</p>
<ul>
  <li><strong>Stop-loss placement:</strong> ATR-based, placed beyond the sweep wick where the trap was sprung</li>
  <li><strong>Reward-to-risk:</strong> Minimum 1.5R. The engine will not take a trade with poor asymmetry</li>
  <li><strong>Swing confirmation:</strong> The recent swing high or low must support the direction</li>
  <li><strong>Position sizing:</strong> 2% equity risk per trade, sized based on the distance to stop</li>
</ul>
<p>The entry itself is a market order — the engine acts immediately when conditions are met.</p>
<div class="key-takeaway">
  <strong>Key takeaway:</strong> Entry is the last step. The engine only acts after sweep + confirmation + risk check.
</div>
""",
            },
            {
                "title": "Risk management",
                "slug": "risk-management",
                "sort_order": 2,
                "estimated_minutes": 4,
                "concept_tags": ["risk", "stop-loss", "position-sizing"],
                "content": """
<h2>Staying in the game</h2>
<p>Delta One has multiple layers of risk control:</p>
<ul>
  <li><strong>Per-trade risk:</strong> 2% of equity per trade. If equity is $10,000, max loss per trade is $200</li>
  <li><strong>ATR-based stops:</strong> Stops are placed at a multiple of ATR beyond the sweep point, adjusted for swing structure</li>
  <li><strong>Daily circuit breaker:</strong> If the account loses more than the max daily loss threshold, trading stops for the day</li>
  <li><strong>Consecutive loss breaker:</strong> After a configurable number of consecutive losses, trading halts until reviewed</li>
</ul>
<p>These rules ensure no single trade or string of losses can meaningfully damage the account.</p>
<div class="key-takeaway">
  <strong>Key takeaway:</strong> Risk management is not optional. The engine survives because it controls downside first.
</div>
""",
            },
            {
                "title": "When to flip direction",
                "slug": "when-to-flip-direction",
                "sort_order": 3,
                "estimated_minutes": 3,
                "concept_tags": ["flip", "reversal", "exit"],
                "content": """
<h2>Exiting and reversing</h2>
<p>Delta One does not hold positions indefinitely. Every trade has a take-profit target based on the 4-hour range width.</p>
<p>When price hits the target, the position is closed. If the sweep structure reverses again — a sweep of the opposite range edge — the engine may <strong>flip</strong> and take a trade in the new direction.</p>
<p>The flip condition requires fresh confirmation: a new sweep on the opposite side, the same confluence checks, and the trend filter aligned with the new direction.</p>
<div class="key-takeaway">
  <strong>Key takeaway:</strong> The strategy is directional but not stubborn. If the market reverses, the engine can flip.
</div>
""",
            },
        ],
    },
    {
        "title": "Understanding the Signals",
        "slug": "understanding-the-signals",
        "description": "Connect the curriculum to the product. Learn how to read a Delta One signal and what to do with it.",
        "icon": "signal",
        "sort_order": 4,
        "lessons": [
            {
                "title": "How to read a Delta One signal",
                "slug": "how-to-read-a-delta-one-signal",
                "sort_order": 0,
                "estimated_minutes": 4,
                "concept_tags": ["signal", "dashboard", "reading"],
                "content": """
<h2>What you see on screen</h2>
<p>A Delta One signal card shows:</p>
<ul>
  <li><strong>Symbol</strong> — Which equity was detected (NVDA, META, etc.)</li>
  <li><strong>Side</strong> — Long (expecting price to rise) or Short (expecting price to fall)</li>
  <li><strong>Price</strong> — The price at which the sweep was detected</li>
  <li><strong>Timestamp</strong> — When the detection happened</li>
  <li><strong>Event type</strong> — What the engine detected (scan, entry, exit, etc.)</li>
</ul>
<p>Each signal in the Explorer includes an <strong>educational explanation</strong> linking the event back to the curriculum concept — so you learn why the engine acted.</p>
<div class="key-takeaway">
  <strong>Key takeaway:</strong> A signal is a snapshot of what the engine saw. The educational explanation tells you why it mattered.
</div>
""",
            },
            {
                "title": "What the signal is telling you",
                "slug": "what-the-signal-is-telling-you",
                "sort_order": 1,
                "estimated_minutes": 3,
                "concept_tags": ["interpretation", "context", "education"],
                "content": """
<h2>Read the story behind the event</h2>
<p>A signal is not a prediction. It is a report: "Price swept this level, and these confluences aligned." The educational overlay translates that into plain language.</p>
<p>For example: "Price broke above the 4H resistance at $180, swept the stops clustered above it, and closed back inside the range. The 50 EMA is rising, confirming the uptrend. This was a long-entry signal."</p>
<p>Over time, reading these explanations trains you to see the same patterns yourself on any chart.</p>
<div class="key-takeaway">
  <strong>Key takeaway:</strong> The signal tells you what happened and why. Study the explanation to train your own eye.
</div>
""",
            },
            {
                "title": "What the signal is NOT telling you",
                "slug": "what-the-signal-is-not-telling-you",
                "sort_order": 2,
                "estimated_minutes": 3,
                "concept_tags": ["limitations", "risk", "education"],
                "content": """
<h2>No guarantees, no predictions</h2>
<p>No signal can tell you the future. A sweep setup can fail, the trend can reverse without warning, or a news event can override technical structure entirely.</p>
<p>The signal does not tell you: "This trade will win." It tells you: "This setup meets the criteria." There is a difference.</p>
<p>Delta One manages this uncertainty with risk controls (stops, position sizing, circuit breakers). As a user, your role is to understand that every signal carries risk. Use the curriculum to learn why the signal matters — not as a reason to gamble.</p>
<div class="key-takeaway">
  <strong>Key takeaway:</strong> Signals are educational, not prophetic. Never trade money you cannot afford to lose.
</div>
""",
            },
            {
                "title": "Paper trading a signal",
                "slug": "paper-trading-a-signal",
                "sort_order": 3,
                "estimated_minutes": 5,
                "concept_tags": ["paper-trading", "simulation", "practice"],
                "content": """
<h2>Learn without risk</h2>
<p>Paper trading means placing simulated trades with fake money. It is how you learn to read signals and manage trades without real financial risk.</p>
<p>To paper trade a Delta One signal:</p>
<ol>
  <li>Open the signal card in the Explorer</li>
  <li>Note the symbol, side, and entry price</li>
  <li>Set a stop-loss based on the educational explanation (the sweep wick + ATR)</li>
  <li>Set a take-profit at the opposite range edge</li>
  <li>Track the trade in a journal — did it work? Why or why not?</li>
</ol>
<p>The goal is not to be right. The goal is to understand why the market behaved the way it did.</p>
<div class="key-takeaway">
  <strong>Key takeaway:</strong> Paper trading builds skill without cost. Track every trade, win or lose, and study the outcome.
</div>
""",
            },
        ],
    },
]


def seed():
    with app.app_context():
        existing = Module.query.count()
        if existing > 0:
            print(f"Database already has {existing} modules. Deleting and re-seeding...")
            Module.query.delete()
            Lesson.query.delete()
            db.session.commit()

        total_lessons = 0
        for mod_data in MODULES:
            lessons_data = mod_data.pop("lessons")
            mod_data.setdefault("is_published", True)
            module = Module(**mod_data)
            db.session.add(module)
            db.session.flush()

            for les_data in lessons_data:
                les_data.setdefault("is_published", True)
                lesson = Lesson(module_id=module.id, **les_data)
                db.session.add(lesson)
                total_lessons += 1

        db.session.commit()
        print(f"Seeded {len(MODULES)} modules with {total_lessons} lessons.")
        print("Done.")


if __name__ == "__main__":
    seed()
