.. _ar4_datatype_ImplementationDataTypeElement:

ImplementationDataTypeElement
=============================

.. table::
    :align: left

    +--------------+-------------------------------------------------------------------------+
    | XML tag      | <IMPLEMENTATION-DATA-TYPE-ELEMENT>                                      |
    +--------------+-------------------------------------------------------------------------+
    | Module       | autosar.datatype                                                        |
    +--------------+-------------------------------------------------------------------------+
    | Inherits     | :ref:`autosar.element.Element <ar4_element_Element>`                    |
    +--------------+-------------------------------------------------------------------------+

Describes the element of an array, struct, or union data type. Used as sub-element to :ref:`ar4_datatype_ImplementationDataType`.

Constructor
-----------

.. py:method:: datatype.ImplementationDataTypeElement(name, [category = None], [arraySize = None], [arraySizeSemantics = None], [variantProps = None], [parent = None], [adminData = None])

    :param str name: Short name.
    :param category: Category string.
    :type category: None, str
    :param arraySize: Array size.
    :type arraySize: None, int
    :param arraySizeSemantics: Array size semantics.
    :type arraySizeSemantics: None, str
    :param variantProps: variant properties.
    :type variantProps: None, :ref:`ar4_base_SwDataDefPropsConditional`, list
    :param parent: Parent package.
    :type parent: None, :ref:`ar4_package_Package`
    :param adminData: Admin data.
    :type adminData: None, :ref:`ar4_base_AdminData`

arraySizeSemantics
~~~~~~~~~~~~~~~~~~

+----------------------------+------------------------------------------------------------------------------------------------+
| Value                      | Description                                                                                    |
+============================+================================================================================================+
| :literal:`None`            | Array size semantics not set                                                                   |
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

    +-----------------------------+---------------------------------------------------+------------------------+
    | Name                        | Type                                              | Description            |
    +=============================+===================================================+========================+
    | **arraySize**               | None, int                                         | <ARRAY-SIZE>           |
    +-----------------------------+---------------------------------------------------+------------------------+
    | **arraySizeSemantics**      | None, str                                         | <ARRAY-SIZE-SEMANTICS> |
    +-----------------------------+---------------------------------------------------+------------------------+
    | **variantProps**            | list of :ref:`ar4_base_SwDataDefPropsConditional` | <SW-DATA-DEF-PROPS>    |
    +-----------------------------+---------------------------------------------------+------------------------+


Public Methods
--------------

This class has no additional methods.
