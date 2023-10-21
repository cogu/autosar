"""
Unit example
"""
import os
import autosar.xml
from autosar.xml.document import Document
import autosar.xml.element as ar_element


if __name__ == "__main__":

    # Create document
    package = ar_element.Package('Units')
    elem = ar_element.Unit("KmPerHour", "KmPerHour")
    package.append(elem)
    document = Document()
    document.append(package)

    # Write document to file system
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))
    file_path = os.path.join(base_path, "unit_example.arxml")
    writer = autosar.xml.Writer()
    writer.write_file(document, file_path)

    # Read document from file system
    reader = autosar.xml.Reader()
    document = reader.read_file(file_path)
    unit = document.find('/Units/KmPerHour')
    print(f"{unit.name}: {str(type(unit))}")
