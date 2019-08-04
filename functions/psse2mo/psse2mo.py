#==========================================================================      
# Author: Marcelo de Castro Fernandes
#           
# Description: - - -
#==========================================================================
# ----- Init. libraries:
import time                     # importing time 
import numpy as np              # importing numpy
from numpy.linalg import inv    # importing inv function
import math                     # importing library for math
import cmath                    # importing library for complex numbers
# ----- Initializing contents:
rawContent = []
rawIndex = []
# ----- Opening the file:
start_time = time.time() # starting to count the time:
with open("testsystem.raw", "r+") as raw_file: # opens the file for reading
    for line in raw_file:
        rawContent.append(line)     # adds line
raw_file.close() # closes the file
# ----- Finding specific parameters:
FirstLine = rawContent[0]
system_base = float(FirstLine[2:10])
psse_version = float(FirstLine[12:15])
system_frequency = float(FirstLine[22:27])
# ----- Writing modelica file:
modelica_file = open("testsystem.mo","w+")
modelica_file.write("model testsystem\n")
modelica_file.write("  inner OpenIPSL.Electrical.SystemBase SysData(S_b = %.0f, fn = %.2f);\n" % (float(system_base*1000000),float(system_frequency)))
modelica_file.close()
# ----- Printing report file:
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
# ----- Finding indexes for bus data:
rawIndex = ['3']
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
	BUSD[ii,0] = ii
	BUSD[ii,1] = float(line[0:6])
	BUSNAME.append(line[8:20])
	BUSD[ii,2] = float(line[22:30])
	BUSD[ii,3] = float(line[32:33])
	BUSD[ii,4] = float(line[34:38])
	BUSD[ii,5] = float(line[39:43])
	BUSD[ii,6] = float(line[44:48])
	BUSD[ii,7] = float(line[49:56])
	BUSD[ii,8] = float(line[57:66])
	BUSD[ii,9] = float(line[67:74])
	BUSD[ii,10] = float(line[75:82])
# ----- Writing the modelica file:
nameornumber = 1
if nameornumber == 0:
	modelica_file = open("testsystem.mo","a")
	for ii in range(0,nbuses,1):
		modelica_file.write("  OpenIPSL.Electrical.Buses.BusExt %s (V_b = %.1f, v_0 = pfdata.voltages.V%d, angle_0 = pfdata.angles.A%d); \n" % (str(BUSNAME[ii]), BUSD[ii,2]*1000,int(BUSD[ii,1]),int(BUSD[ii,1]) ))
	modelica_file.close()
else:
	modelica_file = open("testsystem.mo","a")
	for ii in range(0,nbuses,1):
		modelica_file.write("  OpenIPSL.Electrical.Buses.BusExt B_%d (V_b = %.1f, v_0 = pfdata.voltages.V%d, angle_0 = pfdata.angles.A%d); \n" % (int(BUSD[ii,1]), BUSD[ii,2]*1000,int(BUSD[ii,1]),int(BUSD[ii,1])))
	modelica_file.close()
# ----- Finishing counting time:		
elapsedtime = time.time() - start_time
# ----- Ending modelica file:
modelica_file = open("testsystem.mo","a")
modelica_file.write("end testsystem;")
modelica_file.close()
# ----- Printing intermediate files:
#for each in BUSNAME:
#	print each
#np.savetxt('BUS.txt',BUS, fmt='%.4f')