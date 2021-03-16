#=========================================================================================      
# Description: Functions used to translate .raw and .dyr files into .mo files.
#=========================================================================================  
# ----- Init. libraries:
import os
#from network_structure import DynSys # object class for buses
#from network_structure import DynNode # object class for buses
#from network_structure import DynCircuit # object class for buses
import tkinter as tk # importing tk for GUI
import tkinter.messagebox as tkMessageBox # functions for meassage box
import tkinter.ttk as ttk # functions for displaying lists
from em_psse import * # importing raw PARSER
from andes_dyr import * # importing dyr PARSER
import argparse # importing additional libraries
import logging # importing additional libraries
#=========================================================================================      
# Function: getRawBase
# Authors: marcelofcastro        
# Description: this function asks for and transforms raw file in list of objects.
# The function also extracts info about the system so it can be confirmed by user.
#=========================================================================================
def getRawBase(rawfile):
	rawContent = [] # starting raw list.
	# ----- Opening the .raw file:
	with open(rawfile, "r+") as raw_file: # opens the raw file for reading
		for line in raw_file:
			rawContent.append(line) # adds line
	FirstLine = rawContent[0].strip().split('/')
	FirstLine = FirstLine[0].split(',')
	# ----- Finding specific parameters:
	system_base = float(FirstLine[1]) # finding system base in first line
	psse_version = float(FirstLine[2]) # finding psse version in first line
	system_frequency = float(FirstLine[5]) # finding system_frequency in first line
	# ----- Message for confirming data is correct:
	message = " PSS(R)E version: %.0f.\n System power base: %.1f MVA.\n System frequency: %.0f Hz." % (psse_version,system_base,system_frequency)
	tkMessageBox.showinfo("PSSE File Parsed", message) # displays psse version, base power and system frequency
	return [system_base,system_frequency]
#=========================================================================================      
# Function: readRaw
# Authors: anderson-optimization and marcelofcastro          
# Description: It uses the PSSE parser developed by https://github.com/anderson-optimization
# The parser can be found in https://github.com/anderson-optimization/em-psse. In 
# addition, the code also extracts information about the system.
#=========================================================================================
def readRaw(rawfile):
	raw_data=parse_raw(rawfile)
	sysdata=format_all(raw_data)
	[system_base,system_frequency] = getRawBase(rawfile)
	# df_fixshnt=sysdata['fixedshunt']
	# df_tf=sysdata['transformer']
	# df_gen=sysdata['gen']
	# df_branch=sysdata['branch']
	# df_load=sysdata['load']
	# df_bus=sysdata['bus']
	return [system_base,system_frequency,sysdata]
#=========================================================================================      
# Function: readDyr
# Authors: cuihantao and marcelofcastro          
# Description: It uses the PSSE DYR parser developed by https://github.com/cuihantao
# The expanded by marcelofcastro to be compatible with OpenIPSL models. 
# The function returns each model and the data used in each model.
#=========================================================================================
def readDyr(dyrfile):
	dyrdata=parse_dyr(dyrfile)
	return dyrdata
#=========================================================================================      
# Function: lookFor
# Authors: marcelofcastro          
# Description: It finds models connected to a particular bus and circuit.
#=========================================================================================
def lookFor(modeltype,bus,circuit,dyrdata):	
	# ----- Lists of models:
	macmodels = ['GENCLS','GENSAL','GENSAE','GENROU','GENROE','CSVGN1','WT4G1']
	excmodels = ['ESAC1A','ESAC2A','ESDC1A','ESDC2A','ESST1A','ESST4B','EXAC1','EXAC2','EXNI','EXST1','IEEET1','IEEET2','IEEEX1','SCRX','SEXS','ST5B','URST5T']
	govmodels = ['GAST','GGOV1','GGOV1DU','HYGOV','IEEEG1','IEESGO','TGOV1']
	pssmodels = ['IEEEST','IEE2ST','PSS2A','PSS2B','STAB2A','STAB3','STABNI','STBSVC']
	wndmodels = ['WT4E1']
	cmpmodels = ['IEEEVC']
	# ----- Determining which list will be used:
	if modeltype == 'machine':
		models = macmodels
	elif modeltype == 'exciter':
		models = excmodels
	elif modeltype == 'governor':
		models = govmodels
	elif modeltype == 'stabilizer':
		models = pssmodels
	elif modeltype == 'wind':
		models = wndmodels
	elif modeltype == 'compensator':
		models = cmpmodels
	# ----- Searching for model:
	mdldata = 'None'
	index = 0
	flag = False
	#for mdl in models:
	for i in range(len(models)):
		mdl = models[i]
		try:
			mdlinst = dyrdata[mdl]
			flag = True
			if flag == True:
				buses = mdlinst[0]
				circuits = mdlinst[1]
				for ii in range(len(mdlinst)):
					if buses[ii] == int(bus):
						if circuits[ii] == int(circuit):
							mdldata = mdl
							index = ii
				flag = False
		except:
			continue
	return [mdldata,index] 
#=========================================================================================      
# Function: writeSysMo
# Authors: marcelofcastro        
# Description: It writes the files needed for system package and the network file.
#=========================================================================================
def writeSysMo(sdir,pkg_name,pkg_ordr,networkname,sysdata,system_frequency,system_base):
	# ----- Extracting information from system
	buses = sysdata['bus'] # getting bus data 
	gens = sysdata['gen'] # getting generator data
	lines = sysdata['branch'] # getting transmission line data
	transf = sysdata['transformer'] # getting transformer data
	loads = sysdata['load'] # getting load data
	try:
		shunts = sysdata['fixedshunt'] # getting shunt data
	except:
		shunts = []
	# ----- Changing directory to system directory
	os.chdir(sdir)
	# ----- Creating system package .mo file:
	packagemo = open(pkg_name,"w+")
	packagemo.write("package System \"System automatically translated from PSSE using Python_OpenIPSL.\" \n\n")
	packagemo.write("annotation (uses(Modelica(version=\"3.2.3\"), Complex, OpenIPSL(version = \"2.0.0-beta.1\")), \n")
	packagemo.write("            Documentation(info=\"<html> This package contains power system models translated from PSSE using Python_OpenIPSL.</html>\"));\n")
	packagemo.write("end System;")
	packagemo.close()
	# ----- Creating system package .order file:
	packageorder = open(pkg_ordr,"w+")
	packageorder.write("%s\n" % (str(networkname)))
	packageorder.write("Generators\n")
	packageorder.write("Data")
	packageorder.close()
	# ----- Creating and writing system data into modelica system file:
	system_file = open(networkname+".mo","w+")
	system_file.write("within System;\n")
	system_file.write("model %s\n" % (str(networkname)))
	system_file.write("  inner OpenIPSL.Electrical.SystemBase SysData(S_b = %.0f, fn = %.2f) annotation (Placement(transformation(extent={{-94,80},{-60,100}})));\n" % (float(system_base)*1000000,float(system_frequency)))
	system_file.write("  inner System.Data.pfdata flowdata (redeclare replaceable record voltages = Data.voltage_data, redeclare replaceable record powers = Data.power_data)  annotation (Placement(transformation(extent={{-88,60},{-68,80}})));\n")
	# LISTING BUSES in the modelica file:
	system_file.write("// -- Buses:\n")
	if len(buses) != 0:
		for ii in range(len(buses)):
			bn = int(buses.iloc[ii,0])
			system_file.write("  OpenIPSL.Electrical.Buses.Bus bus_%d (V_b = flowdata.voltages.BaseVoltage%d, v_0 = flowdata.voltages.V%d, angle_0 = flowdata.voltages.A%d); \n" % (bn,bn,bn,bn))
	else:
		system_file.write("// system has no bus\n")
	# LISTING BRANCHES in the modelica file:
	system_file.write("// -- Lines:\n")
	if len(lines) != 0:
		for ii in range(len(lines)):
			system_file.write("  OpenIPSL.Electrical.Branches.PwLine line%d (R = %.4f, X = %.4f, G = 0.0, B = %.4f); \n" % ((ii+1),float(lines.iloc[ii,3]),float(lines.iloc[ii,2]),float(lines.iloc[ii,4]/2)))
	else:
		system_file.write("// system has no line\n")
	# LISTING TRANSFORMERS in the modelica file:
	system_file.write("// -- Transformers:\n")
	if len(transf) != 0:
		for ii in range(len(transf)):
			system_file.write("  OpenIPSL.Electrical.Branches.PSSE.TwoWindingTransformer twTransformer%d (R = %.4f, X = %.4f, G = 0.0, B = 0.0, t1 = %.6f, t2 = %.6f ); \n" % ((ii+1),float(transf.iloc[ii,2]),float(transf.iloc[ii,3]),float(transf.iloc[ii,12]),float(transf.iloc[ii,13])))
	else:
		system_file.write("// system has no transformer\n")
	# LISTING LOADS in modelica file:
	system_file.write("// -- Loads:\n")
	if len(loads) != 0:
		for ii in range(len(loads)):
			bn = int(loads.iloc[ii,0])
			system_file.write("  OpenIPSL.Electrical.Loads.PSSE.Load load%d_bus%d (V_b = flowdata.voltages.BaseVoltage%d, v_0 = flowdata.voltages.V%d, angle_0 = flowdata.voltages.A%d, P_0 = %.4f, Q_0 = %.4f); \n" % ((ii+1),bn,bn,bn,bn,float(loads.iloc[ii,1]),float(loads.iloc[ii,2])))
	else:
		system_file.write("// system has no load\n")
	# LISTING SHUNT in modelica file:
	system_file.write("// -- Shunts:\n")
	if len(shunts) != 0:
		for ii in range(len(shunts)):
			bn = int(loads.iloc[ii,0])
			system_file.write("  OpenIPSL.Electrical.Banks.PSSE.Shunt bank%d_bus%d (G = 0.0, B = %.4f); \n" % ((ii+1),int(shunts.iloc[ii,0]),float(shunts.iloc[ii,1])))
	else:
		system_file.write("// system has no shunt bank\n")
	# LISTING GENERATION UNITS in modelica file:
	system_file.write("// -- Generator Units:\n")
	if len(gens) != 0:
		for ii in range(len(gens)):
			bn = gens.iloc[ii,0]
			system_file.write("  System.Generators.Gen%d_%d gen%d_%d (V_b = flowdata.voltages.BaseVoltage%d, v_0 = flowdata.voltages.V%d, angle_0 = flowdata.voltages.A%d, P_0 = flowdata.powers.P%d_%d, Q_0 = flowdata.powers.Q%d_%d); \n" % ((ii+1),bn,(ii+1),bn,bn,bn,bn,(ii+1),bn,(ii+1),bn))
	else:
		system_file.write("// system has no generator\n")
	# Starting EQUATION section (connections):
	system_file.write("equation\n")
	# Starting CONNECTION OF BRANCHES:
	if len(lines) != 0:
		system_file.write("// -- Connecting branches:\n")
		for ii in range(len(lines)):
			system_file.write("  connect(bus_%d.p,line%d.p); \n" % (int(lines.iloc[ii,0]),(ii+1)))
			system_file.write("  connect(line%d.n,bus_%d.p); \n" % ((ii+1),int(lines.iloc[ii,1])))
	else:
		system_file.write("// No branch to connect.\n")
	# Starting CONNECTION OF TRANSFORMERS:
	if len(transf) != 0:
		system_file.write("// -- Connecting transformers:\n")
		for ii in range(len(transf)):
			system_file.write("  connect(bus_%d.p,twTransformer%d.p); \n" % (int(transf.iloc[ii,0]),(ii+1)))
			system_file.write("  connect(twTransformer%d.n,bus_%d.p); \n" % ((ii+1),int(transf.iloc[ii,1])))
	else:
		system_file.write("// No transformer to connect.\n")
	# Starting CONNECTION OF LOADS:
	if len(loads) != 0:
		system_file.write("// -- Connecting loads:\n")
		for ii in range(len(loads)):
			system_file.write("  connect(load%d_bus%d.p,bus_%d.p); \n" % ((ii+1),int(loads.iloc[ii,0]),int(loads.iloc[ii,0])))
	else:
		system_file.write("// No load to connect.\n")
	# Starting CONNECTION OF BANKS:
	if len(shunts) != 0:
		system_file.write("// -- Connecting banks:\n")
		for ii in range(len(shunts)):
			system_file.write("  connect(bank%d_bus%d.p,bus_%d.p); \n" % ((ii+1),int(shunts.iloc[ii,0]),int(shunts.iloc[ii,0])))
	else:
		system_file.write("// No shunt bank to connect.\n")
	# Starting CONNECTION OF GENERATION UNITS:
	if len(gens) != 0:
		system_file.write("// -- Connecting generation units:\n")
		for ii in range(len(gens)):
			system_file.write("  connect(gen%d_%d.pin,bus_%d.p); \n" % ((ii+1),int(gens.iloc[ii,0]),int(gens.iloc[ii,0])))
	else:
		system_file.write("// No generator to connect.\n")
	# Closing file modelica file:
	system_file.write("end %s;" % (str(networkname)))
	system_file.close()
#=========================================================================================      
# Function: writeDataMo
# Authors: marcelofcastro       
# Description: It writes the files needed for data package.
#=========================================================================================
def writeDataMo(ddir,pkg_name,pkg_ordr,sysdata):
	# ----- Extracting information from system
	buses = sysdata['bus'] # getting bus data 
	gens = sysdata['gen'] # getting generator data
	# ----- Changing directory to system data directory:
	os.chdir(ddir)
	# ----- Creating data package .mo file:
	packagemo = open(pkg_name,"w+")
	packagemo.write("within System;\n")
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
	pfdatamo.write("within System.Data;\n")
	pfdatamo.write("record pfdata \" Translated and calculated power flow data.\"\n")
	pfdatamo.write("  extends Modelica.Icons.Record;\n")
	pfdatamo.write("  replaceable record voltages = voltage_data constrainedby voltage_data annotation (choicesAllMatching);\n")
	pfdatamo.write("  replaceable record powers = power_data constrainedby power_data annotation (choicesAllMatching);\n")
	pfdatamo.write("end pfdata;")
	pfdatamo.close()
	# ----- Writing voltage record:
	vdatamo = open("voltage_data.mo","w+")
	vdatamo.write("within System.Data;\n")
	vdatamo.write("record voltage_data\n")
	vdatamo.write("  extends Modelica.Icons.Record;\n")
	for ii in range(len(buses)):
		vdatamo.write("  //Bus %d - %s \n" % (int(buses.iloc[ii,0]),buses.iloc[ii,1]))
		vdatamo.write("  parameter Real BaseVoltage%d = %.0f;\n" % (int(buses.iloc[ii,0]),float(buses.iloc[ii,2])*1000))# I need to change the unit here to what's used in OpenIPSL
		vdatamo.write("  parameter Real V%d = %.4f;\n" % (int(buses.iloc[ii,0]), float(buses.iloc[ii,4])))# I need to change the unit here to what's used in OpenIPSL
		vdatamo.write("  parameter Real A%d = %.4f;\n" % (int(buses.iloc[ii,0]), float(buses.iloc[ii,5]))) # I need to change the unit here to what's used in OpenIPSL
	vdatamo.write("end voltage_data;")
	# ----- Writing power record:
	pdatamo = open("power_data.mo","w+")
	pdatamo.write("within System.Data;\n")
	pdatamo.write("record power_data\n")
	pdatamo.write("  extends Modelica.Icons.Record;\n")
	for ii in range(len(gens)):
		pdatamo.write("  //Generator in Bus %d\n" % (int(gens.iloc[ii,0])))
		pdatamo.write("  parameter Real P%d_%d = %.0f;\n" % ((ii+1),int(gens.iloc[ii,0]), float(gens.iloc[ii,2])*1000000))# I need to change the unit here to what's used in OpenIPSL
		pdatamo.write("  parameter Real Q%d_%d = %.0f;\n" % ((ii+1),int(gens.iloc[ii,0]), float(gens.iloc[ii,4])*1000000)) # I need to change the unit here to what's used in OpenIPSL
	pdatamo.write("end power_data;")
#=========================================================================================      
# Function: writeMac
# Authors: marcelofcastro        
# Description: It writes machine model.
#=========================================================================================
def writeMac(genpdata,index,dyrdata,result,file):
	# ----- Extract results:
	model = result[0]
	row = result[1]
	# ----- Extract list of models that match:
	genlist = dyrdata[model]
	# ----- Extract Mb:
	Mb = float(genpdata.iloc[index,9])*1000000
	# ----- Writing Parameters for models:
	file.write("  //Writing machine:\n")
	if model == 'GENCLS':
		file.write("  OpenIPSL.Electrical.Machines.PSSE.GENCLS machine(\n")
		file.write("   H = %.4f,\n" % float(genlist.iloc[row,2]))
		file.write("   D = %.4f,\n" % float(genlist.iloc[row,3]))
		file.write("   M_b = %.2f,\n" % Mb)
		file.write("   V_b = V_b,\n")
		file.write("   P_0 = P_0,\n")
		file.write("   Q_0 = Q_0,\n")
		file.write("   v_0 = v_0,\n")
		file.write("   angle_0 = angle_0,\n")
		file.write("   omega(fixed = true))\n")
	elif model == 'GENSAL':
		file.write("  OpenIPSL.Electrical.Machines.PSSE.GENSAL machine(\n")
		file.write("   Tpd0 = %.4f,\n" % float(genlist.iloc[row,2]))
		file.write("   Tppd0 = %.4f,\n" % float(genlist.iloc[row,3]))
		file.write("   Tppq0 = %.4f,\n" % float(genlist.iloc[row,4]))
		file.write("   H = %.4f,\n" % float(genlist.iloc[row,5]))
		file.write("   D = %.4f,\n" % float(genlist.iloc[row,6]))
		file.write("   Xd = %.4f,\n" % float(genlist.iloc[row,7]))
		file.write("   Xq = %.4f,\n" % float(genlist.iloc[row,8]))
		file.write("   Xpd = %.4f,\n" % float(genlist.iloc[row,9]))
		file.write("   Xppd = %.4f,\n" % float(genlist.iloc[row,10]))
		file.write("   Xl = %.4f,\n" % float(genlist.iloc[row,11]))
		file.write("   S10 = %.4f,\n" % float(genlist.iloc[row,12]))
		file.write("   S12 = %.4f,\n" % float(genlist.iloc[row,13]))
		file.write("   Xppq = Xppd,\n")
		file.write("   Ra = 0,\n")
		file.write("   M_b = %.2f,\n" % Mb)
		file.write("   V_b = V_b,\n")
		file.write("   P_0 = P_0,\n")
		file.write("   Q_0 = Q_0,\n")
		file.write("   v_0 = v_0,\n")
		file.write("   angle_0 = angle_0)\n")
	elif model == 'GENSAE':
		file.write("  OpenIPSL.Electrical.Machines.PSSE.GENSAE machine(\n")
		file.write("   Tpd0 = %.4f,\n" % float(genlist.iloc[row,2]))
		file.write("   Tppd0 = %.4f,\n" % float(genlist.iloc[row,3]))
		file.write("   Tppq0 = %.4f,\n" % float(genlist.iloc[row,4]))
		file.write("   H = %.4f,\n" % float(genlist.iloc[row,5]))
		file.write("   D = %.4f,\n" % float(genlist.iloc[row,6]))
		file.write("   Xd = %.4f,\n" % float(genlist.iloc[row,7]))
		file.write("   Xq = %.4f,\n" % float(genlist.iloc[row,8]))
		file.write("   Xpd = %.4f,\n" % float(genlist.iloc[row,9]))
		file.write("   Xppd = %.4f,\n" % float(genlist.iloc[row,10]))
		file.write("   Xl = %.4f,\n" % float(genlist.iloc[row,11]))
		file.write("   S10 = %.4f,\n" % float(genlist.iloc[row,12]))
		file.write("   S12 = %.4f,\n" % float(genlist.iloc[row,13]))
		file.write("   Xppq = Xppd,\n")
		file.write("   Ra = 0,\n")
		file.write("   M_b = %.2f,\n" % Mb)
		file.write("   V_b = V_b,\n")
		file.write("   P_0 = P_0,\n")
		file.write("   Q_0 = Q_0,\n")
		file.write("   v_0 = v_0,\n")
		file.write("   angle_0 = angle_0)\n")
	elif model == 'GENROU':
		file.write("  OpenIPSL.Electrical.Machines.PSSE.GENROU machine(\n")
		file.write("   Tpd0 = %.4f,\n" % float(genlist.iloc[row,2]))
		file.write("   Tppd0 = %.4f,\n" % float(genlist.iloc[row,3]))
		file.write("   Tpq0 = %.4f,\n" % float(genlist.iloc[row,4]))
		file.write("   Tppq0 = %.4f,\n" % float(genlist.iloc[row,5]))
		file.write("   H = %.4f,\n" % float(genlist.iloc[row,6]))
		file.write("   D = %.4f,\n" % float(genlist.iloc[row,7]))
		file.write("   Xd = %.4f,\n" % float(genlist.iloc[row,8]))
		file.write("   Xq = %.4f,\n" % float(genlist.iloc[row,9]))
		file.write("   Xpd = %.4f,\n" % float(genlist.iloc[row,10]))
		file.write("   Xpq = %.4f,\n" % float(genlist.iloc[row,11]))
		file.write("   Xppd = %.4f,\n" % float(genlist.iloc[row,12]))
		file.write("   Xl = %.4f,\n" % float(genlist.iloc[row,13]))
		file.write("   S10 = %.4f,\n" % float(genlist.iloc[row,14]))
		file.write("   S12 = %.4f,\n" % float(genlist.iloc[row,15]))
		file.write("   Xppq = Xppd,\n")
		file.write("   Ra = 0,\n")
		file.write("   M_b = %.2f,\n" % Mb)
		file.write("   V_b = V_b,\n")
		file.write("   P_0 = P_0,\n")
		file.write("   Q_0 = Q_0,\n")
		file.write("   v_0 = v_0,\n")
		file.write("   angle_0 = angle_0)\n")
	elif model == 'GENROE':
		file.write("  OpenIPSL.Electrical.Machines.PSSE.GENROE machine(\n")
		file.write("   Tpd0 = %.4f,\n" % float(genlist.iloc[row,2]))
		file.write("   Tppd0 = %.4f,\n" % float(genlist.iloc[row,3]))
		file.write("   Tpq0 = %.4f,\n" % float(genlist.iloc[row,4]))
		file.write("   Tppq0 = %.4f,\n" % float(genlist.iloc[row,5]))
		file.write("   H = %.4f,\n" % float(genlist.iloc[row,6]))
		file.write("   D = %.4f,\n" % float(genlist.iloc[row,7]))
		file.write("   Xd = %.4f,\n" % float(genlist.iloc[row,8]))
		file.write("   Xq = %.4f,\n" % float(genlist.iloc[row,9]))
		file.write("   Xpd = %.4f,\n" % float(genlist.iloc[row,10]))
		file.write("   Xpq = %.4f,\n" % float(genlist.iloc[row,11]))
		file.write("   Xppd = %.4f,\n" % float(genlist.iloc[row,12]))
		file.write("   Xl = %.4f,\n" % float(genlist.iloc[row,13]))
		file.write("   S10 = %.4f,\n" % float(genlist.iloc[row,14]))
		file.write("   S12 = %.4f,\n" % float(genlist.iloc[row,15]))
		file.write("   Xppq = Xppd,\n")
		file.write("   Ra = 0,\n")
		file.write("   M_b = %.2f,\n" % Mb)
		file.write("   V_b = V_b,\n")
		file.write("   P_0 = P_0,\n")
		file.write("   Q_0 = Q_0,\n")
		file.write("   v_0 = v_0,\n")
		file.write("   angle_0 = angle_0)\n")
	file.write("  annotation(Placement(transformation(extent={{20,-10},{40,10}})));\n")
#=========================================================================================      
# Function: writeExc
# Authors: marcelofcastro        
# Description: It writes exciter model.
#=========================================================================================
def writeExc(dyrdata,result,file):
	# ----- Extract results:
	model = result[0]
	row = result[1]
	# ----- Extract list of models that match:
	if model != 'None':
		eslist = dyrdata[model]
	# ----- List of special models:
	list_01 = ['ESST4B']
	# ----- Test if we have exciter:
	if model == 'None':
		file.write("  //No exciter, so constant excitation will be used\n")
		file.write("  Modelica.Blocks.Sources.Constant uel(k=0) annotation(Placement(transformation(extent={{-40,-62},{-20,-42}})));\n")
		file.write("  Modelica.Blocks.Sources.Constant oel(k=0) annotation(Placement(transformation(extent={{-40,-94},{-20,-74}})));\n")
		file.write("  OpenIPSL.Electrical.Controls.PSSE.ES.ConstantExcitation exciter\n")
	elif model == 'ESAC1A':
		file.write("  Modelica.Blocks.Sources.Constant uel(k=0) annotation(Placement(transformation(extent={{-40,-62},{-20,-42}})));\n")
		file.write("  Modelica.Blocks.Sources.Constant oel(k=0) annotation(Placement(transformation(extent={{-40,-94},{-20,-74}})));\n")
		file.write("  OpenIPSL.Electrical.Controls.PSSE.ES.ESAC1A exciter(\n")
		file.write("   T_R = %.4f,\n" % float(eslist.iloc[row,2]))
		file.write("   T_B = %.4f,\n" % float(eslist.iloc[row,3]))
		file.write("   T_C = %.4f,\n" % float(eslist.iloc[row,4]))
		file.write("   K_A = %.4f,\n" % float(eslist.iloc[row,5]))
		file.write("   T_A = %.4f,\n" % float(eslist.iloc[row,6]))
		file.write("   V_AMAX = %.4f,\n" % float(eslist.iloc[row,7]))
		file.write("   V_AMIN = %.4f,\n" % float(eslist.iloc[row,8]))
		file.write("   T_E = %.4f,\n" % float(eslist.iloc[row,9]))
		file.write("   K_F = %.4f,\n" % float(eslist.iloc[row,10]))
		file.write("   T_F = %.4f,\n" % float(eslist.iloc[row,11]))
		file.write("   K_C = %.4f,\n" % float(eslist.iloc[row,12]))
		file.write("   K_D = %.4f,\n" % float(eslist.iloc[row,13]))
		file.write("   K_E = %.4f,\n" % float(eslist.iloc[row,14]))
		file.write("   E_1 = %.4f,\n" % float(eslist.iloc[row,15]))
		file.write("   S_EE_1 = %.4f,\n" % float(eslist.iloc[row,16]))
		file.write("   E_2 = %.4f,\n" % float(eslist.iloc[row,17]))
		file.write("   S_EE_1 = %.4f,\n" % float(eslist.iloc[row,18]))
		file.write("   V_RMAX = %.4f,\n" % float(eslist.iloc[row,19]))
		file.write("   V_RMIN = %.4f)\n" % float(eslist.iloc[row,20]))
	elif model == 'ESAC2A':
		file.write("  Modelica.Blocks.Sources.Constant uel(k=0) annotation(Placement(transformation(extent={{-40,-62},{-20,-42}})));\n")
		file.write("  Modelica.Blocks.Sources.Constant oel(k=0) annotation(Placement(transformation(extent={{-40,-94},{-20,-74}})));\n")
		file.write("  OpenIPSL.Electrical.Controls.PSSE.ES.ESAC2A exciter(\n")
		file.write("   T_R = %.4f,\n" % float(eslist.iloc[row,2]))
		file.write("   T_B = %.4f,\n" % float(eslist.iloc[row,3]))
		file.write("   T_C = %.4f,\n" % float(eslist.iloc[row,4]))
		file.write("   K_A = %.4f,\n" % float(eslist.iloc[row,5]))
		file.write("   T_A = %.4f,\n" % float(eslist.iloc[row,6]))
		file.write("   V_AMAX = %.4f,\n" % float(eslist.iloc[row,7]))
		file.write("   V_AMIN = %.4f,\n" % float(eslist.iloc[row,8]))
		file.write("   K_B = %.4f,\n" % float(eslist.iloc[row,9]))
		file.write("   V_RMAX = %.4f,\n" % float(eslist.iloc[row,10]))
		file.write("   V_RMIN = %.4f,\n" % float(eslist.iloc[row,11]))
		file.write("   T_E = %.4f,\n" % float(eslist.iloc[row,12]))
		file.write("   V_FEMAX = %.4f,\n" % float(eslist.iloc[row,13]))
		file.write("   K_H = %.4f,\n" % float(eslist.iloc[row,14]))
		file.write("   K_F = %.4f,\n" % float(eslist.iloc[row,15]))
		file.write("   T_F = %.4f,\n" % float(eslist.iloc[row,16]))
		file.write("   K_C = %.4f,\n" % float(eslist.iloc[row,17]))
		file.write("   K_D = %.4f,\n" % float(eslist.iloc[row,18]))
		file.write("   K_E = %.4f,\n" % float(eslist.iloc[row,19]))
		file.write("   E_1 = %.4f,\n" % float(eslist.iloc[row,20]))
		file.write("   S_EE_1 = %.4f,\n" % float(eslist.iloc[row,21]))
		file.write("   E_2 = %.4f,\n" % float(eslist.iloc[row,22]))
		file.write("   S_EE_1 = %.4f)\n" % float(eslist.iloc[row,23]))
	elif model == 'ESDC1A':
		file.write("  Modelica.Blocks.Sources.Constant uel(k=-Modelica.Constants.inf) annotation(Placement(transformation(extent={{-40,-62},{-20,-42}})));\n")
		file.write("  Modelica.Blocks.Sources.Constant oel(k=0) annotation(Placement(transformation(extent={{-40,-94},{-20,-74}})));\n")
		file.write("  OpenIPSL.Electrical.Controls.PSSE.ES.ESDC1A exciter(\n")
		file.write("   T_R = %.4f,\n" % float(eslist.iloc[row,2]))
		file.write("   K_A = %.4f,\n" % float(eslist.iloc[row,3]))
		file.write("   T_A = %.4f,\n" % float(eslist.iloc[row,4]))
		file.write("   T_B = %.4f,\n" % float(eslist.iloc[row,5]))
		file.write("   T_C = %.4f,\n" % float(eslist.iloc[row,6]))
		file.write("   V_RMAX = %.4f,\n" % float(eslist.iloc[row,7]))
		file.write("   V_RMIN = %.4f,\n" % float(eslist.iloc[row,8]))
		file.write("   K_E = %.4f,\n" % float(eslist.iloc[row,9]))
		file.write("   T_E = %.4f,\n" % float(eslist.iloc[row,10]))
		file.write("   K_F = %.4f,\n" % float(eslist.iloc[row,11]))
		file.write("   T_F1 = %.4f,\n" % float(eslist.iloc[row,12]))
		file.write("   E_1 = %.4f,\n" % float(eslist.iloc[row,14]))
		file.write("   S_EE_1 = %.4f,\n" % float(eslist.iloc[row,15]))
		file.write("   E_2 = %.4f,\n" % float(eslist.iloc[row,16]))
		file.write("   S_EE_1 = %.4f)\n" % float(eslist.iloc[row,17]))
	elif model == 'ESDC2A':
		file.write("  Modelica.Blocks.Sources.Constant uel(k=-Modelica.Constants.inf) annotation(Placement(transformation(extent={{-40,-62},{-20,-42}})));\n")
		file.write("  Modelica.Blocks.Sources.Constant oel(k=0) annotation(Placement(transformation(extent={{-40,-94},{-20,-74}})));\n")
		file.write("  OpenIPSL.Electrical.Controls.PSSE.ES.ESDC2A exciter(\n")
		file.write("   T_R = %.4f,\n" % float(eslist.iloc[row,2]))
		file.write("   K_A = %.4f,\n" % float(eslist.iloc[row,3]))
		file.write("   T_A = %.4f,\n" % float(eslist.iloc[row,4]))
		file.write("   T_B = %.4f,\n" % float(eslist.iloc[row,5]))
		file.write("   T_C = %.4f,\n" % float(eslist.iloc[row,6]))
		file.write("   V_RMAX = %.4f,\n" % float(eslist.iloc[row,7]))
		file.write("   V_RMIN = %.4f,\n" % float(eslist.iloc[row,8]))
		file.write("   K_E = %.4f,\n" % float(eslist.iloc[row,9]))
		file.write("   T_E = %.4f,\n" % float(eslist.iloc[row,10]))
		file.write("   K_F = %.4f,\n" % float(eslist.iloc[row,11]))
		file.write("   T_F1 = %.4f,\n" % float(eslist.iloc[row,12]))
		file.write("   E_1 = %.4f,\n" % float(eslist.iloc[row,14]))
		file.write("   S_EE_1 = %.4f,\n" % float(eslist.iloc[row,15]))
		file.write("   E_2 = %.4f,\n" % float(eslist.iloc[row,16]))
		file.write("   S_EE_1 = %.4f)\n" % float(eslist.iloc[row,17]))
	elif model == 'ESST1A':
		file.write("  Modelica.Blocks.Sources.Constant uel(k=-Modelica.Constants.inf) annotation(Placement(transformation(extent={{-40,-62},{-20,-42}})));\n")
		file.write("  Modelica.Blocks.Sources.Constant oel(k=0) annotation(Placement(transformation(extent={{-40,-94},{-20,-74}})));\n")
		file.write("  OpenIPSL.Electrical.Controls.PSSE.ES.ESST1A exciter(\n")
		file.write("   T_R = %.4f,\n" % float(eslist.iloc[row,2]))
		file.write("   V_IMAX = %.4f,\n" % float(eslist.iloc[row,3]))
		file.write("   V_IMIN = %.4f,\n" % float(eslist.iloc[row,4]))
		file.write("   T_C = %.4f,\n" % float(eslist.iloc[row,5]))
		file.write("   T_B = %.4f,\n" % float(eslist.iloc[row,6]))
		file.write("   T_C1 = %.4f,\n" % float(eslist.iloc[row,7]))
		file.write("   T_B1 = %.4f,\n" % float(eslist.iloc[row,8]))
		file.write("   K_A = %.4f,\n" % float(eslist.iloc[row,9]))
		file.write("   T_A = %.4f,\n" % float(eslist.iloc[row,10]))
		file.write("   V_AMAX = %.4f,\n" % float(eslist.iloc[row,11]))
		file.write("   V_AMIN = %.4f,\n" % float(eslist.iloc[row,12]))
		file.write("   V_RMAX = %.4f,\n" % float(eslist.iloc[row,13]))
		file.write("   V_RMIN = %.4f,\n" % float(eslist.iloc[row,14]))
		file.write("   K_C = %.4f,\n" % float(eslist.iloc[row,15]))
		file.write("   K_F = %.4f,\n" % float(eslist.iloc[row,16]))
		file.write("   T_F = %.4f,\n" % float(eslist.iloc[row,17]))
		file.write("   K_LR = %.4f,\n" % float(eslist.iloc[row,18]))
		file.write("   I_LR = %.4f)\n" % float(eslist.iloc[row,19]))
	elif model == 'ESST4B':
		file.write("  Modelica.Blocks.Sources.Constant uel(k=-Modelica.Constants.inf) annotation(Placement(transformation(extent={{-40,-62},{-20,-42}})));\n")
		file.write("  Modelica.Blocks.Sources.Constant oel(k=0) annotation(Placement(transformation(extent={{-40,-94},{-20,-74}})));\n")
		file.write("  OpenIPSL.Electrical.Controls.PSSE.ES.ESST4B exciter(\n")
		file.write("   T_R = %.4f,\n" % float(eslist.iloc[row,2]))
		file.write("   K_PR = %.4f,\n" % float(eslist.iloc[row,3]))
		file.write("   K_IR = %.4f,\n" % float(eslist.iloc[row,4]))
		file.write("   V_RMAX = %.4f,\n" % float(eslist.iloc[row,5]))
		file.write("   V_RMIN = %.4f,\n" % float(eslist.iloc[row,6]))
		file.write("   T_A = %.4f,\n" % float(eslist.iloc[row,7]))
		file.write("   K_PM = %.4f,\n" % float(eslist.iloc[row,8]))
		file.write("   K_IM = %.4f,\n" % float(eslist.iloc[row,9]))
		file.write("   V_MMAX = %.4f,\n" % float(eslist.iloc[row,10]))
		file.write("   V_MMIN = %.4f,\n" % float(eslist.iloc[row,11]))
		file.write("   K_G = %.4f,\n" % float(eslist.iloc[row,12]))
		file.write("   K_P = %.4f,\n" % float(eslist.iloc[row,13]))
		file.write("   K_I = %.4f,\n" % float(eslist.iloc[row,14]))
		file.write("   V_BMAX = %.4f,\n" % float(eslist.iloc[row,15]))
		file.write("   K_C = %.4f,\n" % float(eslist.iloc[row,16]))
		file.write("   X_L = %.4f,\n" % float(eslist.iloc[row,17]))
		file.write("   THETA_P = %.4f);\n" % float(eslist.iloc[row,18]))
	elif model == 'EXAC1':
		file.write("  Modelica.Blocks.Sources.Constant uel(k=0) annotation(Placement(transformation(extent={{-40,-62},{-20,-42}})));\n")
		file.write("  Modelica.Blocks.Sources.Constant oel(k=0) annotation(Placement(transformation(extent={{-40,-94},{-20,-74}})));\n")
		file.write("  OpenIPSL.Electrical.Controls.PSSE.ES.EXAC1 exciter(\n")
		file.write("   T_R = %.4f,\n" % float(eslist.iloc[row,2]))
		file.write("   T_B = %.4f,\n" % float(eslist.iloc[row,3]))
		file.write("   T_C = %.4f,\n" % float(eslist.iloc[row,4]))
		file.write("   K_A = %.4f,\n" % float(eslist.iloc[row,5]))
		file.write("   T_A = %.4f,\n" % float(eslist.iloc[row,6]))
		file.write("   V_RMAX = %.4f,\n" % float(eslist.iloc[row,7]))
		file.write("   V_RMIN = %.4f,\n" % float(eslist.iloc[row,8]))
		file.write("   T_E = %.4f,\n" % float(eslist.iloc[row,9]))
		file.write("   K_F = %.4f,\n" % float(eslist.iloc[row,10]))
		file.write("   T_F = %.4f,\n" % float(eslist.iloc[row,11]))
		file.write("   K_C = %.4f,\n" % float(eslist.iloc[row,12]))
		file.write("   K_D = %.4f,\n" % float(eslist.iloc[row,13]))
		file.write("   K_E = %.4f,\n" % float(eslist.iloc[row,14]))
		file.write("   E_1 = %.4f,\n" % float(eslist.iloc[row,15]))
		file.write("   S_EE_1 = %.4f,\n" % float(eslist.iloc[row,16]))
		file.write("   E_2 = %.4f,\n" % float(eslist.iloc[row,17]))
		file.write("   S_EE_1 = %.4f)\n" % float(eslist.iloc[row,18]))
	elif model == 'EXAC2':
		file.write("  Modelica.Blocks.Sources.Constant uel(k=0) annotation(Placement(transformation(extent={{-40,-62},{-20,-42}})));\n")
		file.write("  Modelica.Blocks.Sources.Constant oel(k=0) annotation(Placement(transformation(extent={{-40,-94},{-20,-74}})));\n")
		file.write("  OpenIPSL.Electrical.Controls.PSSE.ES.EXAC2 exciter(\n")
		file.write("   T_R = %.4f,\n" % float(eslist.iloc[row,2]))
		file.write("   T_B = %.4f,\n" % float(eslist.iloc[row,3]))
		file.write("   T_C = %.4f,\n" % float(eslist.iloc[row,4]))
		file.write("   K_A = %.4f,\n" % float(eslist.iloc[row,5]))
		file.write("   T_A = %.4f,\n" % float(eslist.iloc[row,6]))
		file.write("   V_AMAX = %.4f,\n" % float(eslist.iloc[row,7]))
		file.write("   V_AMIN = %.4f,\n" % float(eslist.iloc[row,8]))
		file.write("   K_B = %.4f,\n" % float(eslist.iloc[row,9]))
		file.write("   V_RMAX = %.4f,\n" % float(eslist.iloc[row,10]))
		file.write("   V_RMIN = %.4f,\n" % float(eslist.iloc[row,11]))
		file.write("   T_E = %.4f,\n" % float(eslist.iloc[row,12]))
		file.write("   K_L = %.4f,\n" % float(eslist.iloc[row,13]))
		file.write("   K_H = %.4f,\n" % float(eslist.iloc[row,14]))
		file.write("   K_F = %.4f,\n" % float(eslist.iloc[row,15]))
		file.write("   T_F = %.4f,\n" % float(eslist.iloc[row,16]))
		file.write("   K_C = %.4f,\n" % float(eslist.iloc[row,17]))
		file.write("   K_D = %.4f,\n" % float(eslist.iloc[row,18]))
		file.write("   V_LR = %.4f,\n" % float(eslist.iloc[row,19]))
		file.write("   K_E = %.4f,\n" % float(eslist.iloc[row,20]))
		file.write("   E_1 = %.4f,\n" % float(eslist.iloc[row,21]))
		file.write("   S_EE_1 = %.4f,\n" % float(eslist.iloc[row,22]))
		file.write("   E_2 = %.4f,\n" % float(eslist.iloc[row,23]))
		file.write("   S_EE_1 = %.4f)\n" % float(eslist.iloc[row,24]))
	elif model == 'EXNI':
		# switch parameter
		sw_fl = int(eslist.iloc[row,10])
		if sw_fl == 1:
			sw = "true"
		else:
			sw = "false"
		file.write("  Modelica.Blocks.Sources.Constant uel(k=0) annotation(Placement(transformation(extent={{-40,-62},{-20,-42}})));\n")
		file.write("  Modelica.Blocks.Sources.Constant oel(k=0) annotation(Placement(transformation(extent={{-40,-94},{-20,-74}})));\n")
		file.write("  OpenIPSL.Electrical.Controls.PSSE.ES.EXNI exciter(\n")
		file.write("   T_R = %.4f,\n" % float(eslist.iloc[row,2]))
		file.write("   K_A = %.4f,\n" % float(eslist.iloc[row,3]))
		file.write("   T_A = %.4f,\n" % float(eslist.iloc[row,4]))
		file.write("   V_RMAX = %.4f,\n" % float(eslist.iloc[row,5]))
		file.write("   V_RMIN = %.4f,\n" % float(eslist.iloc[row,6]))
		file.write("   K_F = %.4f,\n" % float(eslist.iloc[row,7]))
		file.write("   T_F1 = %.4f,\n" % float(eslist.iloc[row,8]))
		file.write("   T_F2 = %.4f,\n" % float(eslist.iloc[row,9]))
		file.write("   SWITCH = %s,\n" % sw)
		file.write("   r_cr_fd = %.4f)\n" % float(eslist.iloc[row,11]))
	elif model == 'EXST1':
		file.write("  Modelica.Blocks.Sources.Constant uel(k=0) annotation(Placement(transformation(extent={{-40,-62},{-20,-42}})));\n")
		file.write("  Modelica.Blocks.Sources.Constant oel(k=0) annotation(Placement(transformation(extent={{-40,-94},{-20,-74}})));\n")
		file.write("  OpenIPSL.Electrical.Controls.PSSE.ES.EXST1 exciter(\n")
		file.write("   T_R = %.4f,\n" % float(eslist.iloc[row,2]))
		file.write("   V_IMAX = %.4f,\n" % float(eslist.iloc[row,3]))
		file.write("   V_IMIN = %.4f,\n" % float(eslist.iloc[row,4]))
		file.write("   T_C = %.4f,\n" % float(eslist.iloc[row,5]))
		file.write("   T_B = %.4f,\n" % float(eslist.iloc[row,6]))
		file.write("   K_A = %.4f,\n" % float(eslist.iloc[row,7]))
		file.write("   T_A = %.4f,\n" % float(eslist.iloc[row,8]))
		file.write("   V_RMAX = %.4f,\n" % float(eslist.iloc[row,9]))
		file.write("   V_RMIN = %.4f,\n" % float(eslist.iloc[row,10]))
		file.write("   K_C = %.4f,\n" % float(eslist.iloc[row,11]))
		file.write("   K_F = %.4f,\n" % float(eslist.iloc[row,12]))
		file.write("   T_F = %.4f)\n" % float(eslist.iloc[row,13]))
	elif model == 'IEEET1':
		file.write("  Modelica.Blocks.Sources.Constant uel(k=0) annotation(Placement(transformation(extent={{-40,-62},{-20,-42}})));\n")
		file.write("  Modelica.Blocks.Sources.Constant oel(k=0) annotation(Placement(transformation(extent={{-40,-94},{-20,-74}})));\n")
		file.write("  OpenIPSL.Electrical.Controls.PSSE.ES.IEEET1 exciter(\n")
		file.write("   T_R = %.4f,\n" % float(eslist.iloc[row,2]))
		file.write("   K_A = %.4f,\n" % float(eslist.iloc[row,3]))
		file.write("   T_A = %.4f,\n" % float(eslist.iloc[row,4]))
		file.write("   V_RMAX = %.4f,\n" % float(eslist.iloc[row,5]))
		file.write("   V_RMIN = %.4f,\n" % float(eslist.iloc[row,6]))
		file.write("   K_E = %.4f,\n" % float(eslist.iloc[row,7]))
		file.write("   T_E = %.4f,\n" % float(eslist.iloc[row,8]))
		file.write("   K_F = %.4f,\n" % float(eslist.iloc[row,9]))
		file.write("   T_F = %.4f,\n" % float(eslist.iloc[row,10]))
		file.write("   E_1 = %.4f,\n" % float(eslist.iloc[row,12]))
		file.write("   S_EE_1 = %.4f,\n" % float(eslist.iloc[row,13]))
		file.write("   E_2 = %.4f,\n" % float(eslist.iloc[row,14]))
		file.write("   S_EE_1 = %.4f)\n" % float(eslist.iloc[row,15]))
	elif model == 'IEEET2':
		file.write("  Modelica.Blocks.Sources.Constant uel(k=0) annotation(Placement(transformation(extent={{-40,-62},{-20,-42}})));\n")
		file.write("  Modelica.Blocks.Sources.Constant oel(k=0) annotation(Placement(transformation(extent={{-40,-94},{-20,-74}})));\n")
		file.write("  OpenIPSL.Electrical.Controls.PSSE.ES.IEEET2 exciter(\n")
		file.write("   T_R = %.4f,\n" % float(eslist.iloc[row,2]))
		file.write("   K_A = %.4f,\n" % float(eslist.iloc[row,3]))
		file.write("   T_A = %.4f,\n" % float(eslist.iloc[row,4]))
		file.write("   V_RMAX = %.4f,\n" % float(eslist.iloc[row,5]))
		file.write("   V_RMIN = %.4f,\n" % float(eslist.iloc[row,6]))
		file.write("   K_E = %.4f,\n" % float(eslist.iloc[row,7]))
		file.write("   T_E = %.4f,\n" % float(eslist.iloc[row,8]))
		file.write("   K_F = %.4f,\n" % float(eslist.iloc[row,9]))
		file.write("   T_F1 = %.4f,\n" % float(eslist.iloc[row,10]))
		file.write("   T_F2 = %.4f,\n" % float(eslist.iloc[row,10]))
		file.write("   E_1 = %.4f,\n" % float(eslist.iloc[row,12]))
		file.write("   S_EE_1 = %.4f,\n" % float(eslist.iloc[row,13]))
		file.write("   E_2 = %.4f,\n" % float(eslist.iloc[row,14]))
		file.write("   S_EE_1 = %.4f)\n" % float(eslist.iloc[row,15]))
	elif model == 'IEEEX1':
		file.write("  Modelica.Blocks.Sources.Constant uel(k=0) annotation(Placement(transformation(extent={{-40,-62},{-20,-42}})));\n")
		file.write("  Modelica.Blocks.Sources.Constant oel(k=0) annotation(Placement(transformation(extent={{-40,-94},{-20,-74}})));\n")
		file.write("  OpenIPSL.Electrical.Controls.PSSE.ES.IEEEX1 exciter(\n")
		file.write("   T_R = %.4f,\n" % float(eslist.iloc[row,2]))
		file.write("   K_A = %.4f,\n" % float(eslist.iloc[row,3]))
		file.write("   T_A = %.4f,\n" % float(eslist.iloc[row,4]))
		file.write("   T_B = %.4f,\n" % float(eslist.iloc[row,5]))
		file.write("   T_C = %.4f,\n" % float(eslist.iloc[row,6]))
		file.write("   V_RMAX = %.4f,\n" % float(eslist.iloc[row,7]))
		file.write("   V_RMIN = %.4f,\n" % float(eslist.iloc[row,8]))
		file.write("   K_E = %.4f,\n" % float(eslist.iloc[row,9]))
		file.write("   T_E = %.4f,\n" % float(eslist.iloc[row,10]))
		file.write("   K_F = %.4f,\n" % float(eslist.iloc[row,11]))
		file.write("   T_F1 = %.4f,\n" % float(eslist.iloc[row,12]))
		file.write("   E_1 = %.4f,\n" % float(eslist.iloc[row,14]))
		file.write("   S_EE_1 = %.4f,\n" % float(eslist.iloc[row,15]))
		file.write("   E_2 = %.4f,\n" % float(eslist.iloc[row,16]))
		file.write("   S_EE_1 = %.4f)\n" % float(eslist.iloc[row,17]))
	elif model == 'SCRX':
		# switch parameter
		sw_fl = int(eslist.iloc[row,8])
		if sw_fl == 1:
			sw = "true"
		else:
			sw = "false"
		file.write("  Modelica.Blocks.Sources.Constant uel(k=0) annotation(Placement(transformation(extent={{-40,-62},{-20,-42}})));\n")
		file.write("  Modelica.Blocks.Sources.Constant oel(k=0) annotation(Placement(transformation(extent={{-40,-94},{-20,-74}})));\n")
		file.write("  OpenIPSL.Electrical.Controls.PSSE.ES.SCRX exciter(\n")
		file.write("   T_AT_B = %.4f,\n" % float(eslist.iloc[row,2]))
		file.write("   T_B = %.4f,\n" % float(eslist.iloc[row,3]))
		file.write("   K = %.4f,\n" % float(eslist.iloc[row,4]))
		file.write("   T_E = %.4f,\n" % float(eslist.iloc[row,5]))
		file.write("   E_MIN = %.4f,\n" % float(eslist.iloc[row,6]))
		file.write("   E_MAX = %.4f,\n" % float(eslist.iloc[row,7]))
		file.write("   SITCH = %s,\n" % sw)
		file.write("   r_cr_fd = %.4f)\n" % float(eslist.iloc[row,9]))
	elif model == 'SEXS':
		file.write("  Modelica.Blocks.Sources.Constant uel(k=0) annotation(Placement(transformation(extent={{-40,-62},{-20,-42}})));\n")
		file.write("  Modelica.Blocks.Sources.Constant oel(k=0) annotation(Placement(transformation(extent={{-40,-94},{-20,-74}})));\n")
		file.write("  OpenIPSL.Electrical.Controls.PSSE.ES.SEXS exciter(\n")
		file.write("   T_AT_B = %.4f,\n" % float(eslist.iloc[row,2]))
		file.write("   T_B = %.4f,\n" % float(eslist.iloc[row,3]))
		file.write("   K = %.4f,\n" % float(eslist.iloc[row,4]))
		file.write("   T_E = %.4f,\n" % float(eslist.iloc[row,5]))
		file.write("   E_MIN = %.4f,\n" % float(eslist.iloc[row,6]))
		file.write("   E_MAX = %.4f)\n" % float(eslist.iloc[row,7]))
	elif model == 'ST5B':
		file.write("  Modelica.Blocks.Sources.Constant uel(k=-Modelica.Constants.inf) annotation(Placement(transformation(extent={{-40,-62},{-20,-42}})));\n")
		file.write("  Modelica.Blocks.Sources.Constant oel(k=Modelica.Constants.inf) annotation(Placement(transformation(extent={{-40,-94},{-20,-74}})));\n")
		file.write("  OpenIPSL.Electrical.Controls.PSSE.ES.ST5B exciter(\n")
		file.write("   T_R = %.4f,\n" % float(eslist.iloc[row,2]))
		file.write("   T_C1 = %.4f,\n" % float(eslist.iloc[row,3]))
		file.write("   T_B1 = %.4f,\n" % float(eslist.iloc[row,4]))
		file.write("   T_C2 = %.4f,\n" % float(eslist.iloc[row,5]))
		file.write("   T_B2 = %.4f,\n" % float(eslist.iloc[row,6]))
		file.write("   K_R = %.4f,\n" % float(eslist.iloc[row,7]))
		file.write("   V_RMAX = %.4f,\n" % float(eslist.iloc[row,8]))
		file.write("   V_RMIN = %.4f,\n" % float(eslist.iloc[row,9]))
		file.write("   T_1 = %.4f,\n" % float(eslist.iloc[row,10]))
		file.write("   K_C = %.4f,\n" % float(eslist.iloc[row,11]))
		file.write("   T_UC1 = %.4f,\n" % float(eslist.iloc[row,12]))
		file.write("   T_UB1 = %.4f,\n" % float(eslist.iloc[row,13]))
		file.write("   T_UC2 = %.4f,\n" % float(eslist.iloc[row,14]))
		file.write("   T_UB2 = %.4f,\n" % float(eslist.iloc[row,15]))
		file.write("   T_OC1 = %.4f,\n" % float(eslist.iloc[row,16]))
		file.write("   T_OB1 = %.4f,\n" % float(eslist.iloc[row,17]))
		file.write("   T_OC2 = %.4f,\n" % float(eslist.iloc[row,18]))
		file.write("   I_OB2 = %.4f)\n" % float(eslist.iloc[row,19]))
	elif model == 'URST5T':
		file.write("  Modelica.Blocks.Sources.Constant uel(k=-Modelica.Constants.inf) annotation(Placement(transformation(extent={{-40,-62},{-20,-42}})));\n")
		file.write("  Modelica.Blocks.Sources.Constant oel(k=Modelica.Constants.inf) annotation(Placement(transformation(extent={{-40,-94},{-20,-74}})));\n")
		file.write("  OpenIPSL.Electrical.Controls.PSSE.ES.URST5T exciter(\n")
		file.write("   T_R = %.4f,\n" % float(eslist.iloc[row,2]))
		file.write("   T_C1 = %.4f,\n" % float(eslist.iloc[row,3]))
		file.write("   T_B1 = %.4f,\n" % float(eslist.iloc[row,4]))
		file.write("   T_C2 = %.4f,\n" % float(eslist.iloc[row,5]))
		file.write("   T_B2 = %.4f,\n" % float(eslist.iloc[row,6]))
		file.write("   KR = %.4f,\n" % float(eslist.iloc[row,7]))
		file.write("   V_RMAX = %.4f,\n" % float(eslist.iloc[row,8]))
		file.write("   V_RMIN = %.4f,\n" % float(eslist.iloc[row,9]))
		file.write("   T_1 = %.4f,\n" % float(eslist.iloc[row,10]))
		file.write("   K_C = %.4f)\n" % float(eslist.iloc[row,11]))
	
	if model not in list_01:
		file.write("    annotation(Placement(transformation(extent={{-16,-20},{4,0}})));\n")
#=========================================================================================      
# Function: connectExc
# Authors: marcelofcastro        
# Description: It connects exciters to machines.
#=========================================================================================
def connectExc(dyrdata,result,file):
	# ----- Extract results:
	model = result[0]
	row = result[1]
	# ----- List of Exciters by Group:
	# list 01: need additional inputs or different connection
	es_type_01 = ['ESST1A','ESST4B'] 
	# list 02: VT is an additional input
	es_type_02 = ['ESDC2A','ESST1A']
	# ----- Connect exciter:
	file.write("  connect(pss.VOTHSG, exciter.VOTHSG) annotation(Line(visible = true, points = {{-49, 0}, {-40, 0}, {-40, -5.663}, {-17, -5.663}, {-17, -6}}, color = {0,0,127}));")
	file.write("  connect(machine.XADFID, exciter.XADFID) annotation(Line(visible = true, points = {{41, -9}, {43.537, -9}, {43.537, -24.895}, {2, -24.895}, {2, -21}}, color = {0,0,127}));")
	file.write("  connect(machine.EFD0, exciter.EFD0) annotation(Line(visible = true, points = {{41, -5}, {46.015, -5}, {46.015, -27.845}, {-20, -27.845}, {-20, -14}, {-17, -14}}, color = {0,0,127}));")
	file.write("  connect(machine.ETERM, exciter.ECOMP) annotation(Line(visible = true, points = {{41, -3}, {50, -3}, {50, -30}, {-21.71, -30}, {-21.71, -10}, {-27, -10}}, color = {0,0,127}));")
	file.write("  connect(machine.EFD, exciter.EFD) annotation(Line(visible = true, points = {{18, -5}, {10, -5}, {10, -10}, {5, -10}}, color = {0,0,127}));")
	# ----- Test if we have exciter:
	if model not in es_type_01:
		file.write("  connect(uel.y,exciter.VUEL) annotation(Line(points={{-19,-52},{-10,-52},{-10,-21}}, color={0,0,127}));\n")
		file.write("  connect(oel.y,exciter.VOEL) annotation(Line(points={{-19,-84},{-6,-84},{-6,-21}}, color={0,0,127}));\n")
	#if model in es_type_02:
		#file.write("  connect(exciter.ECOMP,exciter.VT);")
#=========================================================================================      
# Function: writePss
# Authors: marcelofcastro        
# Description: It writes stabilizers model.
#=========================================================================================
def writePss(dyrdata,result,file):
	# ----- Extract results:
	model = result[0]
	row = result[1]
	# ----- Extract list of models that match:
	if model != 'None':
		stlist = dyrdata[model]
	# ----- Test if we have stabilizer:
	if model == 'None':
		file.write("  // No stabilizer, so disabled will be used\n")
		file.write("  OpenIPSL.Electrical.Controls.PSSE.PSS.DisabledPSS pss  annotation(Placement(transformation(extent = {{-70, -10}, {-50, 10}})));\n")
	else:
		file.write("  //Writing stabilizer:\n")
#=========================================================================================      
# Function: connectPss
# Authors: marcelofcastro        
# Description: It connects stabilizers to machines.
#=========================================================================================
def connectPss(dyrdata,result,file):
	# ----- Extract results:
	model = result[0]
	row = result[1]
	# ----- List of Exciters by Group:
	# ----- Test if we have exciter:
	#if model == 'None':
	#	file.write("  connect(machine.PMECH,machine.PMECH0);\n")
#=========================================================================================      
# Function: writeGov
# Authors: marcelofcastro        
# Description: It writes turbine-governor models.
#=========================================================================================
def writeGov(genpdata,index,dyrdata,result,file):
	# ----- Extract results:
	model = result[0]
	row = result[1]
	# ----- Extract list of models that match:
	if model != 'None':
		tglist = dyrdata[model]
	# ----- Test if we have governor:
	if model == 'None':
		file.write("  // No stabilizer, so disabled will be used:\n")
		file.write("  OpenIPSL.Electrical.Controls.PSSE.TG.ConstantPower governor \n")
	elif model == 'GAST':
		file.write("  OpenIPSL.Electrical.Controls.PSSE.TG.GAST governor(\n")
		file.write("   R = %.4f,\n" % float(tglist.iloc[row,2]))
		file.write("   T_1 = %.4f,\n" % float(tglist.iloc[row,3]))
		file.write("   T_2 = %.4f,\n" % float(tglist.iloc[row,4]))
		file.write("   T_3 = %.4f,\n" % float(tglist.iloc[row,5]))
		file.write("   AT = %.4f,\n" % float(tglist.iloc[row,6]))
		file.write("   K_T = %.4f,\n" % float(tglist.iloc[row,7]))
		file.write("   V_MAX = %.4f,\n" % float(tglist.iloc[row,8]))
		file.write("   V_MIN = %.4f,\n" % float(tglist.iloc[row,9]))
		file.write("   D_turb = %.4f)\n" % float(tglist.iloc[row,10]))
	elif model == 'GGOV1':
		file.write("  OpenIPSL.Electrical.Controls.PSSE.TG.GGOV1 governor(\n")
		file.write("   Rselect = %d,\n" % int(tglist.iloc[row,2]))
		file.write("   Flag = %d,\n" % int(tglist.iloc[row,3]))
		file.write("   R = %.4f,\n" % float(tglist.iloc[row,4]))
		file.write("   T_pelec = %.4f,\n" % float(tglist.iloc[row,5]))
		file.write("   maxerr = %.4f,\n" % float(tglist.iloc[row,6]))
		file.write("   minerr = %.4f,\n" % float(tglist.iloc[row,7]))
		file.write("   Kpgov = %.4f,\n" % float(tglist.iloc[row,8]))
		file.write("   Kigov = %.4f,\n" % float(tglist.iloc[row,9]))
		file.write("   Kdgov = %.4f,\n" % float(tglist.iloc[row,10]))
		file.write("   Tdgov = %.4f,\n" % float(tglist.iloc[row,11]))
		file.write("   Vmax = %.4f,\n" % float(tglist.iloc[row,12]))
		file.write("   Vmin = %.4f,\n" % float(tglist.iloc[row,13]))
		file.write("   Tact = %.4f,\n" % float(tglist.iloc[row,14]))
		file.write("   Kturb = %.4f,\n" % float(tglist.iloc[row,15]))
		file.write("   Wfnl = %.4f,\n" % float(tglist.iloc[row,16]))
		file.write("   Tb = %.4f,\n" % float(tglist.iloc[row,17]))
		file.write("   Tc = %.4f,\n" % float(tglist.iloc[row,18]))
		file.write("   Teng = %.4f,\n" % float(tglist.iloc[row,19]))
		file.write("   Tfload = %.4f,\n" % float(tglist.iloc[row,20]))
		file.write("   Kpload = %.4f,\n" % float(tglist.iloc[row,21]))
		file.write("   Kiload = %.4f,\n" % float(tglist.iloc[row,22]))
		file.write("   Ldref = %.4f,\n" % float(tglist.iloc[row,23]))
		file.write("   Dm = %.4f,\n" % float(tglist.iloc[row,24]))
		file.write("   Ropen = %.4f,\n" % float(tglist.iloc[row,25]))
		file.write("   Rclose = %.4f,\n" % float(tglist.iloc[row,26]))
		file.write("   Kimw = %.4f,\n" % float(tglist.iloc[row,27]))
		file.write("   Aset = %.4f,\n" % float(tglist.iloc[row,28]))
		file.write("   Ka = %.4f,\n" % float(tglist.iloc[row,29]))
		file.write("   Ta = %.4f,\n" % float(tglist.iloc[row,30]))
		file.write("   Trate = %.4f,\n" % float(tglist.iloc[row,31]))
		file.write("   db = %.4f,\n" % float(tglist.iloc[row,32]))
		file.write("   Tsa = %.4f,\n" % float(tglist.iloc[row,33]))
		file.write("   Tsb = %.4f,\n" % float(tglist.iloc[row,34]))
		file.write("   Rup = %.4f,\n" % float(tglist.iloc[row,35]))
		file.write("   Rdown = %.4f,\n" % float(tglist.iloc[row,36]))
		file.write("   DELT = 0.005)\n")
	elif model == 'GGOV1DU':
		file.write("  OpenIPSL.Electrical.Controls.PSSE.TG.GGOV1DU governor(\n")
		file.write("   Rselect = %d,\n" % int(tglist.iloc[row,2]))
		file.write("   Flag = %d,\n" % int(tglist.iloc[row,3]))
		file.write("   R = %.4f,\n" % float(tglist.iloc[row,4]))
		file.write("   T_pelec = %.4f,\n" % float(tglist.iloc[row,5]))
		file.write("   maxerr = %.4f,\n" % float(tglist.iloc[row,6]))
		file.write("   minerr = %.4f,\n" % float(tglist.iloc[row,7]))
		file.write("   Kpgov = %.4f,\n" % float(tglist.iloc[row,8]))
		file.write("   Kigov = %.4f,\n" % float(tglist.iloc[row,9]))
		file.write("   Kdgov = %.4f,\n" % float(tglist.iloc[row,10]))
		file.write("   Tdgov = %.4f,\n" % float(tglist.iloc[row,11]))
		file.write("   Vmax = %.4f,\n" % float(tglist.iloc[row,12]))
		file.write("   Vmin = %.4f,\n" % float(tglist.iloc[row,13]))
		file.write("   Tact = %.4f,\n" % float(tglist.iloc[row,14]))
		file.write("   Kturb = %.4f,\n" % float(tglist.iloc[row,15]))
		file.write("   Wfnl = %.4f,\n" % float(tglist.iloc[row,16]))
		file.write("   Tb = %.4f,\n" % float(tglist.iloc[row,17]))
		file.write("   Tc = %.4f,\n" % float(tglist.iloc[row,18]))
		file.write("   Teng = %.4f,\n" % float(tglist.iloc[row,19]))
		file.write("   Tfload = %.4f,\n" % float(tglist.iloc[row,20]))
		file.write("   Kpload = %.4f,\n" % float(tglist.iloc[row,21]))
		file.write("   Kiload = %.4f,\n" % float(tglist.iloc[row,22]))
		file.write("   Ldref = %.4f,\n" % float(tglist.iloc[row,23]))
		file.write("   Dm = %.4f,\n" % float(tglist.iloc[row,24]))
		file.write("   Ropen = %.4f,\n" % float(tglist.iloc[row,25]))
		file.write("   Rclose = %.4f,\n" % float(tglist.iloc[row,26]))
		file.write("   Kimw = %.4f,\n" % float(tglist.iloc[row,27]))
		file.write("   Aset = %.4f,\n" % float(tglist.iloc[row,28]))
		file.write("   Ka = %.4f,\n" % float(tglist.iloc[row,29]))
		file.write("   Ta = %.4f,\n" % float(tglist.iloc[row,30]))
		file.write("   Trate = %.4f,\n" % float(tglist.iloc[row,31]))
		file.write("   db = %.4f,\n" % float(tglist.iloc[row,32]))
		file.write("   Tsa = %.4f,\n" % float(tglist.iloc[row,33]))
		file.write("   Tsb = %.4f,\n" % float(tglist.iloc[row,34]))
		file.write("   Rup = %.4f,\n" % float(tglist.iloc[row,35]))
		file.write("   Rdown = %.4f,\n" % float(tglist.iloc[row,36]))
		file.write("   DELT = 0.005)\n")
	elif model == 'HYGOV':
		file.write("  OpenIPSL.Electrical.Controls.PSSE.TG.HYGOV governor(\n")
		file.write("   R = %.4f,\n" % float(tglist.iloc[row,2]))
		file.write("   r = %.4f,\n" % float(tglist.iloc[row,3]))
		file.write("   T_r = %.4f,\n" % float(tglist.iloc[row,4]))
		file.write("   T_f = %.4f,\n" % float(tglist.iloc[row,5]))
		file.write("   T_g = %.4f,\n" % float(tglist.iloc[row,6]))
		file.write("   VELM = %.4f,\n" % float(tglist.iloc[row,7]))
		file.write("   G_MAX = %.4f,\n" % float(tglist.iloc[row,8]))
		file.write("   G_MIN = %.4f,\n" % float(tglist.iloc[row,9]))
		file.write("   T_w = %.4f,\n" % float(tglist.iloc[row,10]))
		file.write("   A_t = %.4f,\n" % float(tglist.iloc[row,11]))
		file.write("   D_turb = %.4f,\n" % float(tglist.iloc[row,12]))
		file.write("   q_NL = %.4f)\n" % float(tglist.iloc[row,13]))
	elif model == 'IEEEG1':
		# Find P0 in per unit:
		# ----- Extract Mb:
		Mb = float(genpdata.iloc[index,9])
		# ----- Extract P0:
		P0 = float(genpdata.iloc[index,2])
		# ----- Calculate P0 in per unit:
		p0_pu = P0/Mb;
		file.write("  OpenIPSL.Electrical.Controls.PSSE.TG.IEEEG1 governor(\n")
		file.write("   P0 = %.6f,\n" % p0_pu)
		file.write("   K = %.4f,\n" % float(tglist.iloc[row,2]))
		file.write("   T_1 = %.4f,\n" % float(tglist.iloc[row,3]))
		file.write("   T_2 = %.4f,\n" % float(tglist.iloc[row,4]))
		file.write("   T_3 = %.4f,\n" % float(tglist.iloc[row,5]))
		file.write("   U_o = %.4f,\n" % float(tglist.iloc[row,6]))
		file.write("   U_c = %.4f,\n" % float(tglist.iloc[row,7]))
		file.write("   P_MAX = %.4f,\n" % float(tglist.iloc[row,8]))
		file.write("   P_MIN = %.4f,\n" % float(tglist.iloc[row,9]))
		file.write("   T_4 = %.4f,\n" % float(tglist.iloc[row,10]))
		file.write("   K_1 = %.4f,\n" % float(tglist.iloc[row,11]))
		file.write("   K_2 = %.4f,\n" % float(tglist.iloc[row,12]))
		file.write("   T_5 = %.4f,\n" % float(tglist.iloc[row,13]))
		file.write("   K_3 = %.4f,\n" % float(tglist.iloc[row,14]))
		file.write("   K_4 = %.4f,\n" % float(tglist.iloc[row,15]))
		file.write("   T_6 = %.4f,\n" % float(tglist.iloc[row,16]))
		file.write("   K_5 = %.4f,\n" % float(tglist.iloc[row,17]))
		file.write("   K_6 = %.4f,\n" % float(tglist.iloc[row,18]))
		file.write("   T_7 = %.4f,\n" % float(tglist.iloc[row,19]))
		file.write("   K_7 = %.4f,\n" % float(tglist.iloc[row,20]))
		file.write("   K_8 = %.4f)\n" % float(tglist.iloc[row,21]))
	elif model == 'IEESGO':
		file.write("  OpenIPSL.Electrical.Controls.PSSE.TG.IEESGO governor(\n")
		file.write("   T_1 = %.4f,\n" % float(tglist.iloc[row,2]))
		file.write("   T_2 = %.4f,\n" % float(tglist.iloc[row,3]))
		file.write("   T_3 = %.4f,\n" % float(tglist.iloc[row,4]))
		file.write("   T_4 = %.4f,\n" % float(tglist.iloc[row,5]))
		file.write("   T_5 = %.4f,\n" % float(tglist.iloc[row,6]))
		file.write("   T_6 = %.4f,\n" % float(tglist.iloc[row,7]))
		file.write("   K_1 = %.4f,\n" % float(tglist.iloc[row,8]))
		file.write("   K_2 = %.4f,\n" % float(tglist.iloc[row,9]))
		file.write("   K_3 = %.4f,\n" % float(tglist.iloc[row,10]))
		file.write("   P_MAX = %.4f,\n" % float(tglist.iloc[row,11]))
		file.write("   P_MIN = %.4f)\n" % float(tglist.iloc[row,12]))
	elif model == 'TGOV1':
		file.write("  OpenIPSL.Electrical.Controls.PSSE.TG.TGOV1 governor(\n")
		file.write("   R = %.4f,\n" % float(tglist.iloc[row,2]))
		file.write("   T_1 = %.4f,\n" % float(tglist.iloc[row,3]))
		file.write("   V_MAX = %.4f,\n" % float(tglist.iloc[row,4]))
		file.write("   V_MIN = %.4f,\n" % float(tglist.iloc[row,5]))
		file.write("   T_2 = %.4f,\n" % float(tglist.iloc[row,6]))
		file.write("   T_3 = %.4f,\n" % float(tglist.iloc[row,7]))
		file.write("   D_t = %.4f)\n" % float(tglist.iloc[row,8]))
	# placing turbine governors:
	file.write("    annotation(Placement(transformation(extent = {{-30, 20}, {-10, 40}})));\n")
#=========================================================================================      
# Function: connectGov
# Authors: marcelofcastro        
# Description: It connects turbine-governors to machines.
#=========================================================================================
def connectGov(dyrdata,result,file):
	# ----- Extract results:
	model = result[0]
	row = result[1]
	# ----- Test if we have exciter:
	file.write("  connect(governor.PMECH, machine.PMECH) annotation(Line(visible = true, points = {{-9, 30}, {10, 30}, {10, 5}, {18, 5}}, color = {0,0,127}));\n")
	file.write("  connect(machine.SPEED, governor.SPEED) annotation(Line(visible = true, points = {{41, 7}, {45.661, 7}, {45.661, 50}, {-34.805, 50}, {-34.805, 35.396}, {-28, 35.396}, {-28, 36}}, color = {0,0,127}));\n")
	file.write("  connect(machine.PMECH0, governor.PMECH0) annotation(Line(visible = true, points = {{41, 5}, {50, 5}, {50, 60}, {-40, 60}, {-40, 24}, {-28, 24}}, color = {0, 0, 127}));\n")
#=========================================================================================      
# Function: writeGenMo
# Authors: marcelofcastro        
# Description: It writes the generators package.
#=========================================================================================
def writeGenMo(gdir,pkg_name,pkg_ordr,sysdata,dyrdata):
	# ----- Extracting information from system
	gens = sysdata['gen'] # getting generator data
	ngens = len(gens) # getting number of generators
	# ----- Changing directory to system data directory:
	os.chdir(gdir)
	# ----- Creating machines package .mo file:
	packagemo = open(pkg_name,"w+")
	packagemo.write("within System;\n")
	packagemo.write("package Generators \"Library of machine models translated automatically from PSSE using Python_OpenIPSL.\" \n\n")
	packagemo.write("end Generators;")
	packagemo.close()
	# ----- Creating machines package .order file:
	packageorder = open(pkg_ordr,"w+")
	for ii in range(ngens):
		packageorder.write('Gen%d_%d\n' % ((ii+1),int(gens.iloc[ii,0])))
	packageorder.close()
	# ----- Writing each generator .mo file:
	for ii in range(len(gens)):
		genname = "Gen"+str((ii+1))+"_"+str(int(gens.iloc[ii,0]))
		genmo = open(genname+".mo","w+")
		genmo.write("within System.Generators;\n")
		genmo.write("model %s\n" % genname)
		genmo.write("  extends OpenIPSL.Electrical.Essentials.pfComponent;\n")
		genmo.write("  OpenIPSL.Interfaces.PwPin pin  annotation (Placement(transformation(extent={{100,-10},{120,10}})));\n")
		# Declaring machines:
		macresult = lookFor('machine',gens.iloc[ii,0],int(gens.iloc[ii,8]),dyrdata)
		writeMac(gens,ii,dyrdata,macresult,genmo)
		if macresult[0] != 'GENCLS':
			# Declaring exciters:
			excresult = lookFor('exciter',gens.iloc[ii,0],int(gens.iloc[ii,8]),dyrdata)
			writeExc(dyrdata,excresult,genmo)
			# Declaring stabilizers:
			pssresult = lookFor('stabilizer',gens.iloc[ii,0],int(gens.iloc[ii,8]),dyrdata)
			writePss(dyrdata,pssresult,genmo)
			# Declaring governors:
			govresult = lookFor('governor',gens.iloc[ii,0],int(gens.iloc[ii,8]),dyrdata)
			writeGov(gens,ii,dyrdata,govresult,genmo)
		# Starting connection:
		list_exc = ['ESST4B'] # list of exciters with an integrated voltage compensator
		genmo.write("equation\n")
		if macresult[0] != 'GENCLS':
			if excresult[0] in list_exc:
				genmo.write("  connect(machine.p,exciter.Gen_Terminal);\n") # connecting machine to pin if exciter has an integrated voltage compensator
				genmo.write("  connect(exciter.Bus,pin);\n") # connecting machine to pin if exciter has an integrated voltage compensator
			else:
				genmo.write("  connect(machine.p,pin)  annotation(Line(origin = {75, 0}, points = {{40, 0}, {110, 0}}, color = {0, 0, 255}));\n") # connecting machine to pin if no voltage compensator is present
		else:
			genmo.write("  connect(machine.p,pin)  annotation(Line(origin = {75, 0}, points = {{40, 0}, {110, 0}}, color = {0, 0, 255}));\n") # connecting machine to pin if GENCLS
		
		if macresult[0] != 'GENCLS':
			# Declaring Compensators
			connectExc(dyrdata,excresult,genmo) # connecting exciter to machine
			connectPss(dyrdata,pssresult,genmo) # connecting pss to machine
			connectGov(dyrdata,govresult,genmo) # connecting turbine-governor to machine
		# Create icon for generator:
		genmo.write("  annotation (\n")
		genmo.write("    Icon(coordinateSystem(\n")
		genmo.write("           extent={{-100,-100},{100,100}},\n")
		genmo.write("           preserveAspectRatio=false, grid={1,1}),\n")
		genmo.write("         graphics={Line(\n")
		genmo.write("           points={{-76,-26},{-28,52},{27,-52},{74,23}},\n")
		genmo.write("           color={0,0,255},\n")
		genmo.write("           smooth=Smooth.Bezier), Ellipse(extent={{-100,-100},{100,100}},\n")
		genmo.write("           lineColor={0,0,255})}));\n")
		# End model:
		genmo.write("end %s;" % genname)
#=========================================================================================      
# Function: writeMo
# Authors: marcelofcastro       
# Description: It uses the data from readRaw and readDyr to build the system in Modelica.
#=========================================================================================
def writeMo(wdir,sdir,ddir,gdir,system_base,system_frequency,sysdata,dyrdata):
	# ----- Initializing file name:
	networkname = "power_grid"
	pkg_name = "package.mo"
	pkg_ordr = "package.order"
	# ----- Writing System Package:
	writeSysMo(sdir,pkg_name,pkg_ordr,networkname,sysdata,system_frequency,system_base)
	# ----- Writing System Data Package:
	writeDataMo(ddir,pkg_name,pkg_ordr,sysdata)
	# ----- Writing Generator Data:
	writeGenMo(gdir,pkg_name,pkg_ordr,sysdata,dyrdata)

