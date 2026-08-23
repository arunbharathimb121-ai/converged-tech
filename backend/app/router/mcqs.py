import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.mcq import create_question, list_questions, submit_answer
from app.database import get_db
from app.schemas import McqQuestionCreate, McqQuestionOut, McqResult, McqSubmission

from app.router.auth import current_user
from app.models import Users

router = APIRouter(prefix="/mcqs", tags=["mcqs"])


@router.post("/questions", response_model=McqQuestionOut, status_code=status.HTTP_201_CREATED)
def add_question(question: McqQuestionCreate, db: Session = Depends(get_db)):
    return format_question(create_question(db, question))


@router.get("/questions", response_model=list[McqQuestionOut])
def get_questions(
    user_id: int | None = None,
    level: str | None = None,
    user: Users = Depends(current_user),
    db: Session = Depends(get_db)
):
    target_user_id = user_id or user.id
    try:
        return [format_question(question) for question in list_questions(db, target_user_id, level)]
    except ValueError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc


@router.post("/submit", response_model=McqResult)
def submit(
    submission: McqSubmission,
    user: Users = Depends(current_user),
    db: Session = Depends(get_db)
):
    target_user_id = submission.user_id or user.id
    try:
        correct, average_marks = submit_answer(
            db,
            user_id=target_user_id,
            question_id=submission.question_id,
            selected_answer=submission.selected_answer
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    return {"correct": correct, "score": 100 if correct else 0, "average_marks": average_marks}


def format_question(question):
    return {
        "id": question.id,
        "domain": question.domain,
        "level": question.level,
        "is_technical": question.is_technical,
        "question": question.question,
        "options": json.loads(question.options),
    }
