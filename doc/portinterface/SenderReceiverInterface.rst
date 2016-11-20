SenderReceiverInterface
***********************

class SenderReceiverInterface

**Usage:**

.. code-block:: python
   
   import autosar
   
   ws = autosar.workspace()
   ws.loadXML('DataTypes.arxml') #reads an existing DataType package
   portInterfacePackage = ws.createPackage('PortInterface')
   
   portInterface = autosar.SenderReceiverInterface('LaneKeepSystemActive_I') #creates a new port interface
   element=autosar.DataElement('LaneKeepSystemActive','/DataType/InactiveActiveSpare_T')
   portInterface.append(element) #adds the new data element to our new port interface
   portInterfacePackage.append(portInterface) #adds the new port interface to the PortInterface package
   
   ws.saveXML('PortInterfaces.arxml',packages=['PortInterface'])
   
