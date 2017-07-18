:mod:`autosar.workspace` --- Workspace
======================================

**Usage:**

.. code-block:: python

   import autosar
   
   ws=autosar.workspace()
   ws.loadXML('DataTypes.arxml', roles={'/DataType': 'DataType'})
   ws.loadXML('Constants.arxml', roles={'/Constant': 'Constant'})
   for package in ws.packages:
      print(package.name)

.. _Workspace:

.. py:class:: Workspace()
      
   The AUTOSAR workspace.
      
Attributes
----------
      
.. py:attribute:: Workspace.packages
   
   A list containing the currently loaded AUTOSAR packages.

Examples
--------

.. code-block:: python

   import autosar
   ws = autosar.workspace()



Loading and saving XML Files
----------------------------   

.. py:method:: Workspace.loadXML(filename: str, roles=None)

   automatically opens and loads (imports) all packages found in *filename*. Filename must be a valid .arxml file.
   
   roles is an optional dictionary object with roles as key-value pairs where key is the reference of the package and the value is the role name.
   For valid role names, see the `Workspace.loadPackage <workspace-loadpackage_>`_ method.
   
   **Example:**
   
   .. code-block:: python
   
      import autosar
   
      ws = autosar.workspace()
      ws.loadXML("DataTypes.arxml", roles={"/DataType": "DataType"})
      ws.loadXML("PortInterfaces.arxml", roles={"/PortInterface": "PortInterface"})
      ws.loadXML("Constants.arxml", roles={"/Constant": "Constant"})

.. py:method:: Workspace.saveXML(filename: str, packages=None: list)

   saves (exports) the workspace into .arxml format. By default it writes all packages currently in the Workspace.packages list.
   The packages argument can be used to select a subset of packages to save. It must be a list of strings of package names.
   
   **Example:**
   
   .. code-block:: python

      import autosar
      
      ws = autosar.workspace()
      ws.openXML("ecu_extract.arxml")
      ws.loadPackage("Constant", role="Constant")
      ws.loadPackage("DataType", role="DataType")
      ws.loadPackage("PortInterface", role="PortInterface")

      ws.saveXML("Constants.arxml", packages=["Constant"])
      ws.saveXML("DataTypes.arxml", packages=["DataType"])
      ws.saveXML("PortInterfaces.arxml", packages=["PortInterface"])
           
.. py:method:: Workspace.openXML(filename: str)
   
   Opens *filename* as XML and sets it as the current file. Once opened you can now use the **loadPackage** method repeatedly to load the AUTOSAR packages you want from *filename*.
   
   To both open and load (all) packages from a file use the **loadXML** method instead.

.. _workspace-loadpackage:

.. py:method:: Workspace.loadPackage(packagename: str, role=None)

  Manually load (import) a package into your current workspace. Use the **openXML** method before this call to open the file.
  The loadPackage method can be callled more than once on an opened file.
  
  The role argument is optionally used to tell what role the package has in the workspace.
  Setting a role when loading packages will make you a lot of typing as you only have to mention the names of port interfaces, data types, constants etc.

  Using roles in workspaces is strongly recommended but is not strictly necessary.
  
.. note::

   If you choose not use package roles in the workspace you will need to type the full reference string to all component types, constants, port interfaces etc when inserting/creating them in a package.
  
.. _roles:

  Valid package roles are:
  
  * **Constant** --- Main container for autosar.constant objects
  * **ComponentType** --- Main container for autosar.component and autosar.behavior objects
  * **DataType** --- Main container for autosar.datatype objects  
  * **ModeDclrGroup** --- Main container for autosar.portinterface.ModeDeclarationGroup objects
  * **PortInterface** --- Main container for autosar.portinterface objects  
  * **Unit** --- Main container for autosar.datatype.DataTypeUnitElement objects
  * **CompuMethod** --- Main container for autosar.datatype.CompuRationalElement/CompuConstElement objects
  
   **Example:**
   
   .. code-block:: python
   
      import autosar
      
      ws = autosar.workspace()      
      ws.openXML("ecu_extract.arxml")
      ws.loadPackage("Constant", role="Constant")
      ws.loadPackage("DataType", role="DataType")
      ws.loadPackage("PortInterface", role="PortInterface")
      ws.loadPackage("ComponentType", role="ComponentType")
      

Finding elements in the workspace
---------------------------------

.. py:method:: Workspace.find(ref: str, role=None)

   Any object in the workspace that has the *name* property can be found using a reference string.
   A reference is a string describing the objects path (separated by '/') from the root (of the Workspace) to its location in the workspace hierarchy.
   The root of the workspace has the reference '/'.
   
   The python value None is returned in case the object pointed to by *ref* wasn't found in the workspace.
   
**Example:**

.. code-block:: python   

   ws.find("/") #reference to root, which should be the workspace itself
   ws.find("/DataType") #reference to the 'DataType' package located directly in the root of the workspace
   ws.find("/DataType/CoolantTemp_T") # reference to the CoolantTemp_T integer type in the '/DataType' package
   ws.find("/ComponentType/AntiLockBraking/AntiLockBrakingActive") #reference to the port 'AntiLockBrakingActive' in the component 'AntiLockBraking' of package 'ComponentType'

Note that the initial slash '/' of a reference isn't strictly necessary when find is called directly on the Workspace object.
The following examples are identical the ones seen above.

**Example:**

.. code-block:: python   
   
   ws.find("DataType") #reference to the DataType package
   ws.find("DataType/CoolantTemp_T") #reference to the CoolantTemp_T integer type in the DataType package
   ws.find("ComponentType/AntiLockBraking/AntiLockBrakingActive") #reference to the port 'AntiLockBrakingActive' in the component 'AntiLockBraking' of package 'ComponentType'

Alternative syntax for finding elements
---------------------------------------

In addition to the *Workspace.find()* method this class also support the getitem built-in method.
This allows you to implicitly call the find method by treating the Workspace object as if it was a dictionary by using the reference string as a key.
The examples below are in every way identical to the one above. Using Workspace[ref] is simply syntactic sugar for calling Workspace.find(ref)

**Example:**

.. code-block:: python   
   
   ws["DataType"]
   ws["DataType/CoolantTemp_T"] 
   ws["ComponentType/AntiLockBraking/AntiLockBrakingActive"]

Note that you can with advantage use call chaining on the return value of find and getitem.

**Example:**

.. code-block:: python   

   #sort all elements in the DataType package alphabetically by their element name (case insensitive)
   ws['DataType'].elements = sorted(ws['DataType'].elements, key=lambda x: x.name.lower())

The role argument
-----------------

The role argument of *Workspace.find()* is used extensively by the internal implementation of the autosar modules.
If package roles has been setup correcly when package(s) was loaded the optional role argument can be used to find an element by using only its name instead of its full reference.

**Example:**
   
.. code-block:: python
   
   import autosar
 
   ws = autosar.workspace()
   ws.loadXML("DataTypes.arxml", roles={"/DataType": "DataType"})
   ws.loadXML("PortInterfaces.arxml", roles={"/PortInterface": "PortInterface"})
   ws.loadXML("Constants.arxml", roles={"/Constant": "Constant"})
   ws.loadXML("ComponentTypes.arxml", roles={"/ComponentType": "ComponentType"})
   
   ws.find('CoolantTemp_T', role='DataType') #the role for 'DataType' is currently set as '/DataType'. This translates to ws.find('/DataType/CoolantTemp_T')
   ws.find('AntiLockBraking', role='ComponentType') #the role for 'ComponentType' is currently set as '/ComponentType'. This translates to ws.find('/ComponentType/AntiLockBraking')


.. _workspace-createPackage:

Creating new packages in the workspace
--------------------------------------

.. py:method:: Workspace.createPackage(name : str, role=None)
   
   creates a new package and inserts it into the list of packages known to the workspace.
   
   You can optionally set a `role <roles_>`_ for this new package.
   
**Example:**

.. code-block:: python
   
   import autosar

   ws = autosar.workspace()
   #Create a new datatype package
   package=ws.createPackage("DataType", role="DataType")
   
   #Create a new port interface package
   package=ws.createPackage("PortInterface", role="PortInterface")
   
   #Create a new constant package
   package=ws.createPackage("Constant", role="Constant")

   #Create a new component type package
   package=ws.createPackage("ComponentType", role="ComponentType")
   

Deleting packages and elememts
------------------------------

.. py:method:: Workspace.delete(ref: str)

   deletes the object pointed to by the reference *ref*.
   
.. note:: 
      
      delete is only partially implemented. It currently works only for deleting packages and elements in packages.
   
   
**Example:**

.. code-block:: python
   
   import autosar
      
   ws = autosar.workspace()
   ws.openXML("ecu_extract.arxml")
   ws.loadPackage("Constant", role="Constant")
   ws.loadPackage("DataType", role="DataType")
   ws.loadPackage("PortInterface", "PortInterface")
   
   ws.delete('/PortInterface') #deletes the entire 'PortInterface' package
   ws.delete('/DataType/CoolantTemp_T') #deletes the 'CoolantTemp_T' integer data type in package 'DataType'

Manually setting package roles
------------------------------

.. py:method:: Workspace.setRole(ref: str, role: str)

   Sets the role found in the role string as the reference ref.
   The variable ref must be a valid package reference.
   The role string must be a valid `role <roles_>`_ name.
   
**Example:**

.. code-block:: python
   
   import autosar
   
   ws = autosar.workspace()      
   ws.loadXML("DataTypes.arxml")
   ws.loadXML("PortInterfaces.arxml")
   ws.loadXML("Constants.arxml")
   ws.setRole('/DataType', 'DataType')
   ws.setRole('/PortInterface', 'PortInterface')
   ws.setRole('/Constant', 'Constant')

   
