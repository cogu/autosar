import autosar
   
ws = autosar.workspace('4.2.2')
ws.loadXML('packages.arxml') #see previous example

#Find package named Package1
package = ws.find('/Package1')
print(package.name + "\n")

#Find all top-level packages
for package in ws.findall('/*'):
    print(package.name)