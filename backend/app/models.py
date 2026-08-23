from datetime import datetime
from sqlalchemy import Boolean, String, Integer, Float, Column, Date, Text, DateTime, ForeignKey
from app.database import base

class Users(base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    dob = Column(Date)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    phone = Column(String(30), unique=True, nullable=True)
    career = Column(String)
    org = Column(String)
    bio = Column(Text)
    profile_pic = Column(String)
    email = Column(String)
    resume_url=Column(String)
    role = Column(String, default="student", nullable=False)
    is_technical = Column(Boolean, nullable=True)
    onboarding_completed = Column(Boolean, default=False, nullable=False)
    interested_domains = Column(Text, default="[]", nullable=False)
    average_marks = Column(Float, default=0, nullable=False)
    google_sub = Column(String, unique=True, nullable=True)

class Posts(base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    image = Column(String, nullable=False)
    caption = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    date = Column(DateTime, default=datetime.now)

class Likes(base):
    __tablename__ = "likes"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    post_id = Column(Integer, ForeignKey("posts.id"))

class Comments(base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    post_id = Column(Integer, ForeignKey("posts.id"))
    comment = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now)

class Follows(base):
    __tablename__ = "follows"
    id = Column(Integer, primary_key=True, index=True)
    follower_id = Column(Integer, ForeignKey("users.id"))
    following_id = Column(Integer, ForeignKey("users.id"))

class Message(base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"))
    receiver_id = Column(Integer, ForeignKey("users.id"))
    message = Column(Text)
    created_at = Column(DateTime, default=datetime.now)

class Recruiters(base):
    __tablename__="recruiters"
    id=Column(Integer,primary_key=True,index=True)
    rname=Column(String)
    company=Column(String,nullable=False)
    password=Column(String,nullable=False)
    email=Column(String)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=True)

class JobApplications(base):
    __tablename__ = "job_applications"
    id = Column(Integer, primary_key=True, index=True)
    applicant_id = Column(Integer, ForeignKey("users.id"))
    recruiter_id = Column(Integer, ForeignKey("recruiters.id"))
    job_title = Column(String, nullable=False)
    status = Column(String, default="pending")
    applied_at = Column(DateTime, default=datetime.now)
    notes = Column(Text)
    resume_url = Column(String)

class StreakMaintenance(base):
    __tablename__ = "streak_maintenance"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    current_streak = Column(Integer, default=0, nullable=False)
    longest_streak = Column(Integer, default=0, nullable=False)
    last_login_date = Column(Date, nullable=True)

class Submission(base):
    __tablename__ = "submissions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    question_id = Column(Integer, nullable=False)
    code = Column(Text, nullable=False)
    lan = Column(String, nullable=False)
    passed = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.now)


class McqQuestion(base):
    __tablename__ = "mcq_questions"
    id = Column(Integer, primary_key=True, index=True)
    domain = Column(String, nullable=False)
    level = Column(String, nullable=False)
    is_technical = Column(Boolean, nullable=False)
    question = Column(Text, nullable=False)
    options = Column(Text, nullable=False)
    correct_answer = Column(String, nullable=False)


class McqAttempt(base):
    __tablename__ = "mcq_attempts"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("mcq_questions.id"), nullable=False)
    selected_answer = Column(String, nullable=False)
    is_correct = Column(Boolean, nullable=False)
    score = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
