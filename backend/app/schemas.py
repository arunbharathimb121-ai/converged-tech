from pydantic import BaseModel, ConfigDict
from datetime import datetime, date
from typing import Optional

class Users(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: Optional[int] = None
    name: Optional[str] = None
    dob: Optional[date] = None
    username: str
    password: str
    phone: Optional[str] = None
    career: Optional[str] = None
    org: Optional[str] = None
    bio: Optional[str] = None
    profile_pic: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    tech_stack: Optional[str] = None
    is_technical: Optional[bool] = None
    onboarding_completed: bool = False
    interested_domains: str = "[]"
    average_marks: float = 0

class Posts(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: Optional[int] = None
    username: Optional[str] = None
    image: str
    caption: str
    user_id: int
    date: Optional[datetime] = None

class Likes(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: Optional[int] = None
    user_id: int
    post_id: int

class Comments(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: Optional[int] = None
    user_id: int
    post_id: int
    comment: str
    created_at: Optional[datetime] = None

class Follows(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: Optional[int] = None
    follower_id: int
    following_id: int

class Message(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: Optional[int] = None
    sender_id: int
    receiver_id: int
    message: str
    created_at: Optional[datetime] = None
class RecruiterCreate(BaseModel):
    email: str
    company: Optional[str] = None
    password: str
    rname: Optional[str] = None

class RecruiterOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: str
    company: Optional[str] = None
    rname: Optional[str] = None


class Onboarding(BaseModel):
    name: str
    phone: str
    role: str
    is_technical: Optional[bool] = None
    interested_domains: list[str] = []
    company: Optional[str] = None
    recruiter_name: Optional[str] = None


class GoogleSignIn(BaseModel):
    credential: str


class AuthSession(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    onboarding_required: bool


class AuthUser(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: Optional[str] = None
    username: str
    email: Optional[str] = None
    profile_pic: Optional[str] = None
    role: Optional[str] = None
    is_technical: Optional[bool] = None
    onboarding_completed: bool
    interested_domains: str
    average_marks: float


class McqQuestionCreate(BaseModel):
    domain: str
    level: str
    is_technical: bool
    question: str
    options: list[str]
    correct_answer: str


class McqQuestionOut(BaseModel):
    id: int
    domain: str
    level: str
    is_technical: bool
    question: str
    options: list[str]


class McqSubmission(BaseModel):
    user_id: Optional[int] = None
    question_id: int
    selected_answer: str


class McqResult(BaseModel):
    correct: bool
    score: float
    average_marks: float

class ApplicationCreate(BaseModel):
    id: Optional[int] = None
    applicant_id: Optional[int] = None
    name: Optional[str] = None
    job_title: str
    resume_url: Optional[str] = None
    status: Optional[str] = "pending"
    applied_at: Optional[datetime] = None
    notes: Optional[str] = None

class ApplicationUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None
    resume_url: Optional[str] = None

class ApplicationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    applicant_id: int
    recruiter_id: Optional[int] = None
    job_title: str
    status: str
    resume_url: Optional[str] = None
    applied_at: Optional[datetime] = None
    notes: Optional[str] = None
    applicant_username: Optional[str] = None
    applicant_name: Optional[str] = None
    applicant_email: Optional[str] = None
    is_technical: Optional[bool] = None
    interested_domains: list[str] = []
    average_marks: float = 0
    current_streak: int = 0
    longest_streak: int = 0

class StreakMaintenance(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: int
    user: Optional[str] = None
    current_streak: int
    longest_streak: int
    at_risk: bool
    solved: int = 0
    last_login_date: Optional[date] = None


class StudentApplicationsReport(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    applicant_id: int
    user: Optional[Users] = None
    applications: list[ApplicationOut]
    posts: list[Posts]
    streak: Optional[StreakMaintenance] = None
    average_marks: float = 0
    interested_domains: list[str] = []
    is_technical: Optional[bool] = None

class AnswerSubmission(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: Optional[int] = None
    code: str
    lang: str
    submission_date: Optional[datetime] = None

class SubmitResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    passed: bool
    streak_maintained: StreakMaintenance
