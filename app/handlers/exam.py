from datetime import datetime
from uuid import UUID
from fastapi import  HTTPException, status
from sqlmodel import Session, select
from app.models.content import Content
from app.models.enum import QuestionType
from app.models.exam import MCQ, Answer, CaseStudy, CodingProblem, EssayQuestion, Exam, ExamAttempt, FillInTheBlank, Question, ShortQuestion, TrueFalseQuestion
from app.schemas.exam import BulkAnswerSubmit, ExamCreate
from app.models.user import StudentProfile, User
from app.utils.exam_generation.generate_cpqs import generate_coding_problems
from app.utils.exam_generation.generate_csqs import generate_case_studies
from app.utils.exam_generation.generate_fitbqs import generate_fill_in_the_blank
from app.utils.exam_generation.generate_lqs import generate_essay_questions
from app.utils.exam_generation.generate_mcqs import generate_mcqs
from app.utils.exam_generation.generate_sqs import generate_short_questions
from app.utils.exam_generation.generate_tfqs import generate_true_false_questions

def handle_create_exam(session: Session, current_user: User, exam_data:ExamCreate):
    # Check if the current user has a StudentProfile
    student_profile = session.exec(select(StudentProfile).where(StudentProfile.id == current_user.id)).first()
    
    if student_profile:
         # Fetch the selected contents based on selected_content_ids
        selected_contents = session.exec(
            select(Content).where(Content.id.in_(exam_data.selected_content_ids))
        ).all()

        if not selected_contents:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No valid content found with the provided IDs")
        
        content_list = []

        for content in selected_contents:
            # Extract the necessary fields from the Content model
            content_data = {
                "title": content.title,
                "file_type": content.file_type.value,  # Assuming file_type is an enum (PDF, DOCX, etc.)
                "contents": content.contents,
            }
            
            # Organize them into a format that is more suitable for AI processing
            content_list.append(content_data)
        # Create a new exam and link it to the student profile
        total_marks = exam_data.num_questions * exam_data.marks_per_question
        new_exam = Exam(**exam_data.dict(), student_id=student_profile.id, total_marks=total_marks)
        session.add(new_exam)
        session.commit()
        session.refresh(new_exam)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User does not have a student profile")
    
    # Populate questions based on the type specified in `exam_data`
    if exam_data.questions_type == QuestionType.MCQ:
        mcqs = generate_mcqs(
            no_of_questions=exam_data.num_questions,
            difficulty=exam_data.difficulty.value,
            content=content_list,
            profile_data=student_profile.profile_summary
        )
        
        for mcq_data in mcqs['questions']:
            # Add the main Question record
            main_question = Question(
                exam_id=new_exam.id,
                statement=mcq_data['question'],
                type=QuestionType.MCQ,
                marks=exam_data.marks_per_question
            )
            session.add(main_question)
            session.commit()
            session.refresh(main_question)
            
            # Add the specific MCQ details
            mcq_question = MCQ(
                id=main_question.id,
                option1=mcq_data['option1'],
                option2=mcq_data['option2'],
                option3=mcq_data['option3'],
                option4=mcq_data['option4'],
                correct_option=mcq_data['correct_option'],
                explanation=mcq_data['explanation'] 
            )
            session.add(mcq_question)
    
    elif exam_data.questions_type == QuestionType.SHORT:
        print("exam_data.questions_type: >>>", exam_data.questions_type)
        print("QuestionType.SHORT: >>>", QuestionType.SHORT)
        short_questions = generate_short_questions(
            no_of_questions=exam_data.num_questions,
            difficulty=exam_data.difficulty.value,
            content=content_list,
            profile_data=student_profile.profile_summary
        )
        
        for sq_data in short_questions['questions']:
            main_question = Question(
                exam_id=new_exam.id,
                statement=sq_data,
                type=QuestionType.SHORT,
                marks=exam_data.marks_per_question
            )
            session.add(main_question)
            session.commit()
            session.refresh(main_question)

            short_question = ShortQuestion(
                id=main_question.id
            )
            session.add(short_question)

    elif exam_data.questions_type == QuestionType.TRUE_FALSE:
        true_false_questions = generate_true_false_questions(
            no_of_questions=exam_data.num_questions,
            difficulty=exam_data.difficulty.value,
            content=content_list,
            profile_data=student_profile.profile_summary
        )
        
        for tf_data in true_false_questions['questions']:
            main_question = Question(
                exam_id=new_exam.id,
                statement=tf_data['question'],
                type=QuestionType.TRUE_FALSE,
                marks=exam_data.marks_per_question
            )
            session.add(main_question)
            session.commit()
            session.refresh(main_question)

            true_false_question = TrueFalseQuestion(
                id=main_question.id,
                correct_answer=tf_data['correct_answer'],
                explanation = tf_data['explanation']
            )
            session.add(true_false_question)

    elif exam_data.questions_type == QuestionType.ESSAY:
        essay_questions = generate_essay_questions(
            no_of_questions=exam_data.num_questions,
            difficulty=exam_data.difficulty.value,
            content=content_list,
            profile_data=student_profile.profile_summary
        )
        
        for essay_data in essay_questions['questions']:
            main_question = Question(
                exam_id=new_exam.id,
                statement=essay_data['question'],
                type=QuestionType.ESSAY,
                marks=exam_data.marks_per_question
            )
            session.add(main_question)
            session.commit()
            session.refresh(main_question)

            essay_question = EssayQuestion(
                id=main_question.id,
                guidance=essay_data.get('guidance')
            )
            session.add(essay_question)

    elif exam_data.questions_type == QuestionType.FILL_IN_THE_BLANK:
        fill_in_the_blank_questions = generate_fill_in_the_blank(
            no_of_questions=exam_data.num_questions,
            difficulty=exam_data.difficulty.value,
            content=content_list,
            profile_data=student_profile.profile_summary
        )
        
        for fb_data in fill_in_the_blank_questions['questions']:
            main_question = Question(
                exam_id=new_exam.id,
                statement=fb_data['question'],
                type=QuestionType.FILL_IN_THE_BLANK,
                marks=exam_data.marks_per_question
            )
            session.add(main_question)
            session.commit()
            session.refresh(main_question)

            fill_in_the_blank_question = FillInTheBlank(
                id=main_question.id,
                correct_answer=fb_data['correct_answer'],
                explanation = fb_data['explanation']
            )
            session.add(fill_in_the_blank_question)

    elif exam_data.questions_type == QuestionType.CASE_STUDY:
        case_studies = generate_case_studies(
            no_of_questions=exam_data.num_questions,
            difficulty=exam_data.difficulty.value,
            content=content_list,
            profile_data=student_profile.profile_summary
        )
        
        for case_data in case_studies['questions']:
            main_question = Question(
                exam_id=new_exam.id,
                statement=case_data['question'],
                type=QuestionType.CASE_STUDY,
                marks=exam_data.marks_per_question
            )
            session.add(main_question)
            session.commit()
            session.refresh(main_question)

            case_study_question = CaseStudy(
                id=main_question.id,
                expected_response=case_data['expected_response'],
                case_description=case_data['case_description']
            )

            session.add(case_study_question)

    elif exam_data.questions_type == QuestionType.CODING_PROBLEM:
        coding_problems = generate_coding_problems(
            no_of_questions=exam_data.num_questions,
            difficulty=exam_data.difficulty.value,
            content=content_list,
            profile_data=student_profile.profile_summary,
            language=exam_data.language
        )
        
        for coding_data in coding_problems['questions']:
            main_question = Question(
                exam_id=new_exam.id,
                statement=coding_data['question'],
                type=QuestionType.CODING_PROBLEM,
                marks=exam_data.marks_per_question
            )
            session.add(main_question)
            session.commit()
            session.refresh(main_question)

            coding_problem_question = CodingProblem(
                id=main_question.id,
                sample_input=coding_data['sample_input'],
                sample_output=coding_data['sample_output']
            )
            session.add(coding_problem_question)

    # Finalize and save all questions to the database
    session.commit()
    session.refresh(new_exam)
    
    return new_exam


def handle_complete_exam_attempt(
    exam_id: UUID,
    attempt_id: UUID,
    session: Session,
    current_user: User):
    # Retrieve the specific exam attempt to mark as completed
    attempt = session.get(ExamAttempt, attempt_id)
    if not attempt or attempt.exam_id != exam_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exam attempt not found")

    # Mark the attempt as completed, add score, and timestamp
    attempt.completed = True
    attempt.submitted_at = datetime.utcnow()
    session.add(attempt)
    session.commit()
    session.refresh(attempt)
    return attempt



def handle_submit_answer(exam_id: UUID,
    question_id: UUID,
    response: str,
    session: Session,
    current_user: User):
    # Retrieve the question to ensure it belongs to the specified exam
    question = session.get(Question, question_id)
    if not question or question.exam_id != exam_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found in this exam")

    # Retrieve or create the exam attempt for the student
    attempt = session.exec(
        select(ExamAttempt)
        .where(ExamAttempt.exam_id == exam_id)
        .where(ExamAttempt.student_id == current_user.id)
    ).first()

    if not attempt:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Exam attempt not found. Ensure the exam has been started."
        )
    
    # Prevent duplicate answers for the same question
    existing_answer = session.exec(
        select(Answer)
        .where(Answer.attempt_id == attempt.id)
        .where(Answer.question_id == question_id)
    ).first()

    if existing_answer:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Answer for this question has already been submitted"
        )
    
    # Check if the exam attempt is already completed
    if attempt.completed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This exam attempt has already been completed"
        )

    # Record the user's answer
    try:
        answer = Answer(
            attempt_id=attempt.id,
            question_id=question_id,
            response=response
        )
        session.add(answer)
        session.commit()
        session.refresh(answer)
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail="Failed to submit answer")
    
    return {
        "message": "Answer submitted successfully",
        "question_id": question_id,
        "response": response
    }

def handle_start_exam_attempt(exam_id: UUID,
    session: Session,
    current_user: User):
    # Check if the exam with the given exam_id exists
    exam = session.get(Exam, exam_id)
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exam not found"
        )

    # Check if an existing attempt exists; otherwise, create a new one
    attempt = session.exec(
        select(ExamAttempt)
        .where(ExamAttempt.exam_id == exam_id)
        .where(ExamAttempt.student_id == current_user.id)
    ).first()

    if not attempt:
        # Create a new ExamAttempt record
        attempt = ExamAttempt(
            exam_id=exam_id,
            student_id=current_user.id,
            score=None,  # Initialize score
            completed=False
        )
        session.add(attempt)
        session.commit()
        session.refresh(attempt)

    return {
        "message": "Exam attempt started successfully",
        "attempt": attempt
    }


def handle_get_full_exam(
    exam_id: UUID,
    session: Session):
    # Retrieve the exam by its ID
    exam = session.get(Exam, exam_id)
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exam not found"
        )

    # Retrieve associated questions for the exam
    questions = session.exec(select(Question).where(Question.exam_id == exam_id)).all()
    if not questions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No questions found for this exam"
        )

    # Enrich questions with their specific type data
    enriched_questions = []
    for question in questions:
        question_data = question.dict()

        # Use session.get for efficient primary key-based querying
        if question.type == QuestionType.MCQ:
            question_data["question_data"] = session.get(MCQ, question.id)
        elif question.type == QuestionType.SHORT:
            question_data["question_data"] = session.get(ShortQuestion, question.id)
        elif question.type == QuestionType.TRUE_FALSE:
            question_data["question_data"] = session.get(TrueFalseQuestion, question.id)
        elif question.type == QuestionType.ESSAY:
            question_data["question_data"] = session.get(EssayQuestion, question.id)
        elif question.type == QuestionType.FILL_IN_THE_BLANK:
            question_data["question_data"] = session.get(FillInTheBlank, question.id)
        elif question.type == QuestionType.CASE_STUDY:
            question_data["question_data"] = session.get(CaseStudy, question.id)
        elif question.type == QuestionType.CODING_PROBLEM:
            question_data["question_data"] = session.get(CodingProblem, question.id)

        enriched_questions.append(question_data)

    # Add enriched questions to the exam data
    exam_data = exam.dict()
    exam_data["questions"] = enriched_questions

    return exam_data


def handle_sumbit_all_answers(exam_id: UUID,
    bulk_answers: BulkAnswerSubmit,
    session: Session,
    current_user: User):
    # Retrieve or create the exam attempt for the student
    attempt = session.exec(
        select(ExamAttempt)
        .where(ExamAttempt.exam_id == exam_id)
        .where(ExamAttempt.student_id == current_user.id)
    ).first()

    if not attempt:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Exam attempt not found. Ensure the exam has been started."
        )
    
    # Check if the exam attempt is already completed
    if attempt.completed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This exam attempt has already been completed."
        )
    
    # Process each answer
    submitted_answers = []
    # try:
    for answer_data in bulk_answers.answers:
        # Ensure the question exists and belongs to the specified exam
        question = session.get(Question, answer_data.question_id)
        if not question or question.exam_id != exam_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Question with ID {answer_data.question_id} not found in this exam."
            )
        
        # Prevent duplicate answers for the same question
        existing_answer = session.exec(
            select(Answer)
            .where(Answer.attempt_id == attempt.id)
            .where(Answer.question_id == answer_data.question_id)
        ).first()

        if existing_answer:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Answer for question {answer_data.question_id} has already been submitted."
            )

        # Record the user's answer
        new_answer = Answer(
            attempt_id=attempt.id,
            question_id=answer_data.question_id,
            response=answer_data.response
        )
        session.add(new_answer)
        submitted_answers.append({
            "question_id": answer_data.question_id,
            "response": answer_data.response
        })

    session.commit()
    # except Exception as e:
    #     session.rollback()
    #     raise HTTPException(
    #         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #         detail="Failed to submit answers."
        # )

    return {
        "message": "All answers submitted successfully.",
        "submitted_answers": submitted_answers
    }