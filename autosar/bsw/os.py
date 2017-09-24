class Task:
   def __init__(self, name):
      self.name = name
      self.runnables=[]
      self.event_map = {}

class Config:
   def __init__(self):      
      self.tasks=[]
   
   def create_task(self, name):
      task = Task(name)
      self.tasks.append(task)
      return task
   
   