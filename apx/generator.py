import apx.base
import cfile as C

class SignalInfo:
   def __init__(self, offset, pack_len, func, dsg, init_value=None):
      self.offset=offset
      self.pack_len=pack_len
      self.init_value=init_value
      self.func=func
      self.dsg=dsg
        

class NodeGenerator:
   def __init__(self):
      self.includes=None

   def genPackInteger(self, code,buf,valname,dsg,localvar,offset,indent):   
      dataLen=0
      resolvedDsg = dsg.resolveType()
      if resolvedDsg.data['type']=='c' or resolvedDsg.data['type']=='C':
         dataLen=1
         basetype='sint8' if resolvedDsg.data['type']=='c' else 'uint8'
      elif resolvedDsg.data['type']=='s' or resolvedDsg.data['type']=='S':
         dataLen=2
         basetype='sint16' if resolvedDsg.data['type']=='c' else 'uint16'
      elif resolvedDsg.data['type']=='l' or resolvedDsg.data['type']=='L':
         dataLen=4
         basetype='sint32' if resolvedDsg.data['type']=='c' else 'uint32'
      else:
         raise NotImplementedError(resolvedDsg.data['type'])
      if 'bufptr' in localvar:
         #relative addressing
         code.append(C.statement('packLE(%s,(uint32) %s,(uint8) sizeof(%s))'%(localvar['bufptr'].name,valname,basetype),indent=indent))
         code.append(C.statement('%s+=(uint8) sizeof(%s)'%(localvar['bufptr'].name,basetype),indent=indent))
      else:
         #absolute addressing
         if dataLen==1:
            code.append(C.statement("%s[%d]=(uint8) %s"%(buf.name,offset,valname),indent=indent))
         else:         
            code.append(C.statement('packLE(&%s[%d],(uint32) %s,(uint8) %du)'%(buf.name,offset,valname,dataLen),indent=indent))
      return dataLen
   
   def genPackItem(self, code,buf,val,dsg,localvar,offset,indent,indentStep):
      packLen=0
      if isinstance(val,C.variable):
         valname=val.name
      elif isinstance(val,str):
         valname=val
      else:
         raise ValueError(val)      
      if (dsg.isComplexType()):
         #raise NotImplemented('complex types not yet fully supported')
         if dsg.data['type'].startswith('a'): #string         
            if 'bufptr' in localvar:
               #use relative addressing using 'p' pointer
               code.append(C.statement('memcpy(%s,%s,%d)'%(localvar['bufptr'].name,valname,dsg.data['arrayLen']),indent=indent))
               code.append(C.statement('%s+=%d'%(localvar['bufptr'].name,dsg.data['arrayLen']),indent=indent))
            else:
               #use absolute addressing using buf variable and offset
               code.append(C.statement('memcpy(&%s[%d],%s,%d)'%(buf.name,offset,valname,dsg.data['arrayLen']),indent=indent))
            packLen=dsg.data['arrayLen']
         elif dsg.data['type']=='record':
            if 'bufptr' not in localvar:
               localvar['bufptr']=C.variable('p','uint8',pointer=True)      
            for elem in dsg.data['elements']:                     
               if isinstance(val,C.variable):
                  if val.pointer:
                     childName="%s->%s_RE"%(valname,elem['name'])
                  else:
                     childName="%s.%s_RE"%(valname,elem['name'])
               elif isinstance(val,str):
                  childName="%s.%s"%(valname,elem['name'])
               assert(elem is not None)
               itemLen=genPackItem(code,buf,childName,apx.ApxDataSignature(elem),localvar,offset,indent,indentStep)
               offset+=itemLen
               packLen+=itemLen
         elif dsg.isArray():      
            if 'loopVar' not in localvar:            
               if dsg.data['arrayLen']<256:
                  typename='uint8'
               elif dsg.data['arrayLen']<65536:
                  typename='uint16'
               else:
                  typename='uint32' 
               localvar['loopVar']=C.variable('i',typename)
            else:
               if localvar['loopVar'].typename=='uint8' and (typename=='uint16' or typename=='uint32'):
                  localvar['loopVar'].typename=typename
               elif localvar['loopVar'].typename=='uint16' and typename=='uint32':
                  localvar['loopVar'].typename=typename
            if 'bufptr' not in localvar:         
               localvar['bufptr']=C.variable('p','uint8',pointer=True)         
            code.append(C.statement('for({0}=0;{0}<{1};{0}++)'.format(localvar['loopVar'].name,dsg.data['arrayLen']),indent=indent))
            block=C.block(indent=indent)
            indent+=indentStep
            itemLen=genPackItem(block,buf,valname+'[%s]'%localvar['loopVar'].name,childType,localvar,offset)
            indent-=indentStep
            code.append(block)         
      else:
         packLen=self.genPackInteger(code,buf,valname,dsg,localvar,offset,indent)      
      return packLen
   
   def genPackFunc(self, func, buf, offset, dsg, indent, indentStep):
      indent+=indentStep
      packLen=0
      code=C.block()
      localvar={'buf':'m_outPortdata'}
      val=func.arguments[0]
            
      codeBlock=C.sequence()
      packLen=self.genPackItem(codeBlock, buf, val, dsg, localvar, offset, indent, indentStep)
      initializer=C.initializer(None,['(uint16)%du'%offset,'(uint16)%du'%packLen])
      if 'p' in localvar:
         code.append(C.statement(localvar['p'],indent=indent))
      for k,v in localvar.items():
         if k=='p' or k=='buf':
            continue
         else:
            code.append(C.statement(v,indent=indent))      
      code.append(C.statement('apx_nodeData_lockOutPortData(&m_nodeData)', indent=indent))
      if 'bufptr' in localvar:
         code.append(C.statement('%s=&%s[%d]'%(localvar['bufptr'].name,buf.name,offset),indent=indent))      
      code.extend(codeBlock)
      code.append(C.statement(C.fcall('outPortData_writeCmd', params=[offset, packLen]),indent=indent))
      code.append(C.statement('return E_OK',indent=indent))
      indent-=indentStep
      return code,packLen
   
   def writeHeaderFile(self, fp, signalInfo, guard):
      #indent=0
      #indentStep=3
            
      headerFile=C.hfile(None,guard=guard)
      headerFile.code.append(C.blank(1))
      headerFile.code.append(C.include('Std_Types.h'))
      headerFile.code.append(C.include('Rte_Type.h'))
      headerFile.code.append(C.include('apx_nodeData.h'))
      headerFile.code.append(C.blank(1))
      initFunc = C.function('%s_init'%self.name,'void')
      nodeDataFunc = C.function('%s_getNodeData'%self.name,'apx_nodeData_t',pointer=True)      
      headerFile.code.append(C.statement(initFunc))
      headerFile.code.append(C.statement(nodeDataFunc))
      headerFile.code.append(C.blank(1))
#      self.inPortDataDefname = self.name.upper()+'_IN_PORT_DATA_LEN'
#      self.outPortDataDefname = self.name.upper()+'_OUT_PORT_DATA_LEN'
#      headerFile.code.append(C.define(self.inPortDataDefname,str(0)+'u'))
#      headerFile.code.append(C.define(self.outPortDataDefname,str(packLen)+'u'))
      
      #write function prototypes for write functions
      headerFile.code.append(C.blank(1))
      headerFile.code.append(C.linecomment('function prototypes'))
      
      for elem in signalInfo:
         headerFile.code.append(C.statement(elem.func))
         
      fp.write(str(headerFile))
      return (initFunc,nodeDataFunc)
   
   def writeSourceFile(self, fp, signalInfo, initFunc, nodeDataFunc, node, inPortDataLen, outPortDataLen):
      indent=0
      indentStep=3      
      sourceFile=C.cfile(None)
      code = sourceFile.code
      code.append(C.line('//////////////////////////////////////////////////////////////////////////////'))
      code.append(C.line('// INCLUDES'))
      code.append(C.line('//////////////////////////////////////////////////////////////////////////////'))
      code.append(C.sysinclude('string.h'))
      code.append(C.include('%s.h'%self.name))
      code.append(C.include('pack.h'))
      if self.includes is not None:
         for filename in self.includes:
            code.append(C.include(filename))
      code.append(C.blank(1))
      code.append(C.line('//////////////////////////////////////////////////////////////////////////////'))
      code.append(C.line('// CONSTANTS AND DATA TYPES'))
      code.append(C.line('//////////////////////////////////////////////////////////////////////////////'))
      code.append(C.define('APX_DEFINITON_LEN', str(len(node.text)+1)+'u')) #add 1 for empty newline
      code.append(C.define('APX_IN_PORT_DATA_LEN', str(inPortDataLen)+'u'))
      code.append(C.define('APX_OUT_PORT_DATA_LEN', str(outPortDataLen)+'u'))
      
      code.append(C.line('//////////////////////////////////////////////////////////////////////////////'))
      code.append(C.line('// LOCAL FUNCTIONS'))
      code.append(C.line('//////////////////////////////////////////////////////////////////////////////'))
      code.append(C.statement('static void outPortData_writeCmd(apx_offset_t offset, apx_size_t len )'))

      code.append(C.line('//////////////////////////////////////////////////////////////////////////////'))
      code.append(C.line('// LOCAL VARIABLES'))
      code.append(C.line('//////////////////////////////////////////////////////////////////////////////'))
      
      databuf=C.variable('m_outPortdata','uint8', static=True, array='APX_OUT_PORT_DATA_LEN')
      initData=C.variable('m_outPortInitData','uint8_t', static=True, array='APX_OUT_PORT_DATA_LEN')
      code.append(str(initData)+'= {')
      #TODO: implement support for init values
      #initBytes=[]
      #for port in requirePorts:
      #   initBytes.extend(list(port['initValue']))
      #assert(len(initBytes) == databuf.array)
      code.append('   0')
      code.append('};')      
      code.append(C.blank(1))
    
      code.append(C.statement(databuf))
      code.append(C.statement(C.variable('m_outPortDirtyFlags','uint8_t', static=True, array='APX_OUT_PORT_DATA_LEN')))
      code.append(C.statement(C.variable('m_nodeData','apx_nodeData_t',static=True)))
      code.append(C.line('static const char *m_apxDefinitionData='))
      for line in node.text.split('\n'):
         line=line.replace('"','\\"')
         code.append(C.line('"%s\\n"'%line))         
      code.elements[-1].val+=';'
      code.append(C.blank(1))


      
      code.append(C.line('//////////////////////////////////////////////////////////////////////////////'))
      code.append(C.line('// GLOBAL FUNCTIONS'))
      code.append(C.line('//////////////////////////////////////////////////////////////////////////////'))

      sourceFile.code.append(initFunc)
      body=C.block(innerIndent=indentStep)      
      body.append(C.statement('memcpy(&%s[0],&%s[0],sizeof(%s))'%(databuf.name,initData.name,initData.name)))
      body.append(C.statement('memset(&m_outPortDirtyFlags[0],0,sizeof(m_outPortDirtyFlags))'))
      body.append(C.statement('apx_nodeData_create(&m_nodeData, "%s", (const uint8_t*) &m_apxDefinitionData[0], APX_DEFINITON_LEN, 0, 0, APX_IN_PORT_DATA_LEN, &m_outPortdata[0], &m_outPortDirtyFlags[0], APX_OUT_PORT_DATA_LEN)'%(node.name)))
      body.append(C.line('#ifdef APX_POLLED_DATA_MODE', indent=0))
      body.append(C.statement('rbfs_create(&m_outPortDataCmdQueue, &m_outPortDataCmdBuf[0], APX_NUM_OUT_PORTS, APX_DATA_WRITE_CMD_SIZE)'))
      body.append(C.line('#endif', indent=0))
               
      sourceFile.code.append(body)
      sourceFile.code.append(C.blank(1))
    
      sourceFile.code.append(nodeDataFunc)
      body=C.block(innerIndent=indentStep)
      
      body.append(C.statement('return &m_nodeData'))
      sourceFile.code.append(body)
      sourceFile.code.append(C.blank(1))
    
      for signal in signalInfo:
         sourceFile.code.append(signal.func)
         body,packLen=self.genPackFunc(signal.func,databuf,signal.offset,signal.dsg.resolveType(),indent,indentStep)      
         code.append(body)
         code.append(C.blank())
      
      code.append(C.line('//////////////////////////////////////////////////////////////////////////////'))
      code.append(C.line('// LOCAL FUNCTIONS'))
      code.append(C.line('//////////////////////////////////////////////////////////////////////////////'))
      code.append('''static void outPortData_writeCmd(apx_offset_t offset, apx_size_t len )
{
   if ( (apx_nodeData_getDataWriteMode(&m_nodeData) == true) && (m_outPortDirtyFlags[offset] == 0) )
   {      
      apx_dataWriteCmd_t cmd;
      cmd.offset=offset;
      cmd.len=len;
      m_outPortDirtyFlags[offset] = (uint8_t) 1u;
      apx_nodeData_unlockOutPortData(&m_nodeData);
      apx_nodeData_outPortDataWriteCmd(&m_nodeData, &cmd);
      return;
   }
   apx_nodeData_unlockOutPortData(&m_nodeData);
}
''')
      
      
      fp.write(str(sourceFile))
    
   def generate(self, node, header_fp, source_fp, name=None, includes=None):
      signalInfo=[]
      inPortDataLen=0
      outPortDataLen=0
      offset=0
      if name is None:
         name='Apx_'+node.name
      self.name=name
      self.includes=includes
      #require ports (in ports)
      for port in node.requirePortList:
         is_pointer=False        
         func = C.function("%s_Read_%s"%(name,port.name),"Std_ReturnType")
         if port.dsg.isComplexType(node.typeList):
            is_pointer=True
         func.add_arg(C.variable('val',port.dsg.typename(node.typeList),pointer=is_pointer))         
         packLen=port.dsg.packLen(node.typeList)
         port.dsg.typeList= node.typeList
         signalInfo.append(SignalInfo(offset,packLen,func,port.dsg,0)) #TODO: implement init value
         inPortDataLen+=packLen
         offset+=packLen
      #provide ports (out ports)
      offset=0      
      for port in node.providePortList:
         is_pointer=False        
         func = C.function("%s_Write_%s"%(name,port.name),"Std_ReturnType")
         if port.dsg.isComplexType(node.typeList):
            is_pointer=True    
         func.add_arg(C.variable('val',port.dsg.typename(node.typeList),pointer=is_pointer))         
         packLen=port.dsg.packLen(node.typeList)
         port.dsg.typeList= node.typeList
         signalInfo.append(SignalInfo(offset,packLen,func,port.dsg,0)) #TODO: implement init value
         outPortDataLen+=packLen
         offset+=packLen
            
      (initFunc,nodeDataFunc) = self.writeHeaderFile(header_fp, signalInfo, name.upper()+'_H')
      self.writeSourceFile(source_fp,signalInfo,initFunc,nodeDataFunc, node, inPortDataLen, outPortDataLen)
