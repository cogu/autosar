AUTOSAR
--------

A set of python modules for working with `AUTOSAR <https://www.autosar.org/>`_ XML files

**Usage:**:

    >>> import autosar
    >>> ws = autosar.workspace()
    >>> ws.loadXML('DataTypes.arxml', roles={'/DataType': 'DataType'})
    >>> ws.loadXML('Constants.arxml', roles={'/Constant': 'Constant'})
    >>> ws.loadXML('PortInterfaces.arxml', roles={'/PortInterface': 'PortInterface'})
    >>> package = ws.createPackage('ComponentType', role='ComponentType')
    >>> swc = package.createApplicationSoftwareComponent('EngineStart')
    >>> swc.createProvidePort('EngineStartControlStatus', 'EngineStartControlStatus_I', initValueRef='C_EngineStartControlStatus_IV')
    >>> swc.createRequirePort('EngStartProhibByTransm', 'EngStartProhibByTransm_I', initValueRef='C_EngStartProhibByTransm_IV')
    >>> portAccessList = ['EngStartProhibByTransm', 'EngineStartControlStatus']
    >>> swc.behavior.createRunnable('EngineStart_run', portAccess=portAccessList)
    >>> swc.behavior.createTimingEvent('EngineStart_run', period=20)
    >>> ws.saveXML('EngineStart.arxml', packages=['ComponentType'])

Prerequisites
-------------
Python 3.x 

Documentation
-------------
The documentation can be found `here <http://autosar.readthedocs.io/en/latest/>`_.


