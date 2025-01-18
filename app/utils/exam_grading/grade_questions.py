from app.models.enum import QuestionType
from app.models.exam import MCQ, CaseStudy, CodingProblem, EssayQuestion, TrueFalseQuestion
from app.utils.exam_grading.grade_cpqs import evaluate_coding_problem
from app.utils.exam_grading.grade_csqs import evaluate_case_study
from app.utils.exam_grading.grade_fitb import evaluate_fitb
from app.utils.exam_grading.grade_lqs import evaluate_essay_question
from app.utils.exam_grading.grade_sqs import evaluate_short_question


def grade_questions(questions, student_answers, session):
    graded_questions = []

    for question in questions:
        question_feedback = ""
        obtained_marks = 0
        question_marks = question.marks
        # Grade based on question type
        if question.type == QuestionType.MCQ:
            mcq_data = session.get(MCQ, question.id)
            student_response = student_answers.get(question.id)
            if student_response == mcq_data.correct_option:
                obtained_marks = question.marks
                question_feedback = "Correct answer!"
            else:
                question_feedback = mcq_data.explanation

        elif question.type == QuestionType.TRUE_FALSE:
            tf_data = session.get(TrueFalseQuestion, question.id)
            student_response = student_answers.get(question.id)
            if student_response.lower() == str(tf_data.correct_answer).lower():
                obtained_marks = question.marks
                question_feedback = "Correct answer!"
            else:
                question_feedback = tf_data.explanation

        elif question.type == QuestionType.FILL_IN_THE_BLANK:
            ai_response = evaluate_fitb(
                question.statement,
                student_answers.get(question.id),
                question_marks = question_marks
            )
            obtained_marks = ai_response["marks"]
            question_feedback = ai_response["feedback"]


        elif question.type == QuestionType.SHORT:
            ai_response = evaluate_short_question(
                question.statement,
                student_answers.get(question.id),
                question_marks = question_marks
            )
            obtained_marks = ai_response["marks"]
            question_feedback = ai_response["feedback"]


        elif question.type == QuestionType.ESSAY:
            lq_data = session.get(EssayQuestion, question.id)
            ai_response = evaluate_essay_question(
                question.statement,
                student_answers.get(question.id),
                lq_data.guidance,
                question_marks = question_marks
            )
            obtained_marks = ai_response["marks"]
            question_feedback = ai_response["feedback"]


        elif question.type == QuestionType.CASE_STUDY:
            cs_data = session.get(CaseStudy, question.id)
            ai_response = evaluate_case_study(
                lq_data.case_description,
                question.statement,
                student_answers.get(question.id),
                question_marks = question_marks
            )
            obtained_marks = ai_response["marks"]
            question_feedback = ai_response["feedback"]

        elif question.type == QuestionType.CODING_PROBLEM:
            cp_data = session.get(CodingProblem, question.id)
            ai_response = evaluate_coding_problem(
                question.statement,
                cp_data.sample_input,
                cp_data.sample_output,
                student_answers.get(question.id),
                question_marks = question_marks
            )
            obtained_marks = ai_response["marks"]
            question_feedback = ai_response["feedback"]

        # Add graded question details to list
        graded_questions.append({
            "question_id": question.id,
            "question_type": question.type,
            "total_marks": question.marks,
            "obtained_marks": obtained_marks,
            "feedback": question_feedback
        })

    return graded_questions
