import cfile as C
import autosar
import os
import sys
from autosar.rte.base import *



class RteHeaderGen:
   def generate(self, swc , filename, typefilename, swc_name):
      assert(isinstance(swc, autosar.component.AtomicSoftwareComponent))
      ws=swc.rootWS()
      dataElements=set()
      operations=set()
      functions={'Receive':[], 'Read':[], 'Write':[], 'Send':[], 'Mode':[], 'Call':[], 'CalPrm':[]}
      basename = basename=os.path.splitext(os.path.basename(filename))[0]
      self.headername = str('_%s_H'%basename).upper()
      with open(filename,'w') as fh:
         self._beginFile(fh,typefilename)                  
         for runnable in swc.behavior.runnables:
            for dataPoint in runnable.dataReceivePoints+runnable.dataSendPoints:
               key=(swc.behavior.componentRef, dataPoint.portRef, dataPoint.dataElemRef)
               dataElements.add(key)
            for callPoint in runnable.serverCallPoints:
               for elem in callPoint.operationInstanceRefs:
                  key=(swc.behavior.componentRef, elem.portRef, elem.operationRef)
                  operations.add(key)
         for elem in dataElements:
            (componentRef,portRef,dataElemRef)=elem
            swc=ws.find(componentRef)
            port=ws.find(portRef)
            dataElement = ws.find(dataElemRef)
            if dataElement is None:
               raise ValueError(dataElemRef)
            typeObj=ws.find(dataElement.typeRef)
            pointer=False           
            ftype=None            
            if isinstance(port,autosar.component.RequirePort):
               if dataElement.isQueued:
                  ftype='Receive'                  
               else:
                  ftype='Read'                  
               pointer=True
            else:
               if dataElement.isQueued:
                  ftype='Send'                  
               else:
                  ftype='Write'                  
            assert(ftype is not None)
            fname='Rte_%s_%s_%s_%s'%(ftype, swc_name, port.name, dataElement.name)
            shortname='Rte_%s_%s_%s'%(ftype, port.name, dataElement.name)
            typeArg=self._type2arg(typeObj,pointer)
            func=C.function(fname, 'Std_ReturnType')
            func.add_arg(typeArg)
            functions[ftype].append({'shortname':shortname,'func':func})

         for elem in operations:
            (componentRef,portRef,operationRef)=elem
            swc=ws.find(componentRef)
            port=ws.find(portRef)
            operation = ws.find(operationRef)
            if operation is None:
               raise ValueError('invalid reference: '+operationRef)
            args=[]
            for argument in operation.arguments:
               dataType = ws.find(argument.typeRef)
               pointer = None
               if isinstance(dataType, autosar.datatype.RecordDataType) or isinstance(dataType, autosar.datatype.ArrayDataType):
                  pointer=True
               else:
                  pointer=False
               if argument.direction == 'INOUT' or argument.direction=='OUT':
                  pointer=True               
               args.append(C.variable(argument.name, dataType.name, pointer=pointer))
            fname='_'.join(['Rte_Call', swc_name, port.name, operation.name])
            shortname='_'.join(['Rte_Call', port.name, operation.name])            
            func=C.function(fname, 'Std_ReturnType', args=args)            
            functions['Call'].append({'shortname':shortname,'func':func})

         #process mode ports
         for port in swc.requirePorts:
            portInterface = ws.find(port.portInterfaceRef)
            if isinstance(portInterface, autosar.portinterface.SenderReceiverInterface):
               if portInterface.modeGroups is not None and len(portInterface.modeGroups)>0:
                  for modeGroup in portInterface.modeGroups:                     
                     modeType = ws.find(modeGroup.typeRef)
                     fname='_'.join(['Rte_Mode', swc_name, port.name, modeGroup.name])
                     shortname='_'.join(['Rte_Mode', port.name, modeGroup.name])                     
                     func=C.function(fname, 'Rte_ModeType_%s'%modeType.name)
                     functions['Mode'].append({'shortname':shortname,'func':func})
            elif isinstance(portInterface, autosar.portinterface.ParameterInterface):
               for dataElement in portInterface.dataElements:
                  dataType = ws.find(dataElement.typeRef)
                  fname='_'.join(['Rte_Calprm', swc_name, port.name, dataElement.name])
                  shortname='_'.join(['Rte_Calprm', port.name, dataElement.name])                     
                  func=C.function(fname, dataType.name)
                  functions['CalPrm'].append({'shortname':shortname,'func':func})
                  
         functionsSorted={}
         for k,v in functions.items():
            if len(v)>0:
               functionsSorted[k]=sorted(v, key=lambda x: x['func'].name.upper())
            else:
               functionsSorted[k]=[]
         prototypeList=[]
         prototypeList.extend(functionsSorted['Read'])
         prototypeList.extend(functionsSorted['Write'])
         prototypeList.extend(functionsSorted['Mode'])
         prototypeList.extend(functionsSorted['Call'])
         prototypeList.extend(functionsSorted['CalPrm'])
            
         self._genInitValues(fh, ws, swc.requirePorts+swc.providePorts)
         self._genAPIPrototypes(fh, [x['func'] for x in prototypeList])
         if len(functionsSorted['Read'])>0:
            self._genReadUnqueued(fh, functionsSorted['Read'])
         if len(functionsSorted['Write'])>0:
            self._genWriteUnqueued(fh, functionsSorted['Write'])
         if len(functionsSorted['Mode'])>0:
            self._genMode(fh, functionsSorted['Mode'])
         if len(functionsSorted['Call'])>0:
            self._genCall(fh, functionsSorted['Call'])
         if len(functionsSorted['CalPrm'])>0:
            self._genCalprm(fh, functionsSorted['CalPrm'])
         if swc.behavior is not None:
            if len(swc.behavior.runnables)>0:
               self._genRunnables(fh, swc.behavior.runnables)
         self._endFile(fh)
   
   def _beginFile(self,fh,typefilename):
      fh.write('''#ifndef %s
#define %s

'''%(self.headername,self.headername))

      fh.write('#include "%s"\n'%typefilename)
      fh.write('#include "Rte.h"\n')

   def _endFile(self,fh):
      fh.write('''
#endif //%s
'''%self.headername)
      
   def _genCommentHeader(self,fh,comment):
      fh.write('''
/**********************************************************************************************************************
 * %s
 *********************************************************************************************************************/
'''%comment)
      
      
   def _genInitValues(self, fh, ws, ports):
      ports = sorted(ports, key=lambda port: port.name)
      self._genCommentHeader(fh,'Init Values')
      code = C.sequence()
      for port in ports:                  
         for comspec in port.comspec:               
            if isinstance(comspec, autosar.component.DataElementComSpec):            
               if comspec.initValueRef is not None:
                  initValue = ws.find(comspec.initValueRef)
                  if isinstance(initValue, autosar.constant.Constant):
                     #in case the ref is pointing to a Constant (the parent), grab the child instance using .value
                     initValue=initValue.value
                  if initValue is not None:
                     dataType = ws.find(initValue.typeRef)
                     if dataType is not None:
                        prefix = 'Rte_InitValue_%s_%s'%(port.name, comspec.name)
                        code.extend(self._getInitValue(ws, prefix, initValue, dataType))
      fh.write(str(code))
   
   def _getInitValue(self, ws, def_name, value, dataType):
      """
      returns a list or sequence
      """
      code = C.sequence()
      if isinstance(value, autosar.constant.IntegerValue):
         if dataType.minVal>=0:
            suffix='u'
         else:
            suffix=''
         code.append(C.define(def_name,'((%s)%s%s)'%(dataType.name, value.value,suffix)))
      elif isinstance(value, autosar.constant.StringValue):
         code.append(C.define(def_name,'"%s"'%(value.value)))
      elif isinstance(value, autosar.constant.BooleanValue):
         if value.value:
            text='((boolean) TRUE)'
         else:
            text='((boolean) FALSE)'
         code.append(C.define(def_name,text))
      elif isinstance(value, autosar.constant.RecordValue):
         for element in value.elements:
            prefix = '%s_%s'%(def_name, element.name)
            dataType = ws.find(element.typeRef)
            if dataType is not None:
               code.extend(self._getInitValue(ws, prefix, element, dataType))
      elif isinstance(value, autosar.constant.ArrayValue):
         pass
      else:
         raise NotImplementedError(type(value))
      return code
   
   def _genAPIPrototypes(self,fh,prototypeList):
      self._genCommentHeader(fh,'API prototypes')
      for prototype in prototypeList:
         fh.write('{};\n'.format(str(prototype)))
   
   def _genReadUnqueued(self,fh,funcList):
      self._genCommentHeader(fh,'Rte_Read_<p>_<d> (explicit S/R communication with isQueued = false)')
      for elem in funcList:
         fh.write("# define {0[shortname]} {0[func].name}\n".format(elem))
   
   def _genWriteUnqueued(self,fh,funcList):
      self._genCommentHeader(fh,'Rte_Write_<p>_<d> (explicit S/R communication with isQueued = false)')
      for elem in funcList:
         fh.write("# define {0[shortname]} {0[func].name}\n".format(elem))

   def _genMode(self,fh, funcList):
      self._genCommentHeader(fh,'Rte_Mode_<p>_<m>')
      for elem in funcList:
         fh.write("# define {0[shortname]} {0[func].name}\n".format(elem))

   def _genCalprm(self,fh, funcList):
      self._genCommentHeader(fh,'Rte_Calprm')
      for elem in funcList:
         fh.write("# define {0[shortname]} {0[func].name}\n".format(elem))

   def _genCall(self,fh, funcList):
      self._genCommentHeader(fh,'Rte_Call_<p>_<o> (C/S invocation)')
      for elem in funcList:
         fh.write("# define {0[shortname]} {0[func].name}\n".format(elem))
   
   def _genCData(self,fh):
      self._genCommentHeader(fh,'Rte_CData (SW-C local calibration parameters)')
      
   def _genPIMUserTypes(self ):
      self._genCommentHeader(fh,'Per-Instance Memory User Types')
   
   def _genPIM(self ):
      self._genCommentHeader(fh,'Rte_Pim (Per-Instance Memory)')
   
   def _type2arg(self,typeObj,pointer=False):
      if ( isinstance(typeObj,autosar.datatype.IntegerDataType) or isinstance(typeObj,autosar.datatype.BooleanDataType) ):
         return C.variable('data',typeObj.name,pointer=pointer)
      else:
         pointer=True
         return C.variable('data',typeObj.name,pointer=pointer)
   
   def _genRunnables(self, fh, runnables):
      self._genCommentHeader(fh,'Runnables')
      for runnable in sorted(runnables, key=lambda runnable: runnable.name):
         line = C.statement(C.function(runnable.name, 'void'))
         fh.write(str(line)+'\n');
