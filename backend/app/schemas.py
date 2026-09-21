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


class LoginRequest(BaseModel):
    identifier: str  # username or email
    password: str


class RegisterRequest(BaseModel):
    username: str
    password: str
    email: Optional[str] = None
    name: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = "student"


class DemoLoginRequest(BaseModel):
    role: str = "student"


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


class AuthSession(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    onboarding_required: bool
    user: Optional[AuthUser] = None


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

class DomainQuizDetail(BaseModel):
    domain: str
    total_questions: int = 0
    attended_questions: int = 0
    correct_questions: int = 0
    percentage: float = 0.0

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
    solved_problems: int = 0
    total_problems: int = 0
    highest_month_engaged: Optional[str] = None
    domain_quiz_percentages: dict[str, float] = {}
    domain_quiz_details: list[DomainQuizDetail] = []

class ProblemStatsOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: int
    solved_problems: int = 0
    total_problems: int = 0
    highest_month_engaged: Optional[str] = "None"
    highest_month_count: int = 0
    domain_quiz_percentages: dict[str, float] = {}
    domain_quiz_details: list[DomainQuizDetail] = []

class StudentApplicationsReport(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    applicant_id: int
    user: Optional[Users] = None
    applications: list[ApplicationOut]
    posts: list[Posts]
    likes: list[Likes] = []
    comments: list[Comments] = []
    solved_problems: int = 0
    total_problems: int = 0
    highest_month_engaged: Optional[str] = None
    highest_month_count: int = 0
    average_marks: float = 0
    interested_domains: list[str] = []
    is_technical: Optional[bool] = None
    domain_quiz_percentages: dict[str, float] = {}
    domain_quiz_details: list[DomainQuizDetail] = []

class AnswerSubmission(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: Optional[int] = None
    code: str
    lang: str
    submission_date: Optional[datetime] = None

class SubmitResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    passed: bool
    solved_problems: Optional[int] = 0
