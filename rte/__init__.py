import autosar
import os
import cfile
import sys
from autosar.rte.base import *
from autosar.rte.generator import *
from autosar.rte.partition import *
from autosar.rte.config import *

# class Variable:
#    def __init__(self, name, typename, isQueued=False, queueLen=None, initValue=None):
#       self.name = name
#       self.typename = typename
#       self.hasRead = False
#       self.hasWrite = False
#       self.isQueued = isQueued
#       self.queueLen  = queueLen
#       self.initValue = initValue
# 
# class IntegerVariable(Variable):
#    def __init__(self, name, typename, isQueued=False, queueLen=None, initValue=0):
#       super().__init__(name, typename, isQueued, queueLen, initValue)
#       
# 
# class RecordVariable(Variable):
#    def __init__(self, name, typename, isQueued=False, queueLen=None, initValue=None):
#       super().__init__(name, typename, isQueued, queueLen, initValue)
#       self.elements=[]
# 
# class ArrayVariable(Variable):
#    def __init__(self, name, typename, arrayLen=1, initValue=None):
#       super().__init__(name, typename, initValue=initValue)
#       self.arrayLen=arrayLen
# 
# class BooleanVariable(Variable):
#    def __init__(self, name, typename, initValue=None):
#       super().__init__(name, typename, initValue=initValue)