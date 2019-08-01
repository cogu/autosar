.. _application_swc:

ApplicationSoftwareComponent
============================

.. table::
   :align: left

   +--------------+----------------------------------------------------------------+
   | XML tag      | <APPLICATION-SW-COMPONENT-TYPE>                                |
   +--------------+----------------------------------------------------------------+
   | Module       | autosar.component                                              |
   +--------------+----------------------------------------------------------------+
   | Inherits     | :ref:`autosar.component.AtomicSoftwareComponent <atomic_swc>`  |
   +--------------+----------------------------------------------------------------+
   
Factory Methods
---------------

* :ref:`Package.createApplicationSoftwareComponent <createApplicationSoftwareComponent>`


Attributes
-----------

Detailed Description
--------------------

Factory Method Description
--------------------------

.. _createApplicationSoftwareComponent:

.. py:method:: Package.createApplicationSoftwareComponent(self, swcName, behaviorName, implementationName, multipleInstance)

Arguments
~~~~~~~~~

* (str) **swcName**: shortName of this SWC


Optional Arguments
~~~~~~~~~~~~~~~~~~

* (str) **behaviorName**: shortName for associated InternalBehavior object. Default=None (auto).
* (str) **implementationName**: shortName for associated SwcImplementation object. Default=None (auto).
* (bool) **multipleInstance**: Multiple instance support. Default=False.
