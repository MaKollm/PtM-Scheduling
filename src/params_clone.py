""" 
trimmed version of class Param (values may be changed), is used to test pvlib and electricity_price class methods

"""
import pandas as pd

class Param():
	def __init__(self):

		#pv parameters 
		self.param = {}
		self.param['pv'] = {}
		self.param['pv']['module'] = 'Canadian_Solar_CS5P_220M___2009_'
		self.param['pv']['inverter'] = 'ABB__PVI_3_0_OUTD_S_US__208V_'
		self.param['pv']['powerOfModule'] = 0.22
		self.param['pv']['powerOfSystem'] = 4427 
		self.param['pv']['numberOfUncertaintySamples'] = 100
		self.param['pv']['alpha'] = 0.9
		self.param['pv']['covariance'] = 8

		#new pv parameters
		self.param["pv"]["strPvLat"] = "49.09"
		self.param["pv"]["strPvLon"] = "8.44"

		#controlParameters
		self.param["controlParameters"] = {}
		self.param["controlParameters"]["numHoursToSimulate"] = 24*7 #number of hours to simulate
		self.param["controlParameters"]["pathPVData"] = r""#folder of PV data
		self.param['controlParameters']['considerPV'] = True
		self.param['controlParameters']['pathPPData'] = r""
		

		#newControlParameters
		self.param["controlParameters"]["start_time"] = pd.Timestamp("2023-01-10 12:20")#start time for simulation (next higher array entry is used)

		#excludedControlParameters
		self.param["controlParameters"]["numberOfTimeSteps"] = 24*7
		self.param['controlParameters']['timeStep'] = 1

		#Prices
		self.param["prices"] = {}
		self.param['prices']['numberOfUncertaintySamples'] = 100

