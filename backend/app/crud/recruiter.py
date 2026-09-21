from sqlalchemy.orm import Session
import json

from app.crud.practice import get_user_problem_stats
from app.crud.mcq import get_user_domain_quiz_percentages
from app.models import Recruiters, JobApplications, Users, Posts, Likes, Comments
from datetime import datetime
from typing import Optional

def get_all(db: Session):
    return db.query(Recruiters).all()

def get_recruiter(db: Session, id: int):
    return db.query(Recruiters).filter(Recruiters.id == id).first()

def create_recruiter(
    db: Session,
    rname: str,
    company: str,
    password: str,
    email: str,
    id: Optional[int] = None,
):
    kwargs = {
        "rname": rname,
        "company": company,
        "password": password,
        "email": email
    }
    if id is not None:
        kwargs["id"] = id

    recruiter = Recruiters(**kwargs)
    db.add(recruiter)
    db.commit()
    db.refresh(recruiter)
    return recruiter

def delete_recruiter(db: Session, id: int):
    recruiter = db.query(Recruiters).filter(Recruiters.id == id).first()
    if recruiter:
        db.delete(recruiter)
        db.commit()
    return recruiter

def get_job_applications(db: Session, recruiter_id: int):
    return db.query(JobApplications).filter(JobApplications.recruiter_id == recruiter_id).all()

def get_job_application(db: Session, application_id: int):
    return db.query(JobApplications).filter(JobApplications.id == application_id).first()

def get_applications_by_applicant(db: Session, applicant_id: int):
    return db.query(JobApplications).filter(JobApplications.applicant_id == applicant_id).all()

def create_job_application(
    db: Session,
    recruiter_id: int,
    applicant_id: int,
    job_title: str,
    status: Optional[str] = "pending",
    resume_url: Optional[str] = None,
    applied_at: Optional[datetime] = None,
    notes: Optional[str] = None,
):
    application = JobApplications(
        recruiter_id=recruiter_id,
        applicant_id=applicant_id,
        job_title=job_title,
        status=status or "pending",
        resume_url=resume_url,
        applied_at=applied_at or datetime.now(),
        notes=notes
    )

    db.add(application)
    db.commit()
    db.refresh(application)
    return application  

def update_job_application(
    db: Session,
    application_id: int,
    status: Optional[str] = None,
    notes: Optional[str] = None,
    resume_url: Optional[str] = None,
):
    application = db.query(JobApplications).filter(JobApplications.id == application_id).first()
    if not application:
        return None

    if status is not None:
        application.status = status
    if notes is not None:
        application.notes = notes
    if resume_url is not None:
        application.resume_url = resume_url

    db.commit()
    db.refresh(application)
    return application  

def delete_job_application(db: Session, application_id: int):
    application = db.query(JobApplications).filter(JobApplications.id == application_id).first()
    if application:
        db.delete(application)
        db.commit()
    return application

def get_applicant_posts(db: Session, applicant_id: int):
    return db.query(Posts).filter(Posts.user_id == applicant_id).all()


def get_applicant_details(db: Session, applicant_id: int):
    user = db.query(Users).filter(Users.id == applicant_id).first()
    if not user:
        return None
    posts = get_applicant_posts(db, applicant_id)
    applications = get_applications_by_applicant(db, applicant_id)

    return {
        "user": user,
        "posts": posts,
        "applications": applications
    }

def enrich_application(db: Session, application: JobApplications):
    if not application:
        return None
    if application.applicant_id is not None:
        user = db.query(Users).filter(Users.id == application.applicant_id).first()
        if user:
            application.applicant_username = user.username
            application.applicant_name = user.name
            application.applicant_email = user.email
            application.is_technical = user.is_technical
            application.average_marks = user.average_marks or 0.0
            try:
                application.interested_domains = json.loads(user.interested_domains) if user.interested_domains else []
            except Exception:
                application.interested_domains = []
            
            stats = get_user_problem_stats(db, user.id)
            quiz_stats = get_user_domain_quiz_percentages(db, user.id)
            application.solved_problems = stats["solved_problems"]
            application.total_problems = stats["total_problems"]
            application.highest_month_engaged = stats["highest_month_engaged"]
            application.domain_quiz_details = quiz_stats["domain_details"]
            application.domain_quiz_percentages = quiz_stats["domain_percentages"]
            if not application.resume_url and getattr(user, "resume_url", None):
                application.resume_url = user.resume_url
    return application

def get_student_applications_report(db: Session, applicant_id: int):
    user = db.query(Users).filter(Users.id == applicant_id, Users.role == "student").first()
    if not user:
        return None

    raw_applications = get_applications_by_applicant(db, applicant_id)
    applications = [enrich_application(db, app) for app in raw_applications]
    posts = get_applicant_posts(db, applicant_id)
    likes = db.query(Likes).filter(Likes.user_id == applicant_id).all()
    comments = db.query(Comments).filter(Comments.user_id == applicant_id).all()

    try:
        domains = json.loads(user.interested_domains) if user.interested_domains else []
    except Exception:
        domains = []

    stats = get_user_problem_stats(db, applicant_id)
    quiz_stats = get_user_domain_quiz_percentages(db, applicant_id)

    return {
        "applicant_id": applicant_id,
        "user": user,
        "applications": applications,
        "posts": posts,
        "likes": likes,
        "comments": comments,
        "solved_problems": stats["solved_problems"],
        "total_problems": stats["total_problems"],
        "highest_month_engaged": stats["highest_month_engaged"],
        "highest_month_count": stats["highest_month_count"],
        "average_marks": user.average_marks,
        "interested_domains": domains,
        "is_technical": user.is_technical,
        "domain_quiz_percentages": quiz_stats["domain_percentages"],
        "domain_quiz_details": quiz_stats["domain_details"],
    }
