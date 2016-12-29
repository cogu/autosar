import xml.etree.ElementTree as ElementTree
import autosar.base

class Element(object):
   def __init__(self, name, parent=None, adminData=None):
      if isinstance(adminData, dict):
         adminDataObj=autosar.base.createAdminData(adminData)
      else:
         adminDataObj = adminData
      if (adminDataObj is not None) and not isinstance(adminDataObj, autosar.base.AdminData):
         raise ValueError("adminData must be of type dict or autosar.base.AdminData")
      self.name=name
      self.adminData=adminDataObj
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