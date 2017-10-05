import os
import autosar.rte.partition
import cfile as C
import io
import autosar.base
import autosar.bsw.com

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


   def generate(self, dest_dir = '.', file_name='Rte_Type.h'):
      """
      Generates Rte_Type.h
      Note: The last argument has been deprecated and is no longer in use
      """
      if self.partition.isFinalized == False:
         self.partition.finalize()
      file_path = os.path.join(dest_dir, file_name)
      with io.open(file_path, 'w', newline='\n') as fp:
         hfile=C.hfile(file_name)
         hfile.code.extend([C.line(x) for x in _genCommentHeader('Includes')])
         hfile.code.append(C.include("Std_Types.h"))
         hfile.code.append(C.blank())
         (basicTypes,complexTypes,modeTypes) = self.partition.types.getTypes()
         hfile.code.extend([C.line(x) for x in _genCommentHeader('Data Type Definitions')])
         hfile.code.append(C.blank())
         ws = self.partition.ws
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
         return 'uint8' if minval >= 0 else 'sint8'
      elif bitcount <=16:
         return 'uint16' if minval >= 0 else 'sint16'
      elif bitcount <=32:
         return 'uint32' if minval >= 0 else 'sint32'
      elif bitcount <=64:
         return 'uint64' if minval >= 0 else 'sint64'
      else:
         raise ValueError(bitcount)

class RteGenerator:
   """
   Generates Rte.c based on partition. The prefix argument can be used to change both
   the file name and prefix name used for public function names
   """
   def __init__(self, partition, prefix='Rte', include=None):
      self.partition=partition
      self.includes = [('Rte.h', False), ('Rte_Type.h', False)] #array of tuples, first element is the name of include header, second element is True if this is a sysinclude
      self.prefix=prefix
      self.com_component = None
      self.data_elements = []
      self.extra_static_vars={}
      self.extra_public_functions={}
      self.extra_rte_start=C.sequence()
      #self.com_access = {'receive': {}, 'send': {}}
      if include is not None:
         for elem in include:
            if isinstance(elem, str) or isinstance(elem, tuple):
               self.includes.append(elem)
            else:
               raise ValueError("include items must be of type str or tuple(str,boolean)")
      for component in partition.components:
         if isinstance(component.swc, autosar.bsw.com.ComComponent):
            if self.com_component is None:
               self.com_component = component
            else:
               raise RuntimeError("More than one Com component allowed in a partition")

   def generate(self, dest_dir='.', file_name=None):
      if file_name is None:
         file_name = self.prefix+'.c'
      file_path = os.path.join(dest_dir,file_name)
      with io.open(file_path, 'w', newline='\n') as fp:
         self._write_includes(fp)
         self._write_constants_and_typedefs(fp)
         self._write_local_vars(fp)
         self._write_public_funcs(fp)

   def _write_includes(self, fp):
      lines = _genCommentHeader('Includes')
      fp.write('\n'.join(lines)+'\n')
      code = C.sequence()
      for include in self.includes:
         code.append(C.include(*include))
      if self.com_component is not None:
         code.append(C.include(self.com_component.name+'.h'))
      fp.write('\n'.join(code.lines())+'\n\n')

   def _write_constants_and_typedefs(self, fp):
      fp.write('\n'.join(_genCommentHeader('Constants and Types'))+'\n\n')

   def _write_local_vars(self, fp):
      fp.write('\n'.join(_genCommentHeader('Local Variables'))+'\n')
      code = C.sequence()
      for data_element in sorted(self.partition.data_element_map.values(), key=lambda x: x.symbol):
         var = C.variable(data_element.symbol, data_element.dataType.name, True)
         code.append(C.statement(var))
      for key in sorted(self.extra_static_vars.keys()):
         code.append(C.statement(self.extra_static_vars[key]))
      fp.write('\n'.join(code.lines())+'\n\n')

   def _write_public_funcs(self, fp):      
      fp.write('\n'.join(_genCommentHeader('Public Functions'))+'\n')
      self._write_rte_start(fp)
      if len(self.partition.serverAPI.read)>0:
        self._genRead(fp, sorted(self.partition.serverAPI.final['read'], key=lambda x: x.shortname))
      if len(self.partition.serverAPI.write)>0:
        self._genWrite(fp, sorted(self.partition.serverAPI.final['write'], key=lambda x: x.shortname))
      if len(self.partition.serverAPI.receive)>0:
        self._genReceive(fp, sorted(self.partition.serverAPI.final['receive'], key=lambda x: x.shortname))
      if len(self.partition.serverAPI.send)>0:
        self._genSend(fp, sorted(self.partition.serverAPI.final['send'], key=lambda x: x.shortname))
      if len(self.partition.serverAPI.get)>0:
        self._genGet(fp, sorted(self.partition.serverAPI.final['get'], key=lambda x: x.shortname))
      #if len(self.partition.serverAPI.call)>0:
      #  self._genCall(fp, sorted(self.partition.serverAPI.final['call'], key=lambda x: x.shortname))
      if len(self.extra_public_functions)>0:
         self._genExtra(fp, [self.extra_public_functions[key] for key in sorted(self.extra_public_functions.keys())])

   def _write_rte_start(self, fp):
      func = C.function(self.prefix+'_Start', 'void')
      body = C.block(innerIndent=3)
      self._write_init_values(body)
      if len(self.extra_rte_start)>0:
         body.extend(self.extra_rte_start)
      fp.write(str(func)+'\n')
      fp.write('\n'.join(body.lines())+'\n\n')

   def _write_init_values(self, body):
      for data_element in sorted(self.partition.data_element_map.values(), key=lambda x: x.symbol):
         if data_element.initValue is not None:
            init_str = autosar.constant.initializer_string(data_element.initValue)
            body.code.append(C.statement('%s = %s'%(data_element.symbol, init_str)))



   def _genRead(self, fp, prototypes):
      """Generates all Rte_Read functions"""
      for port_func in prototypes:
         body = C.block(innerIndent=3)
         if port_func.data_element.com_access['Receive'] is not None:
            com_func = port_func.data_element.com_access['Receive']
            body.code.append(C.statement('return '+str(C.fcall(com_func.name, params=[port_func.proto.args[0].name]))))
         else:
            body.code.append(C.statement('*%s = %s'%(port_func.proto.args[0].name, port_func.data_element.symbol)))
            body.code.append(C.statement('return RTE_E_OK'))
         fp.write(str(port_func.proto)+'\n')
         fp.write('\n'.join(body.lines())+'\n\n')

   def _genWrite(self, fp, prototypes):
      for port_func in prototypes:
         hasComSignal = False
         body = C.block(innerIndent=3)
         if port_func.data_element.symbol is not None:
            body.code.append(C.statement('%s = %s'%(port_func.data_element.symbol, port_func.proto.args[0].name)))
         if port_func.data_element.com_access['Send'] is not None:
            com_func = port_func.data_element.com_access['Send']
            body.code.append(C.statement('return '+str(C.fcall(com_func.name, params=[port_func.proto.args[0].name]))))
         else:
            body.code.append(C.statement('return RTE_E_OK'))
         fp.write(str(port_func.proto)+'\n')
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

   def _genGet(self, fp, prototypes):
      for port_func in prototypes:
         body = C.block(innerIndent=3)
         prefix = '&' if port_func.data_element.dataType.isComplexType else ''
         suffix = '[0]' if isinstance(port_func.data_element.dataType, autosar.datatype.ArrayDataType) else ''
         body.code.append(C.statement('return %s%s%s'%(prefix, port_func.data_element.symbol, suffix)))
         fp.write(str(port_func.proto)+'\n')
         fp.write('\n'.join(body.lines())+'\n\n')
   
   def _genExtra(self, fp, prototypes):
      for port_func in prototypes:
         fp.write(str(port_func.proto)+'\n')
         fp.write('\n'.join(port_func.body.lines())+'\n\n')
         


class ComponentHeaderGenerator():
   def __init__(self, partition):
      self.partition = partition
      self.useMockedAPI=False

   def generate(self, destdir, mocked=None):
      if mocked is not None:
         self.useMockedAPI=bool(mocked)
      for component in self.partition.components:
         if not isinstance(component.swc, autosar.bsw.com.ComComponent):
            with io.open(os.path.join(destdir, 'Rte_%s.h'%component.swc.name), 'w', newline='\n') as fp:
               self._genComponentHeader(fp, component)

   def _genComponentHeader(self, fp, component):
      ws = component.swc.rootWS()
      assert(ws is not None)
      hfile=C.hfile(None, guard='RTE_%s_H'%(component.swc.name.upper()))
      hfile.code.append(C.include('Rte.h'))
      hfile.code.append(C.include('Rte_Type.h'))
      hfile.code.append(C.blank())
      lines = self._genInitValues(ws, component.swc.requirePorts+component.swc.providePorts)
      if len(lines)>0:
         hfile.code.extend([C.line(x) for x in _genCommentHeader('Init Values')])
         hfile.code.extend(lines)

      
      #Write API      
      num_funcs = sum(1 for x in component.clientAPI.get_all())
      if num_funcs>0:
         hfile.code.append(C.blank())
         hfile.code.extend([C.line(x) for x in _genCommentHeader('API Prototypes')])
         for func in component.clientAPI.get_all():
            assert func.proto is not None
            hfile.code.append(C.statement(func.proto))
      if len(component.clientAPI.final['read'])>0:
         hfile.code.append(C.blank())
         hfile.code.extend([C.line(x) for x in _genCommentHeader('Rte_Read_<p>_<d>')])
         hfile.code.extend([C.define(func.shortname, func.proto.name) for func in component.clientAPI.final['read']])
      if len(component.clientAPI.final['write'])>0:
         hfile.code.append(C.blank())
         hfile.code.extend([C.line(x) for x in _genCommentHeader('Rte_Write_<p>_<d>')])
         hfile.code.extend([C.define(func.shortname, func.proto.name) for func in component.clientAPI.final['write']])
      if len(component.clientAPI.final['receive'])>0:
         hfile.code.append(C.blank())
         hfile.code.extend([C.line(x) for x in _genCommentHeader('Rte_Receive_<p>_<d>')])
         hfile.code.extend([C.define(func.shortname, func.proto.name) for func in component.clientAPI.final['receive']])
      if len(component.clientAPI.final['send'])>0:
         hfile.code.append(C.blank())
         hfile.code.extend([C.line(x) for x in _genCommentHeader('Rte_Send_<p>_<d>')])
         hfile.code.extend([C.define(func.shortname, func.proto.name) for func in component.clientAPI.final['send']])
      if len(component.clientAPI.final['mode'])>0:
         hfile.code.append(C.blank())
         hfile.code.extend([C.line(x) for x in _genCommentHeader('Rte_Mode_<p>_<d>')])
         hfile.code.extend([C.define(func.shortname, func.proto.name) for func in component.clientAPI.final['mode']])
      if len(component.clientAPI.final['mode'])>0:
         hfile.code.append(C.blank())
         hfile.code.extend([C.line(x) for x in _genCommentHeader('Rte_Mode_<mode>')])
         hfile.code.extend([C.define(func.shortname, func.proto.name) for func in component.clientAPI.final['mode']])
      if len(component.clientAPI.final['calprm'])>0:
         hfile.code.append(C.blank())
         hfile.code.extend([C.line(x) for x in _genCommentHeader('Rte_Calprm_<name>')])
         hfile.code.extend([C.define(func.shortname, func.proto.name) for func in component.clientAPI.final['calprm']])
      if len(component.clientAPI.final['call'])>0:
         hfile.code.append(C.blank())
         hfile.code.extend([C.line(x) for x in _genCommentHeader('Rte_Call_<p>_<o> ')])
         hfile.code.extend([C.define(func.shortname, func.proto.name) for func in component.clientAPI.final['call']])
      if len(component.runnables)>0:
         for runnable in sorted(component.runnables, key=lambda x: x.symbol):
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


class MockRteGenerator(RteGenerator):
   def __init__(self, partition, api_prefix='Rte', file_prefix = 'MockRte', include=None):
      super().__init__(partition, api_prefix, include)
      self.includes.append((file_prefix+'.h', False))
      self.api_prefix = api_prefix
      self.file_prefix = file_prefix
      self.typedefs={}
      for port in partition.unconnectedPorts():
         if isinstance(port, autosar.rte.base.ProvidePort):
            self._create_port_getter_api(port)
         else:
            self._create_port_setter_api(port)
         self.partition.serverAPI.finalize()

   def generate(self, dest_dir):
      super().generate(dest_dir, self.file_prefix+'.c')
      self._generateHeader(dest_dir)

   def _create_port_getter_api(self, port):
      component = port.parent
      for data_element in port.data_elements:
         if "%s/%s"%(port.name, data_element.name) in component.data_element_port_access:
            self._create_data_element_getter(component, port, data_element)

   def _create_data_element_getter(self, component, port, data_element):
      data_type = data_element.dataType
      func_name='%s_GetWriteData_%s_%s_%s'%(self.prefix, component.name, port.name, data_element.name)
      short_name='%s_GetWriteData_%s_%s'%(self.prefix, port.name, data_element.name)
      suffix = '*' if data_type.isComplexType else ''
      proto=C.function(func_name, data_type.name+suffix)
      rte_func = autosar.rte.base.DataElementFunction(proto, port, data_element)
      self._createPortVariable(component, port, data_element)
      self.partition.serverAPI.get[short_name] = autosar.rte.base.GetPortFunction(short_name, proto, data_element)

   def _create_port_setter_api(self, port):
      component = port.parent
      for data_element in port.data_elements:
         if "%s/%s"%(port.name, data_element.name) in component.data_element_port_access:
            self._create_data_element_setter(component, port, data_element)
      for operation in port.operations:
         key = "%s/%s"%(port.name, operation.name)
         if key in component.operation_port_access:
            self._create_operation_setter(component, port, operation, component.operation_port_access[key])

   def _create_data_element_setter(self, component, port, data_element):
      data_type = data_element.dataType
      func_name='%s_SetReadData_%s_%s_%s'%(self.prefix, component.name, port.name, data_element.name)
      short_name='%s_SetReadData_%s_%s'%(self.prefix, port.name, data_element.name)
      proto=C.function(func_name, 'void')
      proto.add_arg(C.variable('data', data_type.name, pointer=data_type.isComplexType))
      rte_func = autosar.rte.base.DataElementFunction(proto, port, data_element)
      self._createPortVariable(component, port, data_element)
      self.partition.serverAPI.set[short_name] = autosar.rte.base.SetPortFunction(short_name, proto, data_element)
      func_name='%s_SetReadResult_%s_%s_%s'%(self.prefix, component.name, port.name, data_element.name)
      short_name='%s_SetReadResult_%s_%s'%(self.prefix, port.name, data_element.name)
      proto=C.function(func_name, 'void')
      proto.add_arg(C.variable('retval', 'Std_ReturnType'))
      self.partition.serverAPI.retval[short_name] = autosar.rte.base.RetValPortFunction(short_name, proto, data_element)

   def _create_operation_setter(self, component, port, operation, port_access):
      func_name='%s_SetCallHandler_%s_%s_%s'%(self.prefix, component.name, port.name, operation.name)
      short_name='%s_SetCallHandler_%s_%s'%(self.prefix, port.name, operation.name)

      type_name = '%s_%s_ServerCallHandler_t'%(port.name, operation.name)
      var_name = 'm_ServerCallHandler_%s_%s_%s'%(component.name, port.name, operation.name)       
      tmp_proto = C.fptr.from_func(port_access.func.proto, type_name)

      self.typedefs[type_name] = 'typedef %s'%str(tmp_proto)
      proto = C.function(func_name, 'void', args=[C.variable('handler_func', type_name, pointer=True)])
      func = autosar.rte.base.SetCallHandlerFunction(short_name, proto, operation, var_name)
      self.extra_public_functions[short_name]=func
      static_var = C.variable(var_name, type_name, static=True, pointer=True)
      self.extra_static_vars[var_name]=static_var
      self.extra_rte_start.append(C.statement('%s = (%s*) 0'%(var_name, type_name)))
      body = self._createMockServerCallFunction(port_access.func.proto, var_name)
      self.extra_public_functions[port_access.func.proto.name]=autosar.rte.base.ServerCallFunction(port_access.func.proto, body)

   def _createMockServerCallFunction(self, proto, var_name):
      body = C.block(innerIndent=3)
      body.append(C.line('if (%s != 0)'%(var_name)))
      inner = C.block(innerIndent=3)
      fcall = C.fcall(var_name)
      for arg in proto.args:
         fcall.add_param(arg.name)
      if proto.typename != 'void':
         inner.append(C.statement('return %s'%str(fcall)))
      else:
         inner.append(C.statement(fcall))
      body.append(inner)
      if proto.typename != 'void':
         body.append(C.statement('return RTE_E_INVALID'))
      return body


   def _createPortVariable(self, component, port, data_element):
      data_element_map = self.partition.data_element_map
      variable_name = '_'.join([component.name, port.name, data_element.name])
      if variable_name not in data_element_map:
         data_element.symbol = variable_name
         data_element_map[variable_name] = data_element

   def _generateHeader(self, dest_dir):
      filepath = os.path.join(dest_dir,self.file_prefix+'.h')
      with io.open(filepath, 'w', newline='\n') as fp:
         for line in self._createHeaderLines(filepath):
            fp.write(line)
            fp.write('\n')
         fp.write('\n')


   def _createHeaderLines(self, filepath):
      hfile = C.hfile(filepath)
      code = hfile.code
      code.extend([C.line(x) for x in _genCommentHeader('Includes')])
      code.append(C.include("Std_Types.h"))
      code.append(C.include("Rte_Type.h"))
      code.append(C.blank())
      code.extend(_genCommentHeader('Constants and Types'))
      for key in sorted(self.typedefs.keys()):
         code.append(C.statement(self.typedefs[key]))
      code.append(C.blank())
      code.extend([C.line(x) for x in _genCommentHeader('Public Function Declarations')])
      code.append(C.blank())
      
      code.append(C.statement(C.function('%s_Start'%self.api_prefix, 'void')))
      for func in sorted(self.partition.serverAPI.final['get'], key=lambda x: x.shortname):
         assert func.proto is not None
         hfile.code.append(C.statement(func.proto))
      for func in sorted(self.partition.serverAPI.final['set'], key=lambda x: x.shortname):
         assert func.proto is not None
         hfile.code.append(C.statement(func.proto))
      for func in sorted(self.partition.serverAPI.final['retval'], key=lambda x: x.shortname):
         assert func.proto is not None
         hfile.code.append(C.statement(func.proto))
      for func in sorted(self.extra_public_functions.values(), key=lambda x: x.shortname):
         assert func.proto is not None
         hfile.code.append(C.statement(func.proto))
      hfile.code.append(C.blank())
      return hfile.lines()


