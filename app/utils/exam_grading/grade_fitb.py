import json
from sqlmodel import SQLModel

from app.schemas.result import QuestionResult
from app.utils.exam_grading import client

def evaluate_fitb(question: str, answer: str, question_marks: int):
    system_content = f'''You are an expert examiner tasked with evaluating and grading student responses to fill in the blank exam questions in a fair and accurate manner. You will be provided with the following information for each fill-in-the-blank question:

        - **question_statement**: The specific question given to the student, containing a blank to be filled.
        - **student_answer**: The student's response to the blank in the question.

        Your task is to analyze the student's response thoroughly and assign a grade out of {question_marks}, based on the following:
        
        1. **Accuracy**: How correct the student's answer is in filling the blank.
        2. **Relevance**: Whether the response fits the context of the question.
        3. **Spelling/Grammar**: Penalize for spelling or grammatical mistakes if they impact the clarity or correctness of the answer.

        Award **full marks** for a correct and contextually accurate answer, and **0 marks** for a completely incorrect or irrelevant response. 

        Your response must include:
        - **marks**: The score you assign, ranging from 0 to {question_marks}.
        - **feedback**: Concise feedback on the student's answer, mentioning:
          - Errors in their response.
          - Suggestions for improvement if the answer is partially correct.
          - Acknowledgment of correct answers.

        Focus on ensuring the evaluation is clear, consistent, and objective.
        '''

    user_content = f"question_statement: \"{question}\", student_answer: \"{answer}\""

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
