Packages Guide
==============

AUTOSAR packages contains elements or sub-packages. AUTOSAR elements can be categorized into these four groups:

- Data Types
- Constants
- Port Interfaces
- Component Types

Package Roles
-------------

The Python AUTOSAR module uses the concept of package roles in order to simplify the creation (and search) of AUTOSAR elements programmatically.
This is especially useful when creating data types which will become apparent later.
If, for example the CompuMethod role has been set by the user, the AUTOSAR Python module knows where to place automatically created
CompuMethod objects while processing a request to create a new user-defined data type.

**Roles related to Data Types**

+----------------+------------------------------+-----------------+
| Role Name      | Description                  | AUTOSAR Version |
+================+==============================+=================+
| DataType       | DataType elements            |   3 and 4       |
+----------------+------------------------------+-----------------+
| CompuMethod    | CompuMethod elements         |   3 and 4       |
+----------------+------------------------------+-----------------+
| Unit           | DataTypeUnitElement elements |   3 and 4       |
+----------------+------------------------------+-----------------+
| BaseType       | BaseType elements            |   4             |
+----------------+------------------------------+-----------------+
| DataConstraint | DataConstraint elements      |   4             |
+----------------+------------------------------+-----------------+

**Roles related to Constants**

+----------------+------------------------------+-----------------+
| Role Name      | Description                  | AUTOSAR Version |
+================+==============================+=================+
| Constant       | Constant elements            |   3 and 4       |
+----------------+------------------------------+-----------------+


**Roles related to Port Interfaces**

+----------------+-------------------------------+-----------------+
| Role Name      | Description                   | AUTOSAR Version |
+================+===============================+=================+
| PortInterface  | Constant elements             |   3 and 4       |
+----------------+-------------------------------+-----------------+
| ModeDclrGroup  | ModeDeclarationGroup elements |   3 and 4       |
+----------------+-------------------------------+-----------------+

**Roles related to ComponentTypes**

+----------------+------------------------------+-----------------+
| Role Name      | Description                  | AUTOSAR Version |
+================+==============================+=================+
| ComponentType  | ComponentType elements       |   3 and 4       |
+----------------+------------------------------+-----------------+

Creating packages
-----------------

Packages are created in the workspace using the Workspace.createPackage(name, role) method.
Sub-packages are created using the the Package.createSubPackage(name, role) method.

Examples
--------

**AUTOSAR 3:**

.. code-block:: python

    import autosar
    
    ws = autosar.workspace(version='3.0.2')
    
    #Create data type packages
    datatypes = ws.createPackage('DataType', role='DataType')
    datatypes.createSubPackage('DataTypeSemantics', role='CompuMethod')
    datatypes.createSubPackage('DataTypeUnits', role='Unit')
    
    #Create constant package
    ws.createPackage('Constant', role="Constant")
    
    #Create port interface packages
    ws.createPackage('PortInterface', role='PortInterface')
    ws.createPackage('ModeDclrGroup', role='ModeDclrGroup')
    
    #Create component type package
    ws.createPackage('ComponentType', role='ComponentType')
    
    

**AUTOSAR 4:**

.. code-block:: python
    
    import autosar
    
    ws = autosar.workspace(version='4.2.2')
    
    #Create data type packages
    datatypes = ws.createPackage('DataTypes', role='DataType')
    datatypes.createSubPackage('BaseTypes', role='BaseType')
    datatypes.createSubPackage('CompuMethods', role='CompuMethod')
    datatypes.createSubPackage('DataConstrs', role='DataConstraint')
    datatypes.createSubPackage('Units', role='Unit')
    
    #Create constants package
    ws.createPackage('Constants', role="Constant")
    
    #Create port interface package
    ws.createPackage('PortInterfaces', role="PortInterface")
    ws.createPackage('ModeDclrGroups', role="ModeDclrGroup")
    
    #Create component type package
    ws.createPackage('ComponentTypes', role='ComponentType')

Exporting packages to XML data
--------------------------------

Once you are done creating the packages and elements that you need, you might want to export your work as an XML file.

Saving your workspace as a single XML file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is the simplest method, all you need to do is call the Workspace.saveXML(filename) method.

**Example:**

.. code-block:: python

    import autosar
    
    ws = autosar.workspace(version='4.2.2')
        
    ws.createPackage('DataTypes', role='DataType')
    ws.createPackage('Constants', role="Constant")
    ws.createPackage('PortInterfaces', role="PortInterface")
    ws.createPackage('ModeDclrGroups', role="ModeDclrGroup")
    ws.createPackage('ComponentTypes', role='ComponentType')
    
    #save the file as XML
    ws.saveXML('Workspace.arxml')

**Workspace.arxml:**

.. code-block:: xml

    <?xml version="1.0" encoding="utf-8"?>
    <AUTOSAR xsi:schemaLocation="http://autosar.org/schema/r4.0 AUTOSAR_4-2-2.xsd" xmlns="http://autosar.org/schema/r4.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
      <AR-PACKAGES>
        <AR-PACKAGE>
          <SHORT-NAME>DataTypes</SHORT-NAME>
        </AR-PACKAGE>
        <AR-PACKAGE>
          <SHORT-NAME>Constants</SHORT-NAME>
        </AR-PACKAGE>
        <AR-PACKAGE>
          <SHORT-NAME>PortInterfaces</SHORT-NAME>
        </AR-PACKAGE>
        <AR-PACKAGE>
          <SHORT-NAME>ModeDclrGroups</SHORT-NAME>
        </AR-PACKAGE>
        <AR-PACKAGE>
          <SHORT-NAME>ComponentTypes</SHORT-NAME>
        </AR-PACKAGE>
      </AR-PACKAGES>
    </AUTOSAR>


Saving your workspace to multiple XML files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This can be achieved by using the filters argument of the Workspace.saveXML() method. The filters argument must be a list of strings
where each string is a reference to either a package or an element. The last character of a filter string can be '*' which is treated
as a wildcard character.

**Example:**

.. code-block:: python

    import autosar
    
    ws = autosar.workspace(version='4.2.2')
        
    ws.createPackage('DataTypes', role='DataType')
    ws.createPackage('Constants', role="Constant")
    ws.createPackage('PortInterfaces', role="PortInterface")
    ws.createPackage('ModeDclrGroups', role="ModeDclrGroup")
    ws.createPackage('ComponentTypes', role='ComponentType')
    
    #save workspace packages into XML files
    ws.saveXML('DataTypes.arxml', filters=['/DataTypes'])
    ws.saveXML('Constants.arxml', filters=['/Constants'])
    ws.saveXML('PortInterfaces.arxml', filters=['/PortInterfaces', '/ModeDclrGroups'])
    ws.saveXML('ComponentTypes.arxml', filters=['/ComponentTypes'])    

**DataTypes.arxml:**

.. code-block:: xml

    <?xml version="1.0" encoding="utf-8"?>
    <AUTOSAR xsi:schemaLocation="http://autosar.org/schema/r4.0 AUTOSAR_4-2-2.xsd" xmlns="http://autosar.org/schema/r4.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
      <AR-PACKAGES>
        <AR-PACKAGE>
          <SHORT-NAME>DataTypes</SHORT-NAME>
        </AR-PACKAGE>
      </AR-PACKAGES>
    </AUTOSAR>

**Constants.arxml:**

.. code-block:: xml

    <?xml version="1.0" encoding="utf-8"?>
    <AUTOSAR xsi:schemaLocation="http://autosar.org/schema/r4.0 AUTOSAR_4-2-2.xsd" xmlns="http://autosar.org/schema/r4.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
      <AR-PACKAGES>
        <AR-PACKAGE>
          <SHORT-NAME>Constants</SHORT-NAME>
        </AR-PACKAGE>
      </AR-PACKAGES>
    </AUTOSAR>

**PortInterfaces.arxml:**

.. code-block:: xml

    <?xml version="1.0" encoding="utf-8"?>
    <AUTOSAR xsi:schemaLocation="http://autosar.org/schema/r4.0 AUTOSAR_4-2-2.xsd" xmlns="http://autosar.org/schema/r4.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
      <AR-PACKAGES>
        <AR-PACKAGE>
          <SHORT-NAME>PortInterfaces</SHORT-NAME>
        </AR-PACKAGE>
        <AR-PACKAGE>
          <SHORT-NAME>ModeDclrGroups</SHORT-NAME>
        </AR-PACKAGE>
      </AR-PACKAGES>
    </AUTOSAR>

**ComponentTypes.arxml:**

.. code-block:: xml

    <?xml version="1.0" encoding="utf-8"?>
    <AUTOSAR xsi:schemaLocation="http://autosar.org/schema/r4.0 AUTOSAR_4-2-2.xsd" xmlns="http://autosar.org/schema/r4.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
      <AR-PACKAGES>
        <AR-PACKAGE>
          <SHORT-NAME>ComponentTypes</SHORT-NAME>
        </AR-PACKAGE>
      </AR-PACKAGES>
    </AUTOSAR>

