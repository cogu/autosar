SenderReceiverInterface
***********************

class SenderReceiverInterface

**Usage:**

.. code-block:: python
   
   import autosar as ar
   
   ws = ar.workspace()
   ws.append(ar.Package('PortInterface'))
   ws.loadXML('DataTypes.arxml') #reads an existing DataType package

   portInterface = ar.SenderReceiverInterface('WheelBasedVehicleSpeed_I')
   element=ar.DataElement('WheelBasedVehicleSpeed','/DataType/Speed16bit_T')
   portInterface.append(element) #adds the new data element to the port interface
   ws['/PortInterface'].append(portInterface) #adds the new port interface the the PortInterface package

   print(ws.toXML(packages=['PortInterface']))