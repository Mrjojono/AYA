"""Tests for OCR pipeline."""

from pathlib import Path


def test_etiquettes_dir_exists() -> None:
    """Test that etiquettes test directory exists."""
    path = Path("tests/etiquettes")
    assert path.exists()


def test_pipeline_structure() -> None:
    """Test OCR pipeline modules exist."""
    import aya_api.ocr.engine  # noqa: F401
    import aya_api.ocr.extract  # noqa: F401
    import aya_api.ocr.pipeline  # noqa: F401
    import aya_api.ocr.preprocess  # noqa: F401
    import aya_api.ocr.quality  # noqa: F401

    assert aya_api.ocr.preprocess is not None
    assert aya_api.ocr.engine is not None
    assert aya_api.ocr.quality is not None
    assert aya_api.ocr.extract is not None
    assert aya_api.ocr.pipeline is not None
