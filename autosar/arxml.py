import os
import sys
import re
import json
import ntpath
from portinterface import PortInterfacePackage
from package import Package
from generator import generatorBase
from project import PackageParser


def loadXML(filename,version=3):
   packages = []
   if version==3:
      xmlroot = parseXMLFile(filename,'http://autosar.org/3.0.2')
      for package in xmlroot.findall('.//AR-PACKAGE'):
         name = package.find("./SHORT-NAME").text
         if name=='DataType':
            pkg = DataTypePackage()
            pkg.loadFromXML(package,version)
            packages.append(pkg)
            
   else:
      raise NotImplementedError('Version of ARXML not supported')
   
   if len(packages)==0: return None
   elif len(packages)==1: return packages[0]
   else: return packages


   
   
