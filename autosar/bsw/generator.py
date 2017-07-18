import cfile as C
import os
import io
import autosar

class OsConfigGenerator:
   def __init__(self, cfg):
      self.cfg = cfg
      self.event_id = 1
      self.num_timer_events = 0
   
   def generateEventCfg(self, destdir, destfile='os_event_cfg.h'):
      self.event_id = 1
      self.num_timer_events = 0
      file = C.hfile(os.path.join(destdir, destfile))
      code = file.code
      with io.open(file.path, 'w', newline='\n') as fp:         
         for os_task in self.cfg.tasks:
            for event_name in sorted(os_task.event_map.keys()):
               rte_event = os_task.event_map[event_name]
               if isinstance(rte_event, autosar.rte.TimerEvent):
                  self.num_timer_events+=1                  
               code.append(C.define(event_name, str(self.event_id)+' '+str(C.linecomment(rte_event.rte_runnable.symbol)), align=60))
               self.event_id+=1
            code.append(C.blank())         
         code.append(C.define('OS_NUM_TIMER_EVENTS', str(self.num_timer_events)))
         for line in file.lines():
            fp.write(line+'\n')
