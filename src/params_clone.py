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
		self.param["pv"]["covScalarPowerOutput"] = 1e+04
		self.param["pv"]["covWeatherData"] = {'poa_global':100, 'poa_direct':100, 'poa_diffuse':100, 'temp_air':100, 'wind_speed':100}

		#controlParameters
		self.param["controlParameters"] = {}
		self.param["controlParameters"]["numHoursToSimulate"] = 24*7 #number of hours to simulate
		self.param["controlParameters"]["pathPVData"] = r""#folder of PV data
		self.param['controlParameters']['considerPV'] = True
		self.param['controlParameters']['pathPPData'] = r""
		

		#newControlParameters
		self.param["controlParameters"]["start_time"] = pd.Timestamp("2025-06-04 12:20")#start time for simulation (next higher array entry is used)
		
		self.param["controlParameters"]["startDateToCalcUncertainty"] = pd.Timestamp("2024-01-01")
		self.param["controlParameters"]["stopDateToCalcUncertainty"] = pd.Timestamp("2025-04-30")
		self.param['controlParameters']['considerWT'] = True

		#excludedControlParameters
		self.param["controlParameters"]["numberOfTimeSteps"] = 24*7
		self.param['controlParameters']['timeStep'] = 1

		#Prices
		self.param["prices"] = {}
		self.param['prices']['numberOfUncertaintySamples'] = 100

		#wt parameters
		self.param["wt"] = {}
		self.param["wt"]["strWtLat"] = "49.09"
		self.param["wt"]["strWtLon"] = "8.44"
		self.param["wt"]["roughnessLength"] = 2 #find true value for actual coordinates
		self.param["wt"]["turbineType"] = "E-126/4200" #as in oedb turbine library
		self.param["wt"]["hubHeight"] = 135 #in m
		self.param['wt']['numberOfUncertaintySamples'] = 100
		self.param["wt"]["covScalarPowerOutput"] = 1e+10
		self.param["wt"]["covWeatherData"] = {"wind_speed": {"80":1 , "120":1 , "180":1}, "wind_direction": {"80": 1 , "120": 1 , "180": 1}, "temperature": {"80":1 , "120": 1, "180":1}}

		#pp parameters
		self.param["pp"] = {}
		self.param["pp"]["covScalarPowerPrice"] = 1e+08

