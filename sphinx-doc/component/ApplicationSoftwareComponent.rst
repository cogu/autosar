ApplicationSoftwareComponent
============================

**Usage:**

.. code-block:: python
   
   import autosar as ar
      
   ws = ar.workspace()
   ws.append(ar.Package('ComponentType'))
   
   swc = ar.ApplicationSoftwareComponent('MyComponent')
   ws['/ComponentType'].append(swc)
   
   print(ws.toXML(packages=['ComponentType']))
   
.. _ApplicationSoftwareComponent:

.. py:class:: ApplicationSoftwareComponent(name : string)
   
   The ApplicationSoftwareComponent is a component type.
   
   .. py:attribute:: name
   
      The name of the object as a string.
     
   .. py:attribute:: ref
      
      (readonly) reference to the object as a string.
   .. note::
   
      In order for the object to get a valid reference it must first be added to a package using the Package.append method.
   
   .. py:attribute:: requirePorts
      
      The require-ports of the component (list).

   .. py:attribute:: providePorts
      
      The provide-ports of the component (list).