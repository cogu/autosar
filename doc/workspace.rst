Workspace
*********

**Usage:**

.. code-block:: python

   import autosar
   
   ws=autosar.workspace()
   ws.loadXML('datatypes.arxml')
   for elem in ws.find('/DataType').elements:
      print(elem.name)

.. _Workspace:

.. py:class:: Workspace()
      
   The AUTOSAR workspace.
      
Attributes
----------
      
.. py:attribute:: Workspace.packages
   
   A list containing the currently loaded AUTOSAR packages.

Loading and saving XML Files
----------------------------   
           
.. py:method:: Workspace.openXML(filename: str)
   
   Opens *filename* as XML and sets it as the current file. Once opened you can now use the **loadPackage** method repeatedly to load the AUTOSAR packages you want from *filename*.
   
   To both open and load (all) packages from a file use the **loadXML** method instead.
   
.. py:method:: Workspace.loadPackage(packagename: str)

  Manually load (import) a package into your current workspace. Use the **openXML** method before this call to open the file.
  The loadPackage method can be callled more than once a file has been opened.
  
   **Example:**
   
   .. code-block:: python
   
      import autosar
      
      ws = autosar.workspace()
      ws.openXML("extract.arxml")
      ws.loadPackage("DataType")
      ws.loadPackage("Constant")
      ws.loadPackage("PortInterface")
      ws.loadPackage("ComponentType")
      
.. py:method:: Workspace.loadXML(filename: str)

   automatically opens and loads (imports) all packages found in file. Filename must be a valid .arxml file.

.. py:method:: Workspace.saveXML(filename: str, packages=None: list)

   saves (exports) the workspace into .arxml format. By default it writes all packages currently the Workspace.packages list.
   The packages argument can be used to select a subset of packages to save. It must be a list of strings.
   
   **Example:**
   
   .. code-block:: python

      import autosar
      
      ws = autosar.workspace()
      ws.openXML("extract.arxml")
      ws.loadPackage("Constant")
      ws.loadPackage("DataType")
      ws.loadPackage("PortInterface")

      ws.saveXML("Constants.arxml", packages=['Constant'])
      ws.saveXML("DataTypes.arxml", packages=['DataType'])
      ws.saveXML("PortInterfaces.arxml", packages=['PortInterface'])
   
   