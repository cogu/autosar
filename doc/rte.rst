:mod:`autosar.rte` --- RTE Submodule
==============================================

**Usage**:

.. code-block:: python
    
   import autosar
    
   ws = autosar.workspace()
    
   #here you need to load or create ApplicationSoftareComponent with ports, runnables etc. store component in variable named swc.
    
   rtegen = autosar.RteGenerator()
   for swc_name in ['Component1', 'Component2']: #change this to match the component names(s) you want to generate
      swc = ws.find('/ComponentType/'+swc_name)
      if swc is not None:
         rtegen.writeComponentHeaders(swc, 'derived')
    

.. _RteGenerator:

RteGenerator
----------------

   A simple RTE generator class. Its main purpose is to generate RTE component headers for SWC development.

Methods
~~~~~~~

.. py:method:: RteGenerator.writeComponentHeaders(swc, outdir='.' : str, name='None' : str)

   Generates RTE component headers for a single ApplicationSoftwareComponent or ComplexDeviceDriverComponent. 
   
   Arguments:
   
   * **swc**: software component instance (must be part of a package belonging to a workspace instance).
   
   Optional arguments:
   
   * **outdir**: output directory where header files will be written to.
   * **name**: temporarily overrides the name of the swc during header generation. This changes the names of the C function prototypes.
   
   
.. py:method:: RteGenerator.writeDummyRTE(ws, componentRefs = None, outdir='.')
  
   Generates a dummy RTE for testing purposes only.
   
   Arguments:
   
   * **ws**: a valid autosar workspace containing SWCs, datatypes, constants and port interfaces.
   * **componentRefs**: list of strings containing references to components to include in the RTE generation.
     If a ComponentType role has been setup in the workspace before this call you need only to mention the component names.
     If no ComponentType has been setup you need to provide full autosar elements references in the list.
    
   Optional arguments:
   
   * **outdir**: output directory where source files will be written to.
