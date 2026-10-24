"""Image preprocessing for OCR."""

from pathlib import Path

import cv2
import numpy as np
from PIL import Image


def preprocess_image(input_path: Path, output_path: Path | None = None) -> Path:
    """Preprocess image for better OCR results."""
    img = cv2.imread(str(input_path))
    if img is None:
        raise ValueError(f"Cannot read image {input_path}")

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Enhance contrast
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    # Denoise
    denoised = cv2.fastNlMeansDenoising(enhanced, h=10)

    # Binary threshold
    _, binary = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    if output_path is None:
        output_path = input_path.with_suffix(".preprocessed.png")

    cv2.imwrite(str(output_path), binary)
    return output_path
