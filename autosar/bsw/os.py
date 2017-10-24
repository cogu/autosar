import autosar
import cfile as C
class Task:
   def __init__(self, name):
      self.name = name
      self.runnables=[]
      self.event_map = {}
      self.is_finalized = False
      self.event_masks=[]
      self.timer_events=[]
      
   
   def map_runnable(self, runnable):
      assert(isinstance(runnable, autosar.rte.partition.Runnable))
      self.runnables.append(runnable)
      component = runnable.parent      
      for event in component.events:
         if event.runnable is runnable:            
            event.symbol = 'EVENT_MASK_%s_%s'%(self.name, event.name)
            if event.symbol not in self.event_map:
                self.event_map[event.symbol] = []
            self.event_map[event.symbol].append(event)
            if event not in runnable.event_triggers:
               runnable.event_triggers.append(event)

   def finalize(self):
      if not self.is_finalized:
         self._define_event_masks()
         self.is_finalized = True

   def _define_event_masks(self):
      bit_mask = 1
      num_timer_events = 0
      for num,event_mask in enumerate(sorted(self.event_map.keys())):
         if num>32:
            raise RuntimeError('Task %s cannot support more than 32 events'%(os_task.name))
         event_list = self.event_map[event_mask]
         for event in event_list:
            if isinstance(event, autosar.rte.TimerEvent):
               self.timer_events.append(event)
         runnables_string = ", ".join([event.runnable.symbol for event in event_list])
         self.event_masks.append(C.define(event_mask, str('((uint32) 0x%08X)'%bit_mask)+' '+str(C.linecomment(runnables_string)), align=80))
         bit_mask=bit_mask<<1


class OsConfig:
   def __init__(self, partition):      
      self.tasks=[]
      self.partition=partition
      self.mode_switch_calls=set()
      self._create_mode_switch_events()
   
   def create_task(self, name):
      task = Task(name)
      self.tasks.append(task)
      return task
   
   def find_os_task_by_runnable(self, runnable):
      assert(isinstance(runnable, autosar.rte.partition.Runnable))
      for task in self.tasks:
         for task_runnable in task.runnables:
            if task_runnable is runnable:
               return task
      return None
   
   def _create_mode_switch_events(self):
      for func in self.partition.mode_switch_functions.values():
         for callback in sorted(func.calls.keys()):
            self.mode_switch_calls.add(callback)

   