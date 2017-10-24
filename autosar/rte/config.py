import autosar.component
import autosar.rte.base
import autosar.bsw.com
from collections import namedtuple
#from autosar.rte.base import PortConnector, PortInstance

class Config:
   """
   RTE Configuration
   """
   def __init__(self, partition):
      self.services=[]
      self.partition = partition
      self.data_elements=[]      
      
   
      
      
      
