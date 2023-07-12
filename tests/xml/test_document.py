"""Unit tests for Document"""

# pylint: disable=missing-class-docstring, missing-function-docstring
import os
import sys
import unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
import autosar.xml.document as ar_document # noqa E402
import autosar.xml.element as ar_element  # noqa E402


class DocumentTests(unittest.TestCase):

    def test_find_package(self):
        package = ar_element.Package("CompuMethods")
        document = ar_document.Document()
        document.append(package)
        package = document.find("/CompuMethods")
        self.assertIsInstance(package, ar_element.Package)
        self.assertEqual(package.name, "CompuMethods")


if __name__ == '__main__':
    unittest.main()
