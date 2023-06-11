"""
CompuMethod examples
"""

import os
import autosar
import autosar.xml.element as ar_element

if __name__ == "__main__":

    # Create package and elements
    package = autosar.xml.package.Package("CompuMethods")
    computation = ar_element.Computation.make_value_table(["FALSE", "TRUE"],
                                                          default_value="FALSE")
    package.append(ar_element.CompuMethod(name='boolean',
                                          int_to_phys=computation,
                                          category="TEXTTABLE"))
    # Create document
    document = autosar.xml.document.Document()
    document.append(package)

    # Write document to file system
    file_path = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                             'data',
                                             'compu_method_value_table_example.arxml'))
    writer = autosar.xml.Writer()
    writer.write_file(document, file_path)

    # Read document from file system
    reader = autosar.xml.Reader()
    document = reader.read_file(file_path)
    compu_method = document.find('/CompuMethods/boolean')
    print(f"{compu_method.name}: {str(type(compu_method))}")
