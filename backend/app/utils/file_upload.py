"""File upload utility functions."""

import os
import uuid
from fastapi import UploadFile, HTTPException, status
from app.core.config import settings

# Allowed MIME types for images
ALLOWED_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
}


async def save_upload_file(upload_file: UploadFile) -> str:
    """Save an uploaded file with security validations."""
    # Validate file exists
    if not upload_file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No filename provided"
        )

    # Validate extension
    ext = upload_file.filename.split(".")[-1].lower() if "." in upload_file.filename else ""
    if ext not in settings.allowed_extensions_list:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File extension '{ext}' not allowed. Allowed: {settings.ALLOWED_EXTENSIONS}"
        )

    # Read file content
    content = await upload_file.read()

    # Check file size
    if len(content) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Max size: {settings.MAX_UPLOAD_SIZE // (1024*1024)}MB"
        )

    # Validate MIME type using python-magic
    try:
        import magic
        mime_type = magic.from_buffer(content, mime=True)
        if mime_type not in ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type. Only images are allowed. Detected: {mime_type}"
            )
    except ImportError:
        # python-magic not installed, skip MIME validation
        pass
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unable to validate file type: {str(e)}"
        )

    # Generate unique filename with safe extension
    unique_filename = f"{uuid.uuid4().hex}.{ext}"

    # Ensure upload directory exists
    upload_dir = settings.UPLOAD_DIR
    os.makedirs(upload_dir, exist_ok=True)

    # Save file
    file_path = os.path.join(upload_dir, unique_filename)
    with open(file_path, "wb") as f:
        f.write(content)

    return unique_filename
