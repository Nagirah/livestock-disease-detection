"""Run with: python -m unittest discover -s tests -v (from project root)."""
import sys
import unittest
from pathlib import Path
from PIL import Image
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'app'))
from edge_cases import assess_image, prediction_warnings

class EdgeCaseTests(unittest.TestCase):
    def test_tiny_rejected(self):
        error, _ = assess_image(Image.new('RGB', (32, 100), 'gray'))
        self.assertIn('too small', error)

    def test_large_dimensions_rejected(self):
        # Test the pixel-cap condition without constructing a giant image.
        class Stub:
            size = (7000, 6000)
        error, _ = assess_image(Stub())
        self.assertIn('large', error)

    def test_dark_warning(self):
        error, warnings = assess_image(Image.new('RGB', (256, 256), (5, 5, 5)))
        self.assertIsNone(error)
        self.assertTrue(any('dark' in w.lower() for w in warnings))

    def test_overexposed_warning(self):
        error, warnings = assess_image(Image.new('RGB', (256, 256), 'white'))
        self.assertIsNone(error)
        self.assertTrue(any('bright' in w.lower() for w in warnings))

    def test_low_confidence_warning(self):
        self.assertTrue(any('uncertain' in w.lower() for w in prediction_warnings('goatpox', .55)))

    def test_healthy_warning(self):
        self.assertTrue(any('does not rule out' in w for w in prediction_warnings('healthy', .99)))

    def test_high_confidence_disease_no_false_warning(self):
        self.assertEqual(prediction_warnings('goatpox', .98), [])

if __name__ == '__main__':
    unittest.main()
