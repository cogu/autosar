Data Types API (AR4)
====================

In AUTOSAR4 you can create different variants of implementation data types.

.. _datatype-createImplementationDataType:

.. py:method:: Package.createImplementationDataType(name : str, baseTypeRef : str, options)

Arguments
---------
   
   * name:
   * baseTypeRef

Optional Arguments
------------------

   * minVal:
   * maxVal:
   * valueTable:
   * bitmask:
   * offset:
   * scaling:
   * unit:
   * forceFloatScaling:
   * dataConstraint:
   * swCalibrationAccess:
   * typeEmitter:
   * adminData:
 

Type References
---------------

.. py:method:: Package.createImplementationDataTypeRef(name : str, implementationTypeRef : str, adminData = None)

   Creates a new implementation data type that is a reference to another implementation type (similar to a typedef in C).

Arguments:
~~~~~~~~~~
    * name: The name of the new data type
    * implementationTypeRef: Reference (string) to existing implementation type. If you have the implementation type as an object, use the .ref attribute to get it as string.
    * adminData (optional): optional AdminData object

Example:
~~~~~~~~

.. include:: examples/createImplementationDataTypeRef.py
    :code: python

Implementation Pointer Data Types
---------------------------------

.. py:method:: Package.createImplementationDataTypePtr(name : str, implementationTypeRef : str, swImplPolicy = None, adminData = None)

   Creates a new implementation data type that is a pointer to a base type (Similar to a pointer type definition in C).

Arguments:
~~~~~~~~~~
    * name: The name of the new data type
    * baseTypeRef: Reference (string) to existing base type. If you have the base type as an object, use the .ref attribute to get it as string.
    * swImplPolicy (optional): Set this to 'CONST' in order to create a const pointer data type
    * adminData (optional): optional AdminData object

Example:
~~~~~~~~

.. include:: examples/createImplementationDataTypePtr.py
    :code: python
