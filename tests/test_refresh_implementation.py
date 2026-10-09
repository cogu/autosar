"""Tests for implementation indexing after the element package rename."""

import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from dev_utils import refresh_implementation  # noqa: E402


class TestElementIndex(unittest.TestCase):
    def test_parse_package(self):
        package_init = REPO_ROOT / "src" / "autosar" / "xml" / "element" / "__init__.py"
        with patch.object(refresh_implementation, "_get_git_class_versions", return_value=({}, [])) as versions:
            result = refresh_implementation.parse_element_file(str(package_init))
        versions.assert_called_once_with(str(REPO_ROOT))
        for name in ["AdminData", "Unit", "Package", "SwcInternalBehavior", "ApplicationPrimitiveDataType"]:
            with self.subTest(name=name):
                self.assertIn(name, result["classes"])
        self.assertEqual(result["classes"]["AdminData"]["category"], "AdminData")
        self.assertEqual(result["classes"]["ApplicationPrimitiveDataType"]["category"], "DataType")
        self.assertTrue(result["classes"]["ApplicationPrimitiveDataType"]["package_element"])
        self.assertEqual(result["tag_variants"]["APPLICATION-PRIMITIVE-DATA-TYPE"], "ApplicationPrimitiveDataType")

    def test_refresh_cache(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "cache.json")
            with patch.object(refresh_implementation, "_get_git_class_versions", return_value=({}, [])):
                result = refresh_implementation.refresh_cache(str(REPO_ROOT), output_path=output_path)
            self.assertIn("Package", result["classes"])
            self.assertIn("ValueFormat", result["enums"])
            self.assertIn("PackageRef", result["references"])
            self.assertTrue(os.path.isfile(output_path))

    def test_release_history_paths(self):
        package_file = "src/autosar/xml/element/package.py"
        with patch.object(refresh_implementation.subprocess, "check_output",
                          side_effect=["v0.5.7\n", "", package_file + "\n", "class Package:\n    pass\n"]) as git:
            classes, tags = refresh_implementation._get_git_class_versions(str(REPO_ROOT))
        self.assertEqual(tags, ["v0.5.7"])
        self.assertEqual(classes, {"v0.5.7": {"Package"}})
        self.assertEqual(git.call_args_list[2].args[0],
                         ["git", "ls-tree", "-r", "--name-only", "v0.5.7",
                          "src/autosar/xml/element", "src/autosar/xml/elements"])


if __name__ == "__main__":
    unittest.main()
