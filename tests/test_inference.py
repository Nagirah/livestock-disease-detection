import sys
from pathlib import Path
import unittest
import numpy as np
from PIL import Image
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))
from inference import load_config, prepare_image, read_probabilities, model_path_for

class InferenceTests(unittest.TestCase):
    def test_assets_and_labels(self):
        config, labels = load_config()
        self.assertEqual(labels["goat"], ["goatpox", "healthy"])
        self.assertEqual(labels["cattle"], ["healthy", "lumpy_skin"])
        for species in ["goat", "cattle"]:
            self.assertTrue(model_path_for(species, config).is_file())
            self.assertEqual(config[species]["image_size"], [224,224])

    def test_raw_pixel_scale(self):
        pixels = prepare_image(Image.new("RGB", (10,10), (255,128,0)), [224,224])
        self.assertEqual(pixels.shape, (1,224,224,3))
        self.assertEqual(pixels.dtype, np.float32)
        self.assertEqual(pixels[0,0,0].tolist(), [255.0,128.0,0.0])

    def test_probabilities(self):
        scores = read_probabilities([[0.2,0.8]], ["goatpox", "healthy"])
        self.assertEqual(scores[0][0], "healthy")
        with self.assertRaises(ValueError):
            read_probabilities([[0.5,0.5,0.0]], ["goatpox", "healthy"])

if __name__ == "__main__":
    unittest.main()
