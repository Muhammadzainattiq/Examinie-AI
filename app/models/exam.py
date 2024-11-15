# exam_models.py
from datetime import datetime
from enum import Enum
from uuid import UUID
import uuid
from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional, Union
from app.models.content import Content
from app.models.enum import DifficultyLevel, QuestionType
from app.models.user import StudentProfile, StudentProgress, TeacherProfile


class OptionEnum(str, Enum):
    option1 = "option1"
    option2 = "option2"
    option3 = "option3"
    option4 = "option4"

class BaseModel(SQLModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

# Primary Question Table

class Question(BaseModel, table=True):
    exam_id: uuid.UUID = Field(foreign_key="exam.id")
    type: QuestionType = Field(..., description="Type of the question")
    marks: int
    statement: Optional[str] = Field(None, description="Common question text")

    # Relationship to specialized question types
    mcq: Optional["MCQ"] = Relationship(back_populates="question")
    short_question: Optional["ShortQuestion"] = Relationship(back_populates="question")
    true_false: Optional["TrueFalseQuestion"] = Relationship(back_populates="question")
    essay: Optional["EssayQuestion"] = Relationship(back_populates="question")
    fill_in_the_blank: Optional["FillInTheBlank"] = Relationship(back_populates="question")
    case_study: Optional["CaseStudy"] = Relationship(back_populates="question")
    coding_problem: Optional["CodingProblem"] = Relationship(back_populates="question")

    # Relationship with Exam and Answer
    exam: Optional["Exam"] = Relationship(back_populates="questions")
    answers: List["Answer"] = Relationship(back_populates="question")

# Specialized Question Models

class MCQ(BaseModel, table=True):
    question_id: uuid.UUID = Field(foreign_key="question.id")
    option1: str
    option2: str
    option3: str
    option4: str
    correct_option: OptionEnum
    explanation: Optional[str]

    question: Optional[Question] = Relationship(back_populates="mcq")

class ShortQuestion(BaseModel, table=True):
    question_id: uuid.UUID = Field(foreign_key="question.id")
    question: Optional[Question] = Relationship(back_populates="short_question")

class TrueFalseQuestion(BaseModel, table=True):
    question_id: uuid.UUID = Field(foreign_key="question.id")
    correct_answer: bool

    question: Optional[Question] = Relationship(back_populates="true_false")

class EssayQuestion(BaseModel, table=True):
    question_id: uuid.UUID = Field(foreign_key="question.id")
    guidance: Optional[str]

    question: Optional[Question] = Relationship(back_populates="essay")

class FillInTheBlank(BaseModel, table=True):
    question_id: uuid.UUID = Field(foreign_key="question.id")
    correct_answer: str

    question: Optional[Question] = Relationship(back_populates="fill_in_the_blank")

class CaseStudy(BaseModel, table=True):
    question_id: uuid.UUID = Field(foreign_key="question.id")
    case_description: str
    expected_response: str

    question: Optional[Question] = Relationship(back_populates="case_study")

class CodingProblem(BaseModel, table=True):
    question_id: uuid.UUID = Field(foreign_key="question.id")
    sample_input: str
    sample_output: str

    question: Optional[Question] = Relationship(back_populates="coding_problem")
class Exam(BaseModel, table=True):
    title: str
    questions_type: QuestionType
    difficulty: DifficultyLevel
    num_questions: int
    time_limit: Optional[int]
    marks_per_question: int
    total_marks: Optional[int]

    # Foreign keys for student and teacher creators
    student_id: Optional[UUID] = Field(default=None, foreign_key="studentprofile.id")
    teacher_id: Optional[UUID] = Field(default=None, foreign_key="teacherprofile.id")

    # Relationships
    student_creator: Optional["StudentProfile"] = Relationship(back_populates="created_exams")
    teacher_creator: Optional["TeacherProfile"] = Relationship(back_populates="created_exams")
    questions: List["Question"] = Relationship(back_populates="exam")
    attempts: List["ExamAttempt"] = Relationship(back_populates="exam")
    contents: List["Content"] = Relationship(back_populates="exam")

class ExamAttempt(BaseModel, table=True):
    exam_id: UUID = Field(foreign_key="exam.id")  # Foreign key reference
    student_id: UUID = Field(foreign_key="studentprofile.id")  # Foreign key reference
    score: Optional[int] = None
    completed: bool = False
    submitted_at: Optional[datetime] = None

    answers: List["Answer"] = Relationship(back_populates="attempt")
    exam: Optional["Exam"] = Relationship(back_populates="attempts")

class Answer(BaseModel, table=True):
    attempt_id: UUID = Field(foreign_key="examattempt.id")  # Foreign key reference
    question_id: UUID = Field(foreign_key="question.id")  # Foreign key reference
    response: str

    attempt: Optional["ExamAttempt"] = Relationship(back_populates="answers")
    question: Optional["Question"] = Relationship()

class Result(BaseModel, table=True):
    exam_attempt_id: UUID = Field(foreign_key="examattempt.id")  # Foreign key reference
    student_id: Optional[uuid.UUID] = Field(foreign_key="studentprofile.id")  # Link to StudentProgress
    exam_title: Optional[str] = None  # Store exam title for reference
    total_marks: Optional[int] = None
    obtained_marks: int
    grade: Optional[str] = None
    percentage: Optional[float] = None
    feedback: Optional[str] = None

    # Relationships
    exam_attempt: Optional["ExamAttempt"] = Relationship()
    student: Optional["StudentProfile"] = Relationship(back_populates="exam_results")
