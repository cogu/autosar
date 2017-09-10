import autosar.component
import autosar.rte.base
import autosar.bsw.com
from collections import namedtuple

PortConnector = namedtuple('PortConnector', ['first_comp', 'first_port', 'second_comp', 'second_port'])

class Config:
   """
   RTE Configuration
   """
   def __init__(self, partition):
      self.services=[]
      self.components=[]
      self.connectors=[]
      self.com = autosar.bsw.com.Config()
      
      
      
