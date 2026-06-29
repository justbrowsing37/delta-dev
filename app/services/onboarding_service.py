# onboarding_service.py
# Quiz questions are scenario-based and curriculum-aligned across 5 topic areas:
# Market Mechanics, Technical Analysis, Risk Management, Trade Execution, Market Psychology
# Two questions per area. 10 total. Beginner < 40%, Intermediate 40-69%, Advanced >= 70%.

QUIZ_QUESTIONS = [

    # ── Market Mechanics (Module 0: What is a stock / What moves a price) ──────
    {
        "id": 1,
        "topic": "Market Mechanics",
        "question": (
            "A company just beat earnings expectations by 20%, but its stock dropped 8% "
            "after the announcement. What's the most likely explanation?"
        ),
        "options": [
            "The market made a mistake and will correct upward tomorrow",
            "Investors had already priced in the beat — the result wasn't surprising enough",
            "Short sellers drove the price down artificially",
            "The earnings report must have contained hidden bad news"
        ],
        "answer": 1
    },
    {
        "id": 2,
        "topic": "Market Mechanics",
        "question": (
            "You're looking at the order book for NVDA. The bid side has 50,000 shares "
            "stacked at $120 and the ask side is thin above $121. What does this suggest?"
        ),
        "options": [
            "NVDA is about to crash — high bids mean sellers are ready to dump",
            "There's strong buying interest below $121, which could support the price",
            "The stock is illiquid and you should avoid trading it",
            "Market makers are manipulating the spread"
        ],
        "answer": 1
    },

    # ── Technical Analysis (Module 1 concepts: indicators, price structure) ────
    {
        "id": 3,
        "topic": "Technical Analysis",
        "question": (
            "A stock has been in a downtrend for 3 weeks. Today's RSI reads 28 and price "
            "touches a level that held as support twice in the past. What should you do first?"
        ),
        "options": [
            "Buy immediately — RSI below 30 is always a buy signal",
            "Wait for confirmation — look for a higher low or volume spike before entering",
            "Short it — the downtrend will continue regardless of RSI",
            "RSI is a lagging indicator so ignore it entirely"
        ],
        "answer": 1
    },
    {
        "id": 4,
        "topic": "Technical Analysis",
        "question": (
            "The 50-day moving average crosses below the 200-day moving average on a stock "
            "you're watching. What is this pattern called and what does it signal?"
        ),
        "options": [
            "Golden cross — a bullish reversal signal",
            "Double bottom — price is forming a base",
            "Death cross — a bearish momentum signal indicating trend weakness",
            "Mean reversion — price will return to its average soon"
        ],
        "answer": 2
    },

    # ── Risk Management ─────────────────────────────────────────────────────────
    {
        "id": 5,
        "topic": "Risk Management",
        "question": (
            "You have a $5,000 account and want to risk no more than 2% per trade. "
            "You're entering a stock at $50 with a stop-loss at $47. What's the max number "
            "of shares you should buy?"
        ),
        "options": [
            "100 shares",
            "33 shares",
            "50 shares",
            "10 shares"
        ],
        "answer": 1
    },
    {
        "id": 6,
        "topic": "Risk Management",
        "question": (
            "A trader has a 40% win rate but consistently makes money. How is that possible?"
        ),
        "options": [
            "It's not — a win rate below 50% means you lose money over time",
            "Their average winning trade is large enough relative to their average losing trade",
            "They must be using leverage to offset the losses",
            "Win rate doesn't matter as long as you trade frequently enough"
        ],
        "answer": 1
    },

    # ── Trade Execution ─────────────────────────────────────────────────────────
    {
        "id": 7,
        "topic": "Trade Execution",
        "question": (
            "You want to buy a stock during a fast-moving market open. Which order type "
            "guarantees you get filled but not necessarily at your desired price?"
        ),
        "options": [
            "Limit order",
            "Stop-limit order",
            "Market order",
            "Good-till-canceled order"
        ],
        "answer": 2
    },
    {
        "id": 8,
        "topic": "Trade Execution",
        "question": (
            "You're long 100 shares of a stock at $80. Price drops to your stop at $75 "
            "but gaps down and opens at $68 the next morning. What actually happens?"
        ),
        "options": [
            "Your stop triggers at exactly $75 — that's what stops are for",
            "Your stop triggers at $68 — the open price, because the gap skipped your level",
            "Your stop doesn't trigger because the price gapped past it",
            "Your broker automatically adjusts the stop to the new open price"
        ],
        "answer": 1
    },

    # ── Market Psychology (Module 0: Bulls, Bears and Market Sentiment) ─────────
    {
        "id": 9,
        "topic": "Market Psychology",
        "question": (
            "After a 3-month rally, retail investor sentiment surveys show record bullishness "
            "and media headlines are saying 'stocks only go up.' A contrarian trader would "
            "interpret this as:"
        ),
        "options": [
            "A strong signal to add more long positions — the trend is confirmed",
            "Irrelevant — sentiment indicators don't affect price",
            "A potential warning sign that the easy money has already been made",
            "A reason to switch entirely to bonds"
        ],
        "answer": 2
    },
    {
        "id": 10,
        "topic": "Market Psychology",
        "question": (
            "A trader exits a winning position early out of fear it will reverse, then watches "
            "it run 30% further. The next week, they hold a losing trade hoping it recovers "
            "and take a large loss. Which two biases are at work?"
        ),
        "options": [
            "Confirmation bias and recency bias",
            "Loss aversion and anchoring",
            "Disposition effect and loss aversion",
            "Overconfidence and gambler's fallacy"
        ],
        "answer": 2
    },
]


def score_quiz(answers: dict) -> dict:
    """
    answers: dict of {question_id (str): selected_option_index (int)}
    returns: { score, skill_level, starting_module, label, message, topic_breakdown }
    """
    correct = 0
    topic_results = {}

    for q in QUIZ_QUESTIONS:
        topic = q["topic"]
        user_answer = answers.get(str(q["id"]))
        is_correct = user_answer is not None and int(user_answer) == q["answer"]
        if is_correct:
            correct += 1
        if topic not in topic_results:
            topic_results[topic] = {"correct": 0, "total": 0}
        topic_results[topic]["total"] += 1
        if is_correct:
            topic_results[topic]["correct"] += 1

    percentage = (correct / len(QUIZ_QUESTIONS)) * 100

    if percentage >= 70:
        skill_level = "advanced"
        starting_module = 4
        label = "Advanced Trader"
        message = (
            "Strong across the board. You clearly have real experience. "
            "We're starting you at Module 4 — advanced signals, strategy, and live market application."
        )
    elif percentage >= 40:
        skill_level = "intermediate"
        starting_module = 2
        label = "Intermediate Trader"
        message = (
            "Solid foundation with room to sharpen your edge. "
            "We're starting you at Module 2 — technical analysis, indicators, and reading price action."
        )
    else:
        skill_level = "beginner"
        starting_module = 1
        label = "Beginner Trader"
        message = (
            "Everyone starts here. Delta One is built for this. "
            "We're starting you at Module 1 — market mechanics, how prices move, and building your framework."
        )

    return {
        "correct": correct,
        "total": len(QUIZ_QUESTIONS),
        "percentage": round(percentage),
        "skill_level": skill_level,
        "starting_module": starting_module,
        "label": label,
        "message": message,
        "topic_breakdown": topic_results,
    }


def get_quiz_questions():
    return QUIZ_QUESTIONS
