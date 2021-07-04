.. _ar4_datatype_CompuScaleElement:

CompuScaleElement
=================

.. table::
    :align: left

    +--------------------+------------------------------------------------------+
    | XML tag            | <COMPU-SCALE>                                        |
    +--------------------+------------------------------------------------------+
    | Module             | autosar.datatype                                     |
    +--------------------+------------------------------------------------------+
    | Inherits           |                                                      |
    +--------------------+------------------------------------------------------+

Contains the properties for one computation.

Computation Variants
--------------------

Attributes in use for all variants:

* label
* adminData

ValueTable
~~~~~~~~~~~

ValueTable is also known as enumeration.

Factory Method: :ref:`Computation.createValueTable <ar4_datatype_Computation_createValueTable>`

Attributes in use:

* lowerLimit (int)
* upperLimit (int)
* textValue (str)

For basic enumerations the value of lowerLimit and upperLimit are equal to each other.
You can also set lowerLimit and upperLimit to different values to denote an interval where the textValue applies.


Rational Scaling
~~~~~~~~~~~~~~~~

Rational scaling, also known as linear scaling.

Factory Method: :ref:`Computation.createRationalScaling <ar4_datatype_Computation_createRationalScaling>`

Attributes in use:

* lowerLimit
* upperLimit
* lowerLimitType
* upperLimitType
* numerator
* denominator
* offset

BitMask
~~~~~~~

Factory method: :ref:`Computation.createBitMask <ar4_datatype_Computation_createBitMask>`

Attributes in use: 

* mask
* symbol

Constructor
-----------

.. py:method:: datatype.CompuScaleElement(lowerLimit, upperLimit, [lowerLimitType = 'CLOSED'], [upperLimitType = 'CLOSED'], [label = None], [symbol = None], [textValue = None], [numerator = None], [denominator = None], [offset = None], [mask = None], [adminData = None])

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
    :param textValue: Optional text value (used for enumration).
    :type textValue: None, str
    :param numerator: Optional numerator (used for scaling).
    :type numerator: int, float
    :param denominator: Optional denominator (used for scaling).
    :type denominator: int, float
    :param denominator: Optional offset (used for scaling).
    :type denominator: int, float
    :param mask: mask (used for bit masks).
    :type mask: None, int
    :param adminData: AdminData.
    :type adminData: :ref:`ar4_base_AdminData`

Attributes
----------

.. table::
    :align: left

    +-------------------------------+---------------------------------+---------------------------------------------------------+
    | Name                          | Type                            | Description                                             |
    +===============================+=================================+=========================================================+
    | **lowerLimit**                | int                             | <LOWER-LIMIT>                                           |
    +-------------------------------+---------------------------------+---------------------------------------------------------+
    | **upperLimit**                | int                             | <UPPER-LIMIT>                                           |
    +-------------------------------+---------------------------------+---------------------------------------------------------+
    | **lowerLimitType**            | str                             | INTERVAL-TYPE (:literal:`'OPEN'`, :literal:`'CLOSED'`)  |
    +-------------------------------+---------------------------------+---------------------------------------------------------+
    | **upperLimitType**            | str                             | INTERVAL-TYPE (:literal:`'OPEN'`, :literal:`'CLOSED'`)  |
    +-------------------------------+---------------------------------+---------------------------------------------------------+
    | **label**                     | None, str                       | <SHORT-LABEL> (used as alternative to name attribute)   |
    +-------------------------------+---------------------------------+---------------------------------------------------------+
    | **symbol**                    | None, str                       | <SYMBOL>                                                |
    +-------------------------------+---------------------------------+---------------------------------------------------------+
    | **textValue**                 | None, str                       | <VT> (used for value table)                             |
    +-------------------------------+---------------------------------+---------------------------------------------------------+
    | **numerator**                 | None, int, float                | <COMPU-NUMERATOR><V> (used for scaling)                 |
    +-------------------------------+---------------------------------+---------------------------------------------------------+
    | **denominator**               | None, int, float                | <COMPU-DENOMINATOR><V> (used for scaling)               |
    +-------------------------------+---------------------------------+---------------------------------------------------------+
    | **offset**                    | None, int, float                | <COMPU-NUMERATOR><V> (used for scaling)                 |
    +-------------------------------+---------------------------------+---------------------------------------------------------+
    | **mask**                      | None, int                       | <MASK> (used for bit masks)                             |
    +-------------------------------+---------------------------------+---------------------------------------------------------+
    | **adminData**                 | None, :ref:`ar4_base_AdminData` | <ADMIN-DATA>                                            |
    +-------------------------------+---------------------------------+---------------------------------------------------------+
