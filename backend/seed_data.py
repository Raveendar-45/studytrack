from sqlalchemy.orm import Session
from backend import models

SEED_STUDENTS = [
    {"name": "Aditi Rao", "email": "aditi.rao@example.com", "age": 22},
    {"name": "Rohan Mehta",  "email": "rohan.mehta@example.com",  "age": 22},
    {"name": "Kavya Nair",   "email": "kavya.nair@example.com",   "age": 19},
    {"name": "Farhan Sheikh", "email": "farhan.sheikh@example.com", "age": 25},
    {"name": "Priya Iyer",    "email": "priya.iyer@example.com",    "age": 18},
    {"name": "Devansh Gupta", "email": "devansh.gupta@example.com", "age": 21},
    {"name": "Meera Joshi",   "email": "meera.joshi@example.com",   "age": 23},
    {"name": "Sameer Khan",   "email": "sameer.khan@example.com",   "age": 20},
    {"name": "Ananya Sharma", "email": "ananya.sharma@example.com", "age": 24},
]

SEED_COURSES = [
    {"course_name": "Algorithms & Data Structures", "credits": 4, "student_email": "aditi.rao@example.com"},
    {"course_name": "Full-Stack Web Development", "credits": 3, "student_email": "aditi.rao@example.com"},
    {"course_name": "Database Systems & SQL", "credits": 4, "student_email": "rohan.mehta@example.com"},
    {"course_name": "System Architecture", "credits": 3, "student_email": "farhan.sheikh@example.com"},
]


def seed_if_empty(db: Session):
    """Seeds the database with exact seed dataset if the Student table is currently empty."""
    student_count = db.query(models.Student).count()
    if student_count == 0:
        print("[Seeding] Seeding initial student dataset into SQLite database...")
        student_map = {}
        for student_data in SEED_STUDENTS:
            student = models.Student(
                name=student_data["name"],
                email=student_data["email"],
                age=student_data["age"]
            )
            db.add(student)
            db.flush()
            student_map[student.email] = student.id
        
        db.commit()

        # Seed initial course enrollments
        for course_data in SEED_COURSES:
            student_id = student_map.get(course_data["student_email"])
            if student_id:
                course = models.Course(
                    course_name=course_data["course_name"],
                    credits=course_data["credits"],
                    student_id=student_id
                )
                db.add(course)
        db.commit()
        print("[Seeding] Database seeding complete.")
