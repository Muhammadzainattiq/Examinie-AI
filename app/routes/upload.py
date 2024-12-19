from typing import Optional
import zipfile
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlmodel import Session, select
from app.models.content import Content
from app.models.exam import Exam
from app.models.user import User
from app.utils.auth import get_current_user
from app.utils.db import get_session
from app.models.enum import FileType
from app.utils.file_format_validation import validate_file_extension
import validators
from app.utils.text_extraction import (
    get_pdf_text,
    get_docx_text,
    get_pptx_text,
    get_web_contents,
    get_xlsx_text,
    get_image_text,
    extract_yt_transcript
) 

upload_router = APIRouter(prefix = "/content_upload")


# Helper function to validate file extension
def validate_file_extension(file: UploadFile, expected_extensions: list):
    if not any(file.filename.endswith(ext) for ext in expected_extensions):
        raise HTTPException(
            status_code=400,
            detail=f"Incorrect file format. Expected one of: {', '.join(expected_extensions)}"
        )

# Helper function to validate URLs
def validate_url(url: str):
    if not validators.url(url):
        raise HTTPException(
            status_code=400,
            detail="Invalid URL format. Please provide a valid URL."
        )


@upload_router.post("/upload_free_text/")
async def upload_free_text(
    title: str = Form(...),
    text: str = Form(...),
    file_type: FileType = Form(FileType.FREE_TEXT),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    if not title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty.")
    if not text.strip():
        raise HTTPException(status_code=400, detail="Content cannot be empty.")
    
    try:
        contents = text.strip()
        content_entry = Content(
            title=title.strip(), 
            file_type=file_type, 
            contents=contents, 
            user_id=current_user.id
        )
        session.add(content_entry)
        session.commit()
        session.refresh(content_entry)
        return {"message": "Free text content uploaded successfully", "contents": content_entry}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@upload_router.post("/upload_topic/")
async def tell_a_topic(
    title: str = Form(...),
    topic: str = Form(...),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    if not title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty.")
    if not topic.strip():
        raise HTTPException(status_code=400, detail="Topic must not be empty.")
    
    try:
        content_entry = Content(
            title=title.strip(),
            file_type=FileType.TOPIC,
            contents=topic.strip(),
            user_id=current_user.id
        )
        session.add(content_entry)
        session.commit()
        session.refresh(content_entry)
        return {"message": "Topic added successfully", "contents": content_entry}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@upload_router.post("/upload_pdf/")
async def upload_pdf(
    title: str = Form(...),
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    if not title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty.")
    
    validate_file_extension(file, [".pdf"])
    
    try:
        file_data = await file.read()
        contents = get_pdf_text(file_data).strip()
        if not contents:
            raise HTTPException(status_code=400, detail="PDF content cannot be empty.")
        
        content_entry = Content(
            title=title.strip(), 
            file_type=FileType.PDF, 
            contents=contents, 
            user_id=current_user.id
        )
        session.add(content_entry)
        session.commit()
        session.refresh(content_entry)
        return {"message": "PDF document uploaded and processed successfully", "contents": content_entry}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@upload_router.post("/upload_docx/")
async def upload_docx(
    title: str = Form(...),
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    if not title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty.")
    
    validate_file_extension(file, [".docx"])
    
    try:
        file_data = await file.read()
        contents = get_docx_text(file_data).strip()
        if not contents:
            raise HTTPException(status_code=400, detail="DOCX content cannot be empty.")
        
        content_entry = Content(
            title=title.strip(), 
            file_type=FileType.DOCX, 
            contents=contents, 
            user_id=current_user.id
        )
        session.add(content_entry)
        session.commit()
        session.refresh(content_entry)
        return {"message": "DOCX document uploaded and processed successfully", "contents": content_entry}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@upload_router.post("/upload_xlsx/")
async def upload_xlsx(
    title: str = Form(...),
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    if not title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty.")
    
    validate_file_extension(file, [".xlsx"])
    
    try:
        file_data = await file.read()
        contents = get_xlsx_text(file_data).strip()
        if not contents:
            raise HTTPException(status_code=400, detail="XLSX content cannot be empty.")
        
        content_entry = Content(
            title=title.strip(), 
            file_type=FileType.XLSX, 
            contents=contents, 
            user_id=current_user.id
        )
        session.add(content_entry)
        session.commit()
        session.refresh(content_entry)
        
        return {"message": "XLSX document uploaded and processed successfully", "contents": content_entry}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@upload_router.post("/upload_pptx/")
async def upload_pptx(
    title: str = Form(...),
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    if not title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty.")
    
    validate_file_extension(file, [".pptx"])
    
    try:
        file_data = await file.read()
        try:
            contents = get_pptx_text(file_data).strip()
        except zipfile.BadZipFile:
            raise HTTPException(status_code=400, detail="Uploaded PPTX file is not valid or corrupted.")
        
        if not contents:
            raise HTTPException(status_code=400, detail="PPTX content cannot be empty.")
        
        content_entry = Content(
            title=title.strip(), 
            file_type=FileType.PPTX, 
            contents=contents, 
            user_id=current_user.id
        )
        session.add(content_entry)
        session.commit()
        session.refresh(content_entry)
        
        return {"message": "PPTX document uploaded and processed successfully", "contents": content_entry}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@upload_router.post("/upload_image/")
async def upload_image(
    title: str = Form(...),
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    if not title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty.")
    
    validate_file_extension(file, [".jpg", ".jpeg", ".png", ".bmp"])
    
    try:
        file_data = await file.read()
        contents = get_image_text(file_data).strip()
        if not contents:
            raise HTTPException(status_code=400, detail="Extracted image content is empty.")
        
        content_entry = Content(
            title=title.strip(),
            file_type=FileType.IMAGE,
            contents=contents,
            user_id=current_user.id
        )
        session.add(content_entry)
        session.commit()
        session.refresh(content_entry)
        
        return {"message": "Image document uploaded and processed successfully", "contents": content_entry}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@upload_router.post("/upload_youtube_video/")
async def upload_youtube_video(
    title: str = Form(...),
    url: str = Form(...),
    file_type: FileType = Form(FileType.Youtube_Video),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    if not title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty.")
    
    validate_url(url)
    
    try:
        contents = extract_yt_transcript(url).strip()
        if not contents:
            raise HTTPException(status_code=400, detail="YouTube transcript is empty.")
        
        content_entry = Content(
            title=title.strip(),
            file_type=file_type,
            contents=contents,
            user_id=current_user.id
        )
        session.add(content_entry)
        session.commit()
        session.refresh(content_entry)
        
        return {"message": "YouTube video transcript extracted successfully", "contents": content_entry}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@upload_router.post("/upload_web_article/")
async def upload_web_article(
    title: str = Form(...),
    url: str = Form(...),
    file_type: FileType = Form(FileType.ARTICLE),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    if not title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty.")
    
    validate_url(url)
    
    try:
        contents = get_web_contents(url).strip()
        if not contents:
            raise HTTPException(status_code=400, detail="Extracted web article content is empty.")
        
        content_entry = Content(
            title=title.strip(),
            file_type=file_type,
            contents=contents,
            user_id=current_user.id
        )
        session.add(content_entry)
        session.commit()
        session.refresh(content_entry)
        
        return {"message": "Web article content extracted successfully", "contents": content_entry}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@upload_router.post("/upload_exam/")
async def upload_exam(
    title: str = Form(...),
    file: UploadFile = File(...),
    file_type: FileType = Form(FileType.EXAM),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    if not title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty.")
    
    try:
        file_data = await file.read()
        contents = ""
        
        if file.content_type == 'application/pdf':
            contents = get_pdf_text(file_data).strip()
        elif file.content_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
            contents = get_docx_text(file_data).strip()
        else:
            raise HTTPException(
                status_code=400,
                detail="Unsupported file format for exams. Only PDF and DOCX are allowed."
            )
        
        if not contents:
            raise HTTPException(status_code=400, detail="Exam content is empty.")
        
        content_entry = Content(
            title=title.strip(),
            file_type=file_type,
            contents=contents,
            user_id=current_user.id
        )
        session.add(content_entry)
        session.commit()
        session.refresh(content_entry)
        
        return {"message": "Exam file uploaded and processed successfully", "contents": content_entry}
    except HTTPException as http_err:
        session.rollback()
        raise http_err
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@upload_router.get("/get_contents_by_student_id/")
async def get_contents_by_student_id(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):    
    try:
        # Query Content table with both conditions
        query = (
            select(Content)
            .outerjoin(Exam, Content.exam_id == Exam.id)
            .where(
                (Exam.student_id == current_user.id) | 
                (Content.exam_id == None) & (Content.user_id == current_user.id)  # Ensure unlinked content belongs to the current user
            )
        )
        contents = session.exec(query).all()

        # Check if contents are empty
        if not contents:
            raise HTTPException(
                status_code=404, detail="No content found for the specified student ID."
            )

        return {"student_id": current_user.id, "contents": contents}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
