from sqlmodel import SQLModel, Field
from enum import Enum
from typing import Optional, List
import json

from openai import OpenAI

from app.config import config
client = OpenAI(api_key = config.OPENAI_API_KEY)

class EssayQuestion(SQLModel):
    question: str = Field(..., description="The essay question text")
    guidance: Optional[str] = Field(None, description="Guidance on expected content in the answer")

class EssayQuestions(SQLModel):
    questions: List[EssayQuestion]

def generate_essay_questions(no_of_questions: int, difficulty: str, content, profile_data: str) -> List[EssayQuestion]:
    system_content = '''Create in-depth essay questions requiring long, detailed responses.You will be given the following things to generate customized and personalized questions:
    -profile_data: This will be the student's personal data which you will use to add personalization in the exams being generated.
    -content: This will be the content which you will use as context to generate the questions from.
    -no_of_questions: how many questions you have to generate.
    -difficulty: how difficult the questions should be. Easy, Medium or Difficult.
    
    In output you should return:
    -questions: A list of questions statements
    -guidance: Guidance on expected content in the answer
    
    Note: Make sure you generate diverse questions.
    '''
    user_content = f"profile_data: \"{profile_data}\", content: \"{content}\", number of questions = \"{no_of_questions}\", difficulty = \"{difficulty}\""

    response = client.beta.chat.completions.parse(
        model='gpt-4o-2024-08-06',
        messages=[
            {'role': 'system', 'content': system_content},
            {'role': 'user', 'content': user_content}
        ],
        temperature=0.7,
        response_format=EssayQuestions
    )
    lqs = response.choices[0].message.content
    lqs_dict = json.loads(lqs)
    return lqs_dict