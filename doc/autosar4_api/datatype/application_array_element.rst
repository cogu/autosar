.. _ar4_datatype_ApplicationArrayElement:

ApplicationArrayElement
=======================

.. table::
    :align: left

    +--------------+-------------------------------------------------------------------------+
    | XML tag      | <ELEMENT>                                                               |
    +--------------+-------------------------------------------------------------------------+
    | Module       | autosar.datatype                                                        |
    +--------------+-------------------------------------------------------------------------+
    | Inherits     | :ref:`autosar.element.Element <ar4_element_Element>`                    |
    +--------------+-------------------------------------------------------------------------+

Describes the properties of the elements in an :ref:`ar4_datatype_ApplicationArrayDataType`.

Usage
-----

..  include:: examples/usage_application_array_element.py
    :code: python3

Constructor
-----------

.. py:method:: datatype.ApplicationArrayElement([name = None], [typeRef = None], [arraySize = None], [sizeHandling = None], [sizeSemantics = 'FIXED-SIZE'], category = 'VALUE',  [parent = None], [adminData = None])

    :param name: ShortName.
    :type name: None, str
    :param typeRef: Type reference.
    :type typeRef: None, str
    :param arraySize: Array size.
    :type arraySize: None, int
    :param sizeHandling: Size handling.
    :type sizeHandling: None, str
    :param sizeSemantics: Size semantics.
    :type sizeSemantics: None, str
    :param category: Category.
    :type category: None, str
    :param parent: Parent datatype.
    :type parent: None, :ref:`ar4_datatype_ApplicationArrayDataType`
    :param adminData: Optional AdminData.
    :type adminData: None, :ref:`ar4_base_AdminData`.

.. _ar4_datatype_ApplicationArrayElement_sizeHandling:

sizeHandling
~~~~~~~~~~~~


+------------------------------------------------------+-----------------------------------------------------------------------------------------------+
| Value                                                | Description                                                                                   |
+======================================================+===============================================================================================+
| :literal:`None`                                      | Size handling not set                                                                         |
+------------------------------------------------------+-----------------------------------------------------------------------------------------------+
| :literal:`"ALL-INDICES-DIFFERENT-ARRAY-SIZE\"`       | All elements of the variable size array may have different sizes.                             |
+------------------------------------------------------+-----------------------------------------------------------------------------------------------+
| :literal:`"ALL-INDICES-SAME-ARRAY-SIZE\"`            | All elements of the variable size array have the same size.                                   |
+------------------------------------------------------+-----------------------------------------------------------------------------------------------+
| :literal:`"INHERITED-FROM-ARRAY-ELEMENT-TYPE-SIZE\"` | The size of the variable size array is determined by the size of the contained array element. |
+------------------------------------------------------+-----------------------------------------------------------------------------------------------+

.. _ar4_datatype_ApplicationArrayElement_sizeSemantics:

sizeSemantics
~~~~~~~~~~~~~

+----------------------------+------------------------------------------------------------------------------------------------+
| Value                      | Description                                                                                    |
+============================+================================================================================================+
| :literal:`None`            | Size semantics not set                                                                         |
+----------------------------+------------------------------------------------------------------------------------------------+
| :literal:`"FIXED-SIZE"`    | The array has a fixed number of elements equal to the arraySize attribute                      |
+----------------------------+------------------------------------------------------------------------------------------------+
| :literal:`"VARIABLE-SIZE"` | The size of the array can vary at run-time. The arraySize attribute sets the upper bound.      |
+----------------------------+------------------------------------------------------------------------------------------------+

Attributes
-----------

For inherited attributes see :ref:`autosar.element.Element <ar4_element_Element>`.

..  table::
    :align: left

    +--------------------------+---------------------------+----------------------------------------------------------------------------+
    | Name                     | Type                      | Description                                                                |
    +==========================+===========================+============================================================================+
    | **typeRef**              | *None, str*               | Type reference                                                             |
    +--------------------------+---------------------------+----------------------------------------------------------------------------+
    | **arraySize**            | *None, int*               | <MAX-NUMBER-OF-ELEMENTS>                                                   |
    +--------------------------+---------------------------+----------------------------------------------------------------------------+
    | **sizeHandling**         | *None, str*               | <ARRAY-SIZE-HANDLING>                                                      |
    +--------------------------+---------------------------+----------------------------------------------------------------------------+
    | **sizeSemantics**        | *None, str*               | <ARRAY-SIZE-SEMANTICS>                                                     |
    +--------------------------+---------------------------+----------------------------------------------------------------------------+

