from fastapi import APIRouter, Depends, HTTPException
from app.database import get_db
from app.schemas import AnswerSubmission
from app.crud.practice import get_question, run_code
from sqlalchemy.orm import Session

from app.router.auth import current_user
from app.models import Users

router = APIRouter(prefix="/practices", tags=["practices"])


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
    
