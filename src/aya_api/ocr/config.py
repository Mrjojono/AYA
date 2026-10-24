"""OCR configuration."""

import os


class OCRConfig:
    """OCR configuration parameters."""

    max_upload_size_mb: int = int(os.getenv("OCR_MAX_UPLOAD_SIZE_MB", "10"))
    allowed_extensions: set[str] | tuple[str, ...] = ("jpg", "jpeg", "png", "webp", "heic")
    tmp_dir: str = os.getenv("OCR_TMP_DIR", "uploads/tmp")
    min_confidence_threshold: float = float(
        os.getenv("OCR_MIN_CONFIDENCE", "0.0")
    )  # set after tests
    grayscale: bool = True
    deskew: bool = True
    enhance_contrast: bool = True
    languages: str = os.getenv("OCR_LANGUAGES", "fra+eng")
    tesseract_cmd: str | None = os.getenv("TESSERACT_CMD")


ocr_config = OCRConfig()
