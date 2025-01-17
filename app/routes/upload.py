from typing import Optional
import zipfile
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlmodel import Session, select
from app.handlers.upload import handle_get_contents_by_student_id, handle_tell_a_topic, handle_upload_docx, handle_upload_exam, handle_upload_free_text, handle_upload_image, handle_upload_pdf, handle_upload_pptx, handle_upload_web_article, handle_upload_youtube_video
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
from app.utils.validating_functions import validate_url 

upload_router = APIRouter(prefix = "/content_upload")


@upload_router.post("/upload_free_text/")
async def upload_free_text(
    title: str = Form(...),
    text: str = Form(...),
    file_type: FileType = Form(FileType.FREE_TEXT),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    return await handle_upload_free_text(title, text, file_type, session, current_user)

@upload_router.post("/upload_topic/")
async def tell_a_topic(
    title: str = Form(...),
    topic: str = Form(...),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    return await handle_tell_a_topic(title, topic, session, current_user)

@upload_router.post("/upload_pdf/")
async def upload_pdf(
    title: str = Form(...),
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    return await handle_upload_pdf(title, file, session, current_user)

@upload_router.post("/upload_docx/")
async def upload_docx(
    title: str = Form(...),
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    return await handle_upload_docx(title, file, session, current_user)

@upload_router.post("/upload_pptx/")
async def upload_pptx(
    title: str = Form(...),
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    return await handle_upload_pptx(file, title, session, current_user)

@upload_router.post("/upload_image/")
async def upload_image(
    title: str = Form(...),
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    return await handle_upload_image(title, file, session, current_user)

@upload_router.post("/upload_youtube_video/")
async def upload_youtube_video(
    title: str = Form(...),
    url: str = Form(...),
    file_type: FileType = Form(FileType.Youtube_Video),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    return await handle_upload_youtube_video(title, url, file_type, session, current_user)

@upload_router.post("/upload_web_article/")
async def upload_web_article(
    title: str = Form(...),
    url: str = Form(...),
    file_type: FileType = Form(FileType.ARTICLE),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    return await handle_upload_web_article(title, url, file_type, session, current_user)

@upload_router.post("/upload_exam/")
async def upload_exam(
    title: str = Form(...),
    file: UploadFile = File(...),
    file_type: FileType = Form(FileType.EXAM),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    return await handle_upload_exam(title, file, file_type, session, current_user)

@upload_router.get("/get_contents_by_student_id/")
async def get_contents_by_student_id(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):    
    return await handle_get_contents_by_student_id(session, current_user)