.. _ar4_datatype_Computation:

Computation
===========

.. table::
    :align: left

    +--------------------+------------------------------------------------------+
    | XML tag            | <COMPU-INTERNAL-TO-PHYS> or <COMPU-PHYS-TO-INTERNAL> |
    +--------------------+------------------------------------------------------+
    | Module             | autosar.datatype                                     |
    +--------------------+------------------------------------------------------+
    | Inherits           |                                                      |
    +--------------------+------------------------------------------------------+

Represents one computation (internal to physical, physical to internal).
Contains a list of CompuScaleElement objects as well as an optional default value.
Instances of this class are used as internal objects of :ref:`ar4_datatype_CompuMethod`.


Factory Methods
---------------

See :ref:`ar4_datatype_CompuMethod`.

Constructor
-----------

.. py:method:: datatype.Computation([defaultValue = None])

    :param defaultValue: Optional default value.
    :type defaultValue: None, str, int or float

Attributes
----------

.. table::
    :align: left

    +-------------------------------+-----------------------+---------------------------------------------------------+
    | Name                          | Type                  | Description                                             |
    +===============================+=======================+=========================================================+
    | **elements**                  | str                   | List of :ref:`ar4_datatype_CompuScaleElement`           |
    +-------------------------------+-----------------------+---------------------------------------------------------+
    | **defaultValue**              | None, str, int, float | Optional default value                                  |
    +-------------------------------+-----------------------+---------------------------------------------------------+

Public Properties
-----------------

..  table::
    :align: left

    +--------------------------+---------------+-------------+
    | Name                     | Type          | Access Type |
    +==========================+===============+=============+
    | **lowerLimit**           | int, float    | Get         |
    +--------------------------+---------------+-------------+
    | **upperLimit**           | int, float    | Get         |
    +--------------------------+---------------+-------------+

lowerLimit
~~~~~~~~~~

Returns lowerLimit of first element. Raises KeyError if *elements* list is empty.

upperLimit
~~~~~~~~~~

Returns upperLimit of first element. Raises KeyError if *elements* list is empty.

Public Methods
--------------

* :ref:`ar4_datatype_Computation_createValueTable`
* :ref:`ar4_datatype_Computation_createRationalScaling`
* :ref:`ar4_datatype_Computation_createBitMask`

Method Description
------------------

.. _ar4_datatype_Computation_createValueTable:

createValueTable
~~~~~~~~~~~~~~~~

.. py:method:: Computation.createValueTable(elements, [autoLabel = True])

    :param list elements: Elements of new value table.
    :param bool autoLabel: Automatically create <SHORT-LABEL> for each element.

    Creates a list of :ref:`CompuScaleElements <ar4_datatype_CompuScaleElement>` with text values.

    When *elements* is a list of strings:

    Creates one :ref:`ar4_datatype_CompuScaleElement` per list item and automatically calculates lower and upper limits.

    When *elements* is a list of tuples:

    If 2-tuple: First element is both lowerLimit and upperLimit, second element is textValue.

    If 3-tuple: First element is lowerLimit, second element is upperLimit, third element is textValue.

    
.. _ar4_datatype_Computation_createRationalScaling:

createRationalScaling
~~~~~~~~~~~~~~~~~~~~~

.. py:method:: Computation.createRationalScaling(offset, numerator, denominator, lowerLimit, upperLimit, [lowerLimitType = 'CLOSED'], [upperLimitType = 'CLOSED'], [label = None], [symbol = None], [adminData = None])

    :param offset: Scaling offset.
    :type offset: int, float
    :param numerator: Scaling numerator.
    :type numerator: int, float
    :param denominator: Scaling denominator.
    :type denominator: int, float
    :param lowerLimit: lower limit.
    :type lowerLimit: int, float
    :param upperLimit: upper limit.
    :type upperLimit: int, float
    :param str lowerLimitType: lower limit type (:literal:`'OPEN'`, :literal:`'CLOSED'`).
    :param str upperLimitType: upper limit type (:literal:`'OPEN'`, :literal:`'CLOSED'`).
    :param label: Optional label (used instead of name attribute).
    :type label: None, str
    :param symbol: Optional symbol name.
    :type symbol: None, str
    :param adminData: AdminData.
    :type adminData: :ref:`ar4_base_AdminData`

    Creates :ref:`ar4_datatype_CompuScaleElement` with it rational scaling properties.

.. _ar4_datatype_Computation_createBitMask:

createBitMask
~~~~~~~~~~~~~

.. py:method:: Computation.createBitMask(elements, [autoLabel = True])

    :param list elements: list of 2-tuples.
    :param bool autoLabel: Automatically create <SHORT-LABEL> for each element.

    Creates a list of :ref:`CompuScaleElements <ar4_datatype_CompuScaleElement>` with text values.
    
    The *element* parameter is expected to be a list tubles.
    
    If 2-tuple: First element is both lowerLimit and upperLimit, second element is textValue.
