from datetime import datetime, timezone

from app.extensions import db
from app.models.module import Module
from app.models.lesson import Lesson
from app.models.progress import UserProgress


class CurriculumService:

    @staticmethod
    def get_published_modules(user_id=None):
        modules = (
            Module.query
            .filter(Module.is_published.is_(True))
            .order_by(Module.sort_order)
            .all()
        )
        result = []
        for m in modules:
            lesson_ids = [l.id for l in m.lessons.all()]
            total = len(lesson_ids)
            completed = 0
            if user_id and lesson_ids:
                completed = (
                    UserProgress.query
                    .filter(
                        UserProgress.user_id == user_id,
                        UserProgress.lesson_id.in_(lesson_ids),
                        UserProgress.status == "completed",
                    )
                    .count()
                )
            result.append({
                "id": m.id,
                "title": m.title,
                "slug": m.slug,
                "description": m.description,
                "icon": m.icon,
                "sort_order": m.sort_order,
                "lesson_count": total,
                "completed_count": completed,
            })
        return result

    @staticmethod
    def get_module_by_slug(slug, user_id=None):
        module = Module.query.filter(
            Module.slug == slug, Module.is_published.is_(True)
        ).first()
        if not module:
            return None

        lessons = (
            Lesson.query
            .filter(Lesson.module_id == module.id, Lesson.is_published.is_(True))
            .order_by(Lesson.sort_order)
            .all()
        )

        completed_ids = set()
        if user_id and lessons:
            rows = (
                UserProgress.query
                .filter(
                    UserProgress.user_id == user_id,
                    UserProgress.lesson_id.in_([l.id for l in lessons]),
                    UserProgress.status == "completed",
                )
                .all()
            )
            completed_ids = {r.lesson_id for r in rows}

        lesson_list = []
        for i, l in enumerate(lessons):
            lesson_list.append({
                "id": l.id,
                "title": l.title,
                "slug": l.slug,
                "sort_order": l.sort_order,
                "estimated_minutes": l.estimated_minutes,
                "concept_tags": l.concept_tags or [],
                "item_type": getattr(l, "item_type", "lesson"),
                "connects_to": getattr(l, "connects_to", []) or [],
                "is_completed": l.id in completed_ids,
            })

        return {
            "id": module.id,
            "title": module.title,
            "slug": module.slug,
            "description": module.description,
            "icon": module.icon,
            "sort_order": module.sort_order,
            "lessons": lesson_list,
        }

    @staticmethod
    def get_lesson(module_slug, lesson_slug, user_id=None):
        module = Module.query.filter(
            Module.slug == module_slug, Module.is_published.is_(True)
        ).first()
        if not module:
            return None

        lesson = (
            Lesson.query
            .filter(
                Lesson.module_id == module.id,
                Lesson.slug == lesson_slug,
                Lesson.is_published.is_(True),
            )
            .first()
        )
        if not lesson:
            return None

        siblings = (
            Lesson.query
            .filter(
                Lesson.module_id == module.id,
                Lesson.is_published.is_(True),
            )
            .order_by(Lesson.sort_order)
            .all()
        )

        current_idx = None
        for i, s in enumerate(siblings):
            if s.id == lesson.id:
                current_idx = i
                break

        prev_lesson = siblings[current_idx - 1] if current_idx and current_idx > 0 else None
        next_lesson = siblings[current_idx + 1] if current_idx is not None and current_idx < len(siblings) - 1 else None

        is_completed = False
        if user_id:
            prog = (
                UserProgress.query
                .filter(
                    UserProgress.user_id == user_id,
                    UserProgress.lesson_id == lesson.id,
                    UserProgress.status == "completed",
                )
                .first()
            )
            is_completed = prog is not None

        return {
            "id": lesson.id,
            "title": lesson.title,
            "slug": lesson.slug,
            "module_slug": module_slug,
            "module_title": module.title,
            "content": lesson.content,
            "content_type": lesson.content_type,
            "estimated_minutes": lesson.estimated_minutes,
            "concept_tags": lesson.concept_tags or [],
            "item_type": getattr(lesson, "item_type", "lesson"),
            "connects_to": getattr(lesson, "connects_to", []) or [],
            "is_completed": is_completed,
            "prev_lesson_slug": prev_lesson.slug if prev_lesson else None,
            "prev_lesson_title": prev_lesson.title if prev_lesson else None,
            "next_lesson_slug": next_lesson.slug if next_lesson else None,
            "next_lesson_title": next_lesson.title if next_lesson else None,
        }

    @staticmethod
    def mark_complete(user_id, lesson_id):
        existing = (
            UserProgress.query
            .filter(
                UserProgress.user_id == user_id,
                UserProgress.lesson_id == lesson_id,
            )
            .first()
        )
        if existing:
            if existing.status != "completed":
                existing.status = "completed"
                existing.completed_at = datetime.now(timezone.utc)
                db.session.commit()
            return existing
        prog = UserProgress(
            user_id=user_id,
            lesson_id=lesson_id,
            status="completed",
            completed_at=datetime.now(timezone.utc),
        )
        db.session.add(prog)
        db.session.commit()
        return prog

    @staticmethod
    def get_progress(user_id, module_id=None):
        q = (
            UserProgress.query
            .join(Lesson, UserProgress.lesson_id == Lesson.id)
            .filter(
                UserProgress.user_id == user_id,
                UserProgress.status == "completed",
                Lesson.is_published.is_(True),
            )
        )
        if module_id:
            q = q.filter(Lesson.module_id == module_id)
            total = Lesson.query.filter(
                Lesson.module_id == module_id,
                Lesson.is_published.is_(True),
            ).count()
        else:
            total = Lesson.query.filter(Lesson.is_published.is_(True)).count()
        completed = q.count()
        return {
            "completed": completed,
            "total": total,
            "percentage": round((completed / total * 100), 1) if total else 0,
        }
