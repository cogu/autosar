"""Unit tests for Document"""

# pylint: disable=missing-class-docstring, missing-function-docstring
import os
import sys
import unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
import autosar.xml.document as ar_document # noqa E402
import autosar.xml.element as ar_element  # noqa E402
import autosar.xml  # noqa E402


class DocumentTests(unittest.TestCase):

    def test_find_package(self):
        package = ar_element.Package("CompuMethods")
        document = ar_document.Document()
        document.append(package)
        package = document.find("/CompuMethods")
        self.assertIsInstance(package, ar_element.Package)
        self.assertEqual(package.name, "CompuMethods")

    def test_read_write_document_with_multi_level_package_structure(self):
        workspace = autosar.xml.Workspace()
        workspace.make_packages("DataTypes/BaseTypes",
                                "DataTypes/ImplementationDataTypes")
        document1 = ar_document.Document([workspace.find("/DataTypes")])
        writer = autosar.xml.Writer()
        xml = writer.write_str(document1, False)
        reader = autosar.xml.Reader()
        document2 = reader.read_str(xml, stop_on_error=True)
        self.assertEqual(len(document2.packages), 1)
        datatype_package: ar_element.Package = document2.find("/DataTypes")
        self.assertEqual(len(datatype_package.packages), 2)
        base_types_package: ar_element.Package = document2.find("/DataTypes/BaseTypes")
        impl_types_package: ar_element.Package = document2.find("/DataTypes/ImplementationDataTypes")
        self.assertEqual(base_types_package.name, "BaseTypes")
        self.assertEqual(impl_types_package.name, "ImplementationDataTypes")


if __name__ == '__main__':
    unittest.main()
