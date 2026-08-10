from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend import models, schemas


# --- Student CRUD Operations ---

def create_student(db: Session, student: schemas.StudentCreate) -> models.Student:
    db_student = models.Student(
        name=student.name,
        email=student.email,
        age=student.age
    )
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student


def get_students(db: Session, min_age: Optional[int] = None) -> List[models.Student]:
    query = db.query(models.Student)
    if min_age is not None:
        query = query.filter(models.Student.age >= min_age)
    return query.all()


def get_student(db: Session, student_id: int) -> Optional[models.Student]:
    return db.query(models.Student).filter(models.Student.id == student_id).first()


def update_student(db: Session, student_id: int, student_update: schemas.StudentUpdate) -> Optional[models.Student]:
    db_student = get_student(db, student_id)
    if not db_student:
        return None
    
    update_data = student_update.model_dump(exclude_unset=True) if hasattr(student_update, "model_dump") else student_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_student, key, value)
    
    db.commit()
    db.refresh(db_student)
    return db_student


def delete_student(db: Session, student_id: int) -> bool:
    db_student = get_student(db, student_id)
    if not db_student:
        return False
    db.delete(db_student)
    db.commit()
    return True


def get_student_course_count(db: Session, student_id: int) -> Optional[int]:
    """Computes course count via a direct database query (func.count)."""
    # Check if student exists first
    student_exists = db.query(models.Student.id).filter(models.Student.id == student_id).first()
    if not student_exists:
        return None
    
    count = db.query(func.count(models.Course.id)).filter(models.Course.student_id == student_id).scalar()
    return count if count is not None else 0


# --- Course CRUD Operations ---

def create_course(db: Session, course: schemas.CourseCreate) -> models.Course:
    # Verify student exists
    student = get_student(db, course.student_id)
    if not student:
        raise ValueError(f"Student with id {course.student_id} does not exist.")
    
    db_course = models.Course(
        course_name=course.course_name,
        credits=course.credits,
        student_id=course.student_id
    )
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course


def get_courses(db: Session) -> List[models.Course]:
    return db.query(models.Course).all()


def get_course(db: Session, course_id: int) -> Optional[models.Course]:
    return db.query(models.Course).filter(models.Course.id == course_id).first()


def update_course(db: Session, course_id: int, course_update: schemas.CourseUpdate) -> Optional[models.Course]:
    db_course = get_course(db, course_id)
    if not db_course:
        return None
    
    update_data = course_update.model_dump(exclude_unset=True) if hasattr(course_update, "model_dump") else course_update.dict(exclude_unset=True)
    if "student_id" in update_data and update_data["student_id"] is not None:
        student = get_student(db, update_data["student_id"])
        if not student:
            raise ValueError(f"Student with id {update_data['student_id']} does not exist.")
            
    for key, value in update_data.items():
        setattr(db_course, key, value)
        
    db.commit()
    db.refresh(db_course)
    return db_course


def delete_course(db: Session, course_id: int) -> bool:
    db_course = get_course(db, course_id)
    if not db_course:
        return False
    db.delete(db_course)
    db.commit()
    return True
