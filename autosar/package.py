import autosar.component
import autosar.behavior
import autosar.element

class Package(object):
   packageName = None
   def __init__(self,name,parent=None):
      self.name = name
      self.elements = []
      self.subPackages = []
      self.parent=parent
   @property
   def ref(self):
      if self.parent is not None:
         return self.parent.ref+'/%s'%self.name
      else:
         return None      

   def findByRef(self,ref):
      ref = ref.partition('/')      
      name = ref[0]
      for package in self.subPackages:
         if package.name == name:
            if len(ref[2])>0:
               return package.findByRef(ref[2])
            else:
               return package
      for elem in self.elements:
         if elem.name == name:
            if len(ref[2])>0:
               return elem.findByRef(ref[2])
            else:
               return elem
      return None
   
   def dir(self,ref=None,_prefix=''):
      if ref==None:
         return [_prefix+x.name for x in self.subPackages]+[_prefix+x.name for x in self.elements]      
      else:
         ref = ref.partition('/')
         result=self.findByRef(ref[0])
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
   
   def findWS(self):
      if self.parent is None:
         return None
      else:
         return self.parent.findWS()
      
   def append(self,elem):
      if isinstance(elem,autosar.element.Element):         
         self.elements.append(elem)
         elem.parent=self
      elif isinstance(elem,Package):
        self.subPackages.append(elem)
        elem.parent=self
      else:
         raise ValueError('unexpected value type %s'%str(type(elem)))

   
   
























