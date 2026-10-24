"""Tests for OCR pipeline."""

from pathlib import Path


def test_etiquettes_dir_exists() -> None:
    """Test that etiquettes test directory exists."""
    path = Path("tests/etiquettes")
    assert path.exists()


def test_pipeline_structure() -> None:
    """Test OCR pipeline modules exist."""
    from aya_api.ocr import engine, extract, pipeline, preprocess, quality

    assert preprocess is not None
    assert engine is not None
    assert quality is not None
    assert extract is not None
    assert pipeline is not None
