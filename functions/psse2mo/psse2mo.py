#==========================================================================      
# Author: Marcelo de Castro Fernandes
#           
# Description: - - -
#==========================================================================
# ----- Init. libraries:
import os                       # importing operational system
import time                     # importing time 
import numpy as np              # importing numpy
from numpy.linalg import inv    # importing inv function
import math                     # importing library for math
import cmath                    # importing library for complex numbers
# ----- Initializing paths:
homedirectory = os.getcwd()
workingdirectory = "/home/marcelo/Desktop/PyOpenIPSL"
systemdirectory = "/home/marcelo/Desktop/PyOpenIPSL/TestSystem"
sysdatadirectory = "/home/marcelo/Desktop/PyOpenIPSL/TestSystem/Data"
sysgensdirectory = "/home/marcelo/Desktop/PyOpenIPSL/TestSystem/Generators"
# ----- Creating working directory:
try:
	os.mkdir(workingdirectory)
except OSError:
    print ("Creation of the directory %s failed" % workingdirectory) 
# ----- Creating package directory:
try:
	os.mkdir(systemdirectory)
except OSError:
    print ("Creation of the directory %s failed" % systemdirectory) 
# ----- Creating systems data directory:
try:
	os.mkdir(sysdatadirectory)
except OSError:
    print ("Creation of the directory %s failed" % sysdatadirectory) 
# ----- Creating systems generators directory:
try:
	os.mkdir(sysgensdirectory)
except OSError:
    print ("Creation of the directory %s failed" % sysgensdirectory) 
# ----- Initializing file name:
networkname = "power_grid"
pkg_name = "package.mo"
pkg_ordr = "package.order"
# ----- Initializing arrays:
rawContent = []
dyrContent = []
rawIndex = ['3'] # relevant information start at third line
# ----- Opening the .raw file:
start_time = time.time() # starting to count the time:
with open("testsystem.raw", "r+") as raw_file: # opens the file for reading
    for line in raw_file:
        rawContent.append(line)     # adds line
raw_file.close() # closes the file
# ----- Opening the .dyr file:
with open("testsystem.dyr", "r+") as dyr_file: # opens the file for reading
    for line in dyr_file:
        dyrContent.append(line)     # adds line
dyr_file.close() # closes the file
# ----- Finding specific parameters:
FirstLine = rawContent[0]
system_base = float(FirstLine[2:10])
psse_version = float(FirstLine[12:15])
system_frequency = float(FirstLine[22:27])
# ----- Finding indexes for bus data:
for ii in range(0,len(rawContent),1):
	busix = rawContent[ii].find("0 /")
	if busix == 0:
		rawIndex.append(ii)
# ----- Calculating the size of bus matrix:
sweep_index = int(rawIndex[0])
while sweep_index != int(rawIndex[1]):
	sweep_index += 1
nbuses = sweep_index - int(rawIndex[0])
BUSD = np.zeros((nbuses,20)) # initializing bus matrix
BUSNAME = [] # initializing bus name array
# ----- Start retrieving buses:
sweep_index = int(rawIndex[0])
for ii in range(0,nbuses,1):
	line = rawContent[ii+int(rawIndex[0])]
	BUSD[ii,0] = ii                  # Auxiliary bus number
	BUSD[ii,1] = float(line[0:6])    # Bus number
	BUSNAME.append(line[8:20])       # Bus name
	BUSD[ii,2] = float(line[22:30])  # Bus base voltage
	BUSD[ii,3] = float(line[32:33])  # Bus type
	BUSD[ii,4] = float(line[34:38])  # 
	BUSD[ii,5] = float(line[39:43])  # 
	BUSD[ii,6] = float(line[44:48])  #
	BUSD[ii,7] = float(line[49:56])  # Bus voltage
	BUSD[ii,8] = float(line[57:66])  # Bus angle
	BUSD[ii,9] = float(line[67:74])  #
	BUSD[ii,10] = float(line[75:82]) #
# ----- Creating system package .mo file:
os.chdir(systemdirectory)
packagemo = open(pkg_name,"w+")
packagemo.write("package TestSystem \"Library of models translated from PSSE using Python_OpenIPSL.\" \n")
packagemo.write("annotation (uses(Modelica(version=\"3.2.2\"), Complex(version = \"3.2.2\"), OpenIPSL(version = \"2.0.0-dev\")), \n")
packagemo.write("            Documentation(info=\"<html> This package contains power system models translated from PSSE using Python_OpenIPSL.</html>\"));\n")
packagemo.write("end TestSystem;")
packagemo.close()
# ----- Creating system package .order file:
packageorder = open(pkg_ordr,"w+")
packageorder.write("%s\n" % (str(networkname)))
packageorder.write("Generators\n")
packageorder.write("Data")
packageorder.close()
# ----- Creating data package .mo file:
os.chdir(sysdatadirectory)
packagemo = open(pkg_name,"w+")
packagemo.write("within TestSystem;\n")
packagemo.write("package Data \"Modelica records for power flow data.\" \n\n")
packagemo.write("end Data;")
packagemo.close()
# ----- Creating data package .order file:
packageorder = open(pkg_ordr,"w+")
packageorder.write("pfdata\n")
packageorder.write("voltage_data\n")
packageorder.write("power_data")
packageorder.close()
# ----- Writing pfdata .mo file:
pfdatamo = open("pfdata.mo","w+")
pfdatamo.write("within TestSystem.Data;\n")
pfdatamo.write("record pfdata \" Translated and calculated power flow data.\"\n")
pfdatamo.write("  extends Modelica.Icons.Record;\n")
pfdatamo.write("  replaceable record voltages = voltage_data constrainedby voltage_data annotation (choicesAllMatching);\n ")
pfdatamo.write("  replaceable record powers = power_data constrainedby power_data annotation (choicesAllMatching);\n ")
pfdatamo.write("end pfdata;")
pfdatamo.close()
# ----- Writing voltage record:
vdatamo = open("voltage_data.mo","w+")
vdatamo.write("within TestSystem.Data;\n")
vdatamo.write("record voltage_data\n")
vdatamo.write("  extends Modelica.Icons.Record;\n")
for ii in range(0,nbuses,1):
	vdatamo.write("  //Bus %d\n" % (int(BUSD[ii,1])))
	vdatamo.write("  parameter Real V%d = %.4f;\n" % (int(BUSD[ii,1]), BUSD[ii,7]))
	vdatamo.write("  parameter Real A%d = %.4f;\n" % (int(BUSD[ii,1]), BUSD[ii,8]))
vdatamo.write("end voltage_data;")
# ----- Writing power record:
vdatamo = open("power_data.mo","w+")
vdatamo.write("within TestSystem.Data;\n")
vdatamo.write("record power_data\n")
vdatamo.write("  extends Modelica.Icons.Record;\n\n")
vdatamo.write("end power_data;")
# ----- Creating generators package .mo file:
os.chdir(sysgensdirectory)
packagemo = open(pkg_name,"w+")
packagemo.write("within TestSystem;\n")
packagemo.write("package Generators \"Library of generators models translated from PSSE using Python_OpenIPSL.\" \n\n")
packagemo.write("end Generators;")
packagemo.close()
# ----- Creating generators package .order file:
packageorder = open(pkg_ordr,"w+")
packageorder.close()
# ----- Creating and writing system data into modelica system file:
os.chdir(systemdirectory)
system_file = open(networkname+".mo","w+")
system_file.write("within TestSystem;")
system_file.write("model power_grid\n")
system_file.write("  inner OpenIPSL.Electrical.SystemBase SysData(S_b = %.0fe6, fn = %.2f);\n" % (float(system_base),float(system_frequency)))
system_file.write("  TestSystem.Data.pfdata pfdata;\n")
system_file.close()
# ----- Listing buses in the modelica file:
nameornumber = 1
if nameornumber == 0:
	system_file = open(networkname+".mo","a")
	for ii in range(0,nbuses,1):
		system_file.write("  OpenIPSL.Electrical.Buses.BusExt %s (V_b = %.1fe3, v_0 = pfdata.voltages.V%d, angle_0 = pfdata.voltages.A%d); \n" % (str(BUSNAME[ii]), BUSD[ii,2],int(BUSD[ii,1]),int(BUSD[ii,1]) ))
	system_file.close()
else:
	system_file = open(networkname+".mo","a")
	for ii in range(0,nbuses,1):
		system_file.write("  OpenIPSL.Electrical.Buses.BusExt bus_%d (V_b = %.1fe3, v_0 = pfdata.voltages.V%d, angle_0 = pfdata.voltages.A%d); \n" % (int(BUSD[ii,1]), BUSD[ii,2],int(BUSD[ii,1]),int(BUSD[ii,1])))
	system_file.close()
# ----- Finishing counting time:		
elapsedtime = time.time() - start_time
# ----- Ending modelica file:
system_file = open(networkname+".mo","a")
system_file.write("end power_grid;")
system_file.close()
# ----- Printing report file:
os.chdir(workingdirectory)
report = open("report_file.txt","w+")
report.write("=================================================================\n")
report.write("                     File Translation Report                     \n")
report.write("\n")
report.write("=================================================================\n")
report.write("PSS(r)E version from .raw file: %.0f\n" % (float(psse_version)))
report.write("System power base: %.2f MVA\n" % (float(system_base)))
report.write("System frequency: %.0f Hz\n" % (float(system_frequency)))
report.write("=================================================================\n")
report.close()
# ----- Printing intermediate files:
#for each in BUSNAME:
#	print each
#np.savetxt('BUS.txt',BUS, fmt='%.4f')