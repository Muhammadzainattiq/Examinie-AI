import json
from sqlmodel import SQLModel

from app.schemas.result import QuestionResult
from app.utils.exam_grading.client import client

def evaluate_case_study(case_description: str, question: str, answer: str, question_marks: int):
    system_content = f'''You are an expert examiner tasked with evaluating and grading student responses to case study exam questions in a fair and accurate manner. You will be provided with the following information for each case study question:

        - **case_description**: A description of the case study from which the question is derived.
        - **question_statement**: The specific question posed to the student based on the case.
        - **student_answer**: The student's response to the question.

        Your task is to thoroughly analyze the student's response and assign a grade out of {question_marks}, based on the relevance, accuracy, and depth of the answer. Award 0 marks if the answer is completely irrelevant, and give full marks for a response that is exceptionally detailed and accurate.

        Your evaluation should include the following:

        - **marks**: The score you assign, ranging from 0 to {question_marks}, based on the quality and completeness of the response.
        - **feedback**: Comprehensive feedback on the student's answer, pointing out mistakes, areas for improvement, necessary corrections, and suggestions for further study.

        Please note that these are case-study questions, and responses should be evaluated based on how well they apply the case details to answer the question. Focus on accuracy, completeness, and relevance. Deduct marks for errors, omissions, or incorrect interpretations of the case information.
        '''

    user_content = f"case_description: \"{case_description}\", question_statment: \"{question}\", student_answer: \"{answer}\""

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