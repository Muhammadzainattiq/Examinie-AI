from typing import Optional
import zipfile
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlmodel import Session
from app.models.content import Content
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
    
    contents = text
    content_entry = Content(title=title, file_type=file_type, contents=contents)
    session.add(content_entry)
    session.commit()
    session.refresh(content_entry)
    return {"message": "Free text content uploaded successfully", "contents": content_entry}

@upload_router.post("/upload_topic/")
async def tell_a_topic(
    title: str = Form(...),
    topic: str = Form(...),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    if not topic:
        raise HTTPException(status_code=400, detail="Topic must be uploaded")
    content_entry = Content(
        title=title,
        file_type="TOPIC",
        contents=topic
    )
    session.add(content_entry)
    session.commit()
    session.refresh(content_entry)
    return {"message": "Topic added successfully", "contents": content_entry}

# PDF Upload Route
@upload_router.post("/upload_pdf/")
async def upload_pdf(
    title: str = Form(...),
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    validate_file_extension(file, [".pdf"])
    file_data = await file.read()
    contents = get_pdf_text(file_data)
    
    content_entry = Content(title=title, file_type=FileType.PDF, contents=contents)
    session.add(content_entry)
    session.commit()
    session.refresh(content_entry)
    
    return {"message": "PDF document uploaded and processed successfully", "contents": content_entry}


# DOCX Upload Route
@upload_router.post("/upload_docx/")
async def upload_docx(
    title: str = Form(...),
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    validate_file_extension(file, [".docx"])
    file_data = await file.read()
    contents = get_docx_text(file_data)
    
    content_entry = Content(title=title, file_type=FileType.DOCX, contents=contents)
    session.add(content_entry)
    session.commit()
    session.refresh(content_entry)
    
    return {"message": "DOCX document uploaded and processed successfully", "contents": content_entry}


# XLSX Upload Route
@upload_router.post("/upload_xlsx/")
async def upload_xlsx(
    title: str = Form(...),
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    validate_file_extension(file, [".xlsx"])
    file_data = await file.read()
    contents = get_xlsx_text(file_data)
    
    content_entry = Content(title=title, file_type=FileType.XLSX, contents=contents)
    session.add(content_entry)
    session.commit()
    session.refresh(content_entry)
    
    return {"message": "XLSX document uploaded and processed successfully", "contents": content_entry}


# PPTX Upload Route
@upload_router.post("/upload_pptx/")
async def upload_pptx(
    title: str = Form(...),
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    validate_file_extension(file, [".pptx"])
    file_data = await file.read()
    try:
        contents = get_pptx_text(file_data)
    except zipfile.BadZipFile:
        raise HTTPException(status_code=400, detail="Uploaded PPTX file is not valid or corrupted.")
    
    content_entry = Content(title=title, file_type=FileType.PPTX, contents=contents)
    session.add(content_entry)
    session.commit()
    session.refresh(content_entry)
    
    return {"message": "PPTX document uploaded and processed successfully", "contents": content_entry}


# Image Upload Route
@upload_router.post("/upload_image/")
async def upload_image(
    title: str = Form(...),
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    validate_file_extension(file, [".jpg", ".jpeg", ".png", ".bmp"])
    file_data = await file.read()
    contents = get_image_text(file_data)
    
    content_entry = Content(title=title, file_type=FileType.IMAGE, contents=contents)
    session.add(content_entry)
    session.commit()
    session.refresh(content_entry)
    
    return {"message": "Image document uploaded and processed successfully", "contents": content_entry}


# YouTube Video Upload Route
@upload_router.post("/upload_youtube_video/")
async def upload_youtube_video(
    title: str = Form(...),
    url: str = Form(...),
    file_type: FileType = Form(FileType.Youtube_Video),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    validate_url(url)
    contents = extract_yt_transcript(url)
    
    content_entry = Content(title=title, file_type=file_type, contents=contents)
    session.add(content_entry)
    session.commit()
    session.refresh(content_entry)
    
    return {"message": "YouTube video transcript extracted successfully", "contents": content_entry}


# Web Article Upload Route
@upload_router.post("/upload_web_article/")
async def upload_web_article(
    title: str = Form(...),
    url: str = Form(...),
    file_type: FileType = Form(FileType.ARTICLE),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    validate_url(url)
    contents = get_web_contents(url)
    
    content_entry = Content(title=title, file_type=file_type, contents=contents)
    session.add(content_entry)
    session.commit()
    session.refresh(content_entry)
    
    return {"message": "Web article content extracted successfully", "contents": content_entry}


# Exam Upload Route
@upload_router.post("/upload_exam/")
async def upload_exam(
    title: str = Form(...),
    file: UploadFile = File(...),
    file_type: FileType = Form(FileType.EXAM),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    file_data = await file.read()
    contents = ""

    if file.content_type == 'application/pdf':
        contents = get_pdf_text(file_data)
    elif file.content_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
        contents = get_docx_text(file_data)
    else:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file format for exams. Only PDF and DOCX are allowed."
        )
    
    content_entry = Content(title=title, file_type=file_type, contents=contents)
    session.add(content_entry)
    session.commit()
    session.refresh(content_entry)
    
    return {"message": "Exam file uploaded and processed successfully", "contents": content_entry}