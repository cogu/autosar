import sys
from autosar.base import splitRef
import autosar.component
from autosar.parser.behavior_parser import BehaviorParser
from autosar.parser.parser_base import ElementParser
from autosar.parser.constant_parser import ConstantParser

def _getDataElemNameFromComSpec(xmlElem,portInterfaceRef):
   if xmlElem.find('./DATA-ELEMENT-REF') is not None:
      dataElemRef = splitRef(xmlElem.find('./DATA-ELEMENT-REF').text)
      assert(dataElemRef is not None)
      dataElemName = dataElemRef.pop()
      tmp = '/'+'/'.join(dataElemRef)
      if portInterfaceRef == tmp:
         return dataElemName
   return None

def _getOperationNameFromComSpec(xmlElem,portInterfaceRef):
   xmlOperation=xmlElem.find('./OPERATION-REF')
   if xmlOperation is not None:
      operationRef = splitRef(xmlOperation.text)
      assert(operationRef is not None)
      operationName = operationRef.pop()
      tmp = '/'+'/'.join(operationRef)
      if portInterfaceRef == tmp:
         return operationName
   return None

def _getParameterNameFromComSpec(xmlElem,portInterfaceRef):
   if xmlElem.tag == 'PARAMETER-REF':
      parameterRef = splitRef(xmlElem.text)
      assert(parameterRef is not None)
      name = parameterRef.pop()
      tmp = '/'+'/'.join(parameterRef)
      if portInterfaceRef == tmp:
         return name
   return None

class ComponentTypeParser(ElementParser):
   """
   ComponentType parser
   """

   def __init__(self,version=3.0):
      super().__init__(version)
      if self.version >=4.0:
         self.behavior_parser = BehaviorParser(version)
         self.constant_parser = ConstantParser(version)

      if self.version >= 3.0 and self.version < 4.0:
         self.switcher = { 'APPLICATION-SOFTWARE-COMPONENT-TYPE': self.parseSoftwareComponent,
                           'COMPLEX-DEVICE-DRIVER-COMPONENT-TYPE': self.parseSoftwareComponent,
                           'SWC-IMPLEMENTATION': self.parseSwcImplementation,
                           'COMPOSITION-TYPE': self.parseCompositionType,
                           'CALPRM-COMPONENT-TYPE': self.parseSoftwareComponent,
                           'SERVICE-COMPONENT-TYPE': self.parseSoftwareComponent
                          }
      elif self.version >= 4.0:
         self.switcher = {
            'APPLICATION-SW-COMPONENT-TYPE': self.parseSoftwareComponent,
            'SWC-IMPLEMENTATION': self.parseSwcImplementation
         }

   def getSupportedTags(self):
      return self.switcher.keys()

   def parseElement(self, xmlElement, parent = None):
      parseFunc = self.switcher.get(xmlElement.tag)
      if parseFunc is not None:
         return parseFunc(xmlElement,parent)
      else:
         return None

   def parseSoftwareComponent(self,xmlRoot,parent=None):
      componentType=None
      handledTags = ['SHORT-NAME','APPLICATION-SOFTWARE-COMPONENT-TYPE', 'COMPLEX-DEVICE-DRIVER-COMPONENT-TYPE', 'APPLICATION-SW-COMPONENT-TYPE']
      if xmlRoot.tag=='APPLICATION-SOFTWARE-COMPONENT-TYPE': #for AUTOSAR 3.x
         componentType = autosar.component.ApplicationSoftwareComponent(self.parseTextNode(xmlRoot.find('SHORT-NAME')),parent)
      elif xmlRoot.tag=='COMPLEX-DEVICE-DRIVER-COMPONENT-TYPE':
         componentType = autosar.component.ComplexDeviceDriverComponent(self.parseTextNode(xmlRoot.find('SHORT-NAME')),parent)
      elif xmlRoot.tag == 'APPLICATION-SW-COMPONENT-TYPE': #for AUTOSAR 4.x
         componentType = autosar.component.ApplicationSoftwareComponent(self.parseTextNode(xmlRoot.find('SHORT-NAME')),parent)
      elif xmlRoot.tag == 'SERVICE-COMPONENT-TYPE':
         componentType = autosar.component.ServiceComponent(self.parseTextNode(xmlRoot.find('SHORT-NAME')),parent)
      elif xmlRoot.tag == 'CALPRM-COMPONENT-TYPE':
         componentType = autosar.component.ParameterComponent(self.parseTextNode(xmlRoot.find('SHORT-NAME')),parent)
      else:
         raise NotImplementedError(xmlRoot.tag)
      for xmlElem in xmlRoot.findall('./*'):
         if xmlElem.tag not in handledTags:
            if xmlElem.tag == 'PORTS':
               self.parseComponentPorts(componentType,xmlRoot)
            elif xmlElem.tag == 'INTERNAL-BEHAVIORS':
               behaviors = xmlElem.findall('./SWC-INTERNAL-BEHAVIOR')
               if len(behaviors)>1:
                  raise ValueError('%s: an SWC cannot have multiple internal behaviors'%(componentType))
               elif len(behaviors) == 1:
                  componentType.behavior = self.behavior_parser.parseSWCInternalBehavior(behaviors[0], componentType)
            else:
               print('Unhandled tag: '+xmlElem.tag, file=sys.stderr)
      return componentType

   def parseComponentPorts(self,componentType,xmlRoot):
      xmlPorts=xmlRoot.find('PORTS')
      assert(xmlPorts is not None)
      for xmlPort in xmlPorts.findall('*'):
         if(xmlPort.tag == "R-PORT-PROTOTYPE"):
            portName = xmlPort.find('SHORT-NAME').text
            portInterfaceRef = self.parseTextNode(xmlPort.find('REQUIRED-INTERFACE-TREF'))
            port = autosar.component.RequirePort(portName,portInterfaceRef,parent=componentType)
            if xmlPort.findall('./REQUIRED-COM-SPECS') is not None:
               for xmlItem in xmlPort.findall('./REQUIRED-COM-SPECS/*'):
                  if xmlItem.tag == 'CLIENT-COM-SPEC':
                     operationName=_getOperationNameFromComSpec(xmlItem,portInterfaceRef)
                     comspec=autosar.component.OperationComSpec(operationName)
                     port.comspec.append(comspec)
                  elif xmlItem.tag == 'UNQUEUED-RECEIVER-COM-SPEC' or xmlItem.tag == 'NONQUEUED-RECEIVER-COM-SPEC':
                     dataElemName = _getDataElemNameFromComSpec(xmlItem,portInterfaceRef)
                     comspec = autosar.component.DataElementComSpec(dataElemName)
                     if xmlItem.find('./ALIVE-TIMEOUT') != None:
                        comspec.aliveTimeout = self.parseTextNode(xmlItem.find('./ALIVE-TIMEOUT'))
                     if self.version >= 4.0:
                        xmlElem = xmlItem.find('./INIT-VALUE')
                        if xmlElem != None:
                           for xmlChild in xmlElem.findall('./*'):
                              if xmlChild.tag == 'CONSTANT-REFERENCE':
                                 comspec.initValueRef = self.parseTextNode(xmlChild.find('./CONSTANT-REF'))
                              else:
                                 values = self.constant_parser.parseValueV4(xmlElem, None)
                                 if len(values) != 1:
                                    raise ValueError('INIT-VALUE cannot cannot contain multiple elements')
                                 comspec.initValue = values[0]
                     else:
                        if xmlItem.find('./INIT-VALUE-REF') != None:
                           comspec.initValueRef = self.parseTextNode(xmlItem.find('./INIT-VALUE-REF'))
                     port.comspec.append(comspec)
                  elif xmlItem.tag == 'QUEUED-RECEIVER-COM-SPEC':
                     dataElemName = _getDataElemNameFromComSpec(xmlItem,portInterfaceRef)
                     comspec = autosar.component.DataElementComSpec(dataElemName)
                     if xmlItem.find('./QUEUE-LENGTH') != None:
                        comspec.queueLength = self.parseTextNode(xmlItem.find('./QUEUE-LENGTH'))
                     port.comspec.append(comspec)
                  elif xmlItem.tag == 'MODE-SWITCH-RECEIVER-COM-SPEC':
                     comspec = self._parseModeSwitchComSpec(xmlItem)
                     port.comspec.append(comspec)
                  elif xmlItem.tag == 'PARAMETER-REQUIRE-COM-SPEC':
                     comspec = self._parseParameterComSpec(xmlItem, portInterfaceRef)
                     port.comspec.append(comspec)
                  else:
                     raise NotImplementedError(xmlItem.tag)
            componentType.requirePorts.append(port)
         elif(xmlPort.tag == 'P-PORT-PROTOTYPE'):
            portName = xmlPort.find('SHORT-NAME').text
            portInterfaceRef = self.parseTextNode(xmlPort.find('PROVIDED-INTERFACE-TREF'))
            port = autosar.component.ProvidePort(portName,portInterfaceRef,parent=componentType)
            if xmlPort.findall('./PROVIDED-COM-SPECS') is not None:
               for xmlItem in xmlPort.findall('./PROVIDED-COM-SPECS/*'):
                  if xmlItem.tag == 'SERVER-COM-SPEC':
                     operationName=_getOperationNameFromComSpec(xmlItem,portInterfaceRef)
                     comspec=autosar.component.OperationComSpec(operationName)
                     comspec.queueLength=self.parseIntNode(xmlItem.find('QUEUE-LENGTH'))
                     port.comspec.append(comspec)
                  elif xmlItem.tag == 'UNQUEUED-SENDER-COM-SPEC' or xmlItem.tag == 'NONQUEUED-SENDER-COM-SPEC':
                     dataElemName = _getDataElemNameFromComSpec(xmlItem,portInterfaceRef)
                     comspec = autosar.component.DataElementComSpec(dataElemName)
                     if self.version >= 4.0:
                        if xmlItem.find('./INIT-VALUE') != None:
                           comspec.initValueRef = self.parseTextNode(xmlItem.find('./INIT-VALUE/CONSTANT-REFERENCE/CONSTANT-REF'))
                     else:
                        if xmlItem.find('./INIT-VALUE-REF') != None:
                           comspec.initValueRef = self.parseTextNode(xmlItem.find('./INIT-VALUE-REF'))
                     if xmlItem.find('./CAN-INVALIDATE') != None:
                        comspec.canInvalidate = True if self.parseTextNode(xmlItem.find('./CAN-INVALIDATE'))=='true' else False
                     port.comspec.append(comspec)
                  elif xmlItem.tag == 'QUEUED-SENDER-COM-SPEC':
                     dataElemName = _getDataElemNameFromComSpec(xmlItem,portInterfaceRef)
                     comspec = autosar.component.DataElementComSpec(dataElemName)
                     port.comspec.append(comspec)
                  else:
                     raise NotImplementedError(xmlItem.tag)
            componentType.providePorts.append(port)

   def parseSwcImplementation(self,xmlRoot,parent=None):
      ws = parent.rootWS()
      assert(ws is not None)
      name = self.parseTextNode(xmlRoot.find('SHORT-NAME'))
      behaviorRef = self.parseTextNode(xmlRoot.find('BEHAVIOR-REF'))
      implementation = autosar.component.SwcImplementation(name,behaviorRef,parent=parent)
      behavior = ws.find(behaviorRef)
      if behavior is not None:
         swc = ws.find(behavior.componentRef)
         if swc is not None:
            swc.implementation=implementation
      return implementation

   def parseCompositionType(self,xmlRoot,parent=None):
      """
      parses COMPOSITION-TYPE
      """
      assert(xmlRoot.tag=='COMPOSITION-TYPE')
      swc=autosar.component.CompositionComponent(self.parseTextNode(xmlRoot.find('SHORT-NAME')),parent)
      for elem in xmlRoot.findall('./*'):
         if elem.tag=='SHORT-NAME':
            continue
         if elem.tag=='PORTS':
            self.parseComponentPorts(swc,xmlRoot)
         elif elem.tag=='COMPONENTS':
            self.parseComponents(elem,swc)
         elif elem.tag=='CONNECTORS':
            self.parseConnectors(elem,swc)
         else:
            raise NotImplementedError(elem.tag)
      return swc

   def parseComponents(self,xmlRoot,parent):
      """
      parses <COMPONENTS>
      """
      assert(xmlRoot.tag=='COMPONENTS')
      for elem in xmlRoot.findall('./*'):
         if elem.tag=='COMPONENT-PROTOTYPE':
            name=self.parseTextNode(elem.find('SHORT-NAME'))
            typeRef=self.parseTextNode(elem.find('TYPE-TREF'))
            parent.components.append(autosar.component.ComponentPrototype(name,typeRef,parent))
         else:
            raise NotImplementedError(elem.tag)

   def parseConnectors(self,xmlRoot,parent=None):
      """
      parses <CONNECTORS>
      """
      assert(xmlRoot.tag=='CONNECTORS')
      for elem in xmlRoot.findall('./*'):
         if elem.tag=='ASSEMBLY-CONNECTOR-PROTOTYPE':
            name=self.parseTextNode(elem.find('SHORT-NAME'))
            providerComponentRef=self.parseTextNode(elem.find('./PROVIDER-IREF/COMPONENT-PROTOTYPE-REF'))
            providerPortRef=self.parseTextNode(elem.find('./PROVIDER-IREF/P-PORT-PROTOTYPE-REF'))
            requesterComponentRef=self.parseTextNode(elem.find('./REQUESTER-IREF/COMPONENT-PROTOTYPE-REF'))
            requesterPortRef=self.parseTextNode(elem.find('./REQUESTER-IREF/R-PORT-PROTOTYPE-REF'))
            parent.assemblyConnectors.append(autosar.component.AssemblyConnector(name, autosar.component.ProviderInstanceRef(providerComponentRef,providerPortRef), autosar.component.RequesterInstanceRef(requesterComponentRef,requesterPortRef)))
         elif elem.tag=='DELEGATION-CONNECTOR-PROTOTYPE':
            name=self.parseTextNode(elem.find('SHORT-NAME'))
            innerComponentRef=self.parseTextNode(elem.find('./INNER-PORT-IREF/COMPONENT-PROTOTYPE-REF'))
            innerPortRef=self.parseTextNode(elem.find('./INNER-PORT-IREF/PORT-PROTOTYPE-REF'))
            outerPortRef=self.parseTextNode(elem.find('./OUTER-PORT-REF'))
            parent.delegationConnectors.append(autosar.component.DelegationConnector(name, autosar.component.InnerPortInstanceRef(innerComponentRef,innerPortRef), autosar.component.OuterPortRef(outerPortRef)))
         else:
            raise NotImplementedError(elem.tag)

   def _parseModeSwitchComSpec(self, xmlRoot):
      (enhancedMode, supportAsync) = (False, False)
      for xmlElem in xmlRoot.findall('./*'):
         if xmlElem.tag == 'ENHANCED-MODE-API':
            enhancedMode = self.parseBooleanNode(xmlElem)
         elif xmlElem.tag == 'SUPPORTS-ASYNCHRONOUS-MODE-SWITCH':
            supportAsync = self.parseBooleanNode(xmlElem)
         else:
            raise NotImplementedError(xmlElem.tag)
      return autosar.component.ModeSwitchComSpec(enhancedMode, supportAsync)

   def _parseParameterComSpec(self, xmlRoot, portInterfaceRef):
      (initValue, name) = (None, None)
      for xmlElem in xmlRoot.findall('./*'):
         if xmlElem.tag == 'INIT-VALUE':
            values = self.constant_parser.parseValueV4(xmlElem, None)
            if len(values) != 1:
               raise ValueError('INIT-VALUE cannot cannot contain multiple elements')
            initValue = values[0]
         elif xmlElem.tag == 'PARAMETER-REF':
            name = _getParameterNameFromComSpec(xmlElem, portInterfaceRef)
         else:
            raise NotImplementedError(xmlElem.tag)
      if (name is not None):
         return autosar.component.ParameterComSpec(name, initValue)
      else:
         raise RuntimeError('PARAMETER-REQUIRE-COM-SPEC must have a PARAMETER-REF')