from autosar.workspace import Workspace
import autosar.component
import autosar.behavior
import autosar.portinterface
import autosar.datatype
import autosar.constant
import autosar.signal
import autosar.package
import autosar.rte
import autosar.builder
import autosar.port
import autosar.element
from abc import (ABC,abstractmethod)
import autosar.base
import autosar.bsw.com
import autosar.bsw.os
import autosar.util

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
   return autosar.element.DataElement(name, typeRef, isQueued, softwareAddressMethodRef, swCalibrationAccess, swImplPolicy, parent, adminData)

def ApplicationError(name, errorCode, parent=None, adminData=None):
   return autosar.portinterface.ApplicationError(name, errorCode, parent, adminData)

def ModeGroup(name, typeRef, parent=None, adminData=None):
   return autosar.mode.ModeGroup(name, typeRef, parent, adminData)

def ParameterDataPrototype(name, typeRef, swAddressMethodRef=None, swCalibrationAccess=None, initValue = None, parent=None, adminData=None):
   return autosar.element.ParameterDataPrototype(name, typeRef, swAddressMethodRef, swCalibrationAccess, initValue, parent, adminData)


#template support
class Template(ABC):

   usageCount = 0 #number of times this template have been applied
   static_ref = ''

   @classmethod
   def ref(cls, ws):
      return cls.static_ref

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
