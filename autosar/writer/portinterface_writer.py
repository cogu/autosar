from autosar.writer.writer_base import WriterBase
import autosar.portinterface

class PortInterfaceWriter(WriterBase):
   def __init__(self,version):
      super().__init__(version)
   