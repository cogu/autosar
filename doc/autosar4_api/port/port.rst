..  _ar4_port_Port:

Port
====

.. table::
   :align: left

   +--------------------+------------------------------------------------------+
   | XML tag            | (abstract class)                                     |
   +--------------------+------------------------------------------------------+
   | Module             | autosar.port                                         |
   +--------------------+------------------------------------------------------+
   | Inherits           | :ref:`autosar.element.Element <ar4_element_Element>` |
   +--------------------+------------------------------------------------------+

This is the base class for component ports.

* :ref:`ar4_port_ProvidePort`
* :ref:`ar4_port_RequirePort`

Attributes
----------

For inherited attributes see :ref:`autosar.element.Element <ar4_element_Element>`.

..  table::
    :align: left

    +--------------------------+-------------------+-----------------------------------------------------+
    | Name                     | Type              | Description                                         |
    +==========================+===================+=====================================================+
    | **portInterfaceRef**     | str               | Reference to :ref:`ar4_portinterface_portinterface` |
    +--------------------------+-------------------+-----------------------------------------------------+
    | **comspec**              | list              | List of ComSpec objects                             |
    +--------------------------+-------------------+-----------------------------------------------------+
