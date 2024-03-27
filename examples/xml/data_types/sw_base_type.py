"""
SwBaseType example
"""
import os
import autosar.xml
import autosar.xml.element as ar_element


if __name__ == "__main__":

    # Create document
    package = ar_element.Package('BaseTypes')
    elem = ar_element.SwBaseType('Typename')
    package.append(elem)
    document = autosar.xml.Document()
    document.append(package)

    # Write document to file system
    file_path = os.path.join(os.path.dirname(__file__), 'data', 'sw_base_type_example.arxml')
    writer = autosar.xml.Writer()
    writer.write_file(document, file_path)

    # Read document from file system
    reader = autosar.xml.Reader()
    document = reader.read_file(file_path)
    data_type = document.find('/BaseTypes/Typename')
    print(f"{data_type.name}: {str(type(data_type))}")
