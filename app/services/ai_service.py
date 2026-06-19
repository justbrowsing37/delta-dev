from datetime import datetime, timezone
from flask import current_app
import groq

from app.extensions import db
from app.models.ai_interaction import AiInteraction


class RateLimitExceeded(Exception):
    def __init__(self, limit: int):
        self.limit = limit
        super().__init__(f"Daily limit of {limit} reached")


FALLBACK_RESPONSE = (
    "The AI assistant is temporarily unavailable. "
    "Please try again in a moment."
)


class AiService:

    @classmethod
    def ask(cls, user, message: str) -> str:
        cls._check_rate_limit(user)

        system_prompt = cls._build_system_prompt()

        api_key = current_app.config["GROQ_API_KEY"]
        model = current_app.config["GROQ_MODEL"]

        if not api_key:
            return FALLBACK_RESPONSE

        client = groq.Groq(api_key=api_key)

        try:
            completion = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message},
                ],
                max_tokens=350,
                temperature=0.7,
            )
        except Exception:
            current_app.logger.exception("Groq API call failed")
            return FALLBACK_RESPONSE

        response_text = completion.choices[0].message.content or ""
        tokens_used = completion.usage.total_tokens if completion.usage else 0

        record = AiInteraction(
            user_id=user.id,
            message=message,
            response=response_text,
            tokens_used=tokens_used,
            model_name=model,
            tier=user.tier,
        )
        db.session.add(record)
        db.session.commit()

        return response_text

    @classmethod
    def get_usage_today(cls, user) -> int:
        today_start = datetime.now(timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        return (
            AiInteraction.query
            .filter(
                AiInteraction.user_id == user.id,
                AiInteraction.created_at >= today_start,
            )
            .count()
        )

    @classmethod
    def _build_system_prompt(cls) -> str:
        return (
            "You are Delta, an educational assistant for Delta One, "
            "a market learning platform. Your job is to help users "
            "understand why markets move, how to read signals, and "
            "how the sweep strategy works.\n\n"
            "You are NOT a financial advisor. You must NEVER recommend "
            "specific trades, specific entry or exit prices, or specific "
            "position sizes. If a user asks for direct trade advice, "
            "acknowledge their question, explain that Delta One is a "
            "learning tool rather than an advisory service, and redirect "
            "the conversation toward the educational concept underlying "
            "the question.\n\n"
            "Keep responses concise, structured in plain English, and "
            "appropriate for someone who is new to markets but willing "
            "to learn properly. Do not exceed 350 tokens per response."
        )

    @classmethod
    def _check_rate_limit(cls, user):
        if user.tier == "pro":
            limit = current_app.config["AI_DAILY_LIMIT_PRO"]
        else:
            limit = current_app.config["AI_DAILY_LIMIT_FREE"]

        if limit == -1:
            return

        today_start = datetime.now(timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        count = (
            AiInteraction.query
            .filter(
                AiInteraction.user_id == user.id,
                AiInteraction.created_at >= today_start,
            )
            .count()
        )

        if count >= limit:
            raise RateLimitExceeded(limit)
