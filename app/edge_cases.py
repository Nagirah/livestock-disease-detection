"""Lightweight, model-independent input checks for PentAI.

These checks are heuristics, NOT animal verification, out-of-distribution
recognition, disease diagnosis, or a calibrated uncertainty estimator.
"""
from PIL import Image, ImageFilter, ImageStat

MIN_SIDE = 64
MAX_PIXELS = 35_000_000
LOW_CONFIDENCE_CUTOFF = 0.65  # provisional UI warning; not calibrated


def assess_image(image: Image.Image):
    """Return (blocking_error, advisory_warnings) for a decoded RGB image."""
    width, height = image.size
    if min(width, height) < MIN_SIDE:
        return (f"Image too small ({width}x{height}); use at least {MIN_SIDE}px on each side.", [])
    if width * height > MAX_PIXELS:
        return ("Image dimensions are exceptionally large; upload a smaller photo.", [])

    thumb = image.copy()
    thumb.thumbnail((512, 512))
    gray = thumb.convert("L")
    brightness = ImageStat.Stat(gray).mean[0]
    warnings = []
    if brightness < 35:
        warnings.append("Very dark photo: consider retaking it in better light.")
    elif brightness > 225:
        warnings.append("Very bright photo: details may be washed out.")

    # Edge variation is an imperfect proxy for sharpness; never block on it.
    edge_variation = ImageStat.Stat(gray.filter(ImageFilter.FIND_EDGES)).stddev[0]
    if edge_variation < 10:
        warnings.append("Low image detail: the photo may be blurry or lack useful texture.")
    return (None, warnings)


def prediction_warnings(best_label: str, score: float):
    """Show cautions without pretending these are calibrated probabilities."""
    warnings = []
    if score < LOW_CONFIDENCE_CUTOFF:
        warnings.append("Uncertain model output: review the image and seek veterinary advice.")
    if best_label == "healthy":
        warnings.append("A Healthy classification does not rule out disease or other illness.")
    return warnings
