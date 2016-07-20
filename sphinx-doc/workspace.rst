Workspace
*********

**Usage:**

.. code-block:: python

   import autosar as ar
   
   ws=ar.workspace()
   ws.loadXML('datatypes.arxml')
   for elem in ws.find('/DataType').elements:
      print(elem.name)
   