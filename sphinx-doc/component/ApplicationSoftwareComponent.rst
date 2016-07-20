ApplicationSoftwareComponent
****************************

class ApplicationSoftwareComponent

**Usage:**

.. code-block:: python
   
   import autosar as ar
      
   ws = ar.workspace()
   ws.loadXML('PortInterfaces.arxml')     #loads PortInterface package
   ws.loadXML('Constants.arxml')          #loads Constant package
   ws.append(ar.Package('ComponentType')) #creates ComponentType package
   
   swc = ar.ApplicationSoftwareComponent('MyComponent')   
   swc.append(ar.RequirePort('WheelBasedVehicleSpeed','/PortInterface/WheelBasedVehicleSpeed_I',
                             comspec={'initValueRef':'/Constant/C_WheelBasedVehicleSpeed_IV','aliveTimeout':30}))
   ws['/ComponentType'].append(swc) #adds new swc to the ComponentType package
   
   print(ws.toXML(packages=['ComponentType'])) #exports ComponentType package only