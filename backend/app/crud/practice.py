import json
from datetime import datetime
from pathlib import Path
from typing import Optional
from sqlalchemy.orm import Session

from app.crud.streak import update_streak_maintenance
from app.models import Submission, Users
from app.sandbox import execute

BASE_DIR = Path(__file__).resolve().parents[1]
QUESTIONS_DIR = BASE_DIR / "codes"
TESTS_DIR = BASE_DIR / "tests"
selected_question_id: Optional[int] = None


def get_question(question_id: int):
    global selected_question_id

    question_path = QUESTIONS_DIR / f"code{question_id}.json"
    if not question_path.exists():
        raise FileNotFoundError(f"Question {question_id} not found.")

    selected_question_id = question_id
    with question_path.open() as f:
        data = json.load(f)
    return data


def get_test(question_id: str):
    test_path = TESTS_DIR / f"test{question_id}.json"
    if not test_path.exists():
        raise FileNotFoundError(f"Test file test{question_id}.json not found.")
    with test_path.open() as f:
        return json.load(f)


def run_code(
    db: Session,
    code: str,
    lang: str,
    user_id: int,
    submission_date: Optional[datetime] = None,
) -> dict:
    if selected_question_id is None:
        raise ValueError("Select a question before submitting code.")

    user = db.query(Users).filter(Users.id == user_id).first()
    if not user:
        raise ValueError("User not found.")
    if not user.onboarding_completed or user.role != "student" or not user.is_technical:
        raise ValueError("Coding practice is available to technical students only.")

    if db.query(Submission).filter_by(
        user_id=user_id,
        question_id=selected_question_id,
        passed=1,
    ).first():
        return {"result": "You have already submitted a solution for this question."}

    submitted_at = submission_date or datetime.now()
    test_data = get_test(str(selected_question_id))
    tests = test_data["visible"] + test_data["hidden"]
    total = len(tests)

    last_result = {"output": "", "error": None}
    passed_count = 0

    for case in tests:

        input_data = "".join(
            f"{' '.join(map(str, v))}\n"
            if isinstance(v, list)
            else f"{v}\n"
            for v in case["input"].values()
        )

        last_result = execute(
            data=code,
            input_str=input_data,
            lang=lang
        )

        if (
            last_result["output"].strip().lower()
            != str(case["expected"]).strip().lower()
        ):

            submission = Submission(
                user_id=user_id,
                question_id=selected_question_id,
                code=code,
                lan=lang,
                passed=0,
                created_at=submitted_at,
            )

            db.add(submission)
            db.commit()

            return {
                "result": f"Wrong Answer {passed_count}/{total}",
                "output": last_result["output"],
                "error": last_result["error"],
            }

        passed_count += 1

    update_streak_maintenance(
        db,
        user_id=user_id
    )

    submission = Submission(
        user_id=user_id,
        question_id=selected_question_id,
        code=code,
        lan=lang,
        passed=1,
        created_at=submitted_at,
    )

    db.add(submission)
    db.commit()
    db.refresh(submission)

    return {
        "result": f"Correct Answer {passed_count}/{total}",
        "output": last_result["output"],
        "error": last_result["error"],
        "submitted_at": submission.created_at.strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
    }
