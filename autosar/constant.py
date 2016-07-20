from autosar.element import Element


class ConstantPackageParser(object):
   """
   Constant package parser.
   Variable pkg needs to be of type ConstantPackage
   """
   def __init__(self,pkg,version=3):
      if version == 3:
         self.version=version
      else:
         raise NotImplementedError('Version %d of ARXML not supported'%version)
      self.pkg=pkg
                  
   def parseConstantSpecification(self,xmlRoot,rootProject=None,parent=None):
      xmlName = xmlRoot.find('SHORT-NAME')
      if xmlName is not None:
         name = xmlName.text         
         xmlValue = xmlRoot.find('./VALUE/*')         
         if xmlValue is not None:
            constantValue = self.parseConstantValue(xmlValue)
         else:
            constantValue = None
         return Constant(name,constantValue)
      return None
               
   def parseConstantValue(self,xmlValue):
      constantValue = None
      xmlName = xmlValue.find('SHORT-NAME')
      if xmlName is not None:
         name=xmlName.text
         if xmlValue.tag == 'INTEGER-LITERAL':
            typeRef = xmlValue.find('./TYPE-TREF').text
            innerValue = xmlValue.find('./VALUE').text
            constantValue = IntegerValue(name,typeRef,innerValue)
         elif xmlValue.tag=='STRING-LITERAL':
            typeRef = xmlValue.find('./TYPE-TREF').text
            innerValue = xmlValue.find('./VALUE').text
            constantValue = StringValue(name,typeRef,innerValue)
         elif xmlValue.tag=='BOOLEAN-LITERAL':
            typeRef = xmlValue.find('./TYPE-TREF').text
            innerValue = xmlValue.find('./VALUE').text
            constantValue = BooleanValue(name,typeRef,innerValue)
         elif xmlValue.tag=='BOOLEAN-LITERAL':
            typeRef = xmlValue.find('./TYPE-TREF').text
            innerValue = xmlValue.find('./VALUE').text
            constantValue = BooleanValue(name,typeRef,innerValue)
         elif xmlValue.tag == 'RECORD-SPECIFICATION' or xmlValue.tag == 'ARRAY-SPECIFICATION':
            typeRef = xmlValue.find('./TYPE-TREF').text
            if xmlValue.tag == 'RECORD-SPECIFICATION':
               constantValue=RecordValue(name,typeRef)                        
            else:
               constantValue=ArrayValue(name,typeRef)
            for innerElem in xmlValue.findall('./ELEMENTS/*'):               
               innerConstant = self.parseConstantValue(innerElem)
               if innerConstant is not None:
                  constantValue.elements.append(innerConstant)
      return constantValue

class Value(object):
   def __init__(self,name,parent=None):
      self.name = name
      self.parent=parent
   def asdict(self):
      data={'type': self.__class__.__name__}
      data.update(self.__dict__)
      return data
   @property
   def ref(self):
      if self.parent is not None:
         return self.parent.ref+'/%s'%self.name
      else:
         return '/%s'%self.name
   
   def findWS(self):
      if self.parent is None:
         return None
      else:
         return self.parent.findWS()

      

class IntegerValue(Value):
   def __init__(self,name,typeRef=None,value=None):
      super().__init__(name)
      self.typeRef=typeRef
      self.value=value
      
   @property
   def value(self):      
      return self._value
   
   @value.setter
   def value(self,val):      
      if val is not None:
         self._value=int(val)
      else:
         self._value=None

class StringValue(Value):
   def __init__(self,name,typeRef=None,value=None):
      super().__init__(name)
      if value is None:
         value=''
      assert(isinstance(value,str))
      self.typeRef=typeRef
      self.value=value
      
   @property
   def value(self):      
      return self._value
   
   @value.setter
   def value(self,val):      
      if val is not None:
         self._value=str(val)
      else:
         self._value=None

class BooleanValue(Value):
   def __init__(self,name,typeRef=None,value=None):
      super().__init__(name)
      self.typeRef=typeRef
      self.value=value
      
   @property
   def value(self):      
      return self._value
   
   @value.setter
   def value(self,val):      
      if val is not None:
         self._value=bool(val)
      else:
         self._value=None

class RecordValue(Value):
   def __init__(self,name,typeRef=None):
      super().__init__(name)
      self.typeRef=typeRef
      self.elements=[]
   def asdict(self):
      data={'type': self.__class__.__name__,'name':self.name,'typeRef':self.typeRef,'elements':[]}
      for element in self.elements:
         data['elements'].append(element.asdict())
      return data
      
   
class ArrayValue(Value):
   def __init__(self,name,typeRef=None):
      super().__init__(name)
      self.typeRef=typeRef
      self.elements=[]
   def asdict(self):
      data={'type': self.__class__.__name__,'name':self.name,'typeRef':self.typeRef,'elements':[]}
      for element in self.elements:
         data['elements'].append(element.asdict())
      return data


class Constant(Element):
   def __init__(self,name,value=None):
      super().__init__(name)
      self.value=value
      if value is not None:
         value.parent=self
   
   def asdict(self):
      data={'type': self.__class__.__name__,'name':self.name}
      data['value']=self.value.asdict()
      return data

   def findByRef(self,ref):
      if self.value.name==ref:
         return self.value
      return None
   

