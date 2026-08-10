from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List


# --- Course Schemas ---

class CourseBase(BaseModel):
    course_name: str
    credits: int = Field(..., ge=1, le=6)
    student_id: int


class CourseCreate(CourseBase):
    pass


class CourseUpdate(BaseModel):
    course_name: Optional[str] = None
    credits: Optional[int] = Field(default=None, ge=1, le=6)
    student_id: Optional[int] = None


class CourseResponse(CourseBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
    # Fallback for Pydantic v1
    class Config:
        orm_mode = True


# --- Student Schemas ---

class StudentBase(BaseModel):
    name: str
    email: str
    age: int = Field(..., gt=0)

    @field_validator('email')
    @classmethod
    def validate_email_at_symbol(cls, v: str) -> str:
        if not isinstance(v, str) or '@' not in v:
            raise ValueError("Email must contain an '@' character.")
        return v


class StudentCreate(StudentBase):
    pass


class StudentUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    age: Optional[int] = Field(default=None, gt=0)

    @field_validator('email')
    @classmethod
    def validate_email_at_symbol(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and (not isinstance(v, str) or '@' not in v):
            raise ValueError("Email must contain an '@' character.")
        return v


class StudentResponse(StudentBase):
    id: int
    courses: List[CourseResponse] = []

    model_config = ConfigDict(from_attributes=True)
    class Config:
        orm_mode = True
