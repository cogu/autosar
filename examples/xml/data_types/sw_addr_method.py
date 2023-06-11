"""
SwAddrMethod example
"""
import os
import autosar
import autosar.xml.element as ar_element


if __name__ == "__main__":

    #Create document
    package = autosar.xml.package.Package('SwAddrMethod')
    elem = ar_element.SwAddrMethod('DEFAULT')
    package.append(elem)
    document = autosar.xml.document.Document()
    document.append(package)

    file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data', 'sw_addr_method_example.arxml'))
    #Write document to file system
    writer = autosar.xml.Writer()
    writer.write_file(document, file_path)

    #Read document from file system
    reader = autosar.xml.Reader()
    document = reader.read_file(file_path)
    addr_method = document.find('/SwAddrMethod/DEFAULT')
    print(f"{addr_method.name}: {str(type(addr_method))}")
