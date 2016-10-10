IntegerDataType
***************

class IntegerDataType

**Usage:**

.. code-block:: python

   import autosar as ar
   
   ws = ar.workspace()
   dataTypePackage=ar.Package('DataType')
   ws.append(dataTypePackage)
   semanticsPackage=ar.Package('DataTypeSemantics')
   dataTypePackage.append(semanticsPackage)

   compuMethod=ar.CompuMethodConst('InactiveActiveSpare_T',['InactiveActiveSpare_Inactive','InactiveActiveSpare_Active','InactiveActiveSpare_Spare','InactiveActiveSpare_NotAvailable'])
   semanticsPackage.append(compuMethod)
   InactiveActiveSpare_T=ar.IntegerDataType('InactiveActiveSpare_T',0,3,compuMethodRef=compuMethod.ref)
   dataTypePackage.append(InactiveActiveSpare_T)

   print(ws.toXML())
