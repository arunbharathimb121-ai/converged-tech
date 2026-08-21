import os
import sys
import pytest
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import base, get_db
from app.main import app
from app.crud import user as crud_user
from app.crud import post as crud_post
from app.crud import like as crud_like
from app.crud import comment as crud_comment
from app.crud import follow as crud_follow
from app.crud import message as crud_message
from app.crud import recruiter as crud_recruiter

from sqlalchemy.pool import StaticPool

# Setup SQLite in-memory test database
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def setup_db():
    base.metadata.create_all(bind=engine)
    yield
    base.metadata.drop_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    if "text/html" in response.headers.get("content-type", ""):
        assert "<title>ConvoTech" in response.text
    else:
        assert response.json()["status"] == "online"

    status_res = client.get("/api-status")
    assert status_res.status_code == 200
    assert status_res.json()["status"] == "online"


def test_user_crud_and_endpoints():
    user_data = {
        "name": "Alice Developer",
        "dob": "1995-05-15",
        "username": "alice",
        "password": "secretpassword",
        "phone": "+1234567890",
        "career": "Software Engineer",
        "org": "TechCorp",
        "bio": "Coding enthusiast",
        "profile_pic": "https://example.com/pic.jpg",
        "email": "alice@example.com"
    }
    # Create User
    res = client.post("/users/", json=user_data)
    assert res.status_code == 201
    created = res.json()
    assert created["username"] == "alice"
    user_id = created["id"]

    # Get All Users
    res = client.get("/users/")
    assert res.status_code == 200
    users = res.json()
    assert len(users) == 1

    # Get Single User
    res = client.get(f"/users/{user_id}")
    assert res.status_code == 200
    assert res.json()["name"] == "Alice Developer"

    # Non-existent User
    res = client.get("/users/999")
    assert res.status_code == 404

    # Delete User
    res = client.delete(f"/users/{user_id}")
    assert res.status_code == 200

    # Verify Deletion
    res = client.get(f"/users/{user_id}")
    assert res.status_code == 404

def test_post_crud_and_endpoints():
    db = TestingSessionLocal()
    # Create user for foreign key
    u = crud_user.create_user(
        db=db, username="bob", password="pw", phone="+1987654321", name="Bob"
    )
    
    post_data = {
        "username": "bob",
        "image": "https://example.com/image.png",
        "caption": "Hello world post!",
        "user_id": u.id
    }
    res = client.post("/posts/", json=post_data)
    assert res.status_code == 201
    created_post = res.json()
    assert created_post["caption"] == "Hello world post!"
    post_id = created_post["id"]

    res = client.get(f"/posts/{post_id}")
    assert res.status_code == 200
    assert res.json()["image"] == "https://example.com/image.png"

    res = client.get("/posts/")
    assert res.status_code == 200
    assert len(res.json()) == 1

    res = client.delete(f"/posts/{post_id}")
    assert res.status_code == 200

def test_image_upload_endpoints():
    db = TestingSessionLocal()
    u = crud_user.create_user(db=db, username="uploader", password="pw", phone="+1555000111", name="Uploader")

    # 1. Test standalone image upload endpoint
    file_data = {"file": ("test.png", b"fake binary image data", "image/png")}
    res = client.post("/posts/upload-image/", files=file_data)
    assert res.status_code == 200
    upload_res = res.json()
    assert "image_url" in upload_res
    assert upload_res["image_url"].startswith("/uploads/")

    # 2. Test create post with image file upload
    form_data = {
        "user_id": u.id,
        "username": "uploader",
        "caption": "Uploaded from local document!"
    }
    file_data2 = {"file": ("document_photo.jpg", b"fake jpeg image data", "image/jpeg")}
    res = client.post("/posts/with-image", data=form_data, files=file_data2)
    assert res.status_code == 201
    post_res = res.json()
    assert post_res["caption"] == "Uploaded from local document!"
    assert post_res["image"].startswith("/uploads/")


def test_likes_crud_and_endpoints():
    db = TestingSessionLocal()
    u = crud_user.create_user(db=db, username="charlie", password="pw", phone="+1112223334")
    p = crud_post.create_post(db=db, image="img.jpg", caption="cap", user_id=u.id)

    like_data = {"user_id": u.id, "post_id": p.id}
    res = client.post("/likes/", json=like_data)
    assert res.status_code == 201
    like_id = res.json()["id"]

    res = client.get(f"/likes/{like_id}")
    assert res.status_code == 200

    res = client.delete(f"/likes/{like_id}")
    assert res.status_code == 200

def test_comments_crud_and_endpoints():
    db = TestingSessionLocal()
    u = crud_user.create_user(db=db, username="david", password="pw", phone="+4445556667")
    p = crud_post.create_post(db=db, image="img.jpg", caption="cap", user_id=u.id)

    comment_data = {"user_id": u.id, "post_id": p.id, "comment": "Great post!"}
    res = client.post("/comments/", json=comment_data)
    assert res.status_code == 201
    comment_id = res.json()["id"]

    res = client.get(f"/comments/{comment_id}")
    assert res.status_code == 200
    assert res.json()["comment"] == "Great post!"

    res = client.delete(f"/comments/{comment_id}")
    assert res.status_code == 200

def test_follows_crud_and_endpoints():
    db = TestingSessionLocal()
    u1 = crud_user.create_user(db=db, username="user1", password="pw", phone="+1001")
    u2 = crud_user.create_user(db=db, username="user2", password="pw", phone="+1002")

    follow_data = {"follower_id": u1.id, "following_id": u2.id}
    res = client.post("/follows/", json=follow_data)
    assert res.status_code == 201
    follow_id = res.json()["id"]

    res = client.get(f"/follows/{follow_id}")
    assert res.status_code == 200
    assert res.json()["follower_id"] == u1.id
    assert res.json()["following_id"] == u2.id

    res = client.delete(f"/follows/{follow_id}")
    assert res.status_code == 200

def test_messages_crud_and_endpoints():
    db = TestingSessionLocal()
    u1 = crud_user.create_user(db=db, username="sender", password="pw", phone="+2001")
    u2 = crud_user.create_user(db=db, username="receiver", password="pw", phone="+2002")

    msg_data = {"sender_id": u1.id, "receiver_id": u2.id, "message": "Hey there!"}
    res = client.post("/messages/", json=msg_data)
    assert res.status_code == 201
    msg_id = res.json()["id"]

    res = client.get(f"/messages/{msg_id}")
    assert res.status_code == 200
    assert res.json()["message"] == "Hey there!"

    res = client.delete(f"/messages/{msg_id}")
    assert res.status_code == 200

def test_recruiter_crud_and_endpoints():
    recruiter_data = {
        "email": "recruiter@techcorp.com",
        "company": "TechCorp Inc",
        "password": "recruiterpass",
        "rname": "Jane HR"
    }
    # Create Recruiter
    res = client.post("/recruiters/", json=recruiter_data)
    assert res.status_code == 201
    created = res.json()
    assert created["company"] == "TechCorp Inc"
    assert created["rname"] == "Jane HR"
    recruiter_id = created["id"]

    # Get All Recruiters
    res = client.get("/recruiters/")
    assert res.status_code == 200
    assert len(res.json()) >= 1

    # Get Single Recruiter
    res = client.get(f"/recruiters/{recruiter_id}")
    assert res.status_code == 200
    assert res.json()["email"] == "recruiter@techcorp.com"

    # Delete Recruiter
    res = client.delete(f"/recruiters/{recruiter_id}")
    assert res.status_code == 200

    # Verify Deletion
    res = client.get(f"/recruiters/{recruiter_id}")
    assert res.status_code == 404

def test_job_application_and_applicant_details():
    db = TestingSessionLocal()
    # Create student (user)
    student = crud_user.create_user(
        db=db,
        username="student_applicant",
        password="password123",
        phone="+9998887776",
        name="Student Applicant",
        email="student@university.edu"
    )
    # Create post, like, comment for student
    post = crud_post.create_post(
        db=db,
        image="portfolio.jpg",
        caption="My ML Project",
        user_id=student.id,
        username=student.username
    )
    like = crud_like.create_like(db=db, user_id=student.id, post_id=post.id)
    comment = crud_comment.create_comment(db=db, user_id=student.id, post_id=post.id, comment="Nice work!")

    # Create recruiter
    recruiter = crud_recruiter.create_recruiter(
        db=db,
        rname="Hiring Manager",
        company="AI Labs",
        password="pass",
        email="hr@ailabs.com"
    )

    # Student applies to recruiter
    app_data = {
        "applicant_id": student.id,
        "job_title": "Backend AI Developer",
        "resume_url": "https://example.com/resume.pdf",
        "status": "pending",
        "notes": "Eager to contribute!"
    }
    res = client.post(f"/recruiters/{recruiter.id}/applications", json=app_data)
    assert res.status_code == 201
    created_app = res.json()
    assert created_app["job_title"] == "Backend AI Developer"
    assert created_app["status"] == "pending"
    assert created_app["resume_url"] == "https://example.com/resume.pdf"
    app_id = created_app["id"]

    # Recruiter views applications
    res = client.get(f"/recruiters/{recruiter.id}/applications")
    assert res.status_code == 200
    apps = res.json()
    assert len(apps) == 1
    assert apps[0]["id"] == app_id

    # Recruiter gets specific application
    res = client.get(f"/recruiters/{recruiter.id}/applications/{app_id}")
    assert res.status_code == 200
    assert res.json()["job_title"] == "Backend AI Developer"

    # Recruiter updates application status and notes
    patch_data = {"status": "interview_scheduled", "notes": "Interview set for Monday"}
    res = client.patch(f"/recruiters/{recruiter.id}/applications/{app_id}", json=patch_data)
    assert res.status_code == 200
    assert res.json()["status"] == "interview_scheduled"
    assert res.json()["notes"] == "Interview set for Monday"

    # Student views their submitted applications (and activity report)
    res = client.get(f"/recruiters/applicants/{student.id}/applications")
    assert res.status_code == 200
    report = res.json()
    assert len(report["applications"]) == 1
    assert len(report["posts"]) == 1
    assert len(report["likes"]) == 1
    assert len(report["comments"]) == 1

    # Recruiter deletes/removes job application
    res = client.delete(f"/recruiters/{recruiter.id}/applications/{app_id}")
    assert res.status_code == 200
    assert res.json()["detail"] == "Application deleted successfully"

    # Verify application removed
    res = client.get(f"/recruiters/{recruiter.id}/applications/{app_id}")
    assert res.status_code == 404

def test_apply_by_id_or_name_and_student_applications():
    db = TestingSessionLocal()
    user = crud_user.create_user(
        db=db,
        username="jane_applicant",
        name="Jane Applicant",
        password="password",
        phone="+1234999",
        email="jane@example.com"
    )
    post = crud_post.create_post(
        db=db,
        image="design.png",
        caption="My UI Design Portfolio",
        user_id=user.id,
        username=user.username
    )
    like = crud_like.create_like(db=db, user_id=user.id, post_id=post.id)
    comment = crud_comment.create_comment(db=db, user_id=user.id, post_id=post.id, comment="Awesome design!")

    recruiter = crud_recruiter.create_recruiter(
        db=db,
        rname="Tech Recruiter",
        company="DesignCorp",
        password="pass",
        email="recruiter@designcorp.com"
    )

    # 1. Apply passing 'id' instead of 'applicant_id'
    app_data_1 = {
        "id": user.id,
        "job_title": "UI/UX Designer",
        "notes": "Applying with user id"
    }
    res = client.post(f"/recruiters/{recruiter.id}/applications", json=app_data_1)
    assert res.status_code == 201
    body_1 = res.json()
    assert body_1["applicant_id"] == user.id
    assert body_1["applicant_username"] == "jane_applicant"
    assert body_1["applicant_name"] == "Jane Applicant"

    # 2. Apply passing 'name'
    app_data_2 = {
        "name": "Jane Applicant",
        "job_title": "Product Designer",
        "notes": "Applying with name"
    }
    res = client.post(f"/recruiters/{recruiter.id}/applications", json=app_data_2)
    assert res.status_code == 201
    body_2 = res.json()
    assert body_2["applicant_id"] == user.id

    # 3. Get Student Applications Report (/recruiters/applicants/{applicant_id}/applications)
    res = client.get(f"/recruiters/applicants/{user.id}/applications")
    assert res.status_code == 200
    report = res.json()
    assert report["applicant_id"] == user.id
    assert report["user"]["username"] == "jane_applicant"
    assert len(report["applications"]) == 2
    assert len(report["posts"]) == 1
    assert report["posts"][0]["caption"] == "My UI Design Portfolio"
    assert len(report["likes"]) == 1
    assert len(report["comments"]) == 1


