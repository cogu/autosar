import autosar.component
import autosar.behavior
import autosar.element
import autosar.portinterface
import autosar.datatype
import copy
import autosar.base
import re
from fractions import Fraction

class Package(object):
   packageName = None
   def __init__(self,name,parent=None):
      self.name = name
      self.elements = []
      self.subPackages = []
      self.parent=parent
      self.role=None
   @property
   def ref(self):
      if self.parent is not None:
         return self.parent.ref+'/%s'%self.name
      else:
         return None      

   def find(self,ref):
      if ref.startswith('/'): return self.root().find(ref)
      ref = ref.partition('/')      
      name = ref[0]
      for package in self.subPackages:
         if package.name == name:
            if len(ref[2])>0:
               return package.find(ref[2])
            else:
               return package
      for elem in self.elements:
         if elem.name == name:
            if len(ref[2])>0:
               return elem.find(ref[2])
            else:
               return elem
      return None
   
   def findall(self,ref):
      """
      experimental find-method that has some rudimentary support for globs.      
      """
      if ref is None: return None
      if ref[0]=='/': ref=ref[1:] #removes initial '/' if it exists
      ref = ref.partition('/')
      if ref[0]=='*' and len(ref[2])==0:
         result=list(self.elements)
         result.extend(self.subPackages)
      else:
         result=[]
         for item in (self.elements+self.subPackages):
            if item.name == ref[0] or ref[0]=='*':
               if len(ref[2])>0:
                  result.extend(item.findall(ref[2]))
               else:
                  result.append(item)
         if (len(result)==0) and ('*' in ref[0]):
            p = re.compile(ref[0].replace('*','.*'))
            for item in (self.elements+self.subPackages):
               m = p.match(item.name)
               if m is not None:
                  if len(ref[2])>0:
                     result.extend(item.findall(ref[2]))
                  else:
                     result.append(item)
      return result      
   
   def dir(self,ref=None,_prefix=''):
      if ref==None:
         return [_prefix+x.name for x in self.subPackages]+[_prefix+x.name for x in self.elements]      
      else:
         ref = ref.partition('/')
         result=self.find(ref[0])
         if result is not None:
            return result.dir(ref[2] if len(ref[2])>0 else None,_prefix+ref[0]+'/')
         else:
            return None
      
   
   def asdict(self):
      data={'type':self.__class__.__name__,'name':self.name,'elements':[],'subPackages':[]}
      for element in self.elements:
         if hasattr(element,'asdict'):            
            data['elements'].append(element.asdict())
         else:
            print(type(element))
      for subPackage in self.subPackages:         
         data['subPackages'].append(subPackage.asdict())
      if len(data['elements'])==0: del data['elements']
      if len(data['subPackages'])==0: del data['subPackages']
      return data
   
   def createComponentType(self,name,componentType):
      if componentType is autosar.component.ApplicationSoftwareComponent:         
         swc=autosar.component.ApplicationSoftwareComponent(name,parent=self)
      elif componentType is autosar.component.ComplexDeviceDriverSoftwareComponent:
         swc.autosar.component.ComplexDeviceDriverSoftwareComponent(name,parent=self)
      else:
         raise ValueError(componentType+ "is an unsupported type")
      internalBehavior=autosar.behavior.InternalBehavior('%s_InternalBehavior'%name,self.ref+'/%s'%name,parent=self)
      implementation=autosar.component.SwcImplementation('%s_Implementation'%name,internalBehavior.ref,parent=self)
      swc.behavior=internalBehavior
      swc.implementation=implementation
      self.elements.append(swc)
      self.elements.append(internalBehavior)
      self.elements.append(implementation)
      return swc

   def createIntegerDataType(self,name,min=None,max=None,valueTable=None,offset=None, scaling=None, unit=None):
      """
      Convenience method for creating integer datatypes in a package.
      In order to use this function you must have a subpackage present with role='CompuMethod'
      """
      if (valueTable is not None) and (min is None) and (max is None):
         #used for enumeration types using valueTables with implicitly calculated min and max
         compuMethod=autosar.CompuMethodConst(str(name),list(valueTable))
         semanticsPackage=None
         for pkg in self.subPackages:
            if pkg.role == 'CompuMethod':
               semanticsPackage=pkg
               break
         if (semanticsPackage is not None):
            semanticsPackage.append(compuMethod)
            newType=autosar.IntegerDataType(name,0,len(valueTable)-1,compuMethodRef=compuMethod.ref)
            self.append(newType)
         else:
            raise RuntimeError("no package found with role='CompuMethod'")
      elif (min is not None) and (max is not None) and (offset is not None) and (scaling is not None):
         #creates an integer data type with rational scaling
         f=Fraction.from_float(scaling)
         if f.denominator > 1000: #use the float version in case its not a rational number
            semanticElements=[{'offset':offset, 'numerator':scaling, 'denominator':1}]
         else:
            semanticElements=[{'offset':offset, 'numerator':f.numerator, 'denominator':f.denominator}]
         compuMethod=autosar.CompuMethodRational(name,None,semanticElements)
         for pkg in self.subPackages:
            if pkg.role == 'CompuMethod':
               semanticsPackage=pkg
            elif pkg.role == 'Unit':
               unitPackage = pkg
            
         if (semanticsPackage is not None):
            semanticsPackage.append(compuMethod)
            newType=autosar.IntegerDataType(name,min,max,compuMethodRef=compuMethod.ref)
            self.append(newType)
         else:
            raise RuntimeError("no package found with role='CompuMethod'")
         if unit is not None:
            if unitPackage is not None:
                result = unitPackage.find(str(unit))
                if result == None:
                  unitElem = autosar.datatype.DataTypeUnitElement(unit,unit)
                  unitPackage.append(unitElem)
                  compuMethod.unitRef=unitElem.ref
            else:
               raise RuntimeError("no package found with role='Unit'")
      else:         
         raise NotImplementedError("not implemented")         

   def createSenderReceiverInterface(self,name,dataElements=None,modeDeclarationGroups=None, isService=False):
      """
      creates a new sender-receiver port interface. dataElements can either be a single instance of DataElement or a list of DataElements.
      The same applies to modeDeclarationGroups. isService must be boolean
      """
      portInterface = autosar.SenderReceiverInterface(str(name))
      if isinstance(dataElements,list):
         for elem in dataElements:
            portInterface.append(elem)
      elif isinstance(dataElements,autosar.portinterface.DataElement):         
         portInterface.append(dataElements)
      else:
         raise ValueError("dataElements: expected autosar.DataElement instance or list")
      self.append(portInterface)
   
   def setRole(self,role):
         role=str(role)
         if role in ['CompuMethod','Unit']:
            self.role=role
         else:
            raise ValueError("unknown role type: '%s'"%role)
      
   
   def createSubPackage(self, name, role=None):
      pkg = Package(name)
      if role is not None:
         pkg.setRole(role)
      self.append(pkg)
   
   
         
   def rootWS(self):
      if self.parent is None:
         return None
      else:
         return self.parent.root()
      
   def append(self,elem):
      """appends elem to the self.elements list"""
      if isinstance(elem,autosar.element.Element):         
         self.elements.append(elem)
         elem.parent=self
      elif isinstance(elem,Package):
        self.subPackages.append(elem)
        elem.parent=self
      else:
         raise ValueError('unexpected value type %s'%str(type(elem)))

   def update(self,other):
      """copies/clones each element from other into self.elements"""
      if type(self) == type(other):
         for otherElem in other.elements:            
            newElem=copy.deepcopy(otherElem)
            assert(newElem is not None)
            try:
               i=self.index('elements',otherElem.name)
               oldElem=self.elements[i]
               self.elements[i]=newElem
               oldElem.parent=None               
            except ValueError:
               self.elements.append(newElem)
            newElem.parent=self
      else:
         raise ValueError('cannot update from object of different type')

   def index(self,container,name):
      if container=='elements':
         lst=self.elements
      elif container=='subPackages':
         lst=self.subPackages
      else:
         raise KeyError("%s not in %s"%(container,self.__class__.__name__))
      return autosar.base.indexByName(lst,name)


   def createApplicationSoftwareComponent(self,swcName,behaviorName=None,multipleInstance=False):
      """
      creates an instante of autosar.component.ApplicationSoftwareComponent and adds it to the package.
      It also creates a behavior object of type autosar.behavior.InternalBehavior.
      If behaviorName is None (default) the name of the InteralBehavior object is {swcName}_InternalBehavior
      
      Returns the tuple (swc: object,behavior: object).
      
      Usage:
      (swc,behavior) = Package.createApplicationSoftwareComponent(swcName)
      """
      
      if behaviorName is None:
         behaviorName = str(swcName)+'_InternalBehavior'
      swc = autosar.component.ApplicationSoftwareComponent(swcName,self)      
      behavior = autosar.behavior.InternalBehavior(behaviorName,swc.ref,multipleInstance,self)
      self.append(swc)
      self.append(behavior)
      return (swc,behavior)
      



















