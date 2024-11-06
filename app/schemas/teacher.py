from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlmodel import SQLModel

class TeacherProfileCreate(SQLModel):
    # Define fields specific to the teacher profile creation
    # Include necessary fields from the model
    pass

class TeacherProfileResponse(SQLModel):
    user_id: UUID  # Change to UUID
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime]
    # Include necessary fields for response