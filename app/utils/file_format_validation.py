from fastapi import HTTPException, UploadFile


def validate_file_extension(file: UploadFile, expected_extensions: list):
    if not any(file.filename.endswith(ext) for ext in expected_extensions):
        raise HTTPException(
            status_code=400,
            detail=f"Incorrect file format. Expected one of: {', '.join(expected_extensions)}"
        )