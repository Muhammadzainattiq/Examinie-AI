from datetime import datetime
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.models.exam import MCQ, Answer, CaseStudy, CodingProblem, EssayQuestion, Exam, ExamAttempt, FillInTheBlank, Question, Result, ShortQuestion, TrueFalseQuestion
from app.schemas.result import ResultCreate, ResultResponse
from app.utils.db import get_session
from app.utils.auth import get_current_user
from app.models.user import StudentProfile, StudentProgress, User
from app.models.enum import LatestGrade, QuestionType
from app.utils.exam_grading.grade_cpqs import evaluate_coding_problem
from app.utils.exam_grading.grade_csqs import evaluate_case_study
from app.utils.exam_grading.grade_lqs import evaluate_essay_question
from app.utils.exam_grading.grade_sqs import evaluate_short_question
from app.utils.student_progress import calculate_grade

result_router = APIRouter(prefix="/results")

@result_router.post("/create_result/{exam_attempt_id}", response_model=ResultResponse)
async def create_result(
    exam_attempt_id: UUID,
    result_data: ResultCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    if result_data.obtained_marks > result_data.total_marks:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Obtained marks cannot be greater than total marks.")
    # Retrieve the student's profile
    profile = session.exec(select(StudentProfile).where(StudentProfile.id == current_user.id)).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student profile not found.")

    # Retrieve the exam attempt based on the exam attempt ID
    exam_attempt = session.get(ExamAttempt, exam_attempt_id)
    if not exam_attempt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exam attempt not found.")

    exam = session.get(Exam, exam_attempt.exam_id)
    if not exam:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found.")

    # Retrieve the latest StudentProgress record for the student
    latest_progress = session.exec(
        select(StudentProgress)
        .where(StudentProgress.profile_id == profile.id)
        .order_by(StudentProgress.created_at.desc())
    ).first()

    # Initialize fields for the new StudentProgress record based on the latest progress
    total_exams_taken = (latest_progress.total_exams_taken if latest_progress else 0) + 1

    # Calculate the grade and percentage
    if result_data.total_marks:
        percentage = (result_data.obtained_marks / result_data.total_marks) * 100
    else:
        percentage = 0.0  # Handle case where total_marks is None

    grade = calculate_grade(percentage)

    # Calculate exams passed/failed based on grade
    exams_passed = (latest_progress.exams_passed if latest_progress else 0) + (1 if grade not in [LatestGrade.F, LatestGrade.INCOMPLETE, LatestGrade.FAIL] else 0)
    exams_failed = (latest_progress.exams_failed if latest_progress else 0) + (1 if grade in [LatestGrade.F, LatestGrade.INCOMPLETE, LatestGrade.FAIL] else 0)

    # Calculate total points and time spent
    total_points = (latest_progress.total_points if latest_progress else 0) + (result_data.obtained_marks or 0)

    # Create a new StudentProgress record
    progress_record = StudentProgress(
        profile_id=profile.id,
        date_recorded=datetime.utcnow(),
        last_exam_score=result_data.obtained_marks or 0,
        total_exams_taken=total_exams_taken,
        exams_passed=exams_passed,
        exams_failed=exams_failed,
        total_points=total_points,
        overall_grade=None,  # Placeholder for calculation below
        overall_percentage=0.0,  # Placeholder for calculation below
    )

    # Add the new progress record to the session
    session.add(progress_record)
    session.commit()
    session.refresh(progress_record)

    # Create the result entry and link it to the new progress record
    new_result = Result(
        exam_attempt_id=exam_attempt.id,
        student_id=current_user.id,
        exam_title=exam.title,
        total_marks=result_data.total_marks,
        obtained_marks=result_data.obtained_marks,
        grade=str(grade),
        percentage=percentage,
        feedback=result_data.feedback
    )
    session.add(new_result)
    session.commit()
    session.refresh(new_result)

    # Calculate overall grade and percentage based on all results for the student
    all_results = session.exec(select(Result).where(Result.student_id == current_user.id)).all()
    if all_results:
        total_obtained = sum(result.obtained_marks for result in all_results)
        total_max = sum(result.total_marks for result in all_results if result.total_marks)

        if total_max > 0:
            overall_percentage = (total_obtained / total_max) * 100
            progress_record.overall_percentage = overall_percentage
            progress_record.overall_grade = calculate_grade(overall_percentage)

    # Update and save the new progress record with the calculated grade and percentage
    session.add(progress_record)
    session.commit()
    session.refresh(progress_record)

    return new_result


@result_router.get("/get_result/{result_id}/", response_model=ResultResponse)
async def get_result(
    result_id: UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    # Retrieve result details by result_id
    result = session.get(Result, result_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Result not found")
    return result


@result_router.get("/get_all_student_results/", response_model=List[ResultResponse])
async def get_student_results(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    # Get all results associated with the student's profile through StudentProgress
    results = session.exec(
        select(Result)
        .where(Result.student_id == current_user.id)
    ).all()

    return results

@result_router.get("/get_last_exam_result/", response_model=ResultResponse)
async def get_last_exam_result(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    # Fetch the most recent result for the current user
    last_result = session.exec(
        select(Result)
        .where(Result.student_id == current_user.id)
        .order_by(Result.created_at.desc())
    ).first()

    if not last_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No exam results found for the student."
        )

    return last_result



from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import select, Session
from uuid import UUID

@result_router.post("/generate_result/{exam_attempt_id}")
async def generate_result(
    exam_attempt_id: UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    try:
        # Fetch exam attempt
        attempt = session.get(ExamAttempt, exam_attempt_id)
        if not attempt:
            raise HTTPException(status_code=404, detail="Exam attempt not found")

        # Fetch related exam and questions
        exam = session.get(Exam, attempt.exam_id)
        if not exam:
            raise HTTPException(status_code=404, detail="Exam not found for the attempt")

        questions = session.exec(
            select(Question).where(Question.exam_id == exam.id)
        ).all()
        if not questions:
            raise HTTPException(status_code=404, detail="No questions found for the exam")

        answers = session.exec(
            select(Answer).where(Answer.attempt_id == attempt.id)
        ).all()

        # Map answers by question_id
        student_answers = {answer.question_id: answer.response for answer in answers}

        # Handle unattempted questions by assigning "Unattempted" as the answer
        for question in questions:
            if question.id not in student_answers:
                student_answers[question.id] = "Unattempted"

        # Grade each question
        graded_questions = grade_questions(questions, student_answers, session)

        # Summarize the overall result for saving in the database
        total_marks = sum(q["total_marks"] for q in graded_questions)
        obtained_marks = sum(q["obtained_marks"] for q in graded_questions)
        summarized_feedback = " | ".join(q["feedback"] for q in graded_questions if q["feedback"])

        # Save overall result in the database
        result = Result(
            exam_attempt_id=attempt.id,
            student_id=attempt.student_id,
            exam_title=exam.title,
            total_marks=total_marks,
            obtained_marks=obtained_marks,
            grade=calculate_grade(obtained_marks, total_marks),
            percentage=(obtained_marks / total_marks) * 100 if total_marks > 0 else 0,
            feedback=summarized_feedback
        )
        session.add(result)
        session.commit()

        # Prepare response payload
        response_payload = {
            "overall_result": {
                "result_id": result.id,
                "exam_title": result.exam_title,
                "total_marks": result.total_marks,
                "obtained_marks": result.obtained_marks,
                "grade": result.grade,
                "percentage": result.percentage,
                "feedback": result.feedback
            },
            "question_results": graded_questions  # Detailed question-level results
        }

        # Return the complete result
        return response_payload

    except SQLAlchemyError:
        session.rollback()
        raise HTTPException(status_code=500, detail="Database error occurred")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
            if student_response == tf_data.correct_answer:
                obtained_marks = question.marks
                question_feedback = "Correct answer!"
            else:
                question_feedback = tf_data.explanation

        elif question.type == QuestionType.FILL_IN_THE_BLANK:
            fb_data = session.get(FillInTheBlank, question.id)
            student_response = student_answers.get(question.id)
            if student_response == fb_data.correct_answer:
                obtained_marks = question.marks
                question_feedback = "Correct answer!"
            else:
                question_feedback = fb_data.explanation

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


@result_router.post("/generate_and_update_result/{exam_attempt_id}")
async def generate_and_update_result(
    exam_attempt_id: UUID,
    result_data: ResultCreate = None,  # Optional parameter if manual data is passed
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    # Fetch exam attempt
    attempt = session.get(ExamAttempt, exam_attempt_id)
    if not attempt:
        raise HTTPException(status_code=404, detail="Exam attempt not found")
    # Check if the exam attempt is completed
    if not attempt.completed:
        raise HTTPException(
            status_code=400,  # Bad Request
            detail="Result cannot be generated because the exam attempt is not completed."
        )
    # Fetch related exam and questions
    exam = session.get(Exam, attempt.exam_id)
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found for the attempt")

    questions = session.exec(
        select(Question).where(Question.exam_id == exam.id)
    ).all()
    if not questions:
        raise HTTPException(status_code=404, detail="No questions found for the exam")

    answers = session.exec(
        select(Answer).where(Answer.attempt_id == attempt.id)
    ).all()

    # Map answers by question_id
    student_answers = {answer.question_id: answer.response for answer in answers}

    # Handle unattempted questions by assigning "Unattempted" as the answer
    for question in questions:
        if question.id not in student_answers:
            student_answers[question.id] = "Unattempted"

    # Grade each question
    graded_questions = grade_questions(questions, student_answers, session)

    # Summarize the overall result
    total_marks = sum(q["total_marks"] for q in graded_questions)
    obtained_marks = sum(q["obtained_marks"] for q in graded_questions)
    summarized_feedback = " | ".join(q["feedback"] for q in graded_questions if q["feedback"])

    # Calculate grade and percentage
    percentage = (obtained_marks / total_marks) * 100 if total_marks > 0 else 0
    grade = calculate_grade(percentage)

    # Save overall result in the database
    result = Result(
        exam_attempt_id=attempt.id,
        student_id=attempt.student_id,
        exam_title=exam.title,
        total_marks=total_marks,
        obtained_marks=obtained_marks,
        grade=grade,
        percentage=percentage
    )
    session.add(result)
    session.commit()
    session.refresh(result)

    # Retrieve student's profile
    profile = session.exec(select(StudentProfile).where(StudentProfile.id == current_user.id)).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Student profile not found")

    # Retrieve the latest StudentProgress record for the student
    latest_progress = session.exec(
        select(StudentProgress)
        .where(StudentProgress.profile_id == profile.id)
        .order_by(StudentProgress.created_at.desc())
    ).first()

    # Calculate updated progress metrics
    total_exams_taken = (latest_progress.total_exams_taken if latest_progress else 0) + 1
    exams_passed = (latest_progress.exams_passed if latest_progress else 0) + (1 if grade not in [LatestGrade.F, LatestGrade.INCOMPLETE, LatestGrade.FAIL] else 0)
    exams_failed = (latest_progress.exams_failed if latest_progress else 0) + (1 if grade in [LatestGrade.F, LatestGrade.INCOMPLETE, LatestGrade.FAIL] else 0)
    total_points = (latest_progress.total_points if latest_progress else 0) + obtained_marks

    # Create or update StudentProgress record
    progress_record = StudentProgress(
        profile_id=profile.id,
        date_recorded=datetime.utcnow(),
        last_exam_score=obtained_marks,
        total_exams_taken=total_exams_taken,
        exams_passed=exams_passed,
        exams_failed=exams_failed,
        total_points=total_points,
        overall_grade=None,  # Placeholder for now
        overall_percentage=0.0  # Placeholder for now
    )
    session.add(progress_record)
    session.commit()
    session.refresh(progress_record)

    # Recalculate overall grade and percentage
    all_results = session.exec(select(Result).where(Result.student_id == current_user.id)).all()
    if all_results:
        total_obtained = sum(r.obtained_marks for r in all_results)
        total_max = sum(r.total_marks for r in all_results if r.total_marks > 0)

        if total_max > 0:
            overall_percentage = (total_obtained / total_max) * 100
            progress_record.overall_percentage = overall_percentage
            progress_record.overall_grade = calculate_grade(overall_percentage)

    # Save updated progress
    session.add(progress_record)
    session.commit()
    session.refresh(progress_record)

    # Prepare response payload
    response_payload = {
        "overall_result": {
            "result_id": result.id,
            "exam_title": result.exam_title,
            "total_marks": result.total_marks,
            "obtained_marks": result.obtained_marks,
            "grade": result.grade,
            "percentage": result.percentage,
        },
        "question_results": graded_questions,  # Detailed question-level results
        "student_progress": {
            "total_exams_taken": progress_record.total_exams_taken,
            "exams_passed": progress_record.exams_passed,
            "exams_failed": progress_record.exams_failed,
            "total_points": progress_record.total_points,
            "overall_percentage": progress_record.overall_percentage,
            "overall_grade": progress_record.overall_grade
        }
    }

    return response_payload