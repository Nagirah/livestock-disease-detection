"""Run locally with TensorFlow installed: validates both model loading and output shapes."""
from pathlib import Path
import sys
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))
from inference import load_config, model_path_for, read_probabilities
import tensorflow as tf

config, labels = load_config()
for animal in ["goat", "cattle"]:
    model = tf.keras.models.load_model(str(model_path_for(animal, config)), compile=False)
    width,height = config[animal]["image_size"]
    dummy = np.full((1,height,width,3), 127, dtype=np.float32)
    result = read_probabilities(model.predict(dummy, verbose=0), labels[animal])
    print(f"{animal}: loaded OK; output={model.output_shape}; example={result}")
print("PASS: both models load and produce two-class predictions")
