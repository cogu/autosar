import sys
sys.path.insert(0,'..')
import autosar

def _createProvidePortHelper(swc, name, portInterfaceTemplate, initValueTemplate=None):
   ws = swc.rootWS()
   ws.apply(portInterfaceTemplate)
   if initValueTemplate is not None:
      ws.apply(initValueTemplate)
      swc.createProvidePort(name, portInterfaceTemplate.__name__, initValueRef=initValueTemplate.__name__)
   else:
      swc.createProvidePort(name, portInterfaceTemplate.__name__)

def _createRequirePortHelper(swc, name, portInterfaceTemplate, initValueTemplate=None, aliveTimeout=0):
   ws = swc.rootWS()
   ws.apply(portInterfaceTemplate)
   if initValueTemplate is not None:
      ws.apply(initValueTemplate)
      swc.createRequirePort(name, portInterfaceTemplate.__name__, initValueRef=initValueTemplate.__name__, aliveTimeout=aliveTimeout)
   else:
      swc.createRequirePort(name, portInterfaceTemplate.__name__, aliveTimeout=aliveTimeout)

def _createProvidePortTemplate(innerClassName, templateName, portInterfaceTemplate, initValueTemplate):
   @classmethod
   def apply(cls, swc):
      _createProvidePortHelper(swc, cls.name, cls.portInterfaceTemplate, cls.initValueTemplate)
   return type(innerClassName, (autosar.Template,), dict(name=templateName, portInterfaceTemplate=portInterfaceTemplate, initValueTemplate=initValueTemplate, apply=apply))

def _createRequirePortTemplate(innerClassName, templateName, portInterfaceTemplate, initValueTemplate, aliveTimeout=0):
   @classmethod
   def apply(cls, swc):
      _createRequirePortHelper(swc, cls.name, cls.portInterfaceTemplate, cls.initValueTemplate, cls.aliveTimeout)
   return type(innerClassName, (autosar.Template,), dict(name=templateName, portInterfaceTemplate=portInterfaceTemplate, initValueTemplate=initValueTemplate, aliveTimeout=aliveTimeout, apply=apply))
   

def createSenderReceiverPortTemplate(name, portInterfaceTemplate, initValueTemplate=None, aliveTimeout=0):
   return type(name, (), dict(Provide=_createProvidePortTemplate('Provide', name, portInterfaceTemplate, initValueTemplate),
                              Send=_createProvidePortTemplate('Send', name, portInterfaceTemplate, initValueTemplate),
                              Require=_createRequirePortTemplate('Require', name, portInterfaceTemplate, initValueTemplate, aliveTimeout),
                              Receive=_createRequirePortTemplate('Receive', name, portInterfaceTemplate, initValueTemplate, aliveTimeout)))
