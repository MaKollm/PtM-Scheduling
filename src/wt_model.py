import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

from windpowerlib import ModelChain, WindTurbine, create_power_curve

import openmeteo_requests
import requests_cache
from retry_requests import retry
import warnings


class WT:

	def __init__(self,param):
		self.param = param
		self.roughnessLength = param.param["wt"]["roughnessLength"]
		self.turbineType = param.param["wt"]["turbineType"]
		self.hubHeight = param.param["wt"]["hubHeight"]
		self.powerOfSystem = param.param['wt']['powerOfSystem']
		self.powerOfModule = param.param['wt']['powerOfTurbine']
		self.strWTLat = param.param["wt"]["strWTLat"]
		self.strWTLon = param.param["wt"]["strWTLon"]

		self.numberOfUncertaintySamples = param.param["wt"]["numberOfUncertaintySamples"]
		self.pathWTData = param.param['controlParameters']['pathWTData']
		self.covScalarPowerOutput = param.param["wt"]["covScalarPowerOutput"]
		self.covWeatherData = param.param["wt"]["covWeatherData"]
		self.startDateToCalcUncertainty = param.param["wt"]["startDateToCalcUncertainty"]
		self.stopDateToCalcUncertainty = param.param["wt"]["stopDateToCalcUncertainty"]


		self.online_weather_data = None
		self.weather_data_noisy = None
		self.csv_weather_data = None
		self.weather_data = None

		self.funcLoadCSV()


	def funcUpdate(self, param, iteration):
		self.param = param

		self.funcGetOnlineData()

		# choose weather data
		if self.param.param['controlParameters']['useRealForecast']:
			self.weather_data = self.online_weather_data
		else:
			self.weather_data = self.csv_weather_data

		# calculate uncertainties
		if param.param["controlParameters"]["use_wtUncertainty"]:
			self.funcCalcUncertaintyWeather(plot=False, correctWeather=False)
			if param.param["controlParameters"]["wtUncertainty"] == "weather_noise":
				self.funcAddNoiseWeather(useSigmaFrame=False)
				self.weather_data = self.weather_data_noisy
			elif param.param["controlParameters"]["wtUncertainty"] == "weather_forecast":
				self.funcAddNoiseWeather(useSigmaFrame=True)
				self.weather_data = self.weather_data_noisy

		self.funcCreatePowerData(use_csv= not self.param.param['controlParameters']['useRealForecast'], use_wtUncertainty=self.param.param['controlParameters']['use_wtUncertainty'])

		if param.param["controlParameters"]["use_wtUncertainty"] and param.param["controlParameters"]["wtUncertainty"] == "power_noise":
			self.funcAddNoisePowerOutput()
			self.powerOutput = self.powerOutputNoisy

		# timestamps are saved in param
		start = self.param.param["controlParameters"]["startTimeIteration"]
		end = start + pd.Timedelta(hours = self.param.param["controlParameters"]["optimizationHorizon"] - 1)

		if param.param["controlParameters"]["considerWT"]:
			#print(self.powerOutput.index[0])
			self.arrPowerAvailable = self.powerOutput[start:end].to_numpy()
		else:
			self.arrPowerAvailable = np.zeros(len(self.powerOutput))


		if len(self.arrPowerAvailable) < self.param.param["controlParameters"]["numberOfTimeSteps"]:
			raise Exception("Error: The start time and the time of the weather forecast or the historical weather data do not match")





	def funcLoadCSV(self):
		# Weather
		weather_data = pd.read_csv(self.param.param['controlParameters']['pathWTData'] + r"\open-meteo-49.10N8.45E125m.csv", skiprows=3,index_col=0)

		poa_data = pd.DataFrame(columns= pd.MultiIndex.from_tuples([('temperature',"2"),('wind_speed',"10"),('wind_speed',"100"),('wind_direction',"10"),('wind_direction',"100")]),
		index=weather_data.index)


		poa_data.loc[:,('temperature',"2")] = weather_data['temperature_2m (°C)'] + self.param.param['T0']
		poa_data.loc[:,('wind_speed',"10")] = weather_data['wind_speed_10m (m/s)']
		poa_data.loc[:, ('wind_speed', "100")] = weather_data['wind_speed_100m (m/s)']
		poa_data.loc[:, ('wind_direction', "10")] = weather_data['wind_direction_10m (°)']
		poa_data.loc[:, ('wind_direction', "100")] = weather_data['wind_direction_100m (°)']
		poa_data.index = pd.to_datetime(poa_data.index, format="%Y-%m-%dT%H:%M")
		if poa_data.index[0].minute != 0 or poa_data.index[0].second != 0 or poa_data.index[0].microsecond != 0:
			poa_data.index = pd.date_range(start=poa_data.index[0] - pd.Timedelta(minutes=poa_data.index[0].minute,seconds= poa_data.index[0].second,microseconds = poa_data.index[0].microsecond), periods=len(poa_data), freq='h')

		self.csv_weather_data = poa_data


	#get data from open-meteo:  wind_speed and temperature at different heights
	def funcGetOnlineData(self):

		# Setup the Open-Meteo API client with cache and retry on error
		cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
		retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
		openmeteo = openmeteo_requests.Client(session = retry_session)

		# Make sure all required weather variables are listed here
		# The order of variables in hourly or daily is important to assign them correctly below
		url = "https://api.open-meteo.com/v1/forecast"
		specs = {
			"latitude": float(self.strWTLat),
			"longitude": float(self.strWTLon),
			"hourly": ["wind_speed_80m", "wind_speed_120m", "wind_speed_180m", "temperature_80m", "temperature_120m", "temperature_180m","wind_direction_80m", "wind_direction_120m", "wind_direction_180m"],
			"wind_speed_unit": "ms",
			"timezone": "Europe/Berlin"
		}

		#request parameters
		responses = openmeteo.weather_api(url, params=specs)

		#hopurly data to numpy
		response = responses[0]
		hourly = response.Hourly()
		hourly_wind_speed_80m = hourly.Variables(0).ValuesAsNumpy()
		hourly_wind_speed_120m = hourly.Variables(1).ValuesAsNumpy()
		hourly_wind_speed_180m = hourly.Variables(2).ValuesAsNumpy()
		hourly_temperature_80m = hourly.Variables(3).ValuesAsNumpy() + self.param.param['T0']
		hourly_temperature_120m = hourly.Variables(4).ValuesAsNumpy() + self.param.param['T0']
		hourly_temperature_180m = hourly.Variables(5).ValuesAsNumpy() + self.param.param['T0']
		hourly_wind_direction_80m = hourly.Variables(6).ValuesAsNumpy()
		hourly_wind_direction_120m = hourly.Variables(7).ValuesAsNumpy()
		hourly_wind_direction_180m = hourly.Variables(8).ValuesAsNumpy()

		#data to pandas Dataframe

		index =pd.date_range(
			start = pd.to_datetime(hourly.Time(), unit = "s", utc = True).tz_convert("Europe/Berlin").tz_localize(None),
			end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True).tz_convert("Europe/Berlin").tz_localize(None),
			freq = pd.Timedelta(seconds = hourly.Interval()),
			inclusive = "left"
		)


		result = pd.DataFrame(
			{
			"date": index,
			("wind_speed", "80"): hourly_wind_speed_80m,
			("wind_speed", "120"): hourly_wind_speed_120m,
			("wind_speed", "180"): hourly_wind_speed_180m,
			("wind_direction", "80"): hourly_wind_direction_80m,
			("wind_direction", "120"): hourly_wind_direction_120m,
			("wind_direction", "180"): hourly_wind_direction_180m,
			("temperature", "80"): hourly_temperature_80m,
			("temperature", "120"): hourly_temperature_120m,
			("temperature", "180"): hourly_temperature_180m
			}
		).set_index("date")

		result.columns = pd.MultiIndex.from_tuples(result.columns)
		
		self.online_weather_data = result


	#creates powerdata and saves it as pd.Series
	def funcCreatePowerData(self, use_csv = False, use_wtUncertainty = False):

		#ignore wind_direction - maybe use it later for corrections(dependent of turbine angle)
		#weather_dict = {"online" : self.online_weather_data, "online_noisy" : self.online_weather_data_noisy, "csv": self.csv_weather_data}
		weather = self.weather_data[["wind_speed","temperature"]].copy()

		#add constant roughness length to the dataframe - not noticeably applied 
		weather["roughness_length"] = self.roughnessLength
		
		#define the turbine (can also be done with individual turbine with specific power curve)
		turbine_specs = {"turbine_type":self.turbineType, "hub_height":self.hubHeight}  #turbine type as in oedb turbine library

		#initialize WindTurbine object
		turbine = WindTurbine(**turbine_specs)

		#change modelchain parameters if wanted
		modelchain_data = {
	    'wind_speed_model': 'logarithmic',      # 'logarithmic' (default),
	                                            # 'hellman' or
	                                            # 'interpolation_extrapolation'
	    'density_model': 'barometric',           # 'barometric' (default), 'ideal_gas'
	                                            #  or 'interpolation_extrapolation'
	    'temperature_model': 'linear_gradient', # 'linear_gradient' (def.) or
	                                            # 'interpolation_extrapolation'
	    'power_output_model':
	        'power_curve',          # 'power_curve' (default) or
	                                            # 'power_coefficient_curve'
	    'density_correction': False,             # False (default) or True
	    'obstacle_height': 0,                   # default: 0
	    'hellman_exp': None                    # None (default) or None
	    }

		modelChain = ModelChain(turbine,**modelchain_data).run_model(weather)

		self.powerOutput = modelChain.power_output.rename("Power [kW]") * self.param.param['wt']['powerOfSystem'] / self.param.param['wt']['powerOfTurbine'] / 1000
		self.powerOutput.index = pd.to_datetime(self.powerOutput.index, format="%Y%m%d:%H%M")

	########## Uncertainty ##########

	#add normal distributed noise to each entry of the powerOutput array and save it as different pd.Series
	def funcAddNoisePowerOutput(self):
		l = len(self.powerOutput)
		cov = np.zeros((l,l))
		for i in range(l):
			cov[i][i] = self.covScalarPowerOutput

		samples = np.random.multivariate_normal(self.powerOutput.to_numpy(), cov, size=1)
		self.powerOutputNoisy = (self.powerOutput.copy(deep=True)*0 + samples[0]).rename("Power + Noise [MW]")
		#fix negative values
		mask = self.powerOutputNoisy <0
		self.powerOutputNoisy[mask]  =0


	#add normal distributed noise to each of the weather data columns
	def funcAddNoiseWeather(self, useSigmaFrame = False):
		weather = self.weather_data.copy(deep=True)
		if useSigmaFrame == False:
			#iterate through all columns and sub columns
			for key1 in self.covWeatherData:
				for key2 in self.covWeatherData[key1]:
					series = weather[key1][key2]
					l = len(series)
					cov = np.zeros((l,l))
					for i in range(l):
						cov[i][i] = self.covWeatherData[key1][key2]

					samples = np.random.multivariate_normal(series.to_numpy(), cov, size=1)
					weather.loc[weather[key1][key2] > 0.01,(key1,key2)] = samples[0][weather[key1][key2] > 0.01].astype(np.float32)

		else:
			for key1 in ["wind_speed","wind_direction","temperature"]:
				for key2 in ["80","120","180"]:
					sigma = self.weather_data.loc[:,"sigma_"+key1].to_numpy()[0]
					series = weather[key1][key2]
					cov = np.identity(len(series)) *sigma
					samples = np.random.multivariate_normal(series.to_numpy(), cov, size=1)
					weather.loc[weather[key1][key2] > 0.01,(key1,key2)] = samples[0][weather[key1][key2] > 0.01].astype(np.float32)


		self.weather_data_noisy = weather
		#fix negative values
		mask = self.weather_data_noisy < 0
		self.weather_data_noisy[mask] = 0


	#calculate uncertainty and mean correction for wind_speed, temperature and wind_direction as difference between forecast and actual data- calculate only from 2m value for temperature, 10m for wind values, since historical data only contain these values
	def funcCalcUncertaintyWeather(self, plot = False, correctWeather = True):

		#get archived forecast data
		cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
		retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
		openmeteo = openmeteo_requests.Client(session = retry_session)

		url = "https://historical-forecast-api.open-meteo.com/v1/forecast"
		specs = {
			"latitude": float(self.strWTLat),
			"longitude": float(self.strWTLon),
			"start_date": self.startDateToCalcUncertainty.strftime("%Y-%m-%d"),
			"end_date": self.stopDateToCalcUncertainty.strftime("%Y-%m-%d"),
			"hourly": ["wind_speed_10m","wind_direction_10m","temperature_2m"],
			"timezone": "Europe/Berlin"
		}

		responses = openmeteo.weather_api(url, params=specs)

		#hopurly data to numpy
		response = responses[0]
		hourly = response.Hourly()
		hourly_wind_speed_10m_hist_forecast = hourly.Variables(0).ValuesAsNumpy()
		hourly_wind_direction_10m_hist_forecast = hourly.Variables(1).ValuesAsNumpy()
		temperature_2m_hist_forecast = hourly.Variables(2).ValuesAsNumpy() + self.param.param['T0']
		

		#get historical data - specs are the same
		url = "https://archive-api.open-meteo.com/v1/archive"

		responses = openmeteo.weather_api(url, params=specs)

		#hourly data to numpy
		response = responses[0]
		hourly = response.Hourly()
		hourly_wind_speed_10m_hist = hourly.Variables(0).ValuesAsNumpy()
		hourly_wind_direction_10m_hist = hourly.Variables(1).ValuesAsNumpy()
		temperature_2m_hist = hourly.Variables(2).ValuesAsNumpy() + self.param.param['T0']

		wind_speed_diff = hourly_wind_speed_10m_hist_forecast-hourly_wind_speed_10m_hist
		wind_direction_diff = hourly_wind_direction_10m_hist_forecast-hourly_wind_direction_10m_hist
		temp_diff = temperature_2m_hist_forecast-temperature_2m_hist


		#gauss fit the difference histograms - get mu and sigma for each array - plot the curves if plot = True
		nbins = 81 #try different number of bins if fit does not work
		array_fit_parameters = []

		if plot:
			fig,axs = plt.subplots(nrows=1,ncols=3,figsize=(4.7*2,5))

		
		def gauss_function(x, A,mu, sigma):
			return A * np.exp(-(x - mu)**2 / (2 * sigma**2))

		def curve_fit_adv(array,nbins):
			ydata, bins  = np.histogram(array,bins=nbins)
			xdata = bins[0:nbins] + 0.5 * (bins[1]-bins[0]) #mitte der bins
			popt, pcov,infodict, mesg, ier = curve_fit(gauss_function, xdata, ydata,full_output=True)
			if ier != 1:
				popt, pcov, xdata, ydata = curve_fit_adv(array,nbins+1)
			return popt, pcov, xdata, ydata

		for i,array in enumerate([wind_speed_diff,wind_direction_diff,temp_diff]):
			with warnings.catch_warnings():
				warnings.simplefilter("ignore")
				popt, pcov, xdata, ydata = curve_fit_adv(array,nbins)
			popt[2] = abs(popt[2])
			array_fit_parameters.append([popt[1],popt[2]])
			

			if plot: #show fit_curves if plot = True
				axs[i].plot(xdata,ydata, label ="data")
				axs[i].plot(xdata, gauss_function(xdata,*popt), label = r"$\mu = {:.3f},\sigma = {:.3f}$".format(popt[1],popt[2]))
				axs[i].legend()

		if plot:
			axs[0].set_title("wind_speed_10m")
			axs[1].set_title("wind_direction_10m")
			axs[2].set_title("temperature_2m")
			fig.suptitle("Gauss fitted difference of forecast and historical data "+self.startDateToCalcUncertainty.strftime("%d.%m.%Y")+"-" +self.stopDateToCalcUncertainty.strftime("%d.%m.%Y"))
			plt.legend()
			plt.show()


		array_fit_parameters = np.array(array_fit_parameters)

		#use array_fit_parameters (mu) to correct the weather data with the most common deviation
		#values should not be negative
		if correctWeather:
			wdat = ["wind_speed","wind_direction","temperature"]
			for i in range(3):
				for key in ["80","120","180"]:
					self.weather_data.loc[:,(wdat[i],key)] = self.weather_data.loc[:,(wdat[i],key)] - array_fit_parameters[i][0]
		#correct negative values
		mask = self.weather_data < 0
		self.weather_data[mask] = 0

		
		for i,key in enumerate(["wind_speed","wind_direction","temperature"]):
			self.weather_data.loc[:,"mu_"+key] = float(array_fit_parameters[i][0])
			self.weather_data.loc[:,"sigma_"+key] = float(array_fit_parameters[i][1])
		

		

	

