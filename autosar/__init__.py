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


class DcfParser:
   def parseXML(self,filename):
      xmltree = ElementTree.ElementTree()
      xmltree.parse(filename)
      xmlroot = xmltree.getroot();
      return xmlroot

   def parseDCF(self,xmlroot):
      result = {'fileRef':[]}
      for elem in xmlroot.findall('./FILEREF'):
         node = elem.find('./ARXML')
         result['fileRef'].append({'itemType':node.attrib['ROOTITEM'],'path':node.text})
      return result

   def adjustDcfFileRef(self,dcf,basedir):
      for elem in dcf['fileRef']:
         basename = ntpath.basename(elem['path'])
         dirname=ntpath.normpath(ntpath.join(basedir,ntpath.dirname(elem['path'])))
         elem['path']=ntpath.join(dirname,basename)
         if os.path.sep == '/': #are we running in cygwin/Linux?
            elem['path'] = elem['path'].replace(r'\\','/')

   def readFile(self,filename):
      basedir = ntpath.dirname(filename)
      xmlroot = self.parseXML(filename)
      dcf = self.parseDCF(xmlroot)
      self.adjustDcfFileRef(dcf,basedir)
      return dcf


def workspace(version=3.0, patch = 2, schema=None, EcuName=None, packages=None):
   if schema is None and version == 3.0 and patch == 2:
      schema = 'autosar_302_ext.xsd'
   return autosar.Workspace(version, patch, schema, EcuName, packages)

def dcfImport(filename):
   parser = DcfParser()
   dcf = parser.readFile(filename)
   ws = workspace()
   result = {}
   for elem in dcf['fileRef']:
      ws.loadXML(elem['path'])
   return ws

def loadDcf(filename):
   parser = DcfParser()
   dcf = parser.readFile(filename)
   ws = workspace()
   result = []
   lookupTable = {
                     'CONSTANT': {'/Constant': 'Constant'},
                     'DATATYPE': {'/DataType': 'DataType'},
                     'PORTINTERFACE': {'/PortInterface': 'PortInterface'},
                     'COMPONENTTYPE': {'/ComponentType': 'ComponentType'}
                  }
   for elem in dcf['fileRef']:
      roles = lookupTable[elem['itemType']]
      result.append({'type': 'FileRef', 'path': elem['path'], 'roles': roles})
   return result
   

def splitRef(ref):
   return autosar.base.splitRef(ref)

def DataElement(name, typeRef, isQueued=False, softwareAddressMethodRef=None, parent=None, adminData=None):
   return autosar.portinterface.DataElement(name, typeRef, isQueued, softwareAddressMethodRef, None, None, parent, adminData)

def ApplicationError(name, errorCode, parent=None, adminData=None):
   return autosar.portinterface.ApplicationError(name, errorCode, parent, adminData)

def ModeGroup(name, typeRef, parent=None, adminData=None):
   return autosar.portinterface.ModeGroup(name, typeRef, parent, adminData)

def CompuMethodConst(name, elements, parent=None, adminData=None):
   return autosar.datatype.CompuMethodConst(name, elements, parent, adminData)


#template support
class Template(ABC):
   @classmethod
   @abstractmethod
   def apply(cls, ws):
      """
      Applies this class template to the workspace ws
      """
