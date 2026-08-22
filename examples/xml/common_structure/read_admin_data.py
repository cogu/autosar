"""
Read admin data from xml
"""
import os
import autosar


def main():
    """
    Reads and validates admin-data fields from XML file
    """
    file_path = os.path.join(os.path.dirname(__file__), 'data', 'swc_with_admin_data.arxml')
    reader = autosar.xml.Reader()
    document = reader.read_file(file_path)
    admin_data = document.find("/ComponentTypes/SWC").admin_data
    assert admin_data is not None
    assert len(admin_data.sdgs) == 1
    sdg = admin_data.sdgs[0]
    assert sdg.gid == "Settings"
    assert len(sdg.content) == 1
    assert sdg.content[0].gid == "Enabled"
    assert sdg.content[0].text == "true"


if __name__ == "__main__":
    main()
