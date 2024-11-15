from sqlmodel import SQLModel, Session, create_engine
from app.config import config 
from app.models.user import StudentProfile, StudentProgress
from app.models.exam import Exam, ExamAttempt, Question, Answer, Result
engine = create_engine(config.DATABASE_URL, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session