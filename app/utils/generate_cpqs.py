from sqlmodel import SQLModel, Field
from enum import Enum
from typing import Optional, List
import json
from config import config
from openai import OpenAI
client = OpenAI(api_key = config.OPENAI_API_KEY)


class CodingProblem(SQLModel):
    question: str = Field(..., description="The coding problem description.")
    sample_input: str = Field(..., description="Sample input for the coding problem")
    sample_output: str = Field(..., description="Sample output for the coding problem")

class CodingProblems(SQLModel):
    questions: List[CodingProblem]

def generate_coding_problems(no_of_questions: int, difficulty: str, content, profile_data: str, language) -> List[CodingProblem]:
    system_content = f''' You are a coding problems type questions Generator in {language} programming language with sample input/output examples.You will be given the following things to generate customized and personalized questions:
    -profile_data: This will be the student's personal data which you will use to add personalization in the exams being generated.
    -content: This will be the content which you will use as context to generate the questions from.
    -no_of_questions: how many questions you have to generate.
    -difficulty: how difficult the questions should be. Easy, Medium or Difficult.
    
    In output you should return:
    -question: The coding problem statement.
    -sample_input: The sample input to the function for student's help.
    -sample_output: The sample output from the function for student's help.
    
    Note: Make sure you generate diverse questions.'''
    user_content = f"profile_data: \"{profile_data}\", content: \"{content}\", number of questions = \"{no_of_questions}\", difficulty = \"{difficulty}\""

    response = client.beta.chat.completions.parse(
        model='gpt-4o-2024-08-06',
        messages=[
            {'role': 'system', 'content': system_content},
            {'role': 'user', 'content': user_content}
        ],
        temperature=0.7,
        response_format=CodingProblems
    )
    cqs = response.choices[0].message.content
    cqs_dict = json.loads(cqs)
    return cqs_dict

conten = """@result_router.get("/get_all_student_results/", response_model=List[ResultResponse])
async def get_student_results(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    # Get the student's profile
    student_profile = session.exec(select(StudentProfile).where(StudentProfile.id == current_user.id)).first()
    if not student_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student profile not found")

    # Get all results associated with the student's profile through StudentProgress
    results = session.exec(
        select(Result)
        .join(StudentProgress, StudentProgress.id == Result.student_progress_id)
        .where(StudentProgress.profile_id == student_profile.id)
    ).all()

    return results
"""