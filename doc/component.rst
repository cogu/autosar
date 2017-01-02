:mod:`autosar.component` --- ComponentType
==========================================

**Usage:**

.. code-block:: python

   import autosar

   ws = autosar.workspace()
   ws.loadXML("DataTypes.arxml", roles={"/DataType": "DataType"})
   ws.loadXML("PortInterfaces.arxml", roles={"/PortInterface": "PortInterface"})
   ws.loadXML("Constants.arxml", roles={"/Constant": "Constant"})

   package=ws.createPackage("ComponentType", role="ComponentType")
   swc = package.createApplicationSoftwareComponent('AntiLockBraking')
   swc.createProvidePort('AntiLockBrakingActive', 'AntiLockBrakingActive_I', initValueRef='C_AntiLockBrakingActive_IV')   
   
   ws.saveXML('ComponentTypes.arxml', packages=['ComponentType'])
   
.. _ApplicationSoftwareComponent:

ApplicationSoftwareComponent
----------------------------
   
.. py:class:: ApplicationSoftwareComponent(name : string)

   ApplicationSoftwareComponent is used to represent a application software components ("APPLICATION-SOFTWARE-COMPONENT-TYPE").

Attributes
~~~~~~~~~~

   .. py:attribute:: ApplicationSoftwareComponent.name
      
      The name of the object as a string.
        
   .. py:attribute:: ApplicationSoftwareComponent.ref
         
      (readonly) reference to the object as a string.
      
   .. note::
      
      In order for the object to get a valid reference it must first be added to a package using the Package.append method.
      
   .. py:attribute:: ApplicationSoftwareComponent.requirePorts
         
      The require-ports of the component (list).
   
   .. py:attribute:: ApplicationSoftwareComponent.providePorts
         
      The provide-ports of the component (list).


.. _ComplexDeviceDriverComponent:

ComplexDeviceDriverComponent
----------------------------
   
.. py:class:: ComplexDeviceDriverComponent(name : string)

   ApplicationSoftwareComponent is used to represent complex device driver components ("COMPLEX-DEVICE-DRIVER-COMPONENT-TYPE").

Attributes
~~~~~~~~~~

   .. py:attribute:: ComplexDeviceDriverComponent.name
      
      The name of the object as a string.
        
   .. py:attribute:: ComplexDeviceDriverComponent.ref
         
      (readonly) reference to the object as a string.
      
   .. note::
      
      In order for the object to get a valid reference it must first be added to a package using the Package.append method.
      
   .. py:attribute:: ComplexDeviceDriverComponent.requirePorts
         
      The require-ports of the component (list).
   
   .. py:attribute:: ComplexDeviceDriverComponent.providePorts
         
      The provide-ports of the component (list).   

.. _CompositionComponent:

CompositionComponent
--------------------
   
.. py:class:: CompositionComponent(name : string)
   
   CompositionComponent is used to represent composition types ("COMPOSITION-TYPE").
   
Attributes
~~~~~~~~~~
   
   .. py:attribute:: CompositionComponent.name
   
      The name of the object as a string.
     
   .. py:attribute:: CompositionComponent.ref
      
      (readonly) reference to the object as a string.
   
   .. py:attribute:: CompositionComponent.requirePorts
         
      The require-ports of the component (list).
   
   .. py:attribute:: CompositionComponent.providePorts
         
      The provide-ports of the component (list).   

   .. py:attribute:: CompositionComponent.components
   
      list of components inside this composition. Each entry in the list is of type ComponentPrototype_.

   .. py:attribute:: CompositionComponent.assemblyConnectors
   
      list of assembly connectors in the composition

   .. py:attribute:: CompositionComponent.delegationConnectors
   
      list of delegation connectors in the composition

      

   
.. _ComponentPrototype:
.. py:class:: ComponentPrototype(name: str, typeRef: str)
   
   internal class used by CompositionComponent_ to represent instances of "COMPONENT-PROTOTYPE"
