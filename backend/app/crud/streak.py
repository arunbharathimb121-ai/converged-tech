from datetime import date, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from app.models import StreakMaintenance, Submission, Users

def get_streak_maintenance(db: Session, user_id: int):
    return db.query(StreakMaintenance).filter(StreakMaintenance.user_id == user_id).first()

def create_streak_maintenance(db: Session, user_id: int, current_streak: int = 0, last_login_date: Optional[date] = None):
    streak_maintenance = StreakMaintenance(
        user_id=user_id,
        current_streak=current_streak,
        longest_streak=current_streak,
        last_login_date=last_login_date,
    )
    db.add(streak_maintenance)
    db.commit()
    db.refresh(streak_maintenance)
    return streak_maintenance

def update_streak_maintenance(db: Session, user_id: int):

    today = date.today()

    s = get_streak_maintenance(db, user_id)

    if not s:
        s = create_streak_maintenance(
            db,
            user_id,
            current_streak=1,
            last_login_date=today
        )
        return s

    if s.last_login_date == today:
        return s

    if s.last_login_date == today - timedelta(days=1):
        s.current_streak += 1
    else:
        s.current_streak = 1

    s.longest_streak = max(
        s.longest_streak,
        s.current_streak
    )

    s.last_login_date = today

    db.commit()
    db.refresh(s)

    return s
def streak_report(db: Session, user_id: int):
    s = get_streak_maintenance(db, user_id)
    user = db.query(Users).filter(Users.id == user_id).first()
    if not user:
        return None

    today = date.today()
    solved_today = db.query(Submission).filter(
        Submission.user_id == user_id,
        Submission.created_at >= today,
        Submission.passed == 1,
    ).count()
    if not s:
        return {
            "user_id": user_id,
            "user": user.name,
            "longest_streak": 0,
            "last_login_date": None,
            "at_risk": False,
            "current_streak": 0,
            "solved": 0,
        }
    return {
        "user_id": user_id,
        "user":user.name,
        "at_risk": s.current_streak > 0 and s.last_login_date < today,
        "longest_streak": s.longest_streak,
        "last_login_date": s.last_login_date,
        "current_streak": s.current_streak,
        "solved": solved_today,
    }
        
