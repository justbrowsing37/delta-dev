cd ~/delta-one
cat > README.md << 'EOF'
# Delta One

> Trade what the market is actually doing.

Delta One is a two-tier trading intelligence platform built to bring
institutional-grade market analysis to everyday traders — without the
$30,000 price tag.

## What We're Building

**Delta Core** — Free, permanently. A modular learning terminal that
teaches users why markets move, not just when to trade. Lesson pathway,
applied simulations, AI assistant, and a notes system built for
long-term learning.

**Delta Pro** — $20/month. A live multi-pane terminal workspace.
Real-time charts, news and sentiment feed with AI context, and a macro
event overlay built for watching live market events and actually
understanding what you're seeing.

## Strategy Methodology

The engine is built on a 4H liquidity sweep and stop-hunt reversal
model. The core thesis is that when price sweeps beyond a key level and
fails to hold, the breakout was a trap — and a reversal trade is
available in the opposite direction.

Entry decisions layer three confluences:
- 4H range structure built from 1H data
- Breakout and reentry detection on the 5M execution layer
- 50 EMA trend filter to block counter-trend entries

Risk is managed at every layer — ATR-based stops with swing structure
confirmation, a minimum 1.5R reward-to-risk requirement, 2% equity risk
per trade, and account-level circuit breakers that halt trading on
excessive drawdown or consecutive losses.

The system is currently under paper trading validation on Alpaca.

## Status

Active development. Paper trading validation underway.
Projected launch: 2027.

## Built By

Bhanu Sugguna — Founder  
[LinkedIn](https://linkedin.com/in/bhanusugguna)

Company Page
[LinkedIn](https://linkedin.com/company/thedeltaone)