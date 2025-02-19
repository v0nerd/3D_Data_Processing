import unittest
import sys
from unittest.mock import patch, MagicMock
from pathlib import Path

# Ensure src directory is in sys.path
sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

import main


class TestMain(unittest.TestCase):

    @patch("main.objaverse.load_uids", return_value=["uid1", "uid2", "uid3"])
    @patch("main.download_glb_file")
    @patch("main.validate_and_convert_glb")
    def test_main_flow(self, mock_validate, mock_download, mock_load_uids):
        mock_download.return_value = ("uid1", "obj1", "datasets/uid1.glb", True, "")
        mock_validate.return_value = ("uid1", "obj1", True, "")

        # Run main function
        main.main()

        # Check if download was triggered
        mock_download.assert_called_with(("uid1", "obj1", "datasets"))

        # Check if validation was triggered
        mock_validate.assert_called_with(
            ("uid1", "obj1", "datasets/uid1.glb", "datasets")
        )


if __name__ == "__main__":
    unittest.main()
