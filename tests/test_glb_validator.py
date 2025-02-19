import unittest
import sys
from pathlib import Path

# Ensure src directory is in sys.path
sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from glb_checker.glb_validator import GLBMeshValidator


class TestGLBValidator(unittest.TestCase):

    def test_valid_glb(self):
        validator = GLBMeshValidator("datasets/sample_valid.glb")
        is_valid, errors = validator.validate()
        self.assertTrue(is_valid)

    def test_invalid_glb(self):
        validator = GLBMeshValidator("datasets/sample_invalid.glb")
        is_valid, errors = validator.validate()
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)


if __name__ == "__main__":
    unittest.main()
