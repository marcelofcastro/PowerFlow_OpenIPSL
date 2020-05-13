#=========================================================================================      
# Authors: marcelofcastro and ManuelNvro     
# Description: Functions used to translate .raw and .dyr files into .mo files.
#=========================================================================================  
# ----- Init. libraries:
from network_structure import Node # object class for buses
from network_structure import Branch # object class for buses
import tkinter as tk # importing tk for GUI
import tkinter.messagebox as tkMessageBox # functions for meassage box
import tkinter.ttk as ttk # functions for displaying lists
#=========================================================================================      
# Function: getRaw
# Authors: marcelofcastro and ManuelNvro          
# Description: this function asks for and transforms raw file in list of objects.
# The function also extracts info about the system so it can be confirmed by user.
#=========================================================================================
def getRaw(rawfile):
	rawContent = [] # starting raw list.
	# ----- Opening the .raw file:
	with open(rawfile, "r+") as raw_file: # opens the raw file for reading
		for line in raw_file:
			rawContent.append(line) # adds line
	raw_file.close() # closes the raw file
	# ----- Finding specific parameters:
	FirstLine = rawContent[0] # finding first line of raw file
	system_base = float(FirstLine[2:10]) # finding system base in first line
	psse_version = float(FirstLine[12:15]) # finding psse version in first line
	system_frequency = float(FirstLine[22:27]) # finding system_frequency in first line
	# ----- Finding Indexes for raw file:
	rawIndex = [3] # relevant information start at third line
	# ----- Finding indexes for bus data:
	for ii in range(0,len(rawContent),1):
		busix = rawContent[ii].find("0 /")
		if busix == 0:
			rawIndex.append(ii+1)
	# ----- Message for confirming data is correct:
	message = " PSS(R)E version: %.0f.\n System power base: %.2f MVA.\n System frequency: %.0f Hz." % (float(psse_version),float(system_base),float(system_frequency))
	tkMessageBox.showinfo("Data Extracted", message) # displays psse version, base power and system frequency
	MsgBox = tkMessageBox.askquestion ('Confirm Extracted Data','Are you sure that extracted information is correct?',icon = 'warning') # asks for data confirmation 
	if MsgBox == 'yes':
		return [rawContent,rawIndex,system_base,system_frequency] # return data
	else:
		tkMessageBox.showinfo("Failure", "Execution of translation will be terminated") # display failure message
#=========================================================================================      
# Function: getNode
# Authors: marcelofcastro and ManuelNvro          
# Description: gets raw content and writes all buses as a list of objects. The function 
# also displays the information so data can be checked by the user.
#=========================================================================================
def getNode(rawContent,rawIndex):
	# ----- Calculating the size of bus matrix:
	nbuses = int(rawIndex[1])-int(rawIndex[0])-1
	BUSES = []
	# ----- Start retrieving bus information:
	for ii in range(nbuses):
		line = rawContent[ii+int(rawIndex[0])]
		BUSES.append(Node(ii+1,int(line[0:6]),line[8:20],float(line[22:30]),int(line[32:33]),float(line[49:56]),float(line[57:66])))
	# ----- Displaying information:
	DataBox = tk.Tk()
	DataBox.title("System Structure") 
	label = tk.Label(DataBox, text="Bus Information", font=("Arial",22)).grid(row=0, columnspan=7)
	cols = ('Element','Bus Number','Name','Base Voltage [kV]','Bus Type','Bus Voltage [pu]','Bus Angle [deg]')
	listBox = ttk.Treeview(DataBox, columns=cols, show='headings')
	for obj in BUSES:
		data = [obj.busOrdr, obj.busNmbr, obj.busName, obj.busKV, obj.busType, obj.busVoltage, obj.busAngle]
		listBox.insert("", "end", values=data)
	for col in cols:
		listBox.heading(col, text=col)
	listBox.grid(row=1, column=0, columnspan=2)
	closeButton = tk.Button(DataBox, text="Close", width=15, command=DataBox.destroy).grid(row=4, column=1)
	DataBox.wait_window()
	# ----- Message to confirm bus data structure is correct:
	MsgBox = tkMessageBox.askquestion ('Confirm Bus Data','Confirm if bus data is correct.',icon = 'warning') # asks for data confirmation 
	if MsgBox == 'yes':
		return BUSES # return bus structure
	else:
		tkMessageBox.showinfo("Failure", "Execution of translation will be terminated") # display failure message
#=========================================================================================      
# Function: getBranch
# Authors: marcelofcastro and ManuelNvro          
# Description: gets raw content and writes all branches a list of objects. The function 
# also displays the information so data can be checked by the user.
#=========================================================================================
def getBranch(rawContent,rawIndex):
	# ----- Calculating the number of branches:
	nbranches = int(rawIndex[5])-int(rawIndex[4])-1
	BRANCHES = []
	# ----- Start retrieving bus information:
	for ii in range(nbranches):
		line = rawContent[ii+int(rawIndex[4])]
		BRANCHES.append(Branch(int(line[0:6]),int(line[8:13]),int(line[15:17]),float(line[19:30]),float(line[31:42]),float(line[43:53])))
	# ----- Displaying information:
	DataBox = tk.Tk()
	DataBox.title("System Structure") 
	label = tk.Label(DataBox, text="Branch Information", font=("Arial",22)).grid(row=0, columnspan=6)
	cols = ('Bus From','Bus To','Circuit','Branch R [pu]','Branch X [pu]','Branch B [pu]')
	listBox = ttk.Treeview(DataBox, columns=cols, show='headings')
	for obj in BRANCHES:
		data = [obj.busFrom, obj.busTo, obj.branchNmbr, obj.branchR, obj.branchX, obj.branchB]
		listBox.insert("", "end", values=data)
	for col in cols:
		listBox.heading(col, text=col)
	listBox.grid(row=1, column=0, columnspan=2)
	closeButton = tk.Button(DataBox, text="Close", width=15, command=DataBox.destroy).grid(row=4, column=1)
	DataBox.wait_window()
	# ----- Message to confirm bus data structure is correct:
	MsgBox = tkMessageBox.askquestion ('Confirm Branch Data','Confirm if bus branch is correct.',icon = 'warning') # asks for data confirmation 
	if MsgBox == 'yes':
		return BRANCHES# return bus structure
	else:
		tkMessageBox.showinfo("Failure", "Execution of translation will be terminated") # display failure message
#=========================================================================================      
# Function: readRaw
# Authors: marcelofcastro and ManuelNvro          
# Description: this reads the Raw file and returns a system object
#=========================================================================================
def readRaw(rawfile):
	[rawContent,rawIndex,system_base,system_frequency] = getRaw(rawfile)
	BUSES = getNode(rawContent,rawIndex)
	BRANCHES = getBranch(rawContent,rawIndex)
	return [BUSES,BRANCHES]