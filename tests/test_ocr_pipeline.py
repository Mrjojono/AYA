"""Tests for OCR pipeline."""

from pathlib import Path


def test_etiquettes_dir_exists() -> None:
    """Test that etiquettes test directory exists."""
    path = Path("tests/etiquettes")
    assert path.exists()


def test_pipeline_structure() -> None:
    """Test OCR pipeline modules exist."""
    import aya_api.ocr.engine
    import aya_api.ocr.extract
    import aya_api.ocr.pipeline
    import aya_api.ocr.preprocess
    import aya_api.ocr.quality

    assert aya_api.ocr.preprocess is not None
    assert engine is not None
    assert quality is not None
    assert extract is not None
    assert pipeline is not None
