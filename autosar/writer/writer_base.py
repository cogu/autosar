import autosar.base
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
            if sdg.GID is not None:
               lines.append(self.indent('<SDG GID="%s">'%sdg.GID,2))
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
      
      # 							<ADMIN-DATA>
# 								<SDGS>
# 									<SDG GID="edve:InitValueRef">
# 										<SD GID="edve:ValRef"></SD>
# 									</SDG>
# 								</SDGS>
# 							</ADMIN-DATA>