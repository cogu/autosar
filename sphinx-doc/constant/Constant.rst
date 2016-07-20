Constant
***************

class Constant

**Usage:**

.. code-block:: python

   import autosar as ar
   
   ws = ar.workspace()
   ws.loadXML('DataTypes.arxml') #contains a package named "DataType"
   constantPkg=ar.Package('Constant')
   ws.append(constantPkg)

   datatype=ws.find('/DataType/InactiveActive_T')
   assert(datatype is not None)
   value=ar.IntegerValue('C_SomeSignal_IV',datatype.ref,datatype.maxval)
   constantPkg.append(ar.Constant('C_SomeSignal_IV',value))

   print(ws.toXML(packages=['Constant']))
