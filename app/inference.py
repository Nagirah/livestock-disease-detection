"""Model loading and inference for the PentAI demo."""
from pathlib import Path
import json
import numpy as np
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
MODELS_DIR = ROOT / "models"


def load_config():
    with open(MODELS_DIR / "model_config.json", encoding="utf-8") as f:
        config = json.load(f)
    with open(MODELS_DIR / "labels.json", encoding="utf-8") as f:
        labels = json.load(f)
    return config, labels


def prepare_image(image: Image.Image, image_size):
    """RGB uint8 -> batched float32 in 0..255; preprocessing is INSIDE Keras."""
    image = ImageOps.exif_transpose(image).convert("RGB")
    width, height = map(int, image_size)
    image = image.resize((width, height), resample=Image.Resampling.BILINEAR)
    pixels = np.asarray(image, dtype=np.float32)
    return np.expand_dims(pixels, axis=0)


def read_probabilities(prediction, labels):
    values = np.asarray(prediction, dtype=np.float64)
    if values.shape != (1, len(labels)):
        raise ValueError(f"Unexpected output shape: {values.shape}; expected (1, {len(labels)})")
    probs = values[0]
    if not np.all(np.isfinite(probs)) or np.any(probs < 0) or np.any(probs > 1):
        raise ValueError("Model output is not valid probabilities")
    if not np.isclose(probs.sum(), 1.0, atol=1e-3):
        raise ValueError("Softmax probabilities do not sum to 1")
    return sorted(zip(labels, [float(x) for x in probs]), key=lambda pair: pair[1], reverse=True)


def model_path_for(animal, config):
    if animal not in config:
        raise ValueError("Unsupported animal type")
    return MODELS_DIR / config[animal]["model_file"]
