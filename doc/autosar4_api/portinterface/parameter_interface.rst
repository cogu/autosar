

.. _ar4_portinterface_ParameterInterface:

ParameterInterface
==================

.. table::
    :align: left

   +--------------------+-----------------------------------------------------------------------------+
   | XML tag            | <PARAMETER-INTERFACE>                                                       |
   +--------------------+-----------------------------------------------------------------------------+
   | Module             | autosar.portinterface                                                       |
   +--------------------+-----------------------------------------------------------------------------+
   | Inherits           | :ref:`autosar.portinterface.PortInteface <ar4_portinterface_Portinterface>` |
   +--------------------+-----------------------------------------------------------------------------+

Represents a parameter interface.

Usage
-----

.. include:: examples/usage_parameter_interface.py
    :code: python3

Factory Methods
---------------

* :ref:`ar4_package_Package_createParameterInterface`

Attributes
-----------

For inherited attributes see :ref:`autosar.portinterface.PortInteface <ar4_portinterface_Portinterface>`.

..  table::
    :align: left

    +--------------------------+-----------------------------------------------------+--------------------------------------+
    | Name                     | Type                                                | Description                          |
    +==========================+=====================================================+======================================+
    | **parameters**           | list(:ref:`ar4_element_ParameterDataPrototype`)     | Parameters in this interface         |
    +--------------------------+-----------------------------------------------------+--------------------------------------+

Public Methods
--------------

* :ref:`ar4_portinterface_ParameterInterface_append`


Method Description
------------------

.. _ar4_portinterface_ParameterInterface_append:

append
~~~~~~

..  py:method:: ParameterInterface.append(elem)

    Adds element to the self.parameters list.

    :param elem: parameter
    :type elem: :ref:`ar4_element_ParameterDataPrototype`
