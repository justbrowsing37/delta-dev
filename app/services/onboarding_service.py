QUIZ_QUESTIONS = [
    {
        "id": 1,
        "question": "What does a moving average indicator measure?",
        "options": [
            "The volume of trades in a period",
            "The average price of an asset over a set number of periods",
            "The difference between high and low prices",
            "The number of buyers vs sellers"
        ],
        "answer": 1
    },
    {
        "id": 2,
        "question": "What does RSI stand for?",
        "options": [
            "Relative Strength Index",
            "Rate of Stock Increase",
            "Real Signal Indicator",
            "Risk Score Index"
        ],
        "answer": 0
    },
    {
        "id": 3,
        "question": "What is a 'bull market'?",
        "options": [
            "A market with high volatility",
            "A market trending downward",
            "A market trending upward",
            "A market with low volume"
        ],
        "answer": 2
    },
    {
        "id": 4,
        "question": "What does 'going short' on a stock mean?",
        "options": [
            "Buying a stock expecting it to rise",
            "Holding a stock for a short time",
            "Selling a stock you don't own, expecting the price to fall",
            "Buying a low-priced stock"
        ],
        "answer": 2
    },
    {
        "id": 5,
        "question": "What is a stop-loss order?",
        "options": [
            "An order to buy when price hits a target",
            "An order to automatically sell if price drops to a set level",
            "A limit on how many trades you can make",
            "An order that pauses trading during volatility"
        ],
        "answer": 1
    },
    {
        "id": 6,
        "question": "What does MACD stand for?",
        "options": [
            "Moving Average Convergence Divergence",
            "Market Analysis and Chart Data",
            "Mean Asset Change Detection",
            "Momentum and Cycle Direction"
        ],
        "answer": 0
    },
    {
        "id": 7,
        "question": "What is market capitalization?",
        "options": [
            "The total revenue a company generates annually",
            "The price of one share of stock",
            "The total value of a company's outstanding shares",
            "The maximum price a stock has ever reached"
        ],
        "answer": 2
    },
    {
        "id": 8,
        "question": "What does 'diversification' mean in investing?",
        "options": [
            "Putting all money into the best performing stock",
            "Spreading investments across different assets to reduce risk",
            "Trading in multiple markets simultaneously",
            "Changing your strategy frequently"
        ],
        "answer": 1
    }
]


def score_quiz(answers: dict) -> dict:
    """
    answers: dict of {question_id (str): selected_option_index (int)}
    returns: { score, skill_level, starting_module, label, message }
    """
    correct = 0
    for q in QUIZ_QUESTIONS:
        user_answer = answers.get(str(q["id"]))
        if user_answer is not None and int(user_answer) == q["answer"]:
            correct += 1

    percentage = (correct / len(QUIZ_QUESTIONS)) * 100

    if percentage >= 75:
        skill_level = "advanced"
        starting_module = 4
        label = "Advanced Trader"
        message = "Strong fundamentals. We're starting you at Module 4 — advanced signals and strategy."
    elif percentage >= 40:
        skill_level = "intermediate"
        starting_module = 2
        label = "Intermediate Trader"
        message = "Solid base knowledge. We're starting you at Module 2 — technical analysis."
    else:
        skill_level = "beginner"
        starting_module = 1
        label = "Beginner Trader"
        message = "Everyone starts somewhere. We're starting you at Module 1 — the fundamentals."

    return {
        "correct": correct,
        "total": len(QUIZ_QUESTIONS),
        "percentage": round(percentage),
        "skill_level": skill_level,
        "starting_module": starting_module,
        "label": label,
        "message": message
    }


def get_quiz_questions():
    return QUIZ_QUESTIONS
