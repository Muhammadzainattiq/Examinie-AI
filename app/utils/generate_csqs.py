from sqlmodel import SQLModel, Field
from enum import Enum
from typing import Optional, List
import json

from openai import OpenAI

from app.config import config
client = OpenAI(api_key = config.OPENAI_API_KEY)

class CaseStudy(SQLModel):
    case_description: str = Field(..., description="Description of the case")
    question: str = Field(..., description="Question based on the case study")
    expected_response: str = Field(..., description="Expected response or solution")

class CaseStudies(SQLModel):
  questions: List[CaseStudy]

def generate_case_studies(no_of_questions: int, difficulty: str, content, profile_data: str) -> List[CaseStudy]:
    system_content = '''You are a case studies questions generator. You will generate case studies requiring critical analysis. You will be given the following things to generate customized and personalized questions:
    -profile_data: This will be the student's personal data which you will use to add personalization in the exams being generated.
    -content: This will be the content which you will use as context to generate the questions from.
    -no_of_questions: how many questions you have to generate.
    -difficulty: how difficult the questions should be. Easy, Medium or Difficult.
    
    In output you should return:
    -case_description: The detailed description of the case.
    -question: The Question based on the case study.
    -expected_response: The expected response or solution of the question with respect to the case study.
    
    Note: Make sure you generate diverse questions.'''
    user_content = f"profile_data: \"{profile_data}\", content: \"{content}\", number of cases = \"{no_of_questions}\", difficulty = \"{difficulty}\""

    response = client.beta.chat.completions.parse(
        model='gpt-4o-2024-08-06',
        messages=[
            {'role': 'system', 'content': system_content},
            {'role': 'user', 'content': user_content}
        ],
        temperature=0.7,
        response_format=CaseStudies
    )
    csqs = response.choices[0].message.content
    csqs_dict = json.loads(csqs)
    return csqs_dict
