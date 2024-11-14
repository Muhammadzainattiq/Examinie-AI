from datetime import datetime
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.models.content import Content
from app.models.enum import QuestionType
from app.models.exam import MCQ, Answer, CaseStudy, CodingProblem, EssayQuestion, Exam, ExamAttempt, FillInTheBlank, Question, ShortQuestion, TrueFalseQuestion
from app.schemas.exam import ExamCreate, ExamResponse, QuestionCreate, ExamAttemptCreate, ExamAttemptResponse
from app.models.user import StudentProfile, User
from app.utils.generate_cpqs import generate_coding_problems
from app.utils.generate_csqs import generate_case_studies
from app.utils.generate_fitbqs import generate_fill_in_the_blank
from app.utils.generate_lqs import generate_essay_questions
from app.utils.generate_mcqs import generate_mcqs
from app.utils.auth import get_current_user
from app.utils.db import get_session
from app.utils.generate_sqs import generate_short_questions
from app.utils.generate_tfqs import generate_true_false_questions

exam_router = APIRouter(prefix="/exams")

@exam_router.post("/create_exam/", response_model=ExamResponse)
async def create_exam(
    exam_data: ExamCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
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
                question_id=main_question.id,
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
                question_id=main_question.id
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
                question_id=main_question.id,
                correct_answer=tf_data['correct_answer']
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
                question_id=main_question.id,
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
                question_id=main_question.id,
                correct_answer=fb_data['correct_answer']
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
                question_id=main_question.id,
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
                question_id=main_question.id,
                sample_input=coding_data['sample_input'],
                sample_output=coding_data['sample_output']
            )
            session.add(coding_problem_question)

    # Finalize and save all questions to the database
    session.commit()
    session.refresh(new_exam)
    
    return new_exam



@exam_router.get("/get_exam/{exam_id}", response_model=ExamResponse)
async def get_exam(
    exam_id: UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    # Retrieve a specific exam by ID
    exam = session.get(Exam, exam_id)
    if not exam:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found")
    return exam

@exam_router.post("/start_exam_attempt/{exam_id}/")
async def start_exam_attempt(
    exam_id: UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
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

    return attempt


@exam_router.get("/{exam_id}/questions", response_model=List[QuestionCreate])
async def get_exam_questions(
    exam_id: UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    questions = session.exec(select(Question).where(Question.exam_id == exam_id)).all()
    if not questions:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No questions found for this exam")
    
    # Preload associated data for each question type based on `type`
    enriched_questions = []
    for question in questions:
        question_data = question.dict()
        if question.type == QuestionType.MCQ:
            question_data["mcq"] = session.exec(select(MCQ).where(MCQ.question_id == question.id)).first()
        elif question.type == QuestionType.SHORT:
            question_data["short_question"] = session.exec(select(ShortQuestion).where(ShortQuestion.question_id == question.id)).first()
        elif question.type == QuestionType.TRUE_FALSE:
            question_data["true_false"] = session.exec(select(TrueFalseQuestion).where(TrueFalseQuestion.question_id == question.id)).first()
        elif question.type == QuestionType.ESSAY:
            question_data["essay"] = session.exec(select(EssayQuestion).where(EssayQuestion.question_id == question.id)).first()
        elif question.type == QuestionType.FILL_IN_THE_BLANK:
            question_data["fill_in_the_blank"] = session.exec(select(FillInTheBlank).where(FillInTheBlank.question_id == question.id)).first()
        elif question.type == QuestionType.CASE_STUDY:
            question_data["case_study"] = session.exec(select(CaseStudy).where(CaseStudy.question_id == question.id)).first()
        elif question.type == QuestionType.CODING_PROBLEM:
            question_data["coding_problem"] = session.exec(select(CodingProblem).where(CodingProblem.question_id == question.id)).first()
        
        enriched_questions.append(question_data)
    
    return enriched_questions



@exam_router.post("/complete_exam_attempt/{exam_id}/{attempt_id}", response_model=ExamAttemptResponse)
async def complete_exam_attempt(
    exam_id: UUID,
    attempt_id: UUID,
    score: int,  # Calculated score based on responses
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    # Retrieve the specific exam attempt to mark as completed
    attempt = session.get(ExamAttempt, attempt_id)
    if not attempt or attempt.exam_id != exam_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exam attempt not found")

    # Mark the attempt as completed, add score, and timestamp
    attempt.completed = True
    attempt.score = score
    attempt.submitted_at = datetime.utcnow()
    session.add(attempt)
    session.commit()
    session.refresh(attempt)
    return attempt


@exam_router.post("/add_question/{exam_id}/", response_model=QuestionCreate)
async def add_question_to_exam(
    exam_id: UUID,
    question_data: QuestionCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    exam = session.get(Exam, exam_id)
    if not exam:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found")

    # Create question based on type and add it to the exam
    question = Question(**question_data.dict(), exam_id=exam_id)
    session.add(question)
    session.commit()
    session.refresh(question)
    return question


@exam_router.post("/submit_question_answer/{exam_id}/{question_id}/")
async def submit_answer(
    exam_id: UUID,
    question_id: UUID,
    response: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
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

    # Record the user's answer without checking correctness
    answer = Answer(
        attempt_id=attempt.id,  # Associate with the current attempt
        question_id=question_id,
        response=response
    )
    session.add(answer)
    session.commit()
    session.refresh(answer)
    
    return answer
