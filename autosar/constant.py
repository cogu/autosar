from autosar.element import Element

def initializer_string(constant):
   if constant is None:
      return ''
   elif isinstance(constant, IntegerValue):
      return '%d'%(int(constant.value))
   elif isinstance(constant, RecordValue):
      prolog = '{'
      epilog = '}'
      values = []
      for elem in constant.elements:
         values.append(initializer_string(elem))
      return prolog+', '.join(values) + epilog
   else:
      raise NotImplementedError(str(type(constant)))


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

   def rootWS(self):
      if self.parent is None:
         return None
      else:
         return self.parent.rootWS()

#AUTOSAR 3 constant values
class IntegerValue(Value):

   def tag(self,version=None): return "INTEGER-LITERAL"

   def __init__(self, name, typeRef=None, value=None, parent=None):
      super().__init__(name, parent)
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

   def tag(self,version=None): return "STRING-LITERAL"


   def __init__(self, name, typeRef=None, value=None, parent=None):
      super().__init__(name, parent)
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

   def tag(self,version=None): return "BOOLEAN-LITERAL"

   def __init__(self, name, typeRef=None, value=None, parent=None):
      super().__init__(name, parent)
      self.typeRef=typeRef
      self.value=value

   @property
   def value(self):
      return self._value

   @value.setter
   def value(self,val):
      if val is not None:
         if isinstance(val,str):
            self._value = True if val=='true' else False
         else:
            self._value=bool(val)
      else:
         self._value=None

class RecordValue(Value):
   """
   typeRef is only necessary for AUTOSAR 3 constants
   """
   def tag(self,version=None): return "RECORD-VALUE-SPECIFICATION" if version >= 4.0 else "RECORD-VALUE"

   def __init__(self, name, typeRef=None, parent=None):
      super().__init__(name, parent)
      self.typeRef=typeRef
      self.elements=[]
   def asdict(self):
      data={'type': self.__class__.__name__,'name':self.name,'typeRef':self.typeRef,'elements':[]}
      for element in self.elements:
         data['elements'].append(element.asdict())
      return data


class ArrayValue(Value):
   """
   typeRef is only necessary for AUTOSAR 3 constants
   """
   def tag(self,version=None): return "ARRAY-VALUE-SPECIFICATION" if version >= 4.0 else "ARRAY-SPECIFICATION"

   def __init__(self, name, typeRef=None, parent=None):
      super().__init__(name, parent)
      self.typeRef=typeRef
      self.elements=[]
   def asdict(self):
      data={'type': self.__class__.__name__,'name':self.name,'typeRef':self.typeRef,'elements':[]}
      for element in self.elements:
         data['elements'].append(element.asdict())
      return data

#AUTOSAR 4 constant values

class TextValue(Value):
   def tag(self,version=None): return "TEXT-VALUE-SPECIFICATION"

   def __init__(self, name, value=None, parent=None):
      super().__init__(name, parent)
      if value is None:
         value=''
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

class NumericalValue(Value):
   def tag(self,version=None): return "NUMERICAL-VALUE-SPECIFICATION"

   def __init__(self, name, value=None, parent=None):
      super().__init__(name, parent)
      if value is None:
         value=0
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

#Common class
class Constant(Element):
   
   def tag(self, version): return 'CONSTANT-SPECIFICATION'
   
   def __init__(self, name, value=None, parent=None, adminData=None):
      super().__init__(name, parent, adminData)
      self.value=value
      if value is not None:
         value.parent=self

   def asdict(self):
      data={'type': self.__class__.__name__,'name':self.name}
      data['value']=self.value.asdict()
      return data

   def find(self,ref):
      if self.value.name==ref:
         return self.value
      return None

