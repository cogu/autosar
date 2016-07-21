import autosar.package
import autosar.parser.package_parser
import autosar.writer
from autosar.base import parseXMLFile,getXMLNamespace,removeNamespace

class Workspace(object):
   def __init__(self,version=3.0):
      self.packages = []
      self.version=version
      self.packageParser=None      
      self.xmlroot = None
   
   def __getitem__(self,key):
      if isinstance(key,str):
         return self.find(key)
      else:
         raise ValueError('expected string')

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
         
   def loadXML(self,filename):
      self.openXML(filename)
      self.loadPackage('*')
   
   def loadPackage(self,packagename):
      found=False
      if self.xmlroot is None:
         raise ValueError("xmlroot is None, did you call loadXML()?")
      if self.version >= 3.0 and self.version < 4.0:
         if self.xmlroot.find('TOP-LEVEL-PACKAGES'):
            for xmlPackage in self.xmlroot.findall('./TOP-LEVEL-PACKAGES/AR-PACKAGE'):
               name = xmlPackage.find("./SHORT-NAME").text
               if packagename=='*' or packagename==name:
                  found=True
                  package = self.find(name)
                  if package is None:
                     package = autosar.package.Package(name,parent=self)                  
                     self.packages.append(package)
                  self.packageParser.loadXML(package,xmlPackage)                           
      elif self.version>=4.0:
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
      
      
   def find(self,ref):
      if ref is None: return None
      if ref[0]=='/': ref=ref[1:] #removes initial '/' if it exists
      ref = ref.partition('/')
      for pkg in self.packages:
         if pkg.name == ref[0]:
            if len(ref[2])>0:
               return pkg.find(ref[2])
            return pkg
      return None
   
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
         result=self.find(ref[0])
         if result is not None:            
            return result.dir(ref[2] if len(ref[2])>0 else None,_prefix+ref[0]+'/')
         else:
            return None
   
   def findWS(self):
      return self
   
   def saveXML(self,filename,packages=None):
      writer=autosar.writer.WorkspaceWriter()
      with open(filename,'w') as fp:
         writer.saveXML(fp,self,packages)
         
   def toXML(self,packages=None):
      writer=autosar.writer.WorkspaceWriter()
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
