Composition
===========


**Usage:**

.. code-block:: python
   
   import autosar as ar
      
   ws = ar.workspace()
   ws.append(ar.Package('ComponentType'))
   
   swc = ar.Composition('MyComposition')
   ws['/ComponentType'].append(swc)
   
   print(ws.toXML(packages=['ComponentType']))
   
.. _Composition:
.. py:class:: Composition(name : string)
   
   This represents an AUTOSAR CompositionType or <COMPOSITION-TYPE>.
   
   .. py:attribute:: name
   
      The name of the object as a string.
     
   .. py:attribute:: ref
      
      (readonly) reference to the object as a string.
   
   .. py:attribute:: components
   
      list of components inside this composition. Each entry in the list is of type ComponentPrototype_.
   
   .. code-block:: python
   
      for elem in swc.components:
         print(elem.name,elem.typeRef)
   
.. _ComponentPrototype:
.. py:class:: ComponentPrototype(name: string,typeRef: string)
   
