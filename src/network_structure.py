#====================================================================================      
# Authors: marcelofcastro        
# Description: Definition of classes for network structure. 
#====================================================================================
class Node:
	def __init__(self, busOrdr, busNmbr, busName, busKV, busType, busVoltage, busAngle):
		self.busOrdr = busOrdr
		self.busNmbr = busNmbr
		self.busName = busName
		self.busKV = busKV
		self.busType = busType
		self.busVoltage = busVoltage
		self.busAngle = busAngle
