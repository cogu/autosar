"""
SwAddrMethod example
"""
import os
import autosar.xml
import autosar.xml.element as ar_element


def print_package_stats(package: ar_element.Package, parent: str = "/"):
    """
    Prints number of elements in package and sub-packages
    """
    print(f'Number of elements in "{parent}{package.name}": {len(package.elements)}')
    parent_path = parent + package.name + "/"
    for sub_package in package.packages:
        print_package_stats(sub_package, parent_path)


if __name__ == "__main__":

    file_path = os.path.join(os.path.dirname(__file__), 'data', 'xml_with_errors.arxml')
    # This file contains an invalid numerical constants as well as two duplicates.
    # From the 5 elements in the XML only 2 is successfully placed into the resulting document.
    reader = autosar.xml.Reader()
    document = reader.read_file(file_path)
    for pkg in document.packages:
        print_package_stats(pkg)
