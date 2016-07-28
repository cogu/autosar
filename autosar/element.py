import xml.etree.ElementTree as ElementTree


class Element(object):
   def __init__(self,name,parent=None):
      self.name=name
      self.adminData=None
      self.parent=parent
   @property
   def ref(self):
      if self.parent is not None:
         return self.parent.ref+'/%s'%self.name
      else:
         return None
         
   
   def asdict(self):
      data={'type': self.__class__.__name__}
      for key, value in self.__dict__.items():
         if value is not None:
            if key=='adminData':
               if self.adminData is not None:
                  data['adminData']=self.adminData.asdict()
            elif key=='parent':
               continue
            else:
               if hasattr(value,'asdict'):
                  #print('complex'+str(type(value)))
                  data[key]=value.asdict()
               else:
                  #print('simple'+str(type(value)))
                  data[key]=value
      return data
   
   # def findWS(self):
   #    """depcrecated, use root() instead"""
   #    return self.root()
         
   def rootWS(self):
      if self.parent is None:
         return None
      else:
         return self.parent.rootWS()
   
   def __deepcopy__(self,memo):
      raise NotImplementedError(type(self))