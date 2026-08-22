"""
Demonstrates how the XML parser resumes when an error is encountered
"""
import io
import contextlib
import os
import autosar.xml
import autosar.xml.element as ar_element


def count_elements(package: ar_element.Package) -> int:
    """
    Returns total number of elements in package hierarchy
    """
    total = len(package.elements)
    for sub_package in package.packages:
        total += count_elements(sub_package)
    return total


if __name__ == "__main__":

    file_path = os.path.join(os.path.dirname(__file__), 'data', 'xml_with_errors.arxml')
    # This file contains an invalid numerical constants as well as two duplicates.
    # From the 5 elements in the XML only 2 are successfully placed into the resulting document.
    reader = autosar.xml.Reader()
    output_buf = io.StringIO()
    with contextlib.redirect_stdout(output_buf):
        document = reader.read_file(file_path)

    log = output_buf.getvalue()
    assert "Not a number: FiftyFive" in log
    assert "Element with SHORT-NAME 'C_HazardSwitchIllumination_IV' already exists" in log
    assert len(document.packages) == 1
    assert count_elements(document.packages[0]) == 2
