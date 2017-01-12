import autosar
import os
import cfile
import sys
from autosar.rte.base import *
from autosar.rte.generators import *

class RteGenerator:
   def __init__(self):
      pass

   def getComponentDataTypes(self, ws, swc):
      typeManager = autosar.rte.RteTypeManager()
      if swc is not None:
            for port in swc.requirePorts+swc.providePorts:
               portInterface=ws.find(port.portInterfaceRef)            
               if portInterface is not None:
                  if (isinstance(portInterface,autosar.portinterface.ParameterInterface)) or (isinstance(portInterface,autosar.portinterface.SenderReceiverInterface)):
                     for elem in portInterface.dataElements:
                        dataType = ws.find(elem.typeRef)
                        if dataType is None:
                           raise ValueError('invalid reference: '+elem.typeRef)
                        typeManager.processType(ws,dataType)
                     if isinstance(portInterface,autosar.portinterface.SenderReceiverInterface) and portInterface.modeGroups is not None:
                        for modeGroup in portInterface.modeGroups:                     
                           modeType = ws.find(modeGroup.typeRef)
                           if modeType is None:
                              raise ValueError('invalid reference: '+modeGroup.typeRef)
                           typeManager.processType(ws, modeType)
                  elif isinstance(portInterface,autosar.portinterface.ClientServerInterface):
                     for operation in portInterface.operations:
                        for argument in operation.arguments:
                           dataType = ws.find(argument.typeRef)
                           if dataType is None:
                              raise ValueError('invalid reference: '+elem.typeRef)
                           typeManager.processType(ws,dataType)                        
                  else:
                     raise NotImplementedError(portInterface.__class__.__name__)               
               else:
                  raise ValueError(port.portInterfaceRef)
      basicTypes,complexTypes, modeTypes = typeManager.getTypes(ws) #these are references only
      return (sorted(basicTypes, key=lambda x: x.upper()), sorted(complexTypes, key=lambda x: x.upper()), sorted(modeTypes, key=lambda x: x.upper()))

   def writeComponentHeaders(self, ws, swc, destDir='.', name=None):
      if isinstance(swc, autosar.component.AtomicSoftwareComponent):
         if name is None:
            name=swc.name
         basicTypes, complexTypes, modeTypes = self.getComponentDataTypes(ws, swc)
         typegen = RteTypeGen()
         typeFilename = 'Rte_Type_%s.h'%name
         typeFilePath = destDir+os.path.sep+typeFilename
         componentFilePath = destDir+os.path.sep+"Rte_%s.h"%name
         typegen.generate(ws, typeFilePath, basicTypes, complexTypes, modeTypes)
         
         
         componentHeadergen=RteHeaderGen()
         componentHeadergen.generate(swc, componentFilePath, typeFilename)
      else:
         sys.stderr.write('not an atomic software component: %s\n'%swc.name)
   
   def writeTypeHeader(self, ws, swc, destDir='.', name=None):
      if name is None:
         name=swc.name
      hfile=C.hfile(destDir+os.path.sep+"Rte_Type.h", guard='_RTE_TYPE_H')
      hfile.code.append(C.include('Rte_Type_%s.h'%name))
      with open(hfile.path, 'w') as fp:
         fp.write(str(hfile))