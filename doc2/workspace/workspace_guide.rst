Workspace Guide
===============

Creating workspaces
-------------------

An AUTOSAR workspace are created using the autosar.workspace helper method. It retuns an instance of the :ref:`Workspace <Workspace>` class.

**AUTOAR 3.0.2 (default)**

By default, you will get an AUTOSAR 3.0.2 workspace.

.. code-block:: python

    import autosar

    ws = autosar.workspace()
    print(ws.toXML())

.. code-block:: xml

    <?xml version="1.0" encoding="UTF-8"?>
    <AUTOSAR xsi:schemaLocation="http://autosar.org/3.0.2 autosar_302_ext.xsd" xmlns="http://autosar.org/3.0.2" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
        <TOP-LEVEL-PACKAGES>
        </TOP-LEVEL-PACKAGES>
    </AUTOSAR>

Selecting AUTOSAR version
~~~~~~~~~~~~~~~~~~~~~~~~~~

AUTOSAR has three version numbers:

- major version
- minor version
- patch

You often see these numbers in tha star tag of AUTOSAR XML files as strings of the form: "<major>.<minor>.<patch"
When creating your workspace, you can set the AUTOSAR you want to use by setting the version argument to a string literal.

**AUTOAR 4.2.2**

.. code-block:: python

    import autosar

    ws = autosar.workspace(version="4.2.2")
    print(ws.toXML())

.. code-block:: xml

    <?xml version="1.0" encoding="utf-8"?>
    <AUTOSAR xsi:schemaLocation="http://autosar.org/schema/r4.0 AUTOSAR_4-2-2.xsd" xmlns="http://autosar.org/schema/r4.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
      <AR-PACKAGES>
      </AR-PACKAGES>
    </AUTOSAR>


Selecting XML schema file name
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can select the name of the schema (.xsd) file to use by setting the schema argument to an .xsd file name.
This might be important to set in AUTOSAR 3 since the file names does not seem to be standardised.

In AUTOSAR 4 you shouldn't need to set this since the schema file name is now standardised based on AUTOSAR version.

.. code-block:: python

    import autosar

    ws = autosar.workspace(version="3.2.1", schema="AUTOSAR_3-2-1.xsd")
    print(ws.toXML())

.. code-block:: xml

    <?xml version="1.0" encoding="UTF-8"?>
    <AUTOSAR xsi:schemaLocation="http://autosar.org/3.2.1 AUTOSAR_3-2-1.xsd" xmlns="http://autosar.org/3.2.1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
        <TOP-LEVEL-PACKAGES>
        </TOP-LEVEL-PACKAGES>
    </AUTOSAR>
    
    

