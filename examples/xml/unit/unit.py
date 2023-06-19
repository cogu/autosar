"""
Unit example
"""
import os
import autosar
import autosar.xml.element as ar_element


if __name__ == "__main__":

    # Create document
    package = autosar.xml.package.Package('Units')
    elem = ar_element.Unit("KmPerHour", "KmPerHour")
    package.append(elem)
    document = autosar.xml.document.Document()
    document.append(package)

    # Write document to file system
    file_path = os.path.abspath(os.path.join(os.path.dirname(
        __file__), 'data', 'unit_example.arxml'))
    writer = autosar.xml.Writer()
    writer.write_file(document, file_path)

    # Read document from file system
    reader = autosar.xml.Reader()
    document = reader.read_file(file_path)
    unit = document.find('/Units/KmPerHour')
    print(f"{unit.name}: {str(type(unit))}")
