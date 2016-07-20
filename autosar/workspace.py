from autosar.package import Package
from autosar.datatype import DataTypeParser,DataTypeSemanticsParser,DataTypeUnitsParser
import autosar.component
from autosar.base import parseXMLFile,getXMLNamespace,removeNamespace
from autosar.portinterface import PortInterfacePackageParser,CEPParameterGroupPackageParser,ModeDeclarationGroupPackageParser
from autosar.constant import ConstantPackageParser
from autosar.element import Element
from autosar.behavior import BehaviorParser
from autosar.signal import SignalParser
from autosar.system import SystemParser
from autosar.writer import WorkspaceWriter

class PackageParser(object):
   def __init__(self,version,rootProject=None):
      self.version=version
      self.rootProject=rootProject
      
            
   def loadXML(self,package,xmlRoot):
      dataTypeParser = DataTypeParser(self,self.version)
      componentTypeParser = autosar.component.ComponentTypeParser(self,self.version)
      dataTypeSemanticsParser = DataTypeSemanticsParser(self,self.version)
      dataTypeUnitsParser = DataTypeUnitsParser(self,self.version)
      cepParameterGroupPackageParser = CEPParameterGroupPackageParser(self,self.version)
      modeDeclarationGroupPackageParser = ModeDeclarationGroupPackageParser(self,self.version)
      portInterfacePackageParser = PortInterfacePackageParser(self,self.version)
      constantPackageParser = ConstantPackageParser(self,self.version)
      behaviorParser=BehaviorParser(self,self.version)
      signalParser=SignalParser(self,self.version)
      systemParser=SystemParser(self,self.version)
      
      if self.version == 3:
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
                          'SYSTEM-SIGNAL': signalParser.parseSystemSignal,
                          'SYSTEM': systemParser.parseSystem
                          }
         
         if xmlRoot.find('ELEMENTS'):
            for xmlElement in xmlRoot.findall('./ELEMENTS/*'):
               parseFunc = self.switcher.get(xmlElement.tag)
               if parseFunc is not None:
                  element = parseFunc(xmlElement,self.rootProject,parent=package)
                  element.parent=package
                  if isinstance(element,Element)==True:
                     package.elements.append(element)
                  else:
                     #raise ValueError("parse error: %s"%type(element))
                     raise ValueError("parse error: %s"%xmlElement.tag)
               else:
                  print("unhandled: %s"%xmlElement.tag)
         if xmlRoot.find('SUB-PACKAGES'):
            for xmlPackage in xmlRoot.findall('./SUB-PACKAGES/AR-PACKAGE'):
               name = xmlPackage.find("./SHORT-NAME").text
               subPackage = Package(name)           
               self.loadXML(subPackage,xmlPackage)
               package.subPackages.append(subPackage)
      else:
         raise NotImplementedError('Version of ARXML not supported')




class Workspace(object):
   def __init__(self):
      self.packages = []
      self.version=None
      self.packageParser=None      
      self.xmlroot = None

   def openXML(self,filename):
      version = None
      xmlroot = parseXMLFile(filename)  #'http://autosar.org/3.0.2'
      namespace = getXMLNamespace(xmlroot)
      
      assert (namespace is not None)
      if namespace == 'http://autosar.org/3.0.2': version = 3
      if version is None:
         raise NotImplementedError('unsupported autosar vesion: %s'%namespace)
      removeNamespace(xmlroot,namespace)
      self.packageParser = PackageParser(version,self)
      self.version=version
      self.xmlroot = xmlroot
         
   def loadXML(self,filename):
      self.openXML(filename)
      self.loadPackage('*')
   
   def loadPackage(self,packagename):
      found=False
      if self.xmlroot is None:
         raise ValueError("xmlroot is None, did you call loadXML()?")
      if self.version == 3:
         if self.xmlroot.find('TOP-LEVEL-PACKAGES'):
            for xmlPackage in self.xmlroot.findall('./TOP-LEVEL-PACKAGES/AR-PACKAGE'):
               name = xmlPackage.find("./SHORT-NAME").text
               if packagename=='*' or packagename==name:
                  found=True
                  package = self.find(name)
                  if package is None:
                     package = Package(name,parent=self)                  
                     self.packages.append(package)
                  self.packageParser.loadXML(package,xmlPackage)                           
      elif self.version==4:
         if self.xmlroot.find('AR-PACKAGES'):
            for xmlPackage in self.xmlroot.findall('.AR-PACKAGES/AR-PACKAGE'):
               name = xmlPackage.find("./SHORT-NAME").text
               if packagename=='*' or packagename==name :
                  found=True
                  package = Package(name)           
                  self.packageParser.loadXML(package,xmlPackage)
                  self.packages.append(package)
      else:
         raise NotImplementedError('Version %s of ARXML not supported'%version)
      if found==False:
         raise KeyError('package not found: '+packagename)
      
      
   def findByRef(self,ref):
      if ref is None: return None
      if ref[0]=='/': ref=ref[1:] #removes initial '/' if it exists
      ref = ref.partition('/')
      for pkg in self.packages:
         if pkg.name == ref[0]:
            if len(ref[2])>0:
               return pkg.findByRef(ref[2])
            return pkg
      return None
   
   def find(self,value):
      return self.findByRef(value)
   
   def asdict(self):
      retval = {'type': 'Project', 'packages':[]}      
      for package in self.packages:         
         retval['packages'].append(package.asdict())         
      return retval
      
   def createPackage(self,name):
      package = Package(name,self)                  
      self.packages.append(package)
      return package

   def dir(self,ref=None,_prefix='/'):
      if ref is None:
         return [x.name for x in self.packages]
      else:
         if ref[0]=='/':
            ref=ref[1:]            
         ref = ref.partition('/')
         result=self.findByRef(ref[0])
         if result is not None:            
            return result.dir(ref[2] if len(ref[2])>0 else None,_prefix+ref[0]+'/')
         else:
            return None
   
   def findWS(self):
      return self
   
   def saveXML(self,filename,packages=None):
      writer=WorkspaceWriter()
      with open(filename,'w') as fp:
         writer.saveXML(fp,self,packages)
         
   def toXML(self,packages=None):
      writer=WorkspaceWriter()
      return writer.toXML(self,packages)
   
   def append(self,elem):
      if isinstance(elem,autosar.package.Package):
         self.packages.append(elem)
         elem.parent=self
      else:
         raise ValueError(type(elem))
   
   @property
   def ref(self):
      return ''
   
   

if __name__ == '__main__':
   print("done")
