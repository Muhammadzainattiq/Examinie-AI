from typing import Optional
from uuid import UUID
from sqlmodel import SQLModel

class ContentCreate(SQLModel):
    title: str
    description: Optional[str]
    file_type: str  # or use FileType Enum
    file_url: str
    exam_id: Optional[UUID]  # Change to UUID

class ContentResponse(SQLModel):
    title: str
    description: Optional[str]
    file_type: str
    file_url: str
    exam_id: Optional[UUID]  # Change to UUID
