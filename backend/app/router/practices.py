from fastapi import APIRouter, Depends, HTTPException
from app.database import get_db
from app.schemas import AnswerSubmission, ProblemStatsOut
from app.crud.practice import get_question, run_code, get_user_problem_stats
from app.crud.mcq import get_user_domain_quiz_percentages
from sqlalchemy.orm import Session

from app.router.auth import current_user
from app.models import Users

router = APIRouter(prefix="/practices", tags=["practices"])


@router.get("/stats", response_model=ProblemStatsOut)
def get_stats(
    user_id: int | None = None,
    user: Users = Depends(current_user),
    db: Session = Depends(get_db),
):
    target_user_id = user_id or user.id
    stats = get_user_problem_stats(db, target_user_id)
    quiz_stats = get_user_domain_quiz_percentages(db, target_user_id)
    return {
        "user_id": target_user_id,
        "solved_problems": stats["solved_problems"],
        "total_problems": stats["total_problems"],
        "highest_month_engaged": stats["highest_month_engaged"],
        "highest_month_count": stats["highest_month_count"],
        "domain_quiz_percentages": quiz_stats["domain_percentages"],
        "domain_quiz_details": quiz_stats["domain_details"],
    }


@router.get("/question")
def get_question_endpoint(question_id: int):
    try:
        question = get_question(question_id)
        return question
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/submit")
def submit_code(
    submission: AnswerSubmission,
    user: Users = Depends(current_user),
    db: Session = Depends(get_db)
):
    target_user_id = submission.user_id or user.id
    try:
        result = run_code(
            db,
            submission.code,
            submission.lang,
            target_user_id,
            submission.submission_date,
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    if result["result"] == "You have already submitted a solution for this question.":
        raise HTTPException(status_code=409, detail=result)

    if "Wrong Answer" in result["result"]:
        raise HTTPException(status_code=400, detail=result)

    return result
