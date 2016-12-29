from autosar.writer.writer_base import WriterBase
from autosar.writer.package_writer import PackageWriter
import collections

class WorkspaceWriter(WriterBase):
   def __init__(self,version=3):
      super().__init__(version)
      self.packageWriter=PackageWriter(self.version)
   
   def saveXML(self,ws,fp,packages=None):
      fp.write(self.toXML(ws,packages))

   def toXML(self,ws,packages=None):      
      lines=self.beginFile()
      result='\n'.join(lines)+'\n'
      for package in ws.packages:
         if (isinstance(packages,list) and package.name in packages) or (packages is None):
            lines=self.indent(self.packageWriter.toXML(package),2)
            result+='\n'.join(lines)+'\n'
      lines=self.endFile()
      return result+'\n'.join(lines)+'\n'
   
   def toCode(self,ws,packages=None, head=None, tail=None):
      localvars = collections.OrderedDict()
      if head is None:
         lines=['import autosar', 'ws=autosar.workspace()']
         result='\n'.join(lines)+'\n\n'
      else:
         if isinstance(head,list):
            head = '\n'.join(head)
         assert(isinstance(head,str))
         result = head+'\n\n'      
      localvars['ws']=ws
      for package in ws.packages:
         if (isinstance(packages,list) and package.name in packages) or (packages is None):
            lines=self.packageWriter.toCode(package, localvars)
            result+='\n'.join(lines)+'\n'
      if tail is None:
         result+='\n'+'print(ws.toXML())\n'
      else:
         if isinstance(tail,list):
            tail = '\n'.join(tail)
         assert(isinstance(tail,str))
         result+='\n'+tail
      return result
      
   def saveCode(self,ws,fp,packages=None,head=None,tail=None):
      fp.write(self.toCode(ws,packages,head,tail))