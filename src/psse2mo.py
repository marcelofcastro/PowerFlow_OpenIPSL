#==========================================================================      
# Authors: marcelofcastro and ManuelNvro     
# Description: Functions used to translate .raw and .dyr files into .mo files
#==========================================================================
# ----- Init. libraries:
from network_structure import Node
#====================================================================================      
# Function: readRaw
# Authors: marcelofcastro and ManuelNvro          
# Description: this function asks for and reads the Raw file
#====================================================================================
def readRaw(rawfile):
	rawContent = []
	rawIndex = [3] # relevant information start at third line	
	# ----- Opening the .raw file:
	with open(rawfile, "r+") as raw_file: # opens the raw file for reading
		for line in raw_file:
			rawContent.append(line) # adds line
	raw_file.close() # closes the raw file
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
	nbuses = int(rawIndex[1])-int(rawIndex[0])-1
	BUSES = []
	# ----- Start retrieving bus information:
	for ii in range(nbuses):
		line = rawContent[ii+int(rawIndex[0])]
		BUSES.append(Node(ii+1,int(line[0:6]),line[8:20],float(line[22:30]),int(line[32:33]),float(line[49:56]),float(line[57:66])))
	return [BUSES,system_base,psse_version,system_frequency]