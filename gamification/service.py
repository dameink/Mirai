from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from db.models import GamificationState, Achievement


XP_PER_LEVEL = 100

ACHIEVEMENTS = {
    "first_step": {
        "title": "First Step",
        "description": "Complete your first activity",
        "icon": "🌱",
    },
    "first_conversation": {
        "title": "Hello, Mirai",
        "description": "Have your first conversation with Mirai",
        "icon": "💬",
    },
    "first_learning": {
        "title": "Learner",
        "description": "Complete your first learning activity",
        "icon": "📚",
    },
    "three_day_streak": {
        "title": "3 Days",
        "description": "Maintain a 3-day streak",
        "icon": "🔥",
    },
    "seven_day_streak": {
        "title": "7 Days",
        "description": "Maintain a 7-day streak",
        "icon": "🔥",
    },
    "goal_getter": {
        "title": "Goal Getter",
        "description": "Complete a daily goal",
        "icon": "🎯",
    },
}


def get_or_create_state(db: Session, user_id: str) -> GamificationState:
    state = (
        db.query(GamificationState)
        .filter(GamificationState.user_id == user_id)
        .first()
    )

    if state is None:
        state = GamificationState(user_id=user_id)
        db.add(state)
        db.commit()
        db.refresh(state)

    return state


def unlock_achievement(
    db: Session,
    user_id: str,
    achievement_id: str,
):
    existing = (
        db.query(Achievement)
        .filter(
            Achievement.user_id == user_id,
            Achievement.achievement_id == achievement_id,
        )
        .first()
    )

    if existing:
        return existing

    if achievement_id not in ACHIEVEMENTS:
        return None

    achievement = Achievement(
        user_id=user_id,
        achievement_id=achievement_id,
    )

    db.add(achievement)
    db.commit()
    db.refresh(achievement)

    return achievement


def add_xp(
    db: Session,
    user_id: str,
    amount: int,
):
    state = get_or_create_state(db, user_id)

    state.xp += amount

    while state.xp >= XP_PER_LEVEL:
        state.xp -= XP_PER_LEVEL
        state.level += 1

    db.commit()
    db.refresh(state)

    return state


def register_activity(
    db: Session,
    user_id: str,
    xp: int = 10,
):
    state = get_or_create_state(db, user_id)

    now = datetime.now(timezone.utc)

    if state.last_activity_at is None:
        state.streak = 1
        unlock_achievement(db, user_id, "first_step")
    else:
        last = state.last_activity_at

        if last.tzinfo is None:
            last = last.replace(tzinfo=timezone.utc)

        last_date = last.date()
        today = now.date()

        if today == last_date:
            pass
        elif today == last_date + timedelta(days=1):
            state.streak += 1
        else:
            state.streak = 1

    state.last_activity_at = now

    state.daily_goal_date = state.daily_goal_date or now

    if state.daily_goal_date.date() != now.date():
        state.daily_goal_date = now
        state.daily_goal_progress = 0

    if state.daily_goal_progress < state.daily_goal_target:
        state.daily_goal_progress += 1

    db.commit()
    db.refresh(state)

    add_xp(db, user_id, xp)

    if state.streak >= 3:
        unlock_achievement(db, user_id, "three_day_streak")

    if state.streak >= 7:
        unlock_achievement(db, user_id, "seven_day_streak")

    if state.daily_goal_progress >= state.daily_goal_target:
        unlock_achievement(db, user_id, "goal_getter")

    return state


def get_gamification_data(db: Session, user_id: str):
    state = get_or_create_state(db, user_id)

    achievements = (
        db.query(Achievement)
        .filter(Achievement.user_id == user_id)
        .all()
    )

    unlocked_ids = {
        achievement.achievement_id
        for achievement in achievements
    }

    return {
        "xp": state.xp,
        "level": state.level,
        "xp_to_next_level": XP_PER_LEVEL - state.xp,
        "streak": state.streak,
        "daily_goal": {
            "target": state.daily_goal_target,
            "progress": state.daily_goal_progress,
            "completed": (
                state.daily_goal_progress
                >= state.daily_goal_target
            ),
        },
        "achievements": [
            {
                "id": achievement_id,
                **data,
                "unlocked": achievement_id in unlocked_ids,
            }
            for achievement_id, data in ACHIEVEMENTS.items()
        ],
    }