import autosar.package
import autosar.parser.package_parser
import autosar.writer
from autosar.base import (parseXMLFile, getXMLNamespace, removeNamespace, parseAutosarVersionAndSchema, prepareFilter, parseVersionString)
import json
import os
import ntpath
import collections
import re
#default parsers
from autosar.parser.datatype_parser import (DataTypeParser, DataTypeSemanticsParser, DataTypeUnitsParser)
from autosar.parser.portinterface_parser import (PortInterfacePackageParser,SoftwareAddressMethodParser)
from autosar.parser.constant_parser import ConstantParser
from autosar.parser.behavior_parser import BehaviorParser
from autosar.parser.component_parser import ComponentTypeParser
from autosar.parser.system_parser import SystemParser
from autosar.parser.signal_parser import SignalParser
from autosar.parser.mode_parser import ModeDeclarationParser
from autosar.parser.swc_implementation_parser import SwcImplementationParser
#default writers
from autosar.writer.datatype_writer import XMLDataTypeWriter, CodeDataTypeWriter
from autosar.writer.constant_writer import XMLConstantWriter, CodeConstantWriter
from autosar.writer.portinterface_writer import XMLPortInterfaceWriter, CodePortInterfaceWriter
from autosar.writer.component_writer import XMLComponentTypeWriter, CodeComponentTypeWriter
from autosar.writer.behavior_writer import XMLBehaviorWriter, CodeBehaviorWriter
from autosar.writer.signal_writer import SignalWriter
from autosar.writer.mode_writer import XMLModeWriter

_validWSRoles = ['DataType', 'Constant', 'PortInterface', 'ComponentType', 'ModeDclrGroup', 'CompuMethod', 'Unit',
                 'BaseType', 'DataConstraint']

class PackageRoles(collections.UserDict):
    def __init__(self, data = None):
        if data is None:
            data = {'DataType': None,
             'Constant': None,
             'PortInterface': None,
             'ModeDclrGroup': None,
             'ComponentType': None,
             'CompuMethod': None,
             'Unit': None,
             'DataConstraint': None }
        super().__init__(data)

class WorkspaceProfile:
    """
    A Workspace profile allows users to customize default settings and behaviors
    """
    def __init__(self):
        self.compuMethodSuffix = ''
        self.dataConstraintSuffix = '_DataConstr'
        self.errorHandlingOpt = False
        self.swCalibrationAccessDefault = 'NOT-ACCESSIBLE'
        self.modeSwitchEnhancedModeDefault = False
        self.modeSwitchSupportAsyncDefault = False
        self.modeSwitchAutoSetModeGroupRef = False
        self.swBaseTypeEncodingDefault = 'NONE'

class Workspace:
    """
    An autosar worspace
    """
    def __init__(self, version, patch, schema, release = None, attributes = None, useDefaultWriters=True):
        self.packages = []
        if isinstance(version, str):
            (major, minor, patch) = parseVersionString(version)
            self._version=float("%s.%s"%(major, minor))
            self.patch=patch
        elif isinstance(version, float):
            self._version=version
            self.patch=int(patch)
        self.release = None if release is None else int(release)
        self.schema=schema
        self.packageParser=None
        self.packageWriter=None
        self.xmlroot = None
        self.attributes = attributes
        self.useDefaultWriters = bool(useDefaultWriters)
        self.roles = PackageRoles()
        self.roleStack = collections.deque() #stack of PackageRoles
        self.map = {'packages': {}}
        self.profile = WorkspaceProfile()
        self.unhandledParser = set() # [PackageParser] unhandled:
        self.unhandledWriter =set() #[PackageWriter] Unhandled

    @property
    def version(self):
        return self._version

    @version.setter
    def version(self, version):
        if isinstance(version, str):
            (major, minor, patch) = parseVersionString(version)
            self._version=float("%s.%s"%(major, minor))
            self.patch=patch
        elif isinstance(version, float):
            self._version=version

    @property
    def version_str(self):
        if self.patch is None:
            return str(self._version)
        else:
            return str(self._version)+'.'+str(self.patch)

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

    def getRole(self, role):
        return self.roles[role]

    def setRole(self, ref, role):
        if (role is not None) and (role not in _validWSRoles):
            raise ValueError('Invalid role name: '+role)
        if ref is None:
            self.roles[role]=None
        else:
            package = self.find(ref)
            if package is None:
                raise ValueError('Invalid reference: '+ref)
            if not isinstance(package, autosar.package.Package):
                raise ValueError('Invalid type "%s"for reference "%s", expected Package type'%(str(type(package)),ref))
            package.role=role
            self.roles[role]=package.ref

    def setRoles(self, *items):
        """
        Same as setRole but caller gives a list of tuples where the first item is the package reference, and second item is the role name
        """
        for item in items:
            self.setRole(item[0], item[1])

    def pushRoles(self):
        """
        Saves current package role settings in internal role stack
        """
        self.roleStack.append(PackageRoles(self.roles))

    def popRoles(self):
        """
        Restores last saved package role settings
        """
        roles = self.roleStack.pop()
        self.roles.update(roles)

    def openXML(self,filename):
        xmlroot = parseXMLFile(filename)
        namespace = getXMLNamespace(xmlroot)

        assert (namespace is not None)
        (major, minor, patch, release, schema) = parseAutosarVersionAndSchema(xmlroot)
        removeNamespace(xmlroot,namespace)
        self.version=float('%s.%s'%(major,minor))
        self.major = major
        self.minor = minor
        self.patch = patch
        self.release = release
        self.schema = schema
        self.xmlroot = xmlroot
        if self.version < 3.0:
            raise NotImplementedError("Version below 3.0 is not supported")
        if self.packageParser is None:
            self.packageParser = autosar.parser.package_parser.PackageParser(self.version)
        self._registerDefaultElementParsers(self.packageParser)

    def loadXML(self, filename, roles=None):
        global _validWSRoles
        self.openXML(filename)
        self.loadPackage('*')
        if roles is not None:
            if not isinstance(roles, collections.abc.Mapping):
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
            raise NotImplementedError('Version %s of ARXML not supported'%self.version)
        if found==False and packagename != '*':
            raise KeyError('package not found: '+packagename)

        if (self.unhandledParser):
            print("[PackageParser] unhandled: %s" % (", ".join(self.unhandledParser)))
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
                self.map['packages'][name] = package
            self.packageParser.loadXML(package,xmlPackage)
            self.unhandledParser = self.unhandledParser.union(package.unhandledParser)
            if (packagename==name) and (role is not None):
                self.setRole(package.ref, role)
        return found

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
        if ref[0] in self.map['packages']:
            pkg = self.map['packages'][ref[0]]
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

    def findRolePackage(self, roleName):
        """
        Returns package with role set to roleName or None
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
        if name not in self.map['packages']:
            package = autosar.package.Package(name,self)
            self.packages.append(package)
            self.map['packages'][name] = package
            if role is not None:
                self.setRole(package.ref, role)
            return package
        else:
            return self.map['packages'][name]

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

    def saveXML(self, filename, filters=None, ignore=None):
        if self.packageWriter is None:
            self.packageWriter = autosar.writer.package_writer.PackageWriter(self.version, self.patch)
            if self.useDefaultWriters:
                self._registerDefaultElementWriters(self.packageWriter)
        workspaceWriter=autosar.writer.WorkspaceWriter(self.version, self.patch, self.schema, self.packageWriter)
        with open(filename, 'w', encoding="utf-8") as fp:
            if isinstance(filters,str): filters=[filters]
            if isinstance(ignore,str): filters=[ignore]
            if filters is not None:
                filters = [prepareFilter(x) for x in filters]
            workspaceWriter.saveXML(self, fp, filters, ignore)

        if (self.unhandledWriter):
            print( "[PackageWriter] unhandled: %s" % (", ".join(  self.unhandledWriter  )) )

    def toXML(self, filters=None, ignore=None):
        if self.packageWriter is None:
            self.packageWriter = autosar.writer.package_writer.PackageWriter(self.version, self.patch)
            if self.useDefaultWriters:
                self._registerDefaultElementWriters(self.packageWriter)
        workspaceWriter=autosar.writer.WorkspaceWriter(self.version, self.patch, self.schema, self.packageWriter)
        if isinstance(filters,str): filters=[filters]
        if isinstance(ignore,str): filters=[ignore]
        if filters is not None:
            filters = [prepareFilter(x) for x in filters]
        return workspaceWriter.toXML(self, filters, ignore)

    def append(self,elem):
        if isinstance(elem,autosar.package.Package):
            self.packages.append(elem)
            elem.parent=self
            self.map['packages'][elem.name] = elem
        else:
            raise ValueError(type(elem))

### BEGIN DEPRECATED SECTION (2019-11-07)
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
        return writer.toCode(self, filters ,str(header), ws.noDefault)

    def saveCode(self, filename, filters=None, packages=None, ignore=None, head=None, tail=None, module=False, template=False, version=None, patch=None):
        """
        saves the workspace as python code so it can be recreated later
        """
        if version is None:
            version = self.version
        if patch is None:
            patch = self.patch
        if self.packageWriter is None:
            self.packageWriter = autosar.writer.package_writer.PackageWriter(version, patch)
            if self.useDefaultWriters:
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
            writer.saveCode(self, fp, filters, ignore, head, tail, module, template)
#### END DEPRECATED SECTION

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
            raise NotImplementedError('Version %s of ARXML not supported'%self.version)
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
                    del self.map['packages'][ref[0]]
                    break

    def createAdminData(self, data):
        return autosar.base.createAdminData(data)

    def apply(self, template, **kwargs):
        """
        Applies template to this workspace
        """
        if len(kwargs) == 0:
            template.apply(self)
        else:
            template.apply(self, **kwargs)
        template.usageCount+=1



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
            if self.useDefaultWriters:
                self._registerDefaultElementWriters(self.packageWriter)
        self.packageWriter.registerElementWriter(elementWriter)

    def _registerDefaultElementParsers(self, parser):
        parser.registerElementParser(DataTypeParser(self.version))
        parser.registerElementParser(DataTypeSemanticsParser(self.version))
        parser.registerElementParser(DataTypeUnitsParser(self.version))
        parser.registerElementParser(PortInterfacePackageParser(self.version))
        parser.registerElementParser(SoftwareAddressMethodParser(self.version))
        parser.registerElementParser(ModeDeclarationParser(self.version))
        parser.registerElementParser(ConstantParser(self.version))
        parser.registerElementParser(ComponentTypeParser(self.version))
        parser.registerElementParser(BehaviorParser(self.version))
        parser.registerElementParser(SystemParser(self.version))
        parser.registerElementParser(SignalParser(self.version))
        parser.registerElementParser(SwcImplementationParser(self.version))

    def _registerDefaultElementWriters(self, writer):
        writer.registerElementWriter(XMLDataTypeWriter(self.version, self.patch))
        writer.registerElementWriter(XMLConstantWriter(self.version, self.patch))
        writer.registerElementWriter(XMLPortInterfaceWriter(self.version, self.patch))
        writer.registerElementWriter(XMLComponentTypeWriter(self.version, self.patch))
        writer.registerElementWriter(XMLBehaviorWriter(self.version, self.patch))
        writer.registerElementWriter(CodeDataTypeWriter(self.version, self.patch))
        writer.registerElementWriter(CodeConstantWriter(self.version, self.patch))
        writer.registerElementWriter(CodePortInterfaceWriter(self.version, self.patch))
        writer.registerElementWriter(CodeComponentTypeWriter(self.version, self.patch))
        writer.registerElementWriter(CodeBehaviorWriter(self.version, self.patch))
        writer.registerElementWriter(SignalWriter(self.version, self.patch))
        writer.registerElementWriter(XMLModeWriter(self.version, self.patch))
