import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.mcq import (
    create_question,
    list_questions,
    submit_answer,
    seed_quiz_questions,
    get_available_domains,
    get_user_domain_quiz_percentages,
)
from app.database import get_db
from app.schemas import McqQuestionCreate, McqQuestionOut, McqResult, McqSubmission

from app.router.auth import current_user
from app.models import Users

router = APIRouter(prefix="/mcqs", tags=["mcqs"])


@router.post("/seed")
def seed_questions_endpoint(db: Session = Depends(get_db)):
    return seed_quiz_questions(db)


@router.get("/domains")
def list_domains(db: Session = Depends(get_db)):
    return get_available_domains(db)


@router.get("/domain-percentages")
def get_domain_percentages(
    user: Users = Depends(current_user),
    db: Session = Depends(get_db)
):
    return get_user_domain_quiz_percentages(db, user.id)


@router.post("/questions", response_model=McqQuestionOut, status_code=status.HTTP_201_CREATED)
def add_question(question: McqQuestionCreate, db: Session = Depends(get_db)):
    return format_question(create_question(db, question))


@router.get("/questions", response_model=list[McqQuestionOut])
def get_questions(
    user_id: int | None = None,
    level: str | None = None,
    domain: str | None = None,
    is_technical: bool | None = None,
    user: Users = Depends(current_user),
    db: Session = Depends(get_db)
):
    target_user_id = user.id
    try:
        questions = list_questions(
            db,
            user_id=target_user_id,
            level=level,
            domain=domain,
            is_technical=is_technical,
        )
        return [format_question(q) for q in questions]
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


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
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"correct": correct, "score": 100 if correct else 0, "average_marks": average_marks}


def format_question(question):
    options = question.options
    if isinstance(options, str):
        try:
            options = json.loads(options)
        except Exception:
            options = [options]
    return {
        "id": question.id,
        "domain": question.domain,
        "level": question.level,
        "is_technical": question.is_technical,
        "question": question.question,
        "options": options,
    }
