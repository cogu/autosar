import autosar.package
import autosar.parser.package_parser
import autosar.writer
from autosar.base import parseXMLFile,getXMLNamespace,removeNamespace
import json
import os
import ntpath
import collections

_validWSRoles = ['DataType', 'Constant', 'PortInterface', 'ComponentType', 'ModeDclrGroup', 'CompuMethod', 'Unit']

class Workspace(object):
   def __init__(self,version=3.0):
      self.packages = []
      self.version=version
      self.packageParser=None
      self.xmlroot = None
      self.roles = {'DataType': None, 'Constant': None, 'PortInterface': None, 'ModeDclrGroup': None,
                    'ComponentType': None, 'CompuMethod': None, 'Unit': None} #stores references to the actor (i.e. package) that acts the role

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
      version = None
      xmlroot = parseXMLFile(filename)  #'http://autosar.org/3.0.2'
      namespace = getXMLNamespace(xmlroot)

      assert (namespace is not None)
      if namespace == 'http://autosar.org/3.0.2': version = 3.0
      if version is None:
         raise NotImplementedError('unsupported autosar vesion: %s'%namespace)
      removeNamespace(xmlroot,namespace)
      self.packageParser = autosar.parser.package_parser.PackageParser(version,self)
      self.version=version
      self.xmlroot = xmlroot

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
               name = xmlPackage.find("./SHORT-NAME").text
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
      elif self.version>=4.0:
         if self.xmlroot.find('AR-PACKAGES'):
            for xmlPackage in self.xmlroot.findall('.AR-PACKAGES/AR-PACKAGE'):
               name = xmlPackage.find("./SHORT-NAME").text
               if packagename=='*' or packagename==name :
                  found=True
                  package = Package(name)
                  self.packageParser.loadXML(package,xmlPackage)
                  self.packages.append(package)
                  result.append(package)
                  if (packagename==name) and (role is not None):
                     self.setRole(package.ref, role)

      else:
         raise NotImplementedError('Version %s of ARXML not supported'%version)
      if found==False:
         raise KeyError('package not found: '+packagename)
      return result

   def loadJSON(self, filename):      
      with open(filename) as fp:
         basedir = ntpath.dirname(filename)
         data = json.load(fp)         
         if data is not None:
            for item in data:
               if item['type']=='fileRef':
                  adjustedPath = self._adjustFileRef(item, basedir)
                  if adjustedPath.endswith('.arxml'):
                     self.loadXML(adjustedPath)
                  else:
                     raise NotImplementedError(adjustedPath)
               else:
                  raise ValueError('Unknown type: %s'%item['type'])
   

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
   
   def root(self):
      return self
   
   def saveXML(self,filename,packages=None,ignore=None):
      writer=autosar.writer.WorkspaceWriter()
      with open(filename, 'w', encoding="utf-8") as fp:
         if isinstance(packages,str): packages=[packages]
         if isinstance(ignore,str): ignore=[ignore]
         writer.saveXML(self, fp, packages, ignore)

   def toXML(self, packages=None, ignore=None):
      writer=autosar.writer.WorkspaceWriter()
      if isinstance(packages,str): packages=[packages]
      if isinstance(ignore,str): ignore=[ignore]
      return writer.toXML(self, packages, ignore)

   def append(self,elem):
      if isinstance(elem,autosar.package.Package):
         self.packages.append(elem)
         elem.parent=self
      else:
         raise ValueError(type(elem))
   
   def toJSON(self,packages=None,indent=3):
      data=ws.asdict(packages)
      return json.dumps(data,indent=indent)
      
   def saveJSON(self,filename,packages=None,indent=3):
      data=self.asdict(packages)
      with open(filename,'w') as fp:
         json.dump(data,fp,indent=indent)
         
   def toCode(self, packages=None, header=None):
      writer=autosar.writer.WorkspaceWriter()
      if isinstance(packages,str): packages=[packages]
      return writer.toCode(self,list(packages),str(header))
         
   def saveCode(self, filename, packages=None, ignore=None, head=None, tail=None, module=False):
      """
      saves the workspace as python code so it can be recreated later
      """
      writer=autosar.writer.WorkspaceWriter()
      if isinstance(packages,str): packages=[packages]
      with open(filename,'w', encoding="utf-8") as fp:
         writer.saveCode(self, fp, packages, ignore, head, tail, module)

   @property
   def ref(self):
      return ''

   def listXMLPackages(self):
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
   
   def fromDict(self, data):
      for item in data:
         if item['type'] == 'FileRef':
            if os.path.isfile(item['path']):
               roles = item.get('roles',None)
               self.loadXML(item['path'],roles=roles)
            else:
               raise ValueError('invalid file path "%s"'%item['path'])
            
if __name__ == '__main__':
   print("done")
