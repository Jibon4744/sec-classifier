import unittest
import numpy as np
from PIL import Image
from unittest.mock import patch, MagicMock

# Set up dummy environment variables before importing settings
import os
os.environ["OPENAI_API_KEY"] = "fake-key-for-testing"

from app.services.classifier import ClassifierService

class TestClassifierService(unittest.TestCase):
    def setUp(self):
        self.service = ClassifierService()

    def test_load_lookup_tables(self):
        """Verifies metadata tables load successfully."""
        self.assertIsNotNone(self.service.diseases_data)
        self.assertIn("Downy Mildew", self.service.diseases_data)
        self.assertIn("Healthy", self.service.diseases_data)
        
        self.assertIsNotNone(self.service.stages_data)
        self.assertIn("Young Bud", self.service.stages_data)
        self.assertIn("Wilted", self.service.stages_data)

    def test_preprocess_image(self):
        """Verifies input image is resized and scaled correctly."""
        # Create dummy image (size 100x100 RGB)
        dummy_img = Image.new("RGB", (100, 100), color="yellow")
        processed = self.service._preprocess_image(dummy_img)
        
        # Check output shape: (1, 224, 224, 3)
        self.assertEqual(processed.shape, (1, 224, 224, 3))
        # Check type
        self.assertEqual(processed.dtype, np.float32)
        # Check scale range: all pixels are 1.0 (since solid yellow divided by 255.0 will be non-zero but <= 1.0)
        self.assertTrue(np.all(processed >= 0.0) and np.all(processed <= 1.0))

    def test_softmax(self):
        """Validates numerical softmax output."""
        logits = np.array([[1.0, 2.0, 3.0]])
        probs = self.service._softmax(logits)
        
        # Softmax sum should be 1.0
        self.assertAlmostEqual(float(np.sum(probs)), 1.0)
        self.assertTrue(probs[0, 2] > probs[0, 1] > probs[0, 0])

    @patch.object(ClassifierService, '_run_ensemble_inference')
    def test_predict_disease(self, mock_inference):
        """Verifies subset prediction correctly extracts disease class and info."""
        # Create solid mock scores array for the 10 classes in class_names order
        # class_names:
        # ['Alternaria leaf spot', 'Downy Mildew', 'Early Bloom', 'Full Bloom', 
        #  'Healthy', 'Mature Bud', 'Powdery Mildew', 'Wilted', 'Wilted leaf', 'Young Bud']
        # Let's mock a high score for "Downy Mildew" (index 1)
        mock_output = np.zeros(10)
        mock_output[1] = 0.9  # Downy Mildew
        mock_output[2] = 0.8  # Early Bloom (should be ignored in disease mode)
        mock_inference.return_value = mock_output
        
        dummy_img = Image.new("RGB", (100, 100), color="green")
        class_name, confidence, info = self.service.predict_disease(dummy_img)
        
        self.assertEqual(class_name, "Downy Mildew")
        # Since it is normalized over the disease subset scores, let's verify it is picked
        self.assertEqual(info["severity"], "high - can cause systemic infection and significant stand loss if it strikes early")

    @patch.object(ClassifierService, '_run_ensemble_inference')
    def test_predict_growth_stage(self, mock_inference):
        """Verifies subset prediction correctly extracts growth stage class and info."""
        # Mock high score for "Mature Bud" (index 5)
        mock_output = np.zeros(10)
        mock_output[5] = 0.95  # Mature Bud
        mock_output[0] = 0.50  # Alternaria leaf spot (should be ignored in stage mode)
        mock_inference.return_value = mock_output
        
        dummy_img = Image.new("RGB", (100, 100), color="yellow")
        class_name, confidence, info = self.service.predict_growth_stage(dummy_img)
        
        self.assertEqual(class_name, "Mature Bud")
        self.assertEqual(info["typical_days_to_harvest"], "approximately 25-35 days remaining")

if __name__ == '__main__':
    unittest.main()
