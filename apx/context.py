import apx

class Context:
   def __init__(self):
      self.nodes = []
   
   def append(self, node):
      assert(isinstance(node, apx.Node))
      self.nodes.append(node)
      
   def write(self, fp):
      """
      writes context to file fp
      """
      fp.write("APX/1.2\n")
      for node in self.nodes:
         node.write(fp)
      fp.write("\n") #always end file with a new line

   def dumps(self):
      """
      returns context as a string
      """
      lines = []
      lines.append("APX/1.2")
      for node in self.nodes:
         lines.extend(node.lines())
      text = '\n'.join(lines)+'\n'
      return text
   