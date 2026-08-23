import json

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import McqAttempt, McqQuestion, Users


def get_student(db: Session, user_id: int) -> Users:
    user = db.query(Users).filter(Users.id == user_id).first()
    if not user or not user.onboarding_completed or user.role != "student":
        raise ValueError("Student onboarding is required.")
    return user


def create_question(db: Session, data) -> McqQuestion:
    question = McqQuestion(
        domain=data.domain,
        level=data.level,
        is_technical=data.is_technical,
        question=data.question,
        options=json.dumps(data.options),
        correct_answer=data.correct_answer,
    )
    db.add(question)
    db.commit()
    db.refresh(question)
    return question


def list_questions(db: Session, user_id: int, level: str | None = None):
    user = get_student(db, user_id)
    domains = json.loads(user.interested_domains)
    query = db.query(McqQuestion).filter(McqQuestion.is_technical == user.is_technical)
    if domains:
        query = query.filter(McqQuestion.domain.in_(domains))
    if level:
        query = query.filter(McqQuestion.level == level)
    return query.all()


def submit_answer(db: Session, user_id: int, question_id: int, selected_answer: str):
    user = get_student(db, user_id)
    question = db.query(McqQuestion).filter(McqQuestion.id == question_id).first()
    if not question:
        raise FileNotFoundError("MCQ question not found.")
    if question.is_technical != user.is_technical:
        raise ValueError("This question is not available for your track.")

    correct = selected_answer == question.correct_answer
    attempt = McqAttempt(
        user_id=user_id,
        question_id=question_id,
        selected_answer=selected_answer,
        is_correct=correct,
        score=100 if correct else 0,
    )
    db.add(attempt)
    db.flush()
    user.average_marks = db.query(func.avg(McqAttempt.score)).filter(
        McqAttempt.user_id == user_id
    ).scalar() or 0
    db.commit()
    return correct, user.average_marks
