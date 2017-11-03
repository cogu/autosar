import autosar.package
import autosar.parser.package_parser
import autosar.writer
from autosar.base import parseXMLFile,getXMLNamespace,removeNamespace,parseAutosarVersionAndSchema,prepareFilter
import json
import os
import ntpath
import collections
import re
from autosar.parser.datatype_parser import (DataTypeParser, DataTypeSemanticsParser, DataTypeUnitsParser)
from autosar.parser.portinterface_parser import (PortInterfacePackageParser,SoftwareAddressMethodParser,ModeDeclarationGroupPackageParser)
#default parsers
from autosar.parser.constant_parser import ConstantParser
from autosar.parser.behavior_parser import BehaviorParser
from autosar.parser.component_parser import ComponentTypeParser
from autosar.parser.system_parser import SystemParser
from autosar.parser.signal_parser import SignalParser
#default writers
from autosar.writer.datatype_writer import XMLDataTypeWriter, CodeDataTypeWriter
from autosar.writer.constant_writer import XMLConstantWriter, CodeConstantWriter
from autosar.writer.portinterface_writer import XMLPortInterfaceWriter, CodePortInterfaceWriter
from autosar.writer.component_writer import XMLComponentTypeWriter, CodeComponentTypeWriter
from autosar.writer.behavior_writer import XMLBehaviorWriter, CodeBehaviorWriter
from autosar.writer.signal_writer import SignalWriter

_validWSRoles = ['DataType', 'Constant', 'PortInterface', 'ComponentType', 'ModeDclrGroup', 'CompuMethod', 'Unit',
                 'BaseType', 'DataConstraint']

class Workspace(object):
   def __init__(self, version, patch, schema, EcuName = None, packages=None):
      self.packages = []
      self.version=version
      self.patch=patch
      self.schema=schema
      self.packageParser=None
      self.packageWriter=None
      self.xmlroot = None
      self.EcuName = EcuName
      self.roles = {'DataType': None,
                    'Constant': None,
                    'PortInterface': None,
                    'ModeDclrGroup': None,
                    'ComponentType': None,
                    'CompuMethod': None,
                    'Unit': None,
                    'BaseType': None,        #AUTOSAR 4 only
                    'DataConstraint': None }  #AUTOSAR 4 only
      
      self.defaultPackages = {'DataType': 'DataType',
                              'Constant': 'Constant',
                              'PortInterface': 'PortInterface',
                              'ModeDclrGroup': 'ModeDclrGroup',
                              'ComponentType': 'ComponentType',
                              'CompuMethod': 'DataTypeSemantics',
                              'Unit': 'DataTypeUnits'}
      self.errorHandlingOpt = False
      if packages is not None:
         for key,value in packages.items():
            if key in self.defaultPackages:
               self.defaultPackages[key]=value
            else:
               raise ValueError("Unknown role name '%s'"%key)
            

   def __getitem__(self,key):
      if isinstance(key,str):
         return self.find(key)
      else:
         raise ValueError('expected string')

   def _adjustFileRef(self,fileRef,basedir):
      basename = ntpath.basename(fileRef['path'])
      dirname=ntpath.normpath(ntpath.join(basedir,ntpath.dirname(fileRef['path'])))
      retval=ntpath.join(dirname,basename)
      if os.path.sep == '/': #are we running in cygwin/Linux?
         retval = retval.replace(r'\\','/')
      return retval

   def setRole(self, ref, role):
      if (role is not None) and (role not in _validWSRoles):
         raise ValueError('invalid role name: '+role)
      package = self.find(ref)
      if package is None:
         raise ValueError('invalid reference: '+ref)
      if not isinstance(package, autosar.package.Package):
         raise ValueError('invalid type "%s"for reference "%s", expected Package type'%(str(type(package)),ref))
      package.role=role
      self.roles[role]=package.ref

   def openXML(self,filename):      
      xmlroot = parseXMLFile(filename)
      namespace = getXMLNamespace(xmlroot)

      assert (namespace is not None)
      (major, minor, patch, schema) = parseAutosarVersionAndSchema(xmlroot)
      removeNamespace(xmlroot,namespace)
      self.version=float('%s.%s'%(major,minor))
      self.major=major
      self.minor=minor
      self.patch=patch
      self.schema=schema
      self.xmlroot = xmlroot
      if self.packageParser is None:
         self.packageParser = autosar.parser.package_parser.PackageParser(self.version)      
      self._registerDefaultElementParsers(self.packageParser)

   def loadXML(self, filename, roles=None):
      global _validWSRoles
      self.openXML(filename)
      self.loadPackage('*')
      if roles is not None:
         if not isinstance(roles, collections.Mapping):
            raise ValueError('roles parameter must be a dictionary or Mapping')
         for ref,role in roles.items():
            self.setRole(ref,role)
   
   def loadPackage(self, packagename, role=None):
      found=False
      result=[]
      if self.xmlroot is None:
         raise ValueError("xmlroot is None, did you call loadXML() or openXML()?")
      if self.version >= 3.0 and self.version < 4.0:
         if self.xmlroot.find('TOP-LEVEL-PACKAGES'):
            for xmlPackage in self.xmlroot.findall('./TOP-LEVEL-PACKAGES/AR-PACKAGE'):
               if self._loadPackageInternal(result, xmlPackage, packagename, role):
                  found = True
               
               
      elif self.version>=4.0:
         if self.xmlroot.find('AR-PACKAGES'):
            for xmlPackage in self.xmlroot.findall('.AR-PACKAGES/AR-PACKAGE'):
               if self._loadPackageInternal(result, xmlPackage, packagename, role):
                  found = True

      else:
         raise NotImplementedError('Version %s of ARXML not supported'%version)
      if found==False:
         raise KeyError('package not found: '+packagename)
      return result
   
   def _loadPackageInternal(self, result, xmlPackage, packagename, role):
      name = xmlPackage.find("./SHORT-NAME").text
      found = False
      if packagename=='*' or packagename==name:
         found=True
         package = self.find(name)
         if package is None:
            package = autosar.package.Package(name, parent=self)
            self.packages.append(package)
            result.append(package)
         self.packageParser.loadXML(package,xmlPackage)
         if (packagename==name) and (role is not None):
            self.setRole(package.ref, role)
      return found

   # def loadJSON(self, filename):      
   #    with open(filename) as fp:
   #       basedir = ntpath.dirname(filename)
   #       data = json.load(fp)
   #       if data is not None:
   #          for item in data:
   #             if item['type']=='fileRef':
   #                adjustedPath = self._adjustFileRef(item, basedir)
   #                if adjustedPath.endswith('.arxml'):
   #                   self.loadXML(adjustedPath)
   #                else:
   #                   raise NotImplementedError(adjustedPath)
   #             else:
   #                raise ValueError('Unknown type: %s'%item['type'])
   

   def find(self, ref, role=None):
      global _validWSRoles
      if ref is None: return None      
      if (role is not None) and ( ref[0] != '/'):
         if role not in _validWSRoles:
            raise ValueError("unknown role name: "+role)
         if self.roles[role] is not None:
            ref=self.roles[role]+'/'+ref #appends the role packet name in front of ref
      
      if ref[0]=='/': ref=ref[1:] #removes initial '/' if it exists
      ref = ref.partition('/')
      for pkg in self.packages:
         if pkg.name == ref[0]:
            if len(ref[2])>0:
               return pkg.find(ref[2])
            return pkg
      return None

   def findall(self,ref):
      """
      experimental find-method that has some rudimentary support for globs.
      """
      if ref is None: return None
      if ref[0]=='/': ref=ref[1:] #removes initial '/' if it exists
      ref = ref.partition('/')
      if ref[0]=='*' and len(ref[2])==0:
         result=list(self.packages)
      else:
         result=[]
         for pkg in self.packages:
            if pkg.name == ref[0] or ref[0]=='*':
               if len(ref[2])>0:
                  result.extend(pkg.findall(ref[2]))
               else:
                  result.append(pkg)
      return result

   def asdict(self,packages=None):
      retval = {'type': self.__class__.__name__, 'packages':[]}
      for package in self.packages:
         if (isinstance(packages,list) and package.name in packages) or (packages is None):
            retval['packages'].append(package.asdict())
      return retval

   def findRolePackage(self,roleName):
      """
      finds a package with role set to roleName
      """
      if roleName is None: return None
      for pkg in self.packages:
         if pkg.role == roleName:
            return pkg
         elif len(pkg.subPackages)>0:
            for childPkg in pkg.subPackages:
               if childPkg.role == roleName:
                  return childPkg
      return None
   
   def createPackage(self,name,role=None):
      alreadyExists = False
      for package in self.packages:
         if package.name == name:
            #package already exists
            alreadyExists = True
            break
      if alreadyExists == False:
         package = autosar.package.Package(name,self)
         self.packages.append(package)
      if role is not None:
         self.setRole(package.ref, role)      
      return package

   def dir(self,ref=None,_prefix='/'):
      if ref is None:
         return [x.name for x in self.packages]
      else:
         if ref[0]=='/':
            ref=ref[1:]
         ref = ref.partition('/')
         result=self.find(ref[0])
         if result is not None:
            return result.dir(ref[2] if len(ref[2])>0 else None,_prefix+ref[0]+'/')
         else:
            return None

   def findWS(self):
      return self
   
   def rootWS(self):
      return self
   
   def saveXML(self, filename, filters=None, packages=None, ignore=None, version=None, patch=None, schema=None):
      if version is None:
         version = self.version
      if patch is None:
         patch = self.patch
      if schema is None:
         schema = self.schema
      if self.packageWriter is None:
         self.packageWriter = autosar.writer.package_writer.PackageWriter(version, patch)
         self._registerDefaultElementWriters(self.packageWriter)
      writer=autosar.writer.WorkspaceWriter(version, patch, schema, self.packageWriter)
      with open(filename, 'w', encoding="utf-8") as fp:
         if isinstance(filters,str): filters=[filters]
         if isinstance(packages,str): packages=[packages]
         if isinstance(ignore,str): filters=[ignore]
         if packages is not None:
            if filters is None:
               filters = []
            for package in packages:
               if package[-1]=='/':
                  filters.append(package+'*')
               else:
                  filters.append(package+'/*')
         if filters is not None:
            filters = [prepareFilter(x) for x in filters]         
         writer.saveXML(self, fp, filters, ignore)

   def toXML(self, filters=None, packages=None, ignore=None, version=None, patch=None, schema=None):      
      if version is None:
         version = self.version
      if patch is None:
         patch = self.patch
      if schema is None:
         schema = self.schema
      if self.packageWriter is None:
         self.packageWriter = autosar.writer.package_writer.PackageWriter(version, patch)
         self._registerDefaultElementWriters(self.packageWriter)
      writer=autosar.writer.WorkspaceWriter(version, patch, schema, self.packageWriter)
      if isinstance(filters,str): filters=[filters]
      if isinstance(packages,str): packages=[packages]
      if isinstance(ignore,str): filters=[ignore]
      if packages is not None:
         if filters is None:
            filters = []
         for package in packages:
            if package[-1]=='/':
               filters.append(package+'*')
            else:
               filters.append(package+'/*')
      if filters is not None:
         filters = [prepareFilter(x) for x in filters]
      return writer.toXML(self, filters, ignore)

   def append(self,elem):
      if isinstance(elem,autosar.package.Package):
         self.packages.append(elem)
         elem.parent=self
      else:
         raise ValueError(type(elem))
   
   # def toJSON(self,packages=None,indent=3):
   #    data=ws.asdict(packages)
   #    return json.dumps(data,indent=indent)
   #    
   # def saveJSON(self,filename,packages=None,indent=3):
   #    data=self.asdict(packages)
   #    with open(filename,'w') as fp:
   #       json.dump(data,fp,indent=indent)
         
   def toCode(self, filters=None, packages=None, header=None, version=None, patch=None):
      if version is None:
         version = self.version
      if patch is None:
         patch = self.patch
      writer=autosar.writer.WorkspaceWriter(version, patch, None, self.packageWriter)
      if isinstance(filters,str): filters=[filters]
      if isinstance(packages,str): packages=[packages]
      if packages is not None:
         if filters is None:
            filters = []
         for package in packages:
            if package[-1]=='/':
               filters.append(package+'*')
            else:
               filters.append(package+'/*')
      if filters is not None:
         filters = [prepareFilter(x) for x in filters]
      return writer.toCode(self, filters ,str(header))
         
   def saveCode(self, filename, filters=None, packages=None, ignore=None, head=None, tail=None, module=False, version=None, patch=None):
      """
      saves the workspace as python code so it can be recreated later
      """
      if version is None:
         version = self.version
      if patch is None:
         patch = self.patch
      if self.packageWriter is None:
         self.packageWriter = autosar.writer.package_writer.PackageWriter(version, patch)
         self._registerDefaultElementWriters(self.packageWriter)
      writer=autosar.writer.WorkspaceWriter(version, patch, None, self.packageWriter)
      if isinstance(packages,str): packages=[packages]
      if isinstance(filters,str): filters=[filters]
      if isinstance(ignore,str): ignore=[ignore]
      if packages is not None:
         if filters is None:
            filters = []
         for package in packages:
            if package[-1]=='/':
               filters.append(package+'*')
            else:
               filters.append(package+'/*')
      if filters is not None:
         filters = [prepareFilter(x) for x in filters]

      with open(filename,'w', encoding="utf-8") as fp:
         writer.saveCode(self, fp, filters, ignore, head, tail, module)

   @property
   def ref(self):
      return ''

   def listPackages(self):
      """returns a list of strings containg the package names of the opened XML file"""
      packageList=[]
      if self.xmlroot is None:
         raise ValueError("xmlroot is None, did you call loadXML() or openXML()?")
      if self.version >= 3.0 and self.version < 4.0:
         if self.xmlroot.find('TOP-LEVEL-PACKAGES'):
            for xmlPackage in self.xmlroot.findall('./TOP-LEVEL-PACKAGES/AR-PACKAGE'):
               packageList.append(xmlPackage.find("./SHORT-NAME").text)
      elif self.version>=4.0:
         if self.xmlroot.find('AR-PACKAGES'):
            for xmlPackage in self.xmlroot.findall('.AR-PACKAGES/AR-PACKAGE'):
               packageList.append(xmlPackage.find("./SHORT-NAME").text)
      else:
         raise NotImplementedError('Version %s of ARXML not supported'%version)
      return packageList
   
   def delete(self, ref):
      if ref is None: return
      if ref[0]=='/': ref=ref[1:] #removes initial '/' if it exists
      ref = ref.partition('/')
      for i,pkg in enumerate(self.packages):
         if pkg.name == ref[0]:
            if len(ref[2])>0:
               return pkg.delete(ref[2])
            else:
               del self.packages[i]
               break      

   def createAdminData(self, data):
      return autosar.base.createAdminData(data)
   
   # def fromDict(self, data):
   #    for item in data:
   #       if item['type'] == 'FileRef':
   #          if os.path.isfile(item['path']):
   #             roles = item.get('roles',None)
   #             self.loadXML(item['path'],roles=roles)
   #          else:
   #             raise ValueError('invalid file path "%s"'%item['path'])

   def apply(self, template):
      """
      Applies template to this workspace
      """
      template.apply(self)

   #---DEPRECATED CODE, TO BE REMOVED ---#
   @classmethod
   def _createDefaultDataTypes(cls, package):
      package.createBooleanDataType('Boolean')
      package.createIntegerDataType('SInt8', -128, 127)
      package.createIntegerDataType('SInt16', -32768, 32767)
      package.createIntegerDataType('SInt32', -2147483648, 2147483647)
      package.createIntegerDataType('UInt8', 0, 255)
      package.createIntegerDataType('UInt16', 0, 65535)
      package.createIntegerDataType('UInt32', 0, 4294967295)   
      package.createRealDataType('Float', None, None, minValType='INFINITE', maxValType='INFINITE')
      package.createRealDataType('Double', None, None, minValType='INFINITE', maxValType='INFINITE', hasNaN=True, encoding='DOUBLE')
   
   def getDataTypePackage(self):
      """
      Returns the current data type package from the workspace. If the workspace doesn't yet have such package a default package will be created and returned.
      """
      package = self.find(self.defaultPackages["DataType"])
      if package is None:
         package=self.createPackage(self.defaultPackages["DataType"], role="DataType")
         package.createSubPackage(self.defaultPackages["CompuMethod"], role="CompuMethod")   
         package.createSubPackage(self.defaultPackages["Unit"], role="Unit")
         Workspace._createDefaultDataTypes(package)
      return package
      
   def getPortInterfacePackage(self):
      """
      Returns the current port interface package from the workspace. If the workspace doesn't yet have such package a default package will be created and returned.
      """
      package = self.find(self.defaultPackages["PortInterface"])
      if package is None:
         package=self.createPackage(self.defaultPackages["PortInterface"], role="PortInterface")
      return package
      
   def getConstantPackage(self):
      """
      Returns the current constant package from the workspace. If the workspace doesn't yet have such package, a default package will be created and returned.
      """
      package = self.find(self.defaultPackages["Constant"])
      if package is None:
         package=self.createPackage(self.defaultPackages["Constant"], role="Constant")
      return package
      
   def getModeDclrGroupPackage(self):
      """
      Returns the current mode declaration group package from the workspace. If the workspace doesn't yet have such package, a default package will be created and returned.
      """
      package = self.find(self.defaultPackages["ModeDclrGroup"])
      if package is None:
         package=self.createPackage(self.defaultPackages["ModeDclrGroup"], role="ModeDclrGroup")
      return package
      
   def getComponentTypePackage(self):
      """
      Returns the current component type package from the workspace. If the workspace doesn't yet have such package, a default package will be created and returned.
      """      
      if self.roles["ComponentType"] is not None:
         packageName = self.roles["ComponentType"]
      else:
         packageName = self.defaultPackages["ComponentType"]
      package = self.find(packageName)
      if package is None:
         package=self.createPackage(packageName, role="ComponentType")
      return package
   
   #--- END DEPCRECATED CODE ---#
   
   def registerElementParser(self, elementParser):
      """
      Registers a custom element parser object
      """
      if self.packageParser is None:
         self.packageParser = autosar.parser.package_parser.PackageParser(self.version)
         self._registerDefaultElementParsers(self.packageParser)
      self.packageParser.registerElementParser(elementParser)

   def registerElementWriter(self, elementWriter):
      """
      Registers a custom element parser object
      """
      if self.packageWriter is None:
         self.packageWriter = autosar.writer.package_writer.PackageWriter(self.version, self.patch)
         self._registerDefaultElementWriters(self.packageWriter)
      self.packageWriter.registerElementWriter(elementWriter)
   
   def _registerDefaultElementParsers(self, parser):
      parser.registerElementParser(DataTypeParser(self.version))
      parser.registerElementParser(DataTypeSemanticsParser(self.version))
      parser.registerElementParser(DataTypeUnitsParser(self.version))
      parser.registerElementParser(PortInterfacePackageParser(self.version))
      parser.registerElementParser(SoftwareAddressMethodParser(self.version))
      parser.registerElementParser(ModeDeclarationGroupPackageParser(self.version))
      parser.registerElementParser(ConstantParser(self.version))
      parser.registerElementParser(ComponentTypeParser(self.version))
      parser.registerElementParser(BehaviorParser(self.version))
      parser.registerElementParser(SystemParser(self.version))
      parser.registerElementParser(SignalParser(self.version))

   def _registerDefaultElementWriters(self, writer):
      writer.registerElementWriter(XMLDataTypeWriter(self.version, self.patch))      
      writer.registerElementWriter(CodeDataTypeWriter(self.version, self.patch))
      writer.registerElementWriter(XMLConstantWriter(self.version, self.patch))
      writer.registerElementWriter(CodeConstantWriter(self.version, self.patch))
      writer.registerElementWriter(XMLPortInterfaceWriter(self.version, self.patch))
      writer.registerElementWriter(CodePortInterfaceWriter(self.version, self.patch))
      writer.registerElementWriter(XMLComponentTypeWriter(self.version, self.patch))
      writer.registerElementWriter(CodeComponentTypeWriter(self.version, self.patch))
      writer.registerElementWriter(XMLBehaviorWriter(self.version, self.patch))
      writer.registerElementWriter(CodeBehaviorWriter(self.version, self.patch))
      writer.registerElementWriter(SignalWriter(self.version, self.patch))
      
