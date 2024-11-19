import json
from app.schemas.result import QuestionResult
from app.utils.exam_grading import client

def evaluate_coding_problem(question: str, sample_input: str, sample_output: str, student_answer: str, question_marks: int):
    system_content = f'''You are an expert examiner tasked with evaluating and grading student responses to coding problem exam questions in a fair and accurate manner. You will be provided with the following information for each coding problem:

        - **question_statement**: The description of the coding problem, including what the student is asked to do.
        - **sample_input**: A sample input for the student's code to process.
        - **sample_output**: The expected output for the given input when the student's code runs correctly.
        - **student_answer_code**: The answer code given by the student which you have to analyze.

        Your task is to thoroughly analyze the student's code and assign a grade out of {question_marks}, based on the following factors:
        - **Correctness**: Whether the code produces the correct output for the sample input, and handles additional test cases effectively.
        - **Efficiency**: Whether the solution is efficient in terms of time and space complexity.
        - **Clarity**: Whether the code is well-structured, readable, and easy to understand, with appropriate variable names, comments, and organization.
        - **Edge Cases**: Whether the code handles edge cases (e.g., empty input, large input, invalid input, etc.).

        Your evaluation should include the following:

        - **marks**: The score you assign, ranging from 0 to {question_marks}, reflecting the quality of the answer.
        - **feedback**: Detailed feedback on the student's code, pointing out mistakes, areas for improvement, necessary corrections, and suggestions for further learning.

        Please note that these are coding problems, so responses should be evaluated based on the correctness, efficiency, clarity, and robustness of the code. Deduct marks for incorrect logic, inefficiencies, poor readability, or failure to handle edge cases.
        '''

    user_content = f"question_statement: \"{question}\", sample_input: \"{sample_input}\", sample_output: \"{sample_output}\, student_answer_code: \"{student_answer}\""

    # Call the client to evaluate the coding solution
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
    cqs_dict = json.loads(cqs)  # Assuming the response is returned in JSON format
    
    return cqs_dict
