"""OCR engine interface."""

from pathlib import Path
from typing import Protocol

import pytesseract
from PIL import Image

from aya_api.ocr.config import ocr_config


class OCREngine(Protocol):
    """OCR engine interface."""

    def read_text(self, image_path: Path) -> list[dict]: ...


class TesseractEngine:
    """Tesseract OCR implementation."""

    def __init__(self, lang: str | None = None) -> None:
        self.lang = lang or ocr_config.languages
        if ocr_config.tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = ocr_config.tesseract_cmd

    def read_text(self, image_path: Path) -> list[dict]:
        """Read text with confidence per word."""
        image = Image.open(image_path)
        data = pytesseract.image_to_data(
            image, lang=self.lang, output_type=pytesseract.Output.DICT
        )
        words = []
        n = len(data["text"])
        for i in range(n):
            text = data["text"][i].strip()
            if not text:
                continue
            conf = int(data["conf"][i])
            conf = max(conf, 0)
            words.append(
                {
                    "text": text,
                    "confidence": conf / 100.0,
                    "conf_raw": conf,
                    "block_num": data["block_num"][i],
                    "line_num": data["line_num"][i],
                    "left": data["left"][i],
                    "top": data["top"][i],
                    "width": data["width"][i],
                    "height": data["height"][i],
                }
            )
        return words


def get_engine() -> OCREngine:
    return TesseractEngine()
