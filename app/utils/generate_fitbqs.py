from sqlmodel import SQLModel, Field
from enum import Enum
from typing import Optional, List
import json

from openai import OpenAI

from app.config import config
client = OpenAI(api_key = config.OPENAI_API_KEY)

class FillInTheBlank(SQLModel):
    question: str = Field(..., description="The sentence with a blank space")
    correct_answer: str = Field(..., description="The word or phrase that fills in the blank")

class FillInTheBlanks(SQLModel):
  questions: List[FillInTheBlank]

def generate_fill_in_the_blank(no_of_questions: int, difficulty: str, content, profile_data: str) -> List[FillInTheBlank]:
    system_content = '''You are a fill-in-the-blank questions generator with single correct answers. There must be three '*' in place of blank. And the blank should be in center of the sentence. Like the following:
    Example: 
    question: Water boils at *** degrees Celsius.
    You will be given the following things to generate customized and personalized questions:
    -profile_data: This will be the student's personal data which you will use to add personalization in the exams being generated.
    -content: This will be the content which you will use as context to generate the questions from.
    -no_of_questions: how many questions you have to generate.
    -difficulty: how difficult the questions should be. Easy, Medium or Difficult.
    
    In output you should return:
    -question: The true/false question text
    -correct_answer:The word or phrase that fills in the blank
    
    Note: Make sure you generate diverse questions.'''
    user_content = f"profile_data: \"{profile_data}\", content: \"{content}\", number of questions = \"{no_of_questions}\", difficulty = \"{difficulty}\""

    response = client.beta.chat.completions.parse(
        model='gpt-4o-2024-08-06',
        messages=[
            {'role': 'system', 'content': system_content},
            {'role': 'user', 'content': user_content}
        ],
        temperature=0.7,
        response_format=FillInTheBlanks
    )
    fqs = response.choices[0].message.content
    fqs_dict = json.loads(fqs)
    return fqs_dict