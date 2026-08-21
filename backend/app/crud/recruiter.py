from sqlalchemy.orm import Session
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

def get_applicant_likes(db: Session, applicant_id: int):
    return db.query(Likes).filter(Likes.user_id == applicant_id).all()

def get_applicant_comments(db: Session, applicant_id: int):
    return db.query(Comments).filter(Comments.user_id == applicant_id).all()

def get_applicant_details(db: Session, applicant_id: int):
    user = db.query(Users).filter(Users.id == applicant_id).first()
    if not user:
        return None
    posts = get_applicant_posts(db, applicant_id)
    likes = get_applicant_likes(db, applicant_id)
    comments = get_applicant_comments(db, applicant_id)
    applications = get_applications_by_applicant(db, applicant_id)

    return {
        "user": user,
        "posts": posts,
        "likes": likes,
        "comments": comments,
        "applications": applications
    }

def enrich_application(db: Session, application: JobApplications):
    if not application:
        return None
    if application.applicant_id is not None:
        user = db.query(Users).filter(Users.id == application.applicant_id).first()
        application.applicant_username = user.username if user else None
        application.applicant_name = user.name if user else None
        application.applicant_email = user.email if user else None
    return application

def get_student_applications_report(db: Session, applicant_id: int):
    user = db.query(Users).filter(Users.id == applicant_id).first()
    raw_applications = get_applications_by_applicant(db, applicant_id)
    applications = [enrich_application(db, app) for app in raw_applications]
    posts = get_applicant_posts(db, applicant_id)
    likes = get_applicant_likes(db, applicant_id)
    comments = get_applicant_comments(db, applicant_id)

    return {
        "applicant_id": applicant_id,
        "user": user,
        "applications": applications,
        "posts": posts,
        "likes": likes,
        "comments": comments
    }
