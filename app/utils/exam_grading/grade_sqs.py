import json
from sqlmodel import SQLModel

from app.schemas.result import QuestionResult
from app.utils.exam_grading import client

def evaluate_short_question(question: str, answer: str, question_marks: int) -> QuestionResult:
    system_content = f'''You are an expert examiner tasked with evaluating and grading student responses to short exam questions in a fair and accurate manner. You will receive the following information for each question:

    - **question_statement**: The question posed to the student.
    - **student_answer**: The student's response to the question.

    Your task is to thoroughly analyze the student's answer and assign a grade out of {question_marks}, based on the accuracy and relevance of the response. Award 0 marks if the answer is completely irrelevant, and give full marks if the answer is exceptionally accurate and complete.

    Your evaluation should include the following:

    - **marks**: The score you assign, ranging from 0 to {question_marks}, reflecting the quality of the answer.
    - **feedback**: Detailed feedback on the student's response, including any mistakes, areas for improvement, necessary corrections, and suggestions for further learning.

    Please note that these are short-answer questions, so responses are typically between 1 to 5 lines long. The grading should focus on the accuracy and completeness of the answer. Deduct marks for any errors, omissions, or incorrect information.
    '''
    
    user_content = f"question_statment: \"{question}\", student_answer: \"{answer}\""

    response = client.beta.chat.completions.parse(
        model='gpt-4o-2024-08-06',
        messages=[
            {'role': 'system', 'content': system_content},
            {'role': 'user', 'content': user_content}
        ],
        temperature=0.7,
        response_format=QuestionResult
    )
    cqs = response.choices[0].message.content
    cqs_dict = json.loads(cqs)
    return cqs_dict