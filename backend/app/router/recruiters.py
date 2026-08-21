from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status
from app.database import get_db
from app.models import Users
from app.crud.recruiter import (
    get_all,
    create_recruiter,
    get_recruiter,
    delete_recruiter,
    get_job_applications,
    get_job_application,
    get_applications_by_applicant,
    create_job_application,
    update_job_application,
    delete_job_application,
    enrich_application,
    get_student_applications_report,
)
from app.schemas import (
    ApplicationOut,
    RecruiterCreate,
    RecruiterOut,
    ApplicationCreate,
    ApplicationUpdate,
    StudentApplicationsReport,
)
from typing import Optional

router = APIRouter(prefix="/recruiters", tags=["recruiters"])

@router.get("/", response_model=list[RecruiterOut])
def getall(db: Session = Depends(get_db)):
    return get_all(db)

@router.get("/{recruiter_id}", response_model=RecruiterOut)
def getone(recruiter_id: int, db: Session = Depends(get_db)):
    data = get_recruiter(db, recruiter_id)
    if not data:
        raise HTTPException(status_code=404, detail="Recruiter not found")
    return data

@router.post("/", response_model=RecruiterOut, status_code=status.HTTP_201_CREATED)
def addone(recruiter: RecruiterCreate, db: Session = Depends(get_db)):
    return create_recruiter(
        db=db,
        rname=recruiter.rname,
        password=recruiter.password,
        company=recruiter.company,
        email=recruiter.email
    )

@router.delete("/{recruiter_id}")
def removeone(recruiter_id: int, db: Session = Depends(get_db)):
    deleted = delete_recruiter(db, recruiter_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Recruiter not found!")
    return {"detail": "Recruiter deleted successfully"}


@router.post(
    "/{recruiter_id}/applications",
    response_model=ApplicationOut,
    status_code=status.HTTP_201_CREATED
)
def add_application(
    recruiter_id: int,
    application: ApplicationCreate,
    db: Session = Depends(get_db)
):
    recruiter = get_recruiter(db, recruiter_id)
    if not recruiter:
        raise HTTPException(status_code=404, detail="Recruiter not found")

    target_applicant_id = application.applicant_id or application.id
    if not target_applicant_id and application.name:
        user = db.query(Users).filter(Users.name == application.name).first()
        if user:
            target_applicant_id = user.id
        else:
            raise HTTPException(status_code=404, detail=f"User with name '{application.name}' not found")

    if not target_applicant_id:
        raise HTTPException(status_code=400, detail="Must provide applicant_id, id, or name")

    user = db.query(Users).filter(Users.id == target_applicant_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User with ID {target_applicant_id} not found")

    created = create_job_application(
        db=db,
        recruiter_id=recruiter_id,
        applicant_id=target_applicant_id,
        job_title=application.job_title,
        status=application.status,
        resume_url=application.resume_url,
        applied_at=application.applied_at,
        notes=application.notes
    )
    return enrich_application(db, created)

@router.get("/{recruiter_id}/applications", response_model=list[ApplicationOut])
def get_applications(recruiter_id: int, db: Session = Depends(get_db)):
    recruiter = get_recruiter(db, recruiter_id)
    if not recruiter:
        raise HTTPException(status_code=404, detail="Recruiter not found")

    applications = get_job_applications(db, recruiter_id)
    return [enrich_application(db, app) for app in applications]

@router.get("/{recruiter_id}/applications/{application_id}", response_model=ApplicationOut)
def get_application(recruiter_id: int, application_id: int, db: Session = Depends(get_db)):
    application = get_job_application(db, application_id)
    if not application or application.recruiter_id != recruiter_id:
        raise HTTPException(status_code=404, detail="Application not found for this recruiter")
    return enrich_application(db, application)

@router.patch("/{recruiter_id}/applications/{application_id}/status", response_model=ApplicationOut)
def update_application_status_query(
    recruiter_id: int,
    application_id: int,
    status: Optional[str] = None,
    notes: Optional[str] = None,
    db: Session = Depends(get_db)
):
    application = get_job_application(db, application_id)
    if not application or application.recruiter_id != recruiter_id:
        raise HTTPException(status_code=404, detail="Application not found for this recruiter")

    updated = update_job_application(db, application_id, status=status, notes=notes)
    return enrich_application(db, updated)

@router.patch("/{recruiter_id}/applications/{application_id}", response_model=ApplicationOut)
def update_application(
    recruiter_id: int,
    application_id: int,
    update_data: ApplicationUpdate,
    db: Session = Depends(get_db)
):
    application = get_job_application(db, application_id)
    if not application or application.recruiter_id != recruiter_id:
        raise HTTPException(status_code=404, detail="Application not found for this recruiter")

    updated = update_job_application(
        db,
        application_id,
        status=update_data.status,
        notes=update_data.notes,
        resume_url=update_data.resume_url
    )
    return enrich_application(db, updated)

@router.delete("/{recruiter_id}/applications/{application_id}")
def remove_application(recruiter_id: int, application_id: int, db: Session = Depends(get_db)):
    application = get_job_application(db, application_id)
    if not application or application.recruiter_id != recruiter_id:
        raise HTTPException(status_code=404, detail="Application not found for this recruiter")

    delete_job_application(db, application_id)
    return {"detail": "Application deleted successfully"}

@router.get("/applicants/{applicant_id}/applications", response_model=StudentApplicationsReport)
def get_student_applications(applicant_id: int, db: Session = Depends(get_db)):
    return get_student_applications_report(db, applicant_id)
