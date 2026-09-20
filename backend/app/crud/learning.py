import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models import Users, McqAttempt, McqQuestion

logger = logging.getLogger("convotech.learning")

BASE_DIR = Path(__file__).resolve().parents[2]
DATASET_DIR = BASE_DIR / "learning_dataset"
if not DATASET_DIR.exists():
    DATASET_DIR = BASE_DIR / "backend" / "app" / "quizzes" / "learning_dataset"

# 15 Domains List
DOMAINS = [
    {"domain_id": "TECH-SD", "domain_name": "Software Development", "domain_type": "Tech"},
    {"domain_id": "TECH-CS", "domain_name": "Cybersecurity", "domain_type": "Tech"},
    {"domain_id": "TECH-AIML", "domain_name": "Artificial Intelligence & Machine Learning", "domain_type": "Tech"},
    {"domain_id": "TECH-DS", "domain_name": "Data Science & Analytics", "domain_type": "Tech"},
    {"domain_id": "TECH-CD", "domain_name": "Cloud Computing & DevOps", "domain_type": "Tech"},
    {"domain_id": "TECH-NET", "domain_name": "Networking & IT Infrastructure", "domain_type": "Tech"},
    {"domain_id": "TECH-UIUX", "domain_name": "UI/UX & Graphic Design", "domain_type": "Tech"},
    {"domain_id": "NONTECH-DM", "domain_name": "Digital Marketing", "domain_type": "Non-Tech"},
    {"domain_id": "NONTECH-CM", "domain_name": "Content Creation & Media", "domain_type": "Non-Tech"},
    {"domain_id": "NONTECH-SBD", "domain_name": "Sales & Business Development", "domain_type": "Non-Tech"},
    {"domain_id": "NONTECH-FA", "domain_name": "Finance & Accounting", "domain_type": "Non-Tech"},
    {"domain_id": "NONTECH-HR", "domain_name": "Human Resources & Recruitment", "domain_type": "Non-Tech"},
    {"domain_id": "NONTECH-OSC", "domain_name": "Operations & Supply Chain", "domain_type": "Non-Tech"},
    {"domain_id": "NONTECH-BM", "domain_name": "Business & Management", "domain_type": "Non-Tech"},
    {"domain_id": "NONTECH-ERT", "domain_name": "Education, Research & Training", "domain_type": "Non-Tech"},
]

LEVEL_TITLES = {
    1: "Level 1: Fundamentals / Introduction",
    2: "Level 2: Basic Concepts",
    3: "Level 3: Core Concepts",
    4: "Level 4: Practical Concepts",
    5: "Level 5: Intermediate Concepts",
    6: "Level 6: Advanced Practical Concepts",
    7: "Level 7: Problem Solving / Applied Knowledge",
    8: "Level 8: Advanced Concepts",
    9: "Level 9: Professional / Industry-Level Knowledge",
    10: "Level 10: Expert / Advanced-Level Knowledge",
}


def load_level_json(level_number: int) -> Dict[str, Any]:
    file_path = DATASET_DIR / f"level{level_number}.json"
    if not file_path.exists():
        # Check secondary location
        sec_path = Path(__file__).resolve().parents[1] / "quizzes" / "learning_dataset" / f"level{level_number}.json"
        if sec_path.exists():
            file_path = sec_path
        else:
            raise FileNotFoundError(f"Level file for level {level_number} not found.")
    return json.loads(file_path.read_text(encoding="utf-8"))


def get_all_domains() -> List[Dict[str, str]]:
    return DOMAINS


def get_all_levels() -> List[Dict[str, Any]]:
    return [
        {"level_number": num, "level_title": title}
        for num, title in LEVEL_TITLES.items()
    ]


def get_domains_for_level(level_number: int) -> Dict[str, Any]:
    data = load_level_json(level_number)
    return {
        "level_number": level_number,
        "level_title": data.get("level_title", LEVEL_TITLES.get(level_number, f"Level {level_number}")),
        "total_domains": len(data.get("domains", [])),
        "domains": [
            {
                "domain_id": d["domain_id"],
                "domain_name": d["domain_name"],
                "domain_type": d["domain_type"],
                "total_modules": len(d.get("modules", [])),
            }
            for d in data.get("domains", [])
        ]
    }


def get_domain_at_level(level_number: int, domain_id: str) -> Dict[str, Any]:
    data = load_level_json(level_number)
    dom_id_clean = domain_id.strip().upper()
    for d in data.get("domains", []):
        if d["domain_id"].upper() == dom_id_clean or d["domain_name"].lower() == domain_id.strip().lower():
            return {
                "level_number": level_number,
                "domain_id": d["domain_id"],
                "domain_name": d["domain_name"],
                "domain_type": d["domain_type"],
                "modules": d.get("modules", []),
            }
    raise KeyError(f"Domain '{domain_id}' not found in level {level_number}.")


def get_modules_for_domain_level(level_number: int, domain_id: str) -> List[Dict[str, Any]]:
    dom_data = get_domain_at_level(level_number, domain_id)
    modules_summary = []
    for m in dom_data.get("modules", []):
        modules_summary.append({
            "module_id": m["module_id"],
            "module_number": m["module_number"],
            "title": m["title"],
            "objective": m.get("objective", ""),
            "total_mcqs": len(m.get("mcqs", []))
        })
    return modules_summary


def get_module_details(level_number: int, domain_id: str, module_id: str) -> Dict[str, Any]:
    dom_data = get_domain_at_level(level_number, domain_id)
    mod_id_clean = module_id.strip().upper()
    for m in dom_data.get("modules", []):
        if m["module_id"].upper() == mod_id_clean or str(m.get("module_number")) == module_id:
            # Mask out correct_answer and explanation for initial student view
            sanitized_mcqs = []
            for mcq in m.get("mcqs", []):
                sanitized_mcqs.append({
                    "mcq_id": mcq["mcq_id"],
                    "question": mcq["question"],
                    "options": mcq["options"],
                })
            return {
                "domain_id": dom_data["domain_id"],
                "domain_name": dom_data["domain_name"],
                "level_number": level_number,
                "module_id": m["module_id"],
                "module_number": m["module_number"],
                "title": m["title"],
                "objective": m.get("objective", ""),
                "explanation": m.get("explanation", ""),
                "key_points": m.get("key_points", []),
                "examples": m.get("examples", []),
                "important_terms": m.get("important_terms", []),
                "mcqs": sanitized_mcqs,
            }
    raise KeyError(f"Module '{module_id}' not found in domain '{domain_id}' at level {level_number}.")


def grade_quiz_submission(
    level_number: int,
    domain_id: str,
    module_id: str,
    answers: Dict[str, str],
    user_id: Optional[int] = None,
    db: Optional[Session] = None
) -> Dict[str, Any]:
    dom_data = get_domain_at_level(level_number, domain_id)
    mod_id_clean = module_id.strip().upper()
    target_mod = None
    for m in dom_data.get("modules", []):
        if m["module_id"].upper() == mod_id_clean or str(m.get("module_number")) == module_id:
            target_mod = m
            break

    if not target_mod:
        raise KeyError(f"Module '{module_id}' not found.")

    mcqs = target_mod.get("mcqs", [])
    total_q = len(mcqs)
    correct_count = 0
    results = []

    for mcq in mcqs:
        q_id = mcq["mcq_id"]
        correct_ans = mcq.get("correct_answer", "").strip().upper()
        selected_ans = answers.get(q_id, "").strip().upper()
        is_corr = (selected_ans == correct_ans)
        if is_corr:
            correct_count += 1

        results.append({
            "mcq_id": q_id,
            "question": mcq["question"],
            "selected_answer": selected_ans,
            "correct_answer": correct_ans,
            "is_correct": is_corr,
            "explanation": mcq.get("explanation", "")
        })

    wrong_count = total_q - correct_count
    score_pct = round((correct_count / total_q * 100) if total_q > 0 else 0, 1)

    # Optional DB sync for logged-in user
    if user_id and db:
        try:
            user = db.query(Users).filter(Users.id == user_id).first()
            if user:
                # Update user's aggregate average marks
                curr_avg = user.average_marks or 0.0
                user.average_marks = round((curr_avg * 0.8) + (score_pct * 0.2), 2)
                db.commit()
        except Exception as e:
            logger.warning(f"Could not update user average marks: {e}")

    return {
        "domain_id": dom_data["domain_id"],
        "domain_name": dom_data["domain_name"],
        "level_number": level_number,
        "module_id": target_mod["module_id"],
        "total_questions": total_q,
        "correct": correct_count,
        "wrong": wrong_count,
        "score": score_pct,
        "results": results
    }
