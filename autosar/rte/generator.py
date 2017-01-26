import cfile as C
import autosar
import os
import sys
from autosar.rte.base import *

class RteTypeGen:
   
   def generate(self,ws,filename, basicTypes, complexTypes, modeTypes, swc_name):
      hfile=C.hfile(filename)
      hfile.code.append(C.include("Std_Types.h"))
      hfile.code.append('''
                        
/**********************************************************************************************************************
 * Data Type Definitions
 *********************************************************************************************************************/
''')
      first=True
      for ref in sorted(basicTypes)+sorted(complexTypes):
         dataType = ws.find(ref)
         if dataType is not None:
            if first:
               first=False
            else:
               hfile.code.append(C.blank())
            hfile.code.append('#  define Rte_TypeDef_%s'%dataType.name)
            if isinstance(dataType,autosar.datatype.BooleanDataType):
               hfile.code.append('typedef boolean %s;'%(dataType.name))
            elif isinstance(dataType,autosar.datatype.IntegerDataType):
               valrange = dataType.maxVal-dataType.minVal
               bitcount = valrange.bit_length()
               typename = dataType.name
               basetype = self._typename(bitcount,dataType.minVal)
               hfile.code.append(C.statement(C.typedef(basetype, typename)))
               #hfile.code.append('typedef %s %s;'%(basetype, typename))            
               isUnsigned = True if basetype in ('uint8','uint16','uint32') else False
               if isUnsigned:
                  minval=str(dataType.minVal)+'u'
                  maxval=str(dataType.maxVal)+'u'
               else:
                  minval=str(dataType.minVal)
                  maxval=str(dataType.maxVal)
               hfile.code.append('#  define %s_LowerLimit ((%s)%s)'%(typename,typename,minval))
               hfile.code.append('#  define %s_UpperLimit ((%s)%s)'%(typename,typename,maxval))
               if dataType.compuMethodRef is not None:
                  compuMethod = ws.find(dataType.compuMethodRef)
                  if compuMethod is not None:
                     lines1=[]
                     lines2=[]
                     if isinstance(compuMethod,autosar.datatype.CompuMethodConst):
                        for elem in compuMethod.elements:
                           if isUnsigned:
                              value = str(elem.upperLimit)+'u'
                           else:
                              value = str(elem.upperLimit)
                           lines1.append('#  define RTE_CONST_%s (%s)'%(elem.textValue,value))
                           lines2.append('#  define %s ((%s)%s)'%(elem.textValue,typename,value))
                     if len(lines2)>0:
                        tmp=lines1+[C.blank()]+lines2
                     else:
                        tmp=lines1
                     for line in tmp:
                        hfile.code.append(line)
                  else:
                     raise ValueError(dataType.compuMethodRef)
            elif isinstance(dataType, autosar.datatype.RecordDataType):
               body = C.block(indent=3)               
               for elem in dataType.elements:
                  childType = ws.find(elem.typeRef, role='DataType')
                  body.append(C.statement(C.variable(elem.name, childType.name)))
               struct = C.struct(None,body, typedef=dataType.name)
               hfile.code.append(C.statement(struct))
            elif isinstance(dataType, autosar.datatype.StringDataType):
               hfile.code.append('typedef uint8 %s[%d];'%(dataType.name, dataType.length+1))
            elif isinstance(dataType, autosar.datatype.ArrayDataType):
               childType = ws.find(dataType.typeRef, role='DataType')
               if childType is None:
                  raise ValueError('invalid type reference: '+dataType.typeRef)
               hfile.code.append('typedef %s %s[%d];'%(childType.name, dataType.name, dataType.length))
            elif isinstance(dataType, autosar.datatype.RealDataType):
               if dataType.encoding == 'DOUBLE':
                  platform_typename = 'float64'
               else:
                  platform_typename = 'float32'
               hfile.code.append('typedef %s %s;'%(platform_typename, dataType.name))
            else:
               raise NotImplementedError(type(dataType))
               #sys.stderr.write('not implemented: %s\n'%str(type(dataType)))
         else:
            raise ValueError(ref)

      if len(modeTypes)>0:         
         lines=self._genCommentHeader('Mode Types')
         tmp=[]
         hfile.code.extend(lines)
         first=True
         for ref in modeTypes:
            if first:
               first=False
            else:
               tmp.append(C.blank())
            modeType = ws.find(ref)
            hfile.code.append(C.statement(C.typedef('uint8', 'Rte_ModeType_'+modeType.name)))
            
            for i,elem in enumerate(modeType.modeDeclarations):
               # define RTE_MODE_EcuM_Mode_POST_RUN ((Rte_ModeType_EcuM_Mode)0)
               tmp.append(C.define('RTE_MODE_%s_%s'%(modeType.name,elem.name),'((Rte_ModeType_EcuM_Mode)%d)'%i))
            
         hfile.code.append(C.blank())
         hfile.code.extend(tmp)
      hfile.code.append(C.blank())
      hfile.code.extend(self._genCommentHeader('Component Data Structures'))
      hfile.code.append('struct Rte_CDS_%s'%swc_name)
      block = C.block(innerIndent=3)
      block.code.append(C.statement('uint8 _dummy', indent=3))
      hfile.code.append(C.statement(block))
         
      with open(filename,'w') as fh:
         fh.write(str(hfile))
   
   def _typedef(self,fh,left,right):
      fh.write('typedef %s %s;\n'%(left,right))

   def _genCommentHeader(self,comment):
      lines = []
      lines.append('/**********************************************************************************************************************')
      lines.append('* %s'%comment)
      lines.append('*********************************************************************************************************************/')
      return lines
   
   @staticmethod
   def _typename(bitcount,minval):
      if bitcount <=8:
         return 'uint8' if minval == 0 else 'sint8'
      elif bitcount <=16:
         return 'uint16' if minval == 0 else 'sint16'
      elif bitcount <=32:
         return 'uint32' if minval == 0 else 'sint32'
      elif bitcount <=64:
         return 'uint64' if minval == 0 else 'sint64'
      else:
         raise ValueError(bitcount)


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
