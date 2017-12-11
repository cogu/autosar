from autosar.workspace import Workspace
import autosar.component
import autosar.behavior
import autosar.portinterface
import autosar.datatype
import autosar.constant
import autosar.signal
import autosar.package
import autosar.rte
from abc import (ABC,abstractmethod)
from autosar.base import splitRef
import autosar.bsw.com
import autosar.bsw.os

import ntpath
import os
import xml.etree.ElementTree as ElementTree

def workspace(version=3.0, patch = 2, schema=None, attributes=None, useDefaultWriters=True):
   if schema is None and ( (version == 3.0 and patch == 2) or (version == "3.0.2") ):
      schema = 'autosar_302_ext.xsd'
   return autosar.Workspace(version, patch, schema, attributes, useDefaultWriters)


   

def splitRef(ref):
   return autosar.base.splitRef(ref)

def DataElement(name, typeRef, isQueued=False, softwareAddressMethodRef=None, swCalibrationAccess=None, swImplPolicy = None, parent=None, adminData=None):
   return autosar.portinterface.DataElement(name, typeRef, isQueued, softwareAddressMethodRef, swCalibrationAccess, swImplPolicy, parent, adminData)

def ApplicationError(name, errorCode, parent=None, adminData=None):
   return autosar.portinterface.ApplicationError(name, errorCode, parent, adminData)

def ModeGroup(name, typeRef, parent=None, adminData=None):
   return autosar.portinterface.ModeGroup(name, typeRef, parent, adminData)

def CompuMethodConst(name, elements, parent=None, adminData=None):
   return autosar.datatype.CompuMethodConst(name, elements, parent, adminData)

def Parameter(name, typeRef, swAddressMethodRef=None, swCalibrationAccess=None, parent=None, adminData=None):
   return autosar.portinterface.Parameter(name, typeRef, swAddressMethodRef, swCalibrationAccess, parent, adminData)


#template support
class Template(ABC):
   
   usageCount = 0 #number of times this template have been applied
   
   @classmethod
   def get(cls, ws):
      ref = cls.ref(ws)
      if ws.find(ref) is None:
         ws.apply(cls)
      return ws.find(ref)
   
   @classmethod
   @abstractmethod
   def apply(cls, ws, **kwargs):
      """
      Applies this class template to the workspace ws
      """
