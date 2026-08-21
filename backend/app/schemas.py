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
    phone: str
    career: Optional[str] = None
    org: Optional[str] = None
    bio: Optional[str] = None
    profile_pic: Optional[str] = None
    email: Optional[str] = None

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

class StudentApplicationsReport(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    applicant_id: int
    user: Optional[Users] = None
    applications: list[ApplicationOut]
    posts: list[Posts]
    likes: list[Likes]
    comments: list[Comments]

User = Users
Post = Posts
Like = Likes
Comment = Comments
Follow = Follows
RecruiterCreate = RecruiterCreate
RecruiterOut = RecruiterOut
ApplicationCreate = ApplicationCreate
ApplicationUpdate = ApplicationUpdate
ApplicationOut = ApplicationOut
StudentApplicationsReport = StudentApplicationsReport







