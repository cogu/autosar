Package Root
============

The autosar package root only contains one method worth mentioning. It also defines the autosar.Template interface class which
will be desribed in a future release.

Public Methods
--------------

* :ref:`ar4_autosar_workspace_method`

Method Details
--------------

.. _ar4_autosar_workspace_method:

workspace
~~~~~~~~~

.. py:method:: autosar.workspace([version = 3.0], [patch = 2], [schema = None], [attributes = None], [useDefaultWriters = True)

    :param version: AUTOSAR version.
    :type version: str, float
    :param patch: AUTOSAR patch version (deprecated argument)
    :param schema: Used to specify exact XML schema name to use instead of inferring it from *version* parameter.
    :type schema: None, str
    :param attributes: User-defined dictionary containing context-related data. The Workspace object just stores the value(s) for later.
    :type attributes: None, dict
    :param bool useDefaultWriters: If False it disables all XML writing classes. Users can then register their own XML writers.
    :rtype: :ref:`ar4_workspace`

    Factory method for creating instances of :ref:`ar4_workspace` objects.