import autosar
import os
import cfile
import sys
from autosar.rte.base import *
from autosar.rte.generator2 import *
from autosar.rte.partition import *

class Variable:
   def __init__(self, name, typename, isQueued=False, queueLen=None, initValue=None):
      self.name = name
      self.typename = typename
      self.hasRead = False
      self.hasWrite = False
      self.isQueued = isQueued
      self.queueLen  = queueLen
      self.initValue = initValue

class IntegerVariable(Variable):
   def __init__(self, name, typename, isQueued=False, queueLen=None, initValue=0):
      super().__init__(name, typename, isQueued, queueLen, initValue)
      

class RecordVariable(Variable):
   def __init__(self, name, typename, isQueued=False, queueLen=None, initValue=None):
      super().__init__(name, typename, isQueued, queueLen, initValue)
      self.elements=[]

class ArrayVariable(Variable):
   def __init__(self, name, typename, arrayLen=1, initValue=None):
      super().__init__(name, typename, initValue=initValue)
      self.arrayLen=arrayLen

class BooleanVariable(Variable):
   def __init__(self, name, typename, initValue=None):
      super().__init__(name, typename, initValue=initValue)

class RteGenerator:
   def __init__(self):
      pass

   def _getComponentDataTypes(self, ws, swc):
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
                  #raise ValueError(port.portInterfaceRef)
                  print('invalid port interface reference: '+port.portInterfaceRef, file=sys.stderr)                  
      basicTypes,complexTypes, modeTypes = typeManager.getTypes(ws) #these are references only
      return (sorted(basicTypes, key=lambda x: x.upper()), sorted(complexTypes, key=lambda x: x.upper()), sorted(modeTypes, key=lambda x: x.upper()))

   def _writeTypeHeader(self, ws, swc, outdir='.'):
      hfile=C.hfile(outdir+os.path.sep+"Rte_Type.h", guard='_RTE_TYPE_H')
      hfile.code.append(C.include('Rte_Type_%s.h'%self.name))
      with open(hfile.path, 'w') as fp:
         fp.write(str(hfile))
         
   def writeComponentHeaders(self, swc, outdir='.', name=None):
      pass
      # if isinstance(swc, autosar.component.AtomicSoftwareComponent):
      #    if name is None:
      #       name=swc.name
      #    self.name = name
      #    ws = swc.rootWS()
      #    if ws is None:
      #       raise ValueError("swc '%s' does not belong to a workspace"%swc.name)
      #    basicTypes, complexTypes, modeTypes = self._getComponentDataTypes(ws, swc)
      #    typegen = RteTypeGen()
      #    typeFilename = 'Rte_Type_%s.h'%name
      #    typeFilePath = outdir+os.path.sep+typeFilename
      #    componentFilePath = outdir+os.path.sep+"Rte_%s.h"%name
      #    typegen.generate(ws, typeFilePath, basicTypes, complexTypes, modeTypes, self.name)         
      #    
      #    componentHeadergen=RteHeaderGen()
      #    componentHeadergen.generate(swc, componentFilePath, typeFilename, self.name)
      #    self._writeTypeHeader(ws, swc, outdir)
      # else:
      #    sys.stderr.write('not an atomic software component: %s\n'%swc.name)
   
   def writeDummyRTE(self, ws, componentRefs = None, outdir='.'):
      if not isinstance(componentRefs, list):
         ValueError('ComponentRefs argument must be a list')
      self.ws = ws


      
         
