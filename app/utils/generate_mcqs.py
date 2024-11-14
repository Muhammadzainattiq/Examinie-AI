from sqlmodel import SQLModel, Field
from enum import Enum
from typing import Optional, List
import json

from openai import OpenAI

from app.config import config
client = OpenAI(api_key = config.OPENAI_API_KEY)

class OptionEnum(str, Enum):
    option1 = "option1"
    option2 = "option2"
    option3 = "option3"
    option4 = "option4"

class MCQ(SQLModel):
    question: str = Field(..., description="The MCQ question text")
    option1: str = Field(..., description="First answer option")
    option2: str = Field(..., description="Second answer option")
    option3: str = Field(..., description="Third answer option")
    option4: str = Field(..., description="Fourth answer option")
    correct_option: OptionEnum = Field(..., description="Correct answer as option1, option2, option3, or option4")
    explanation: str = Field(description="Detailed Explanation for the correct answer")

class MCQS(SQLModel):
  questions : List[MCQ]



def generate_mcqs(no_of_questions:int, difficulty:str, content:list , profile_data:str) -> MCQS:
    system_content = '''You are a personalized quiz generator. You will be given the following things to generate a customized and personalized quiz:
    -profile_data: This will be the student's personal data which you will use to generate personalized questions.
    -content: This will be the content which you will use to generate the questions from.
    -no_of_questions: how many questions you have to generate.
    -difficulty: how difficult the questions should be. Easy, Medium or Difficult.

    And your output will include the following things:
    -question: the question statement
    -options: the choices for the questions
    -correct_option: the correct option out of the four options
    -explanation: The full explanation of correct option that why its correct and why the other three are wrong. It should be as detailed as possible
    
    Note: Make sure you generate diverse questions.
    '''
    user_content = {f"profile_data: \"{profile_data}\", content: \"{content}\", number of questions = \"{no_of_questions}\", difficulty = \"{difficulty}\""}
    user_content = str(user_content)
    messages = [
        {'role': 'system', 'content': system_content},
        {'role': 'user', 'content': user_content}
    ]
    response = client.beta.chat.completions.parse(model='gpt-4o-2024-08-06', messages=messages, temperature=0.9, response_format =MCQS)
    mcqs = response.choices[0].message.content
    mcq_dict = json.loads(mcqs)
    return mcq_dict