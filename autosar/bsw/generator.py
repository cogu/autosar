import cfile as C
import os
import io
import autosar

innerIndentDefault=3 #default indendation (number of spaces)

def _genCommentHeader(comment):
   code = C.sequence()
   code.append(C.line('/*********************************************************************************************************************'))
   code.append(C.line('* %s'%comment))
   code.append(C.line('*********************************************************************************************************************/'))
   return code

class AlarmVariable:
   def __init__(self, task):
      init_delay=0 #FIXME: allow users to select this at a later time
      self.decl = C.variable('os_alarm_cfg_%s'%task.name, 'os_alarm_cfg_t', static=True, const=True, array='OS_NUM_ALARMS_%s'%task.name)
      self.body = C.block(innerIndent=innerIndentDefault)
      self.body.append(C.linecomment('OS Task,       Event ID,                     Init Delay (ms),  Period (ms)'))
      for event in task.timer_events:
         self.body.append(C.line('{'+'{0: >10},{1: >50},{2: >5},{3: >5}'.format(
            '&m_os_task_'+task.name, 'EVENT_MASK_%s_%s'%(task.name,event.name), init_delay, event.inner.period)+'},'))

class OsTaskCfgVar:
   def __init__(self, tasks):
      self.decl = C.variable('os_task_cfg', 'os_task_elem_t', static=True, const=True, array='OS_NUM_TASKS')
      self.body = C.block(innerIndent=innerIndentDefault)
      for task in tasks:
         fmt='{0: >25},{1: >15},{2: >30},{3: >30}'
         if len(task.timer_events)>0:
            self.body.append(C.line('{'+fmt.format(
               '&m_os_task_'+task.name, task.name, '&os_alarm_cfg_%s[0]'%task.name, 'OS_NUM_ALARMS_%s'%task.name)+'},'))
         else:
            self.body.append(C.line('{'+fmt.format(
               '&m_os_task_'+task.name, task.name, '(os_alarm_cfg_t*) 0', '0')+'},'))

class OsConfigGenerator:
   def __init__(self, cfg):
      self.cfg = cfg
      self.static_vars={}
      self.alarm_vars=[]
      self.os_task_var=None
      
   def generate(self, dest_dir='.'):
      for task in self.cfg.tasks:
         task.finalize()
      self._create_static_vars()
      self.os_task_var = OsTaskCfgVar(self.cfg.tasks)
      self._generate_event_cfg_header(dest_dir)
      header_file = self._generate_task_cfg_header(dest_dir)
      self._generate_task_cfg_source(dest_dir, header_file)
   
   def _create_static_vars(self):
      for os_task in self.cfg.tasks:
         static_var = C.variable('m_os_task_'+os_task.name, 'os_task_t', static=True)
         self.static_vars[static_var.name]=static_var
         if len(os_task.timer_events)>0:
            self.alarm_vars.append(AlarmVariable(os_task))
   
   def _generate_event_cfg_header(self, dest_dir, file_name='os_event_cfg.h'):      
      header = C.hfile(os.path.join(dest_dir, file_name))
      code = header.code
      code.extend(_genCommentHeader('INCLUDES'))
      code.append(C.include('PlatForm_Types.h'))
      code.append('')
      code.extend(_genCommentHeader('PUBLIC CONSTANTS AND DATA TYPES'))
      for os_task in self.cfg.tasks:
         for event_mask in os_task.event_masks:
            code.append(event_mask)
         code.append(C.define('OS_NUM_ALARMS_%s'%os_task.name, str(len(os_task.timer_events))))
         code.append(C.blank())
      with io.open(header.path, 'w', newline='\n') as fp:
         for line in header.lines():
            fp.write(line+'\n')

   def _generate_task_cfg_header(self, dest_dir, file_name = 'os_task_cfg.h'):
      header = C.hfile(os.path.join(dest_dir, file_name))
      code = header.code
      code.extend(_genCommentHeader('INCLUDES'))
      code.append(C.include('os_types.h'))
      code.append(C.include('os_task.h'))
      code.append('')
      code.extend(_genCommentHeader('PUBLIC CONSTANTS AND DATA TYPES'))
      code.append(C.define('OS_NUM_TASKS',str(len(self.cfg.tasks))+'u'))
      code.append('')
      code.extend(_genCommentHeader('PUBLIC VARIABLES'))
      code.append(C.statement('extern os_cfg_t g_os_cfg'))
      code.append('')
      code.extend(_genCommentHeader('PUBLIC FUNCTION PROTOTYPES'))
      for task in self.cfg.tasks:
         code.append(C.statement('OS_TASK_HANDLER(%s, arg)'%task.name))
      for function_name in self.cfg.mode_switch_calls:
         code.append(C.statement(C.function(function_name, 'void')))
      with io.open(header.path, 'w', newline='\n') as fp:
         for line in header.lines():
            fp.write(line+'\n')
      return file_name

   def _generate_task_cfg_source(self, dest_dir, header_file, file_name = 'os_task_cfg.c'):
      source = C.cfile(os.path.join(dest_dir, file_name))
      code = source.code
      code.extend(_genCommentHeader('INCLUDES'))
      code.append(C.include(header_file))
      code.append(C.include('os_event_cfg.h'))
      code.append('')
      code.extend(_genCommentHeader('PRIVATE VARIABLES'))
      for static_var in sorted(self.static_vars.values(), key=lambda x: x.name):
         code.append(C.statement(static_var))
      code.append('')
      for alarm_var in self.alarm_vars:
         code.append(C.line(str(alarm_var.decl)+' ='))
         code.append(C.statement(alarm_var.body))
      code.append(C.line(str(self.os_task_var.decl)+' ='))
      code.append(C.statement(self.os_task_var.body))
      code.append('')
      code.extend(_genCommentHeader('PUBLIC VARIABLES'))
      code.append(C.line('os_cfg_t g_os_cfg ='))
      body = C.block(innerIndent = innerIndentDefault)
      body.append(C.line('&os_task_cfg[0],'))
      body.append(C.line('OS_NUM_TASKS,'))
      body.append(C.line('0,'))
      body.append(C.line('0'))
      code.append(C.statement(body))
      code.append('')
      code.extend(_genCommentHeader('PUBLIC FUNCTIONS'))
      for elem in self.cfg.partition.mode_switch_functions.values():
         for callback_name in sorted(elem.calls.keys()):
            code.extend(self._generate_mode_switch_func(callback_name, elem.calls[callback_name]))
            code.append('')

      with io.open(source.path, 'w', newline='\n') as fp:
         for line in source.lines():
            fp.write(line+'\n')
   
   def _generate_mode_switch_func(self, callback_name, events):
      code = C.sequence()
      generated=set()
      code.append(C.function(callback_name, 'void'))
      block = C.block(innerIndent = innerIndentDefault)
      for event in events:
         task = self.cfg.find_os_task_by_runnable(event.runnable)
         if task is not None:
            if (task.name, event.name) not in generated:               
               block.append(C.statement(C.fcall('os_task_setEvent', params=['&m_os_task_%s'%task.name, 'EVENT_MASK_%s_%s'%(task.name, event.name)])))
               generated.add((task.name, event.name))
      code.append(block)
      return code