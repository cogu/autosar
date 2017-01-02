import autosar.base
import xml.sax.saxutils
import json
import collections

class WriterBase():
   def __init__(self,version=3.0):
      self.version=version
      self.lines=[]
      self.indentChar='\t'
      
   def indent(self,lines,indent):
      if isinstance(lines,list):
         return ['%s%s'%(self.indentChar*indent,x) for x in lines]
      elif isinstance(lines,str):
         return '%s%s'%(self.indentChar*indent,lines)
      else:
         raise NotImplementedError(type(lines))
   
   def beginFile(self):
      lines=[]
      lines.append('<?xml version="1.0" encoding="UTF-8"?>')
      if self.version == 3.0:
         lines.append('<AUTOSAR xsi:schemaLocation="http://autosar.org/3.0.2 autosar_302_ext.xsd" xmlns="http://autosar.org/3.0.2" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">')
         lines.append(self.indentChar+'<TOP-LEVEL-PACKAGES>')
      return lines
   
   def endFile(self):
      lines=[]
      if (self.version >= 3.0) and (self.version<4.0):
         lines.append(self.indentChar+'</TOP-LEVEL-PACKAGES>')
      else:
         lines.append(self.indentChar+'</AR-PACKAGES>')
      lines.append('</AUTOSAR>')
      return lines
   
   def beginPackage(self, name,indent=None):
      lines = []
      lines.append('<AR-PACKAGE>')
      lines.append(self.indentChar+'<SHORT-NAME>%s</SHORT-NAME>'%name)
      return lines
   
   def endPackage(self,indent=None):
      lines = []
      lines.append('</AR-PACKAGE>')
      return lines
   
   def toBoolean(self,value):
      if value: return 'true'
      return 'false'
   
   def writeAdminDataXML(self,elem):
      assert(isinstance(elem,autosar.base.AdminData))
      lines = []
      lines.append('<ADMIN-DATA>')
      if len(elem.specialDataGroups)>0:
         lines.append(self.indent('<SDGS>',1))
         for sdg in elem.specialDataGroups:
            if sdg.SDG_GID is not None:
               lines.append(self.indent('<SDG GID="%s">'%sdg.SDG_GID,2))
            else:
               lines.append(self.indent('<SDG>',2))
            if (sdg.SD is not None) and (sdg.SD_GID is not None):
               lines.append(self.indent('<SD GID="%s">%s</SD>'%(sdg.SD_GID,sdg.SD),3))
            elif (sdg.SD is None) and (sdg.SD_GID is not None):
               lines.append(self.indent('<SD GID="%s"></SD>'%(sdg.SD_GID),3))
            elif (sdg.SD is not None) and (sdg.SD_GID is None):
               lines.append(self.indent('<SD>%s</SD>'%(sdg.SD),3))
            lines.append(self.indent('</SDG>',2))
         lines.append(self.indent('</SDGS>',1))
      else:
         lines.append('<SDGS/>')
      lines.append('</ADMIN-DATA>')
      return lines
      
   def writeDescXML(self,elem):
      if hasattr(elem,'desc'):
         if hasattr(elem,'descAttr'):
            descAttr=elem.descAttr
         else:
            descAttr='FOR-ALL'
         lines = []
         lines.append('<DESC>')
         lines.append(self.indent('<L-2 L="%s">%s</L-2>'%(descAttr,xml.sax.saxutils.escape(elem.desc)),1))
         lines.append('</DESC>')
         return lines
      return None
   
   def writeDescCode(self, elem):
      if hasattr(elem,'desc'):
         if hasattr(elem,'descAttr') and (elem.descAttr != "FOR-ALL"):
            descAttr=elem.descAttr
         else:
            descAttr=None
         return elem.desc,descAttr
      return None,None
   
   def writeListCode(self, varname, data):
      """
      writes data as as an array with varname
      """      
      lines=['','%s = ['%varname] #add newline at beginning to make reading easier
      indent=' '*(len(varname)+6)
      for i,elem in enumerate(data):         
         if i+1==len(data):
            lines.append('%s%s'%(indent,str(elem)))
         else:
            lines.append('%s%s,'%(indent,str(elem)))
      indent=' '*(len(varname)+3)
      lines.append('%s]'%indent)
      return lines

   def writeDictCode(self, varname, data):
      """
      same as writeListCode but replaces surrounding [] with {}
      """
      lines=['','%s = {'%varname] #add newline at beginning to make reading easier
      indent=' '*(len(varname)+6)
      for i,elem in enumerate(data):         
         if i+1==len(data):
            lines.append('%s%s'%(indent,str(elem)))
         else:
            lines.append('%s%s,'%(indent,str(elem)))
      indent=' '*(len(varname)+3)
      lines.append('%s}'%indent)
      return lines

   
   def writeAdminDataCode(self, adminData, localvars):
      """
      turns an autosar.base.AdminData object into a create call from ws
      """
      items=[]
      for sdg in adminData.specialDataGroups:
         data=collections.OrderedDict()
         if sdg.SDG_GID is not None: data['SDG_GID']=sdg.SDG_GID
         if sdg.SD_GID is not None: data['SD_GID']=sdg.SD_GID
         if sdg.SD is not None: data['SD']=sdg.SD
         items.append(data)
      if len(items)==0:
         raise ValueError("adminData doesn't seem to contain any SpecialDataGroups")
      elif len(items)==1:
         return json.dumps(items[0])
      else:
         return json.dumps(items)
      
   def _createTypeRef(self, typeRef, localvars):
      """
      returns a represenation of a typeRef string
      if role 'DataType' is setup in the workspace it will only return the name of the reference,
      otherwise it returns the full reference
      """
      return self._createRef(componentRef, 'DataType', localvars)

   def _createComponentRef(self, componentRef, localvars):
      """
      returns a represenation of a componentRef string
      if role 'ComponentType' is setup in the workspace it will only return the name of the reference,
      otherwise it returns the full reference
      """
      return self._createRef(componentRef, 'ComponentType', localvars)
      
   def _createRef(self, ref, role, localvars):
      ws=localvars['ws']
      assert(ws is not None)
      element = ws.find(ref)
      if element is None:
         raise ValueError('invalid reference: '+ref)
      if ws.roles[role] is not None:
         return element.name #use name only
      else:
         return element.ref #use full reference
   
   