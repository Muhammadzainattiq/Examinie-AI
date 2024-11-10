from typing import Optional
import zipfile
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlmodel import Session
from app.models.content import Content
from app.models.user import User
from app.utils.auth import get_current_user
from app.utils.db import get_session
upload_router = APIRouter(prefix = "/upload")
from app.models.enum import FileType
from app.utils.text_extraction import (
    get_pdf_text,
    get_docx_text,
    get_pptx_text,
    get_web_contents,
    get_xlsx_text,
    get_image_text,
    extract_yt_transcript
)  # Import your functions

upload_router = APIRouter()

@upload_router.post("/upload_free_text/")
async def upload_free_text(
    title: str = Form(...),
    text: str = Form(...),
    file_type: FileType = Form(FileType.FREE_TEXT),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    
    contents = text
    content_entry = Content(title=title, description=text, file_type=file_type, contents=contents)
    session.add(content_entry)
    session.commit()
    session.refresh(content_entry)
    
    return {"message": "Free text content uploaded successfully", "contents": contents}

@upload_router.post("/upload_topic/")
async def tell_a_topic(
    title: str = Form(...),
    topic: Optional[str] = Form(None),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    if not topic:
        raise HTTPException(status_code=400, detail="Description is required for topic.")
    content_entry = Content(
        title=title,
        description=topic,
        file_type="TOPIC",
        contents=topic
    )
    session.add(content_entry)
    session.commit()
    session.refresh(content_entry)
    return {"message": "Topic added successfully", "contents": topic}

@upload_router.post("/upload_document/")
async def upload_document(
    title: str = Form(...),
    file_type: FileType = Form(...),
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    
    file_data = await file.read()
    contents = ""
    
    if file_type == FileType.PDF:
        contents = get_pdf_text(file_data)
    elif file_type == FileType.DOCX:
        contents = get_docx_text(file_data)
    elif file_type == FileType.XLSX:
        contents = get_xlsx_text(file_data)
    elif file_type == FileType.PPTX:
        try:
            contents = get_pptx_text(file_data)
        except zipfile.BadZipFile:
            raise HTTPException(status_code=400, detail="Uploaded PPTX file is not valid or corrupted.")
    elif file_type == FileType.IMAGE:
        contents = get_image_text(file_data)
    else:
        raise HTTPException(status_code=400, detail="Unsupported document type.")
    
    content_entry = Content(title=title, file_type=file_type, contents=contents)
    session.add(content_entry)
    session.commit()
    session.refresh(content_entry)
    
    return {"message": f"{file_type} document uploaded and processed successfully", "contents": contents}

@upload_router.post("/upload_youtube_video/")
async def upload_youtube_video(
    title: str = Form(...),
    url: str = Form(...),
    file_type: FileType = Form(FileType.Youtube_Video),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    
    contents = extract_yt_transcript(url)
    content_entry = Content(title=title, file_type=file_type, contents=contents)
    session.add(content_entry)
    session.commit()
    session.refresh(content_entry)
    
    return {"message": "YouTube video transcript extracted successfully", "contents": contents}

@upload_router.post("/upload_web_article/")
async def upload_web_article(
    title: str = Form(...),
    url: str = Form(...),
    file_type: FileType = Form(FileType.ARTICLE),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    
    contents = get_web_contents(url)
    content_entry = Content(title=title, file_type=file_type, contents=contents)
    session.add(content_entry)
    session.commit()
    session.refresh(content_entry)
    
    return {"message": "Web article content extracted successfully", "contents": contents}

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
        raise HTTPException(status_code=400, detail="Unsupported file format for exams. Only PDF and DOCX are allowed.")
    
    content_entry = Content(title=title, file_type=file_type, contents=contents)
    session.add(content_entry)
    session.commit()
    session.refresh(content_entry)
    
    return {"message": "Exam file uploaded and processed successfully", "contents": contents}
