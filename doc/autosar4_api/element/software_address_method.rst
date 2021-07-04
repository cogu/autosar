.. _ar4_element_SoftwareAddressMethod:

SoftwareAddressMethod
======================

.. table::
    :align: left

    +--------------+-------------------------------------------------------------------------+
    | XML tag      | <SW-ADDR-METHOD>                                                        |
    +--------------+-------------------------------------------------------------------------+
    | Module       | autosar.element                                                         |
    +--------------+-------------------------------------------------------------------------+
    | Inherits     | :ref:`autosar.element.Element <ar4_element_Element>`                    |
    +--------------+-------------------------------------------------------------------------+

Used to assign an addressing method (such as memory section) for various objects. 
Other objects will use their respective swAddressMethodRef attribute (or property) to reference instances of this class.

Factory Methods
---------------

* :ref:`ar4_package_Package_createSoftwareAddressMethod`

Constructor
-----------

.. py:method:: element.SoftwareAddressMethod(name, [parent = None], [adminData = None])

    :param str name: Short name.
    :param parent: Parent package.
    :type parent: None, :ref:`ar4_package_Package`
    :param adminData: Optional AdminData.
    :type adminData: :ref:`ar4_base_AdminData`

Attributes
-----------

For inherited attributes see :ref:`autosar.element.Element <ar4_element_Element>`.

