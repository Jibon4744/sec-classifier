import unittest
import os

os.environ["OPENAI_API_KEY"] = "fake-key-for-testing"

from PIL import Image
from app.core.config import settings

class TestImageConfiguration(unittest.TestCase):
    def test_max_image_pixels_applied_process_wide(self):
        """Verifies the PIL decompression-bomb guard is raised above its default."""
        self.assertEqual(Image.MAX_IMAGE_PIXELS, settings.MAX_IMAGE_PIXELS)
        self.assertGreater(settings.MAX_IMAGE_PIXELS, 178_956_970)

if __name__ == '__main__':
    unittest.main()
