Constant
========

**Usage:**

.. code-block:: python

   import autosar
   
   ws = autosar.workspace()
   ws.loadXML('DataTypes.arxml') #contains a package named "DataType"
   constantPackage=ws.createPackage('Constant')
   
   datatype=ws['/DataType/InactiveActiveSpare_T']
   assert(datatype is not None)
   value=autosar.IntegerValue('C_SomeSignal_IV',datatype.ref,datatype.maxval)
   constant = autosar.Constant('C_SomeSignal_IV',value)
   constantPackage.append(constant)
   ws.saveXML('Constants.arxml',packages=['Constant'])

.. _Constant:

   .. py:class:: Constant(name : str, value : object)
      
      Represents an AUTOSAR constant specification.
         
   .. py:attribute:: Constant.name
           
      
   .. py:attribute:: Constant.value
          
