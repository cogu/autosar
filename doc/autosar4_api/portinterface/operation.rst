.. _ar4_portinterface_Operation:

Operation
=========

.. table::
   :align: left

   +--------------------+----------------------------------------------+
   | XML tag            | <CLIENT-SERVER-OPERATION>                    |
   +--------------------+----------------------------------------------+
   | Module             | autosar.portinterface                        |
   +--------------------+----------------------------------------------+
   | Inherits           | :ref:`autosar.element.Element <ar4_element>` |
   +--------------------+----------------------------------------------+

An operation of a client-server port interface.

Factory Methods
---------------

* :ref:`Package.createClientServerInterface <ar4_package_Package_createClientServerInterface>`


Attributes
----------

..  table::
    :align: left

    +--------------------------+--------------------------+-----------------------------------------------------------------------+
    | Name                     | Type                     | Description                                                           |
    +==========================+==========================+=======================================================================+
    | **arguments**            | list(Arguments)          | List of operation arguments                                           |
    +--------------------------+--------------------------+-----------------------------------------------------------------------+
    | **errorRefs**            | list(str)                | References to ApplicationError objects that this operation can return |
    +--------------------------+--------------------------+-----------------------------------------------------------------------+

Properties
----------

possibleErrors
~~~~~~~~~~~~~~

This is a convenience property setter for seclecting one or more error codes that this operation can possibly return.
You can assign either a string or a list of strings to this property. The object will automatically validate if
the name(s) are possible errors that have been previously assigned to the port interface (its parent object).
The object will convert the names of the errors in to actual references by updating the self.errorRefs list

Example
^^^^^^^

.. include:: examples/operation_setting_possible_errors.py
    :code: python


Public Methods
--------------

* :ref:`operation_createOutArgument`
* :ref:`operation_createInOutArgument`
* :ref:`operation_createInArgument`
* :ref:`operation_append`



Method Description
------------------

.. _operation_createOutArgument:

createOutArgument
~~~~~~~~~~~~~~~~~

..  py:method:: Operation.createOutArgument(name, typeRef, [swCalibrationAccess = None], [serverArgumentImplPolicy=None])

    Creates a new argument with direction set to 'OUT'.

    :param str name: Name of the new argument
    :param str typeRef: Reference to data type.
    :param str swCalibrationAccess: Optional swCalibrationAccess string.
    :param str serverArgumentImplPolicy: Optional serverArgumentImplPolicy string.
    :rtype: Argument

.. _operation_createInOutArgument:

createInOutArgument
~~~~~~~~~~~~~~~~~~~

..  py:method:: Operation.createInOutArgument(name, typeRef, [swCalibrationAccess = None], [serverArgumentImplPolicy=None])

    Creates a new argument with direction set to 'INOUT'.

    :param str name: Name of the new argument
    :param str typeRef: Reference to data type.
    :param str swCalibrationAccess: Optional swCalibrationAccess string.
    :param str serverArgumentImplPolicy: Optional serverArgumentImplPolicy string.
    :rtype: Argument

.. _operation_createInArgument:

createInArgument
~~~~~~~~~~~~~~~~

..  py:method:: Operation.createInArgument(name, typeRef, [swCalibrationAccess = None], [serverArgumentImplPolicy=None])

    Creates a new argument with direction set to 'IN'.

    :param str name: Name of the new argument
    :param str typeRef: Reference to data type.
    :param str swCalibrationAccess: Optional swCalibrationAccess string.
    :param str serverArgumentImplPolicy: Optional serverArgumentImplPolicy string.
    :rtype: Argument

.. _operation_append:

append
~~~~~~

..  py:method:: Operation.append(elem)

    Adds element to either the self.arguments or self.errorRefs depending on its type.

    :param elem: Element
    :type elem: Argument or str
