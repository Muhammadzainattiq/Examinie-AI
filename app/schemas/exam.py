from typing import List, Optional
from uuid import UUID

from sqlmodel import SQLModel


class ExamCreate(SQLModel):
    title: str
    creator_id: UUID  # User ID of the creator as UUID
    question_type: str  # or use QuestionType Enum
    difficulty: str  # or use DifficultyLevel Enum
    num_questions: int
    time_limit: Optional[int]
    marks_per_question: int
    total_marks: Optional[int]

class ExamResponse(SQLModel):
    title: str
    creator_id: UUID  # Change to UUID
    question_type: str
    difficulty: str
    num_questions: int
    time_limit: Optional[int]
    marks_per_question: int
    total_marks: Optional[int]
    # questions: List["QuestionResponse"]  # Reference to the Question schema if needed
