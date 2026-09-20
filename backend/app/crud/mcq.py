import json
<<<<<<< HEAD
=======
import logging
from pathlib import Path
>>>>>>> 6d8865c (updation)

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import McqAttempt, McqQuestion, Users

<<<<<<< HEAD

def get_student(db: Session, user_id: int) -> Users:
    user = db.query(Users).filter(Users.id == user_id).first()
    if not user or not user.onboarding_completed or user.role != "student":
        raise ValueError("Student onboarding is required.")
    return user
=======
logger = logging.getLogger("convotech.mcq")
QUIZZES_DIR = Path(__file__).resolve().parents[1] / "quizzes"


def seed_quiz_questions(db: Session) -> dict:
    added = 0
    total = 0
    for filename in ["tech_quiz.json", "non_tech_quiz.json"]:
        file_path = QUIZZES_DIR / filename
        if not file_path.exists():
            continue
        try:
            items = json.loads(file_path.read_text(encoding="utf-8"))
            for item in items:
                total += 1
                existing = db.query(McqQuestion).filter(
                    McqQuestion.question == item["question"]
                ).first()
                if not existing:
                    question = McqQuestion(
                        domain=item["domain"],
                        level=item["level"].lower(),
                        is_technical=bool(item["is_technical"]),
                        question=item["question"],
                        options=json.dumps(item["options"]),
                        correct_answer=item["correct_answer"],
                    )
                    db.add(question)
                    added += 1
        except Exception as exc:
            logger.warning(f"Failed to seed questions from {filename}: {exc}")
    db.commit()
    total_in_db = db.query(McqQuestion).count()
    return {"total_checked": total, "newly_added": added, "total_in_db": total_in_db}


def get_available_domains(db: Session) -> dict:
    tech_domains = db.query(McqQuestion.domain).filter(McqQuestion.is_technical == True).distinct().all()
    non_tech_domains = db.query(McqQuestion.domain).filter(McqQuestion.is_technical == False).distinct().all()
    return {
        "technical": [d[0] for d in tech_domains],
        "non_technical": [d[0] for d in non_tech_domains],
    }
>>>>>>> 6d8865c (updation)


def create_question(db: Session, data) -> McqQuestion:
    question = McqQuestion(
        domain=data.domain,
<<<<<<< HEAD
        level=data.level,
=======
        level=data.level.lower(),
>>>>>>> 6d8865c (updation)
        is_technical=data.is_technical,
        question=data.question,
        options=json.dumps(data.options),
        correct_answer=data.correct_answer,
    )
    db.add(question)
    db.commit()
    db.refresh(question)
    return question


<<<<<<< HEAD
def list_questions(db: Session, user_id: int, level: str | None = None):
    user = get_student(db, user_id)
    domains = json.loads(user.interested_domains)
    query = db.query(McqQuestion).filter(McqQuestion.is_technical == user.is_technical)
    if domains:
        query = query.filter(McqQuestion.domain.in_(domains))
    if level:
        query = query.filter(McqQuestion.level == level)
=======
def list_questions(
    db: Session,
    user_id: int | None = None,
    level: str | None = None,
    domain: str | None = None,
    is_technical: bool | None = None,
):
    query = db.query(McqQuestion)
    track_filter = is_technical
    domains_filter = [domain] if domain and domain.lower() != "all" else None
    explicit_is_technical = is_technical  # caller-supplied value

    if user_id is not None:
        user = db.query(Users).filter(Users.id == user_id).first()
        if user:
            if track_filter is None and user.is_technical is not None:
                track_filter = user.is_technical
           
            if (
                explicit_is_technical is None
                and track_filter == user.is_technical
                and not domains_filter
                and user.interested_domains
            ):
                try:
                    user_domains = json.loads(user.interested_domains)
                    if isinstance(user_domains, list) and user_domains:
                        domains_filter = user_domains
                except Exception:
                    pass

        
        attended_question_ids = (
            db.query(McqAttempt.question_id)
            .filter(McqAttempt.user_id == user_id)
            .distinct()
            .all()
        )
        attended_ids = [q_id[0] for q_id in attended_question_ids]
        if attended_ids:
            query = query.filter(McqQuestion.id.not_in(attended_ids))

    if track_filter is not None:
        query = query.filter(McqQuestion.is_technical == track_filter)

    if level and level.lower() != "all":
        query = query.filter(McqQuestion.level == level.lower())

    if domains_filter:
        query = query.filter(McqQuestion.domain.in_(domains_filter))

>>>>>>> 6d8865c (updation)
    return query.all()


def submit_answer(db: Session, user_id: int, question_id: int, selected_answer: str):
<<<<<<< HEAD
    user = get_student(db, user_id)
    question = db.query(McqQuestion).filter(McqQuestion.id == question_id).first()
    if not question:
        raise FileNotFoundError("MCQ question not found.")
    if question.is_technical != user.is_technical:
        raise ValueError("This question is not available for your track.")

    correct = selected_answer == question.correct_answer
=======
    user = db.query(Users).filter(Users.id == user_id).first()
    if not user:
        raise ValueError("User not found.")
    question = db.query(McqQuestion).filter(McqQuestion.id == question_id).first()
    if not question:
        raise FileNotFoundError("MCQ question not found.")

    correct = selected_answer.strip() == question.correct_answer.strip()
>>>>>>> 6d8865c (updation)
    attempt = McqAttempt(
        user_id=user_id,
        question_id=question_id,
        selected_answer=selected_answer,
        is_correct=correct,
        score=100 if correct else 0,
    )
    db.add(attempt)
    db.flush()
<<<<<<< HEAD
    user.average_marks = db.query(func.avg(McqAttempt.score)).filter(
        McqAttempt.user_id == user_id
    ).scalar() or 0
    db.commit()
    return correct, user.average_marks
=======
    avg = db.query(func.avg(McqAttempt.score)).filter(
        McqAttempt.user_id == user_id
    ).scalar()
    user.average_marks = round(avg or 0.0, 2)
    db.commit()
    return correct, user.average_marks


def get_user_domain_quiz_percentages(db: Session, user_id: int) -> dict:
  
    user = db.query(Users).filter(Users.id == user_id).first()
    interested_domains = []
    if user and user.interested_domains:
        try:
            parsed = json.loads(user.interested_domains)
            if isinstance(parsed, list):
                interested_domains = parsed
        except Exception:
            pass

    if not interested_domains:
       
        attempted_domains = (
            db.query(McqQuestion.domain)
            .join(McqAttempt, McqAttempt.question_id == McqQuestion.id)
            .filter(McqAttempt.user_id == user_id)
            .distinct()
            .all()
        )
        interested_domains = [d[0] for d in attempted_domains]

    percentages = {}
    details = []

    for domain in interested_domains:
        total_qs = db.query(McqQuestion).filter(McqQuestion.domain == domain).count()

        attempts = (
            db.query(McqAttempt)
            .join(McqQuestion, McqAttempt.question_id == McqQuestion.id)
            .filter(McqAttempt.user_id == user_id, McqQuestion.domain == domain)
            .all()
        )
        attended_count = len(attempts)
        correct_count = sum(1 for a in attempts if a.is_correct)

        if attended_count > 0:
            percentage = round((correct_count / attended_count) * 100.0, 2)
        else:
            percentage = 0.0

        percentages[domain] = percentage
        details.append({
            "domain": domain,
            "total_questions": total_qs,
            "attended_questions": attended_count,
            "correct_questions": correct_count,
            "percentage": percentage,
        })

    return {
        "domain_percentages": percentages,
        "domain_details": details,
    }
>>>>>>> 6d8865c (updation)
