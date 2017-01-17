from apx.node import *
from apx.base import *
import apx.generator
import apx.parser
import apx.context

#helper functions
def Context():
   return apx.context.Context()

def node_from_swc(ws, swc):
   node = Node(swc.name)
   node.import_swc(ws, swc)
   return node

def ApxParser():
   return apx.parser.ApxParser()

def OutPortDataGenerator():
   return apx.generator.OutPortDataGenerator()

def NodeGenerator():
   return apx.generator.NodeGenerator()