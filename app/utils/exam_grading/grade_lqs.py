import json
from sqlmodel import SQLModel

from app.schemas.result import QuestionResult
from app.utils.exam_grading import client

def evaluate_essay_question(question: str, answer: str, question_marks: int) -> QuestionResult:
    system_content = f'''You are an expert examiner tasked with evaluating and grading student responses to essay-type long exam questions in a fair and accurate manner. You will receive the following information for each question:

        - **question_statement**: The question presented to the student.
        - **student_answer**: The student's response to the question.

        Your task is to carefully analyze the student's answer and assign a grade out of {question_marks} based on the accuracy, depth, and relevance of the response. Your evaluation should include the following:

        - **marks**: The score you assign, ranging from 0 to {question_marks}, based on the quality of the answer.
        - **feedback**: Detailed feedback on the student's answer, highlighting mistakes, areas requiring correction, and suggestions for improvement.

        Please note that these are essay-type questions, and responses are expected to be longer, typically between 5 to 15 lines or more. The grading should reflect the thoroughness and completeness of the response. Deduct marks for errors, incorrect answers, and overly brief or incomplete answers.
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