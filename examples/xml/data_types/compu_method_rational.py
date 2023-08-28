"""
CompuMethod examples
"""

import os
import autosar
import autosar.xml.element as ar_element

if __name__ == "__main__":

    # Create package and elements
    package = ar_element.Package("CompuMethods")
    computation = ar_element.Computation.make_rational(scaling_factor=1 / 64,
                                                       offset=0,
                                                       lower_limit=0,
                                                       upper_limit=65535,
                                                       default_value=65535)
    package.append(ar_element.CompuMethod(name='VehicleSpeed_T',
                                          int_to_phys=computation,
                                          category="LINEAR"))
    # Create document
    document = autosar.xml.document.Document()
    document.append(package)

    # Write document to file system
    file_path = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                             'data',
                                             'compu_method_rational_example.arxml'))
    writer = autosar.xml.Writer()
    writer.write_file(document, file_path)

    # Read document from file system
    reader = autosar.xml.Reader()
    document = reader.read_file(file_path)
    compu_method = document.find('/CompuMethods/VehicleSpeed_T')
    print(f"{compu_method.name}: {str(type(compu_method))}")
