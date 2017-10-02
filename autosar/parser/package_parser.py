import autosar.package
import autosar.element


from autosar.base import hasAdminData, parseAdminDataNode, parseTextNode
from autosar.parser.portinterface_parser import PortInterfacePackageParser,CEPParameterGroupPackageParser,ModeDeclarationGroupPackageParser
from autosar.parser.constant_parser import ConstantPackageParser
from autosar.parser.datatype_parser import DataTypeParser,DataTypeSemanticsParser,DataTypeUnitsParser
from autosar.parser.behavior_parser import BehaviorParser
from autosar.parser.signal_parser import SignalParser
from autosar.parser.system_parser import SystemParser
from autosar.parser.component_parser import ComponentTypeParser

class PackageParser(object):
   def __init__(self,version,rootProject=None):
      self.version=version
      self.rootProject=rootProject
      dataTypeParser = DataTypeParser(self,self.version)
      componentTypeParser = ComponentTypeParser(self,self.version)
      dataTypeSemanticsParser = DataTypeSemanticsParser(self,self.version)
      dataTypeUnitsParser = DataTypeUnitsParser(self,self.version)
      cepParameterGroupPackageParser = CEPParameterGroupPackageParser(self,self.version)
      modeDeclarationGroupPackageParser = ModeDeclarationGroupPackageParser(self,self.version)
      portInterfacePackageParser = PortInterfacePackageParser(self,self.version)
      constantPackageParser = ConstantPackageParser(self,self.version)
      behaviorParser=BehaviorParser(self,self.version)
      signalParser=SignalParser(self,self.version)
      systemParser=SystemParser(self,self.version)
      self.switcher=None
      
      if self.version >= 3.0 and self.version < 4.0:
         self.switcher = {'ARRAY-TYPE': dataTypeParser.parseArrayType,
                          'BOOLEAN-TYPE': dataTypeParser.parseBooleanType,
                          'INTEGER-TYPE': dataTypeParser.parseIntegerType,
                          'REAL-TYPE': dataTypeParser.parseRealType,
                          'RECORD-TYPE': dataTypeParser.parseRecordType,
                          'STRING-TYPE': dataTypeParser.parseStringType,
                          'APPLICATION-SOFTWARE-COMPONENT-TYPE': componentTypeParser.parseSoftwareComponent,
                          'COMPLEX-DEVICE-DRIVER-COMPONENT-TYPE': componentTypeParser.parseSoftwareComponent,
                          'INTERNAL-BEHAVIOR': behaviorParser.parseInternalBehavior,
                          'SWC-IMPLEMENTATION': componentTypeParser.parseSwcImplementation,
                          'COMPU-METHOD': dataTypeSemanticsParser.parseCompuMethod,
                          'UNIT': dataTypeUnitsParser.parseUnit,
                          'SW-ADDR-METHOD':cepParameterGroupPackageParser.parseSWAddrMethod,
                          'MODE-DECLARATION-GROUP': modeDeclarationGroupPackageParser.parseModeDeclarationGroup,
                          'SENDER-RECEIVER-INTERFACE':portInterfacePackageParser.parseSenderReceiverInterface,
                          'CALPRM-INTERFACE': portInterfacePackageParser.parseParameterInterface,
                          'CLIENT-SERVER-INTERFACE': portInterfacePackageParser.parseClientServerInterface,
                          'CONSTANT-SPECIFICATION': constantPackageParser.parseConstantSpecification,
                          'COMPOSITION-TYPE': componentTypeParser.parseCompositionType,
                          'CALPRM-COMPONENT-TYPE': componentTypeParser.parseSoftwareComponent,
                          'SERVICE-COMPONENT-TYPE': componentTypeParser.parseSoftwareComponent,
                          'SYSTEM-SIGNAL': signalParser.parseSystemSignal,
                          'SYSTEM-SIGNAL-GROUP': signalParser.parseSystemSignalGroup,
                          'SYSTEM': systemParser.parseSystem,                    
                          }
      elif self.version >= 4.0:         
         self.switcher = {
            'APPLICATION-SW-COMPONENT-TYPE' : componentTypeParser.parseSoftwareComponent,                        
            'COMPU-METHOD': dataTypeSemanticsParser.parseCompuMethod,
            'DATA-CONSTR': dataTypeParser.parseDataConstraint,
            'IMPLEMENTATION-DATA-TYPE': dataTypeParser.parseImplementationDataType,
            'SW-BASE-TYPE': dataTypeParser.parseSwBaseType,
            'SWC-IMPLEMENTATION': componentTypeParser.parseSwcImplementation,
            'UNIT': dataTypeUnitsParser.parseUnit,
            'DATA-TYPE-MAPPING-SET': dataTypeParser.parseDataTypeMappingSet
         }
         
      else:
         raise NotImplementedError('Version of ARXML not supported')      
      
            
   def loadXML(self,package,xmlRoot):
      
      assert(self.switcher is not None)
      if xmlRoot.find('ELEMENTS'):
         elementNames = set([x.name for x in package.elements])
         for xmlElement in xmlRoot.findall('./ELEMENTS/*'):
            parseFunc = self.switcher.get(xmlElement.tag)
            if parseFunc is not None:
               element = parseFunc(xmlElement,self.rootProject,parent=package)
               if element is None:
                  print("[package_parser] skipping: %s"%xmlElement.tag)
                  continue
               element.parent=package
               if isinstance(element,autosar.element.Element)==True:
                  if element.name not in elementNames:
                     #ignore duplicated items                        
                     package.append(element)
                     elementNames.add(element.name)
               else:
                  #raise ValueError("parse error: %s"%type(element))
                  raise ValueError("parse error: %s"%xmlElement.tag)
            else:
               print("[package_parser] unhandled: %s"%xmlElement.tag)
      
      if self.version >= 3.0 and self.version < 4.0:
         if xmlRoot.find('SUB-PACKAGES'):
            for xmlPackage in xmlRoot.findall('./SUB-PACKAGES/AR-PACKAGE'):
               name = xmlPackage.find("./SHORT-NAME").text
               subPackage = autosar.package.Package(name)           
               self.loadXML(subPackage,xmlPackage)
               package.subPackages.append(subPackage)
               subPackage.parent=package
      elif self.version >= 4.0:
         for subPackageXML in xmlRoot.findall('./AR-PACKAGES/AR-PACKAGE'):
            name = parseTextNode(subPackageXML.find("./SHORT-NAME"))
            subPackage = autosar.package.Package(name)
            self.loadXML(subPackage, subPackageXML)
            package.subPackages.append(subPackage)
            subPackage.parent=package
         
