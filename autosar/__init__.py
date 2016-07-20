from autosar.workspace import Workspace
from autosar.component import ApplicationSoftwareComponent,ComponentType,RequirePort,ProvidePort,DataElementComSpec
from autosar.behavior import InternalBehavior
from autosar.portinterface import ParameterInterface,SenderReceiverInterface,ClientServerInterface,DataElement
from autosar.datatype import RecordDataType,BooleanDataType,IntegerDataType,CompuMethodConst,CompuMethodRational,StringDataType,ArrayDataType
from autosar.constant import ArrayValue,IntegerValue,StringValue,BooleanValue,RecordValue,Constant
from autosar.base import splitref
from autosar.signal import SystemSignal
from autosar.package import Package
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

__CurrentWS = None

def workspace():
   global __CurrentWS
   __CurrentWS = Workspace()
   return __CurrentWS

def getCurrentWS():
   return __CurrentWS

def setCurrentWS(ws):
   assert(isinstance(ws,autosar.workspace.Workspace))
   __CurrentWS=ws

def dcfImport(filename):
   parser = DcfParser()
   dcf = parser.readFile(filename)
   prj = project()
   result = {}
   for elem in dcf['fileRef']:
      prj.loadXML(elem['path'])
   return prj
