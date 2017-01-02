:mod:`autosar.constant` --- Constants
=====================================

**Usage:**

.. code-block:: python

   import autosar
   
   ws = autosar.workspace()
   ws.loadXML('DataTypes.arxml', roles={'/DataType': 'DataType'}) #loads a package named "DataType" from "DataTypes.arxml"
   
   package=ws.createPackage('Constant', role='Constant')
   package.createConstant('C_ESCSystemActive_IV', 'InactiveActive_T', 3)
   package.createConstant('C_LampSwitchStatus_IV','OnOff_T', 3)
   ws.saveXML('Constants.arxml', packages=['Constant'])   

.. _Constant:

   .. py:class:: Constant(name : str, value : object)
      
      Represents an AUTOSAR constant specification.
         
   .. py:attribute:: Constant.name
   
      name of the constant object
           
      
   .. py:attribute:: Constant.value
          
      value of the constant object