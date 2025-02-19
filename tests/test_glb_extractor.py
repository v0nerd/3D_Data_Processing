import unittest
import sys
from pathlib import Path

# Ensure src directory is in sys.path
sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from pbr_extraction.texture_extractor import extract_pbr_textures


class TestTextureExtractor(unittest.TestCase):

    def test_texture_extraction(self):
        textures = extract_pbr_textures("datasets/sample_valid.glb")
        self.assertIsInstance(textures, list)
        self.assertGreater(len(textures), 0)


if __name__ == "__main__":
    unittest.main()
