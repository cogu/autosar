:mod:`autosar.rte` --- RTE Submodule
==============================================

**Usage**:

.. code-block:: python
    
   import autosar
    
   ws = autosar.workspace()
    
   #create ApplicationSoftareComponent with ports, runnables etc. store component in variable named swc.
    
   rtegen = autosar.RteGenerator()
   rtegen.writeComponentHeaders(swc, 'derived')
    

.. _RteGenerator:

RteGenerator
----------------

   A simple RTE generator class. Its purpose is to generate RTE headers only, not actual C source files.

Methods
~~~~~~~

.. py:method:: RteGenerator.writeComponentHeaders(swc, outdir='.' : str, name='None' : str)

   Generates RTE headers for a single ApplicationSoftwareComponent or ComplexDeviceDriverComponent. These headers are typically used for SWC testing or unit testing.
   
   arguments:
   
   * *swc*: software component instance (must be part of a package belonging to a workspace instance).
   
   optional arguments:
   
   * *outdir*: output directory where header files will be written to.
   * *name*: temporarily overrides the name of the swc during header generation. This changes the names of the C function prototypes.
   
   
   
