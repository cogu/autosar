.. _ar4_workspace:

Workspace
=========

.. table::
   :align: left

   +--------------+---------------------------------------------------------+
   | XML tag      | <AUTOSAR>                                               |
   +--------------+---------------------------------------------------------+
   | Module       | autosar.workspace                                       |
   +--------------+---------------------------------------------------------+
   | Inherits     |                                                         |
   +--------------+---------------------------------------------------------+

The autosar workspace class.

Usage
-----

.. code-block:: python

   import autosar

   ws = autosar.workspace("4.2.2")

Factory Methods
---------------

* autosar.workspace

Attributes
-----------

..  table::
    :align: left

    +--------------------------+-------------------------+---------------------------------------------------------+
    | Name                     | Type                    | Description                                             |
    +==========================+=========================+=========================================================+
    | **packages**             | *list*                  | List of packages                                        |
    +--------------------------+-------------------------+---------------------------------------------------------+
    | **version**              | *float*                 | AUTOSAR version using major.minor format                |
    +--------------------------+-------------------------+---------------------------------------------------------+
    | **patch**                | *int*                   | AUTOSAR patch version                                   |
    +--------------------------+-------------------------+---------------------------------------------------------+

Public Properties
-----------------

..  table::
    :align: left

    +--------------------------+-------------------------+---------------------------------------------------------+
    | Name                     | Type                    | Description                                             |
    +==========================+=========================+=========================================================+
    | **version_str**          | *str*                   | Full version string using the major.minor.patch format  |
    +--------------------------+-------------------------+---------------------------------------------------------+

Public Methods
--------------

* :ref:`ar4_workspace_Workspace_loadXML`
* :ref:`ar4_workspace_Workspace_openXML`
* :ref:`ar4_workspace_Workspace_loadPackage`
* :ref:`ar4_workspace_Workspace_listPackages`
* :ref:`ar4_workspace_Workspace_saveXML`
* :ref:`ar4_workspace_Workspace_toXML`
* :ref:`ar4_workspace_Workspace_createPackage`
* :ref:`ar4_workspace_Workspace_find`
* :ref:`ar4_workspace_Workspace_findall`



Method Description
------------------

.. _ar4_workspace_Workspace_loadXML:

loadXML
~~~~~~~

.. py:method:: Workspace.loadXML(filename, [roles=None])

    :param str filename: Path to ARXML file to parse
    :param dict roles: Roles dictionary.

   Automatically opens and loads (imports) all packages found in *filename*. Filename must be a valid .arxml file.
   Roles is an optional dictionary object with roles as key-value pairs where key is the reference of the package and the value is the (package) role name.

Examples
^^^^^^^^

.. code-block:: python

    import autosar

    ws = autosar.workspace()
    ws.loadXML("DataTypes.arxml")


.. code-block:: python

    import autosar

    ws = autosar.workspace()
    ws.loadXML("DataTypes.arxml", roles={"/DataTypes": "DataType"})

.. _ar4_workspace_Workspace_openXML:

openXML
~~~~~~~

.. py:method:: Workspace.openXML(filename)

    :param str filename: Path to ARXML file to parse

    Opens an ARXML file but does not automatically import any packages into the workspace. Use the loadPackage method to customize which packages you want to load.


Example
^^^^^^^

.. code-block:: python

    import autosar

    ws = autosar.workspace()
    ws.openXML("ECU_Extract.arxml")

.. _ar4_workspace_Workspace_loadPackage:

loadPackage
~~~~~~~~~~~

.. py:method:: Workspace.loadPackage(packagename, [role=None]):

    :param str packageName: Name of the package in the ARXML file
    :param str role: Path to ARXML file to parse

    Manually import a package into your current workspace. Use the :ref:`ar4_workspace_Workspace_openXML` method before this call to open a file.
    The loadPackage method can be callled more than once on an opened file.

    The role argument is optionally used to tell what role the package has in the workspace.

Example
^^^^^^^

.. code-block:: python

    import autosar

    ws = autosar.workspace()
    ws.openXML("ECU_Extract.arxml")
    ws.loadPackage('DataTypes', role="DataType")
    ws.loadPackage('PortInterfaces', role="PortInterface")
    ws.loadPackage('Constants', role="Constant")
    ws.loadPackage('ComponentTypes', role='ComponentType')

.. _ar4_workspace_Workspace_listPackages:

listPackages
~~~~~~~~~~~~

.. py:method:: Workspace.listPackages():

    Returns a list of strings containing the top-level packages of the opened ARXML.

Example
^^^^^^^

.. code-block:: python

    import autosar

    ws = autosar.workspace()
    ws.openXML('ECU_Extract.arxml')
    print(ws.listPackages())

.. _ar4_workspace_Workspace_saveXML:

saveXML
~~~~~~~

.. py:method:: Workspace.saveXML(filename, [filters=None], [ignore=None])

    :param str filename: Name of the file to write
    :param filters: Selects what packages, sub-packages or elements to export
    :type filters: list(str)
    :param ignore: Deprecated (might be removed later)
    :type filters: list(str)

    Exports the workspace in ARXML file format. It tries to use the Workspace.version attribute to determine what schema to use.
    Note that the version handling mechanism is currently flawed and does not work correctly for AUTOSAR v4.3, v4.4 (will be implemented later).

    By default this method saves all packages found in the workspace and writes them to the same file.
    You can however split your workspace into multiple ARXML files by using the filters option.

Example
^^^^^^^

.. code-block:: python

    import autosar
    ws = autosar.workspace("4.2.2")

    #Create packages and elements
    ...

    #Save your work into a single ARXML file
    ws.saveXML("single_file.arxml")


Using filters
^^^^^^^^^^^^^

Filters allows you to use reference strings to select what to export.

**Save top-level packages into separate files**

.. code-block:: python

    import autosar

    ...

    ws.saveXML("DataTypes.arxml", filters = ["/DataTypes"])
    ws.saveXML("Constants.arxml", filters = ["/Constants"])
    ws.saveXML("PortInterfaces.arxml", filters = ["/PortInterfaces", "/ModeDclrGroups"])
    ws.saveXML("PlatformTypes.arxml", filters = ["/AUTOSAR_Platform"])

**Save each software component to its own file**

.. include:: examples/saving_components_to_files.py
    :code: python3

.. _ar4_workspace_Workspace_toXML:

toXML
~~~~~

.. py:method:: Workspace.toXML([filters=None], [ignore=None])

    :param filters: Selects what packages, sub-packages or elements to export
    :type filters: list(str)
    :param ignore: Deprecated (Might be removed)
    :type filters: list(str)

    This method works exactly like :ref:`ar4_workspace_Workspace_saveXML` but returns a string instead of writing to a file.


.. _ar4_workspace_Workspace_createPackage:

createPackage
~~~~~~~~~~~~~

.. py:method:: Workspace.createPackage(name, [role=None])

    :param str name: ShortName of the new package
    :param str role: Optional :ref:`package role <ar4_package_roles>`
    :rtype: :ref:`ar4_package_Package`

    creates a new package and appends it to the internal list of packages

Example
^^^^^^^

.. code-block:: python

    import autosar

    ws = autosar.workspace('4.2.2')
    ws.createPackage('DataTypes', role='DataType')
    ws.createPackage('Constants', role='Constant')
    ws.createPackage('PortInterfaces', role='PortInterface')



.. _ar4_workspace_Workspace_find:

find
~~~~

.. py:method:: Workspace.find(ref, [role=None]):

    :param str ref: Reference to package or element
    :param str role: Optional role name

    By using the reference string, this methods attempts to find and return the referenced object from the internal model.
    If no object is found (invalid reference) the value None is returned.

Examples
^^^^^^^^

.. code-block:: python

    #Get the workspace itself
    ws.find("/")

    #Get the package with the name 'DataTypes' (if the package exists)
    ws.find("/DataTypes")

    #Get the CoolantTemp_T data type from the DataTypes package
    ws.find("/DataTypes/CoolantTemp_T")

    #Get the AntiLockBrakingActive Port from the AntiLockBraking component type.
    ws.find("/ComponentTypes/AntiLockBraking/AntiLockBrakingActive")

You can also use the role argument in the find method. This allows you to just give the name of the element you want to find without caring about the full reference string.

.. code-block:: python

    #Get the CoolantTemp_T data type from the package currently associated with the "DataType" role
    ws.find("CoolantTemp_T", role="DataType")

An alternative to using the find method directly is to treat the Workspace object as a dictionary. This allows easier syntax when chaining together method calls.

.. code-block:: python

    #Returns the DataTypes package
    ws["DataTypes"]

    #Sort all elements in the DataTypes package alphabetically by their element name (case insensitive)
    ws['DataTypes'].elements = sorted( ws['DataTypes'].elements, key=lambda x: x.name.lower() )

.. _ar4_workspace_Workspace_findall:

findall
~~~~~~~

.. py:method:: Workspace.findall(ref):

    :param str ref: Reference string
    :rtype: List of object

    Experimental find-method that has rudimentary support for wild cards (a.k.a) globs.
    This method returns a list of items it finds

Example
^^^^^^^

.. code-block:: python

    ws = autosar.workspace("4.2.2")
    #Add components to ComponentTypes package
    ...

    #Loop over all SWCs in package "ComponentTypes"
    for swc in ws.findall("/ComponentTypes/*"):
        print(swc.name)




