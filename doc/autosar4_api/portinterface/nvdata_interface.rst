.. _ar4_portinterface_NvDataInterface:

NvDataInterface
===============

.. table::
   :align: left

   +--------------------+-----------------------------------------------------------------------------+
   | XML tag            | <NV-DATA-INTERFACE>                                                         |
   +--------------------+-----------------------------------------------------------------------------+
   | Module             | autosar.portinterface                                                       |
   +--------------------+-----------------------------------------------------------------------------+
   | Inherits           | :ref:`autosar.portinterface.PortInteface <ar4_portinterface_Portinterface>` |
   +--------------------+-----------------------------------------------------------------------------+

Representa a NvData port interface.

Factory Methods
---------------

* :ref:`ar4_package_Package_createNvDataInterface`

Attributes
----------

For inherited attributes see :ref:`autosar.portinterface.PortInteface <ar4_portinterface_Portinterface>`.

..  table::
    :align: left

    +--------------------------+----------------------------+-------------------------------+
    | Name                     | Type                       | Description                   |
    +==========================+============================+===============================+
    | **nvDatas**              | list(DataElement)          | List of data elements         |
    +--------------------------+----------------------------+-------------------------------+

Public Methods
--------------

* :ref:`ar4_portinterface_NvDataInterface_append`


Method Description
------------------

.. _ar4_portinterface_NvDataInterface_append:

append
~~~~~~

..  py:method:: NvDataInterface.append(elem)

    Adds data element to the self.nvDatas list.

    :param elem: Element
    :type elem: :ref:`ar4_element_DataElement`