import os
from autosar.xml import Reader

# Read document from file "data/datatypes.arxml"
base_path = os.path.join(os.path.dirname(__file__), "data")
file_path = os.path.join(base_path, "datatypes.arxml")
reader = Reader()
document = reader.read_file(file_path)
# Find element by reference and then print name and type
data_type = document.find("/DataTypes/ImplementationDataTypes/InactiveActive_T")
print(f"{data_type.name}: {str(type(data_type))}")
