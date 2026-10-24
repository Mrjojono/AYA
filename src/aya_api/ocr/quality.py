"""OCR quality scoring."""


def compute_quality(words: list[dict]) -> dict:
    """Compute overall OCR quality."""
    if not words:
        return {"avg_confidence": 0.0, "should_retake": True, "word_count": 0}
    confidences = [w["confidence"] for w in words]
    avg = sum(confidences) / len(confidences)
    # Threshold will be set after tests
    threshold = 0.0
    return {
        "avg_confidence": avg,
        "should_retake": avg < threshold if threshold > 0 else False,
        "word_count": len(words),
        "min_confidence": min(confidences),
        "max_confidence": max(confidences),
    }
