import os
import autosar.rte.partition
import cfile as C
import io

def _genCommentHeader(comment):
   lines = []
   lines.append('/*********************************************************************************************************************')
   lines.append('* %s'%comment)
   lines.append('*********************************************************************************************************************/')
   return lines

class TypeGenerator:
   
   def __init__(self, partition, useDefaultTypes=True):
      self.partition = partition
      self.defaultTypes = {}
      if useDefaultTypes:
         self._initDefaultType()
      
   
   def generate(self, filename, ws):
      with io.open(filename, 'w', newline='\n') as fp:         
         hfile=C.hfile(filename)
         hfile.code.extend([C.line(x) for x in _genCommentHeader('Includes')])         
         hfile.code.append(C.include("Std_Types.h"))
         hfile.code.append(C.blank())
         (basicTypes,complexTypes,modeTypes) = self.partition.types.getTypes()         
         hfile.code.extend([C.line(x) for x in _genCommentHeader('Data Type Definitions')])
         hfile.code.append(C.blank())
         unusedDefaultTypes = self._findUnusedDefaultTypes(ws, basicTypes)
         
         first=True
         for ref in sorted(basicTypes)+sorted(complexTypes):
            dataType = ws.find(ref)
            if dataType is not None:
               typedef = None
               if first:
                  first=False
               else:
                  hfile.code.append(C.blank())
               hfile.code.append('#define Rte_TypeDef_%s'%dataType.name)
               if isinstance(dataType,autosar.datatype.BooleanDataType):
                  typedef = C.typedef('boolean', dataType.name)
                  hfile.code.append(C.statement(typedef))
               elif isinstance(dataType,autosar.datatype.IntegerDataType):
                  valrange = dataType.maxVal-dataType.minVal
                  bitcount = valrange.bit_length()
                  typename = dataType.name
                  basetype = self._typename(bitcount,dataType.minVal)
                  typedef = C.typedef(basetype, typename)
                  hfile.code.append(C.statement(typedef))                  
                  isUnsigned = True if basetype in ('uint8','uint16','uint32') else False
                  if isUnsigned:
                     minval=str(dataType.minVal)+'u'
                     maxval=str(dataType.maxVal)+'u'
                  else:
                     minval=str(dataType.minVal)
                     maxval=str(dataType.maxVal)
                  hfile.code.append('#define %s_LowerLimit ((%s)%s)'%(typename,typename,minval))
                  hfile.code.append('#define %s_UpperLimit ((%s)%s)'%(typename,typename,maxval))
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
                              lines1.append('#define RTE_CONST_%s (%s)'%(elem.textValue,value))
                              lines2.append('#define %s ((%s)%s)'%(elem.textValue,typename,value))
                        if len(lines2)>0:
                           tmp=lines1+[C.blank()]+lines2
                        else:
                           tmp=lines1
                        for line in tmp:
                           hfile.code.append(line)
                     else:
                        raise ValueError(dataType.compuMethodRef)
               elif isinstance(dataType, autosar.datatype.RecordDataType):
                  body = C.block(innerIndent=3)               
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
         if len(unusedDefaultTypes)>0:
            hfile.code.append(C.blank(2))
            hfile.code.append(C.line('#ifndef RTE_SUPPRESS_UNUSED_DATATYPES'))
            for name in sorted(unusedDefaultTypes):
               hfile.code.append(C.blank())
               hfile.code.extend(self.defaultTypes[name])
            hfile.code.append(C.blank())
            hfile.code.append(C.line('#endif'))            
         fp.write('\n'.join(hfile.lines()))
         fp.write('\n')
         
   
   def _initDefaultType(self):
      self.defaultTypes['Boolean']=C.sequence().extend([C.statement(C.typedef('boolean', 'Boolean'))])
      self.defaultTypes['UInt8']=C.sequence().extend([C.statement(C.typedef('uint8', 'UInt8')), C.define('UInt8_LowerLimit', '((UInt8)0u)'), C.define('UInt8_UpperLimit', '((UInt8)255u)')])
      self.defaultTypes['UInt16']=C.sequence().extend([C.statement(C.typedef('uint16', 'UInt16')), C.define('UInt16_LowerLimit', '((UInt16)0u)'), C.define('UInt16_UpperLimit', '((UInt16)65535u)')])
      self.defaultTypes['UInt32']=C.sequence().extend([C.statement(C.typedef('uint32', 'UInt32')), C.define('UInt32_LowerLimit', '((UInt32)0u)'), C.define('UInt32_UpperLimit', '((UInt32)4294967295u)')])
      self.defaultTypes['SInt8']=C.sequence().extend([C.statement(C.typedef('sint8', 'SInt8')), C.define('SInt8_LowerLimit', '((SInt8)-128)'), C.define('SInt8_UpperLimit', '((SInt8)127)')])
      self.defaultTypes['SInt16']=C.sequence().extend([C.statement(C.typedef('sint16', 'SInt16')), C.define('SInt16_LowerLimit', '((SInt16)-32768)'), C.define('SInt16_UpperLimit', '((SInt16)32767)')])
      self.defaultTypes['SInt32']=C.sequence().extend([C.statement(C.typedef('sint32', 'SInt32')), C.define('SInt32_LowerLimit', '((SInt32)-2147483648)'), C.define('SInt32_UpperLimit', '((SInt32)2147483647)')])
   
   def _findUnusedDefaultTypes(self, ws, typerefs):
      defaultTypeNames = set(self.defaultTypes.keys())
      usedTypeNames = set()
      
      for ref in typerefs:         
         dataType = ws.find(ref)
         if dataType is None:
            raise ValueError('invalid type reference: '+ref)
         usedTypeNames.add(dataType.name)
      return defaultTypeNames-usedTypeNames
         
         
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

class RteGenerator:
   """
   Generates Rte.c based on partition. The prefix argument can be used to change both
   the file name and prefix name used for public function names
   """
   def __init__(self, partition, prefix='Rte', include=None):
      self.partition = partition
      self.includes = [('Rte.h', False), ('Rte_Type.h', False)] #array of tuples, first element is the name of include header, second element is True if this is a sysinclude
      self.prefix=prefix
      self.com_config = None
      self.local_vars = []
      self.local_elements = []
      self.com_access = {'receive': {}, 'send': {}}      
      if include is not None:
         for elem in include:
            self.includes.append(elem)
   
   
   def generate(self, filename):
      self._generate_com_access()
      self._generate_local_vars()
      with io.open(filename, 'w', newline='\n') as fp:
         self._write_includes(fp)
         self._write_constants_and_typedefs(fp)
         self._write_local_vars(fp)
         self._write_public_funcs(fp)
   
   def _generate_com_access(self):
      if self.com_config is not None:                  
         for element_name in self.partition.dataElements:
            if element_name in self.com_config.send:
               data_element = self.partition.dataElements[element_name]
               isPointer = True if data_element.dataType.isComplexType else False
               self.com_access['send'][element_name] = C.function(
                  "%s_Send_%s"%(self.com_config.prefix, element_name),
                  'Std_ReturnType',                  
                  args = [C.variable('value', data_element.dataType.name, pointer=isPointer)])
            elif element_name in self.com_config.receive:
               data_element = self.partition.dataElements[element_name]
               isPointer = True if data_element.dataType.isComplexType else False
               self.com_access['receive'][element_name] = C.function(
                  "%s_Receive_%s"%(self.com_config.prefix, element_name),
                  'Std_ReturnType',                  
                  args = [C.variable('value', data_element.dataType.name, pointer=isPointer)])
            else:
               self.local_elements.push(element_name)

   def _generate_local_vars(self):
      for element_name in self.local_elements:
         print("local var: " + element_name)
   
   def _write_includes(self, fp):
      lines = _genCommentHeader('Includes')
      fp.write('\n'.join(lines)+'\n')
      code = C.sequence()
      for include in self.includes:         
         code.append(C.include(*include))
      fp.write('\n'.join(code.lines())+'\n\n')
   
   def _write_constants_and_typedefs(self, fp):
      fp.write('\n'.join(_genCommentHeader('Constants and Types'))+'\n\n')

   def _write_local_vars(self, fp):
      fp.write('\n'.join(_genCommentHeader('Local Variables'))+'\n')
      code = C.sequence()
      # for key in sorted(self.partition.vars.keys()):
      #    item = self.partition.vars[key]
      #    var = C.variable(key, item.typename, True)
      #    code.append(C.statement(var))
      # fp.write('\n'.join(code.lines())+'\n\n')
   
   def _write_public_funcs(self, fp):
      fp.write('\n'.join(_genCommentHeader('Public Functions'))+'\n')
      func = C.function(self.prefix+'_Start', 'void')
      body = C.block(innerIndent=3)
      #for name in sorted(self.partition.vars.keys()):
         
         # rtevar = self.partition.vars[name]
         # if isinstance(rtevar, autosar.rte.IntegerVariable):
         #    body.code.append(C.statement('%s = %s'%(rtevar.name, rtevar.initValue)))
      fp.write(str(func)+'\n')
      fp.write('\n'.join(body.lines())+'\n\n')     
      if len(self.partition.componentAPI.read)>0:
        self._genRead(fp, sorted(self.partition.componentAPI.final['read'], key=lambda x: x.shortname))
      if len(self.partition.componentAPI.write)>0:
        self._genWrite(fp, sorted(self.partition.componentAPI.final['write'], key=lambda x: x.shortname))
      if len(self.partition.componentAPI.receive)>0:
        self._genReceive(fp, sorted(self.partition.componentAPI.final['receive'], key=lambda x: x.shortname))
      if len(self.partition.componentAPI.send)>0:
        self._genSend(fp, sorted(self.partition.componentAPI.final['send'], key=lambda x: x.shortname))
      #if len(self.partition.componentAPI.call)>0:
      #  self._genCall(fp, sorted(self.partition.componentAPI.final['call'], key=lambda x: x.shortname))


   def _genRead(self, fp, prototypes):
      """Generates all Rte_Read functions"""
      for proto in prototypes:
         body = C.block(innerIndent=3)
         #body.code.append(C.statement('*%s = %s'%(proto.func.args[0].name, proto.rte_var.name)))
         #print(proto.rte_var.typename)
         if proto.data_element.name in self.com_access['receive']:
            func = self.com_access['receive'][proto.data_element.name]
            body.code.append(C.statement('return '+str(C.fcall(func.name, params=[proto.func.args[0].name]))))
         else:
            body.code.append(C.statement('return RTE_E_OK'))
         fp.write(str(proto.func)+'\n')
         fp.write('\n'.join(body.lines())+'\n\n')     
         
   def _genWrite(self, fp, prototypes):
      for proto in prototypes:
         hasComSignal = False
         body = C.block(innerIndent=3)
         if proto.data_element.name in self.com_access['send']:
            func = self.com_access['send'][proto.data_element.name]
            body.code.append(C.statement('return '+str(C.fcall(func.name, params=[proto.func.args[0].name]))))
         else:
            body.code.append(C.statement('return RTE_E_OK'))
         fp.write(str(proto.func)+'\n')
         fp.write('\n'.join(body.lines())+'\n\n')     
         
   def _genReceive(self, fp, prototypes):
      for proto in prototypes:         
         body = C.block(innerIndent=3)         
         body.code.append(C.statement('return RTE_E_OK'))
         fp.write(str(proto.func)+'\n')
         fp.write('\n'.join(body.lines())+'\n\n')     
      
   def _genSend(self, fp, prototypes):
      for proto in prototypes:         
         body = C.block(innerIndent=3)
         body.code.append(C.statement('return RTE_E_OK'))
         fp.write(str(proto.func)+'\n')
         fp.write('\n'.join(body.lines())+'\n\n')     

   def _genCall(self, fp, prototypes):
      for proto in prototypes:         
         body = C.block(innerIndent=3)
         body.code.append(C.statement('return RTE_E_OK'))
         fp.write(str(proto.func)+'\n')
         fp.write('\n'.join(body.lines())+'\n\n')     
      
class ComponentHeaderGenerator():
   def __init__(self, partition):
      self.partition = partition
   
   def generate(self, destdir):
      for component in self.partition.components:
         with io.open(os.path.join(destdir, 'Rte_%s.h'%component.swc.name), 'w', newline='\n') as fp:
            self._genComponentHeader(fp, component)
   
   def _genComponentHeader(self, fp, component):
      ws = component.swc.rootWS()
      assert(ws is not None)
      hfile=C.hfile(None, guard='RTE_%s_H'%(component.swc.name.upper()))
      hfile.code.append(C.include('Rte.h'))
      hfile.code.append(C.include('Rte_Type.h'))      
      lines = self._genInitValues(ws, component.swc.requirePorts+component.swc.providePorts)
      if len(lines)>0:
         hfile.code.extend([C.line(x) for x in _genCommentHeader('Init Values')])
         hfile.code.extend(lines)
      
      #Write API
      hfile.code.append(C.blank())
      hfile.code.extend([C.line(x) for x in _genCommentHeader('API Prototypes')])
      for proto in component.componentAPI.get_all():
         hfile.code.append(C.statement(proto.func))
      if len(component.componentAPI.final['read'])>0:
         hfile.code.append(C.blank())
         hfile.code.extend([C.line(x) for x in _genCommentHeader('Rte_Read_<p>_<d>')])         
         hfile.code.extend([C.define(proto.shortname, proto.func.name) for proto in component.componentAPI.final['read']])
      if len(component.componentAPI.final['write'])>0:
         hfile.code.append(C.blank())
         hfile.code.extend([C.line(x) for x in _genCommentHeader('Rte_Write_<p>_<d>')])         
         hfile.code.extend([C.define(proto.shortname, proto.func.name) for proto in component.componentAPI.final['write']])
      if len(component.componentAPI.final['receive'])>0:
         hfile.code.append(C.blank())
         hfile.code.extend([C.line(x) for x in _genCommentHeader('Rte_Receive_<p>_<d>')])         
         hfile.code.extend([C.define(proto.shortname, proto.func.name) for proto in component.componentAPI.final['receive']])
      if len(component.componentAPI.final['send'])>0:
         hfile.code.append(C.blank())
         hfile.code.extend([C.line(x) for x in _genCommentHeader('Rte_Send_<p>_<d>')])         
         hfile.code.extend([C.define(proto.shortname, proto.func.name) for proto in component.componentAPI.final['send']])
      if len(component.componentAPI.final['mode'])>0:
         hfile.code.append(C.blank())
         hfile.code.extend([C.line(x) for x in _genCommentHeader('Rte_Mode_<p>_<d>')])         
         hfile.code.extend([C.define(proto.shortname, proto.func.name) for proto in component.componentAPI.final['mode']])
      if len(component.componentAPI.final['mode'])>0:
         hfile.code.append(C.blank())
         hfile.code.extend([C.line(x) for x in _genCommentHeader('Rte_Mode_<mode>')])         
         hfile.code.extend([C.define(proto.shortname, proto.func.name) for proto in component.componentAPI.final['mode']])
      if len(component.componentAPI.final['calprm'])>0:
         hfile.code.append(C.blank())
         hfile.code.extend([C.line(x) for x in _genCommentHeader('Rte_Calprm_<name>')])
         hfile.code.extend([C.define(proto.shortname, proto.func.name) for proto in component.componentAPI.final['calprm']])
      if len(component.componentAPI.final['call'])>0:
         hfile.code.append(C.blank())
         hfile.code.extend([C.line(x) for x in _genCommentHeader('Rte_Call_<p>_<o> ')])
         hfile.code.extend([C.define(proto.shortname, proto.func.name) for proto in component.componentAPI.final['call']])         
      if len(component.rteRunnables)>0:
         for name in sorted(component.rteRunnables):
            runnable = component.rteRunnables[name]
            tmp = self._writeRunnableProto(runnable)
            hfile.code.extend(tmp)
      fp.write('\n'.join(hfile.lines()))
      fp.write('\n')

   def _genInitValues(self, ws, ports):
      ports = sorted(ports, key=lambda port: port.name)      
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
      return code
   
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
   
   def _writeRunnableProto(self, runnable):      
      lines = []
      lines.extend([C.line(x) for x in _genCommentHeader('Runnable %s'%runnable.name)])
      lines.append(C.statement(runnable.prototype))
      lines.append(C.blank())
      return lines
      
            