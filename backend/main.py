import os
from typing import List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel

from backend import database, models, schemas, crud, algorithms, ai_service, seed_data


# --- Lifespan Context Manager for App Startup/Shutdown ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables if they do not exist and seed initial dataset
    models.Base.metadata.create_all(bind=database.engine)
    db = database.SessionLocal()
    try:
        seed_data.seed_if_empty(db)
    finally:
        db.close()
    yield
    # Shutdown logic (if any)


app = FastAPI(
    title="StudyTrack API — Unified Study Management & Enablement Platform",
    description="Backend service for Myntra Trainee Enablement containing Roster CRUD, Algorithms Engine, and AI Assistant.",
    version="1.0.0",
    lifespan=lifespan
)

# --- CORS Configuration ---
# Configured explicitly without wildcard "*" per requirement.
ALLOWED_ORIGINS = [
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Helper to convert Student ORM to dict ---
def _student_to_dict(s: models.Student) -> dict:
    return {
        "id": s.id,
        "name": s.name,
        "email": s.email,
        "age": s.age
    }


# ==========================================
# PART 1: CORE ROSTER CRUD ENDPOINTS
# ==========================================

@app.post("/students/", response_model=schemas.StudentResponse, status_code=status.HTTP_201_CREATED, tags=["Students"])
def create_student(student: schemas.StudentCreate, db: Session = Depends(database.get_db)):
    try:
        return crud.create_student(db, student)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A student with this email address already exists."
        )


@app.get("/students/", response_model=List[schemas.StudentResponse], tags=["Students"])
def list_students(min_age: Optional[int] = Query(None, description="Filter students with age >= min_age"), db: Session = Depends(database.get_db)):
    return crud.get_students(db, min_age=min_age)


# --- PART 2: ALGORITHMS ENGINE ENDPOINTS (must be declared BEFORE /students/{student_id}) ---

@app.get("/students/sorted", tags=["Algorithms Engine"])
def get_sorted_students(by: str = Query("age", description="Field to sort by: 'age' or 'name'"), db: Session = Depends(database.get_db)):
    """
    Exposes hand-written Insertion Sort algorithm.
    Sorts roster in-place by specified field ('age' or 'name').
    """
    if by not in ("age", "name"):
        raise HTTPException(status_code=400, detail="Query parameter 'by' must be 'age' or 'name'.")
    
    students_orm = crud.get_students(db)
    student_dicts = [_student_to_dict(s) for s in students_orm]
    
    # Hand-written Insertion Sort
    sorted_list = algorithms.insertion_sort_by_field(student_dicts, field=by)
    return sorted_list


@app.get("/students/search", tags=["Algorithms Engine"])
def search_student_by_name(name: str = Query(..., description="Exact student name to search for"), db: Session = Depends(database.get_db)):
    """
    Exposes hand-written iterative Binary Search algorithm.
    Builds a name-sorted list with sorted() and searches via binary_search_by_name.
    """
    students_orm = crud.get_students(db)
    student_dicts = [_student_to_dict(s) for s in students_orm]
    
    # Sort alphabetically by name first using Python's built-in sorted()
    name_sorted_list = sorted(student_dicts, key=lambda s: s["name"])
    
    # Hand-written Binary Search
    match = algorithms.binary_search_by_name(name_sorted_list, name=name)
    if match == -1:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Student with name '{name}' not found.")
    
    return match


@app.get("/students/report", tags=["Algorithms Engine"])
def get_roster_report(min_age: int = Query(21, description="Minimum age filter threshold"), db: Session = Depends(database.get_db)):
    """
    Generates roster text report and counts students meeting min_age filter.
    """
    students_orm = crud.get_students(db)
    student_dicts = [_student_to_dict(s) for s in students_orm]
    
    report_text = algorithms.format_roster_report(student_dicts)
    count = algorithms.count_students_meeting_min_age(student_dicts, min_age)
    
    return {
        "report": report_text,
        "count_meeting_min_age": count
    }


# --- STUDENT SINGLE RESOURCE ENDPOINTS ---

@app.get("/students/{student_id}", response_model=schemas.StudentResponse, tags=["Students"])
def get_student(student_id: int, db: Session = Depends(database.get_db)):
    student = crud.get_student(db, student_id)
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found.")
    return student


@app.patch("/students/{student_id}", response_model=schemas.StudentResponse, tags=["Students"])
def update_student(student_id: int, student_update: schemas.StudentUpdate, db: Session = Depends(database.get_db)):
    try:
        updated_student = crud.update_student(db, student_id, student_update)
        if not updated_student:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found.")
        return updated_student
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A student with this email address already exists."
        )


@app.delete("/students/{student_id}", status_code=status.HTTP_200_OK, tags=["Students"])
def delete_student(student_id: int, db: Session = Depends(database.get_db)):
    success = crud.delete_student(db, student_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found.")
    return {"detail": "Student deleted successfully", "id": student_id}


@app.get("/students/{student_id}/course-count", tags=["Students"])
def get_student_course_count(student_id: int, db: Session = Depends(database.get_db)):
    """
    Returns course count for student, computed using SQLAlchemy func.count database query.
    """
    count = crud.get_student_course_count(db, student_id)
    if count is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found.")
    return {"student_id": student_id, "course_count": count}


# --- COURSE CRUD ENDPOINTS ---

@app.post("/courses/", response_model=schemas.CourseResponse, status_code=status.HTTP_201_CREATED, tags=["Courses"])
def create_course(course: schemas.CourseCreate, db: Session = Depends(database.get_db)):
    try:
        return crud.create_course(db, course)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Database integrity error while creating course.")


@app.get("/courses/", response_model=List[schemas.CourseResponse], tags=["Courses"])
def list_courses(db: Session = Depends(database.get_db)):
    return crud.get_courses(db)


@app.get("/courses/{course_id}", response_model=schemas.CourseResponse, tags=["Courses"])
def get_course(course_id: int, db: Session = Depends(database.get_db)):
    course = crud.get_course(db, course_id)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found.")
    return course


@app.patch("/courses/{course_id}", response_model=schemas.CourseResponse, tags=["Courses"])
def update_course(course_id: int, course_update: schemas.CourseUpdate, db: Session = Depends(database.get_db)):
    try:
        updated_course = crud.update_course(db, course_id, course_update)
        if not updated_course:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found.")
        return updated_course
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.delete("/courses/{course_id}", status_code=status.HTTP_200_OK, tags=["Courses"])
def delete_course(course_id: int, db: Session = Depends(database.get_db)):
    success = crud.delete_course(db, course_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found.")
    return {"detail": "Course deleted successfully", "id": course_id}


# ==========================================
# PART 3: INTEGRATED AI ASSISTANT ENDPOINTS
# ==========================================

class SummarizeRequest(BaseModel):
    text: str


@app.post("/assistant/summarize", tags=["AI Assistant"])
def summarize_study_notes(payload: SummarizeRequest):
    """
    Summarizes raw study notes and returns fixed schema {topic, key_points, difficulty}.
    Operates deterministically in mock mode with zero network calls.
    """
    return ai_service.summarize_notes(payload.text)


@app.get("/assistant/search", tags=["AI Assistant"])
def search_study_notes(query: str = Query("", description="Search query string")):
    """
    Ranks study notes by cosine similarity of 12-dimensional vocabulary count embeddings.
    Returns notes sorted descending by similarity score.
    """
    return ai_service.search_notes_by_query(query)


# ==========================================
# STATIC FILES MOUNT (SINGLE-PROCESS MODE)
# ==========================================
# Mount frontend directory to serve UI at root http://localhost:8000/
# Registered AFTER API routes so API endpoints take priority.

frontend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="static")
