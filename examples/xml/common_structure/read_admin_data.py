"""
Read admin data from xml
"""
import os
import autosar


def main():
    """
    Prints some admin-data fields from XML file
    """
    file_path = os.path.join(os.path.dirname(__file__), 'data', 'swc_with_admin_data.arxml')
    reader = autosar.xml.Reader()
    document = reader.read_file(file_path)
    admin_data = document.find("/ComponentTypes/SWC").admin_data
    for sdg in admin_data.sdgs:
        print(f"GID = {sdg.gid}")
        for sd in sdg.content:
            print(sd.text)


if __name__ == "__main__":
    main()
