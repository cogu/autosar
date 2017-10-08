import autosar
class Task:
   def __init__(self, name):
      self.name = name
      self.runnables=[]
      self.event_map = {}
   
   def map_runnable(self, runnable):
      assert(isinstance(runnable, autosar.rte.partition.Runnable))
      self.runnables.append(runnable)
      component = runnable.parent      
      for event in component.events:
         if event.runnable is runnable:            
            task_event_name = 'OsEvent_%s_%s'%(self.name,event.name)            
            if task_event_name not in self.event_map:
                self.event_map[task_event_name] = event

class OsConfig:
   def __init__(self):      
      self.tasks=[]
   
   def create_task(self, name):
      task = Task(name)
      self.tasks.append(task)
      return task
   
   