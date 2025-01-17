# Helper function to validate file extension
from fastapi import HTTPException, UploadFile
import validators


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