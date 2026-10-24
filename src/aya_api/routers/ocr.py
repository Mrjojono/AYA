"""OCR routes for label extraction."""

import asyncio
import uuid
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from aya_api.db import get_session
from aya_api.ocr.config import ocr_config
from aya_api.ocr.pipeline import OCRPipeline

router = APIRouter(prefix="/ocr", tags=["ocr"])

SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.post("/label")
async def process_label(
    file: Annotated[UploadFile, File()], session: SessionDep = None
) -> dict:
    """Process label image and extract information."""
    # Validate extension
    ext = (
        file.filename.split(".")[-1].lower()
        if file.filename and "." in file.filename
        else ""
    )
    if ext not in ocr_config.allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported format. Allowed: {ocr_config.allowed_extensions}",
        )

    # Read content
    content = await file.read()
    max_size = ocr_config.max_upload_size_mb * 1024 * 1024
    if len(content) > max_size:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max: {ocr_config.max_upload_size_mb}MB",
        )

    # Save to temp
    tmp_dir = Path(ocr_config.tmp_dir)
    await asyncio.to_thread(tmp_dir.mkdir, parents=True, exist_ok=True)
    filename = f"{uuid.uuid4()}.{ext}"
    filepath = tmp_dir / filename
    await asyncio.to_thread(filepath.write_bytes, content)

    # Process
    pipeline = OCRPipeline()
    try:
        result = await pipeline.process(filepath)
        return {
            "processing_id": str(uuid.uuid4()),
            "filename": file.filename,
            **result,
        }
    except HTTPException:
        raise
    except Exception as e:
        # Ensure cleanup on error
        try:
            if await asyncio.to_thread(filepath.exists):
                await asyncio.to_thread(filepath.unlink)
        except OSError:
            pass
        raise HTTPException(
            status_code=500, detail=f"OCR processing failed: {e!s}"
        ) from e
