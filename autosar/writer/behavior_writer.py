from autosar.writer.writer_base import WriterBase
import autosar.behavior

class BehaviorWriter(WriterBase):
   def __init__(self,version):
      super().__init__(version)
   
   def writeInternalBehaviorXML(self,elem,package):
      assert(isinstance(elem,autosar.behavior.InternalBehavior))
      lines=[]
      ws = elem.rootWS()
      assert(ws is not None)
      lines.append('<%s>'%elem.tag(self.version))
      lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%elem.name,1))
      componentType=ws.find(elem.componentRef)
      assert(componentType is not None)
      lines.append(self.indent('<COMPONENT-REF DEST="%s">%s</COMPONENT-REF>'%(componentType.tag(self.version),componentType.ref),1))      
      if len(elem.runnables)>0:
         lines.append(self.indent('<RUNNABLES>',1))
         for runnable in elem.runnables:
            lines.extend(self.indent(self.writeRunnableXML(runnable),2))
         lines.append(self.indent('</RUNNABLES>',1))
      lines.append(self.indent('<SUPPORTS-MULTIPLE-INSTANTIATION>%s</SUPPORTS-MULTIPLE-INSTANTIATION>'%('true' if elem.multipleInstance else 'false'),1))
      lines.append('</%s>'%elem.tag(self.version))
      return lines
   
   def writeRunnableXML(self,runnable):
      ws=runnable.root()
      assert(ws is not None)
      lines=['<RUNNABLE-ENTITY>',
             self.indent('<SHORT-NAME>%s</SHORT-NAME>'%runnable.name,1),
             self.indent('<CAN-BE-INVOKED-CONCURRENTLY>%s</CAN-BE-INVOKED-CONCURRENTLY>'%('true' if runnable.invokeConcurrently else 'false'),1),
            ]
      if len(runnable.dataReceivePoints)>0:
         lines.append(self.indent('<DATA-RECEIVE-POINTS>',1))
         for dataReceivePoint in runnable.dataReceivePoints:
            lines.append(self.indent('<DATA-RECEIVE-POINT>',2))
            lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%dataReceivePoint.name,3))
            lines.append(self.indent('<DATA-ELEMENT-IREF>',3))
            assert(dataReceivePoint.portRef is not None) and (dataReceivePoint.dataElemRef is not None)
            port = ws.find(dataReceivePoint.portRef)
            assert(port is not None)
            dataElement = ws.find(dataReceivePoint.dataElemRef)
            assert(port is not dataElement)            
            lines.append(self.indent('<R-PORT-PROTOTYPE-REF DEST="%s">%s</R-PORT-PROTOTYPE-REF>'%(port.tag,port.ref),4))
            lines.append(self.indent('<DATA-ELEMENT-PROTOTYPE-REF DEST="%s">%s</DATA-ELEMENT-PROTOTYPE-REF>'%(dataElement.tag,dataElement.ref),4))
            lines.append(self.indent('</DATA-ELEMENT-IREF>',3))
            lines.append(self.indent('</DATA-RECEIVE-POINT>',2))
         lines.append(self.indent('</DATA-RECEIVE-POINTS>',1))
      lines.append(self.indent('<SYMBOL>%s</SYMBOL>'%runnable.symbol,1))
      lines.append('</RUNNABLE-ENTITY>')
      return lines
