from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.crud.streak import streak_report
from app.database import get_db
from app.models import Users
from app.schemas import StreakMaintenance

from app.router.auth import current_user

router = APIRouter(prefix="/streaks", tags=["streaks"])


@router.get("/report", response_model=StreakMaintenance)
def get_streak_report(
    user_id: int | None = None,
    user: Users = Depends(current_user),
    db: Session = Depends(get_db),
):
    target_user = db.query(Users).filter(Users.id == (user_id or user.id)).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    if not target_user.onboarding_completed or target_user.role != "student" or not target_user.is_technical:
        raise HTTPException(status_code=403, detail="Streaks are available to technical students only")

    report = streak_report(db, user_id=target_user.id)
    if report is None:
        raise HTTPException(status_code=404, detail="User not found")
    return report
