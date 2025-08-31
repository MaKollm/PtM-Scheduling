#!/usr/bin/env python3.10


import pvlib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
from scipy.io import savemat

from pvlib.location import Location
from pvlib.modelchain import ModelChain
from pvlib.temperature import TEMPERATURE_MODEL_PARAMETERS
from pvlib.pvsystem import PVSystem

import openmeteo_requests
import requests_cache
from retry_requests import retry
from scipy.optimize import curve_fit
import warnings

########################
########## PV ##########

# This class creates the data for the pv module. It uses the pvlib-package from python and calculates the power of a specific pv-system
# at a chosen loaction with historic weather data such as wind, irradiation and temperature. It also takes a lot of other factors into
# account. For more information visit https://pvlib-python.readthedocs.io/en/stable/user_guide/package_overview.html

# Quelle re.jrc.ec.europa.eu

class PV:
    def __init__(self, param):
        self.param = param
        self.strModule = self.param.param['pv']['module']
        self.strInverter = self.param.param['pv']['inverter']
        self.powerOfSystem = param.param['pv']['powerOfSystem']
        self.powerOfModule = param.param['pv']['powerOfModule']
        self.strPvLat = self.param.param["pv"]["strPvLat"]
        self.strPvLon = self.param.param["pv"]["strPvLon"]

        self.iNumberUncertaintySamples = self.param.param['pv']['numberOfUncertaintySamples']
        self.pathPVData = param.param['controlParameters']['pathPVData']
        self.covScalarPowerOutput = param.param["pv"]["covScalarPowerOutput"]
        self.covWeatherData = param.param["pv"]["covWeatherData"]

        self.startDateToCalcUncertainty = param.param["pv"]["startDateToCalcUncertainty"]
        self.stopDateToCalcUncertainty = param.param["pv"]["stopDateToCalcUncertainty"]

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
        if param.param["controlParameters"]["use_pvUncertainty"]:
            self.funcCalcUncertaintyWeather(plot=False, correctWeather=False)
            if param.param["controlParameters"]["pvUncertainty"] == "weather_noise":
                self.funcAddNoiseWeather(useSigmaFrame = False)
                self.weather_data = self.weather_data_noisy
            elif param.param["controlParameters"]["pvUncertainty"] == "weather_forecast":
                self.funcAddNoiseWeather(useSigmaFrame=True)
                self.weather_data = self.weather_data_noisy

        #calculate uncertainty of power output from weather uncertainty 
        if self.param.constraintTypePV != "deterministic" and self.param.constraintUseSigmaPV == "arr":
            self.funcCalcUncertaintyPowerOutput()

        # calculate power
        self.funcCreatePowerData(use_csv= not self.param.param['controlParameters']['useRealForecast'], use_pvUncertainty=self.param.param['controlParameters']['use_pvUncertainty'])

        if param.param["controlParameters"]["use_pvUncertainty"] and param.param["controlParameters"]["pvUncertainty"] == "power_noise":
            self.funcAddNoisePowerOutput()
            self.powerOutput = self.powerOutputNoisy


        # timestamps are saved in param
        start = self.param.param["controlParameters"]["startTimeIteration"]
        end = start + pd.Timedelta(hours = self.param.param["controlParameters"]["optimizationHorizon"]-1 )
        if param.param["controlParameters"]["considerPV"]:
            self.arrPowerAvailable = self.powerOutput[start:end].to_numpy()
        else:
            self.arrPowerAvailable = np.zeros(len(self.powerOutput))


        if len(self.arrPowerAvailable) < self.param.param["controlParameters"]["numberOfTimeSteps"]:
            raise Exception("Error: The start time and the time of the weather forecast or the historical weather data do not match")


    def funcLoadCSV(self):
        # Weather
        global_data = pd.read_csv(self.param.param['controlParameters']['pathPVData'] + r"\\pvgis_global_2023.csv", skiprows=10, nrows = 8751,index_col=0)
        components_data = pd.read_csv(self.param.param['controlParameters']['pathPVData'] + r"\\pvgis_components_2023.csv", skiprows=10, nrows = 8751,index_col=0)
    

        poa_data = pd.DataFrame(columns=[
            'poa_global','poa_direct','poa_diffuse','temp_air','wind_speed'],
            index=components_data.index)
        
        pv_pvgis = components_data['P'] / 1000
        poa_data['poa_global'] = global_data['G(i)']
        poa_data['poa_direct'] = components_data['Gb(i)']
        poa_data['poa_diffuse'] = components_data['Gd(i)'] #+ components_data['Gr(i)']
        poa_data['temp_air'] = components_data['T2m']
        poa_data['wind_speed'] = components_data['WS10m']
        poa_data.index = pd.to_datetime(poa_data.index, format="%Y%m%d:%H%M")
        #round the entries down to the full hour
        if poa_data.index[0].minute != 0 or poa_data.index[0].second != 0 or poa_data.index[0].microsecond != 0:
            poa_data.index = pd.date_range(start=poa_data.index[0] - pd.Timedelta(minutes=poa_data.index[0].minute,seconds= poa_data.index[0].second,microseconds = poa_data.index[0].microsecond), periods=len(poa_data), freq='h')
        self.csv_weather_data = poa_data


    def funcGetOnlineData(self):

        # Setup the Open-Meteo API client with cache and retry on error
        cache_session = requests_cache.CachedSession(".cache",expire_after = 3600)
        retry_session = retry(cache_session, retries = 5,backoff_factor = 0.2)
        openmeteo = openmeteo_requests.Client(session = retry_session)

        #Specifications for request
        url = "https://api.open-meteo.com/v1/forecast"
        specs = {
            "latitude": float(self.strPvLat),
            "longitude": float(self.strPvLon),
            "hourly": ["temperature_2m", "wind_speed_10m", "global_tilted_irradiance_instant", "direct_normal_irradiance_instant", "diffuse_radiation_instant"],
            "wind_speed_unit": "ms",
            "timezone": "Europe/Berlin" 
        }

        #request parameters
        responses = openmeteo.weather_api(url, params=specs)

        #hourly data to numpy
        responses = responses[0]
        hourly = responses.Hourly()
        hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
        hourly_wind_speed_10m = hourly.Variables(1).ValuesAsNumpy()
        hourly_global_tilted_irradiance_instant = hourly.Variables(2).ValuesAsNumpy()
        hourly_direct_normal_irradiance_instant = hourly.Variables(3).ValuesAsNumpy()
        hourly_diffuse_radiation_instant = hourly.Variables(4).ValuesAsNumpy()

        #data to pandas Dataframe
        hourly_data = {"date": pd.date_range(
            start = pd.to_datetime(hourly.Time(), unit = "s", utc = True).tz_convert("Europe/Berlin").tz_localize(None), #tz_convert converts to german time, tz_localize drops the utc information
            end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True).tz_convert("Europe/Berlin").tz_localize(None),
            freq = pd.Timedelta(seconds = hourly.Interval()),
            inclusive = "left"
        )}

        #print(hourly_data)

        #order important
        hourly_data["poa_global"] = hourly_global_tilted_irradiance_instant
        hourly_data["poa_direct"] = hourly_direct_normal_irradiance_instant
        hourly_data["poa_diffuse"] = hourly_diffuse_radiation_instant
        hourly_data["temp_air"] = hourly_temperature_2m
        hourly_data["wind_speed"] = hourly_wind_speed_10m

        hourly_dataframe = pd.DataFrame(data = hourly_data)
        hourly_dataframe = hourly_dataframe.set_index("date")
        self.online_weather_data = hourly_dataframe


    def funcCreatePowerData(self, use_csv = False, use_pvUncertainty = False, pv_Uncertainty = "power_noise", writeOutput = True):



        # PV
        location = Location(latitude = float(self.strPvLat), longitude = float(self.strPvLon),tz='Europe/Berlin',altitude=110, name='KIT Campus Nord')

        sandia_modules = pvlib.pvsystem.retrieve_sam('SandiaMod')
        sapm_inverters = pvlib.pvsystem.retrieve_sam('cecinverter')

        module = sandia_modules[self.strModule]
        inverter = sapm_inverters[self.strInverter]

        temperature_parameters = pvlib.temperature.TEMPERATURE_MODEL_PARAMETERS['sapm']['open_rack_glass_glass']

        system = PVSystem(surface_tilt=36, surface_azimuth=180,         # gemessen von Norden nach Osten (also sind 180° genau im Süden)
                          module_parameters=module, inverter_parameters=inverter,
                          temperature_model_parameters=temperature_parameters,
                          modules_per_string=1,strings_per_inverter=1)
        
        modelChain = ModelChain(system, location)

        modelChain.run_model_from_poa(self.weather_data)

        self.dataRaw = modelChain.results.ac
        for i in range(0, len(self.dataRaw)):
            if float(self.dataRaw.iloc[i]) < 0.0:
                self.dataRaw.iloc[i] = 0.0

        powerOutput = self.dataRaw.copy(deep=True)  * self.param.param['pv']['powerOfSystem'] / self.param.param['pv']['powerOfModule'] / 1000
        if writeOutput == True: #only overwrite if writeOutput is True
            self.powerOutput = powerOutput
        return powerOutput


########## Uncertainty ##########

    def funcAddNoisePowerOutput(self):
        l = len(self.powerOutput)
        cov = np.zeros((l,l))
        for i in range(l):
            cov[i][i] = self.covScalarPowerOutput

        samples = np.random.multivariate_normal(self.powerOutput.to_numpy(), cov, size=1)

        self.powerOutputNoisy = pd.Series(np.where(self.powerOutput > 0, samples[0], self.powerOutput),index = self.powerOutput.index,name = "Power + Noise [kW]")
        #fix negative values
        mask = self.powerOutputNoisy < 0
        self.powerOutputNoisy[mask]  = 0


    #add normal distributed noise to each of the weather data columns
    def funcAddNoiseWeather(self, useSigmaFrame = False):
        weather = self.weather_data.copy(deep=True)
        if useSigmaFrame == False:
            #iterate through all columns and sub columns
            for key in self.covWeatherData:
                series = weather[key]
                l = len(series)
                cov = np.zeros((l,l))
                for i in range(l):
                    cov[i][i] = self.covWeatherData[key]

                samples = np.random.multivariate_normal(series.to_numpy(), cov, size=1)
                weather.loc[weather[key] > 0.01, key] = samples[0][weather[key] > 0.01].astype(np.float32)

        else:
            for key in ['poa_global', 'poa_direct', 'poa_diffuse', 'temp_air', 'wind_speed']:
                sigma = self.weather_data.loc[:,"sigma_"+key].to_numpy()[0]
                series = weather[key]
                cov = np.identity(len(series)) *sigma
                samples = np.random.multivariate_normal(series.to_numpy(), cov, size=1)
                weather.loc[weather[key] > 0.01,key] = samples[0][weather[key] > 0.01].astype(np.float32)


        self.weather_data_noisy = weather
        #fix negative values
        mask = self.weather_data_noisy < 0
        self.weather_data_noisy[mask] = 0


    def funcCalcUncertaintyWeather(self, plot = False, correctWeather = True):

        #get archived forecast data
        cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
        retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
        openmeteo = openmeteo_requests.Client(session = retry_session)

        url = "https://historical-forecast-api.open-meteo.com/v1/forecast"
        specs = {
            "latitude": float(self.strPvLat),
            "longitude": float(self.strPvLon),
            "start_date": self.startDateToCalcUncertainty.strftime("%Y-%m-%d"),
            "end_date": self.stopDateToCalcUncertainty.strftime("%Y-%m-%d"),
            "hourly": ["temperature_2m", "wind_speed_10m", "global_tilted_irradiance_instant", "direct_normal_irradiance_instant", "diffuse_radiation_instant"],
            "wind_speed_unit": "ms",
            "timezone": "Europe/Berlin"
        }

        responses = openmeteo.weather_api(url, params=specs)

        #hourly data to numpy
        response = responses[0]
        hourly = response.Hourly()
        hourly_temperature_2m_hist_forecast = hourly.Variables(0).ValuesAsNumpy()
        hourly_wind_speed_10m_hist_forecast = hourly.Variables(1).ValuesAsNumpy()
        hourly_global_tilted_irradiance_instant_hist_forecast = hourly.Variables(2).ValuesAsNumpy()
        hourly_direct_normal_irradiance_instant_hist_forecast = hourly.Variables(3).ValuesAsNumpy()
        hourly_diffuse_radiation_instant_hist_forecast = hourly.Variables(4).ValuesAsNumpy()
        

        #get historical data - specs are the same
        url = "https://archive-api.open-meteo.com/v1/archive"

        responses = openmeteo.weather_api(url, params=specs)

        #hourly data to numpy
        response = responses[0]
        hourly = response.Hourly()
        hourly_temperature_2m_hist = hourly.Variables(0).ValuesAsNumpy()
        hourly_wind_speed_10m_hist = hourly.Variables(1).ValuesAsNumpy()
        hourly_global_tilted_irradiance_instant_hist = hourly.Variables(2).ValuesAsNumpy()
        hourly_direct_normal_irradiance_instant_hist = hourly.Variables(3).ValuesAsNumpy()
        hourly_diffuse_radiation_instant_hist = hourly.Variables(4).ValuesAsNumpy()


        temp_diff = hourly_temperature_2m_hist_forecast - hourly_temperature_2m_hist
        wind_speed_diff = hourly_wind_speed_10m_hist_forecast - hourly_wind_speed_10m_hist
        gti_diff = hourly_global_tilted_irradiance_instant_hist_forecast - hourly_global_tilted_irradiance_instant_hist
        dni_diff= hourly_direct_normal_irradiance_instant_hist_forecast - hourly_direct_normal_irradiance_instant_hist
        dri_diff = hourly_diffuse_radiation_instant_hist_forecast - hourly_diffuse_radiation_instant_hist


        #gauss fit the difference histograms - get mu and sigma for each array - plot the curves if plot = True
        nbins = 70  #try different number of bins if fit does not work
        array_fit_parameters = []

        if plot:
            fig,axs = plt.subplots(nrows=1,ncols=5,figsize=(4.7*2,5))

        def gauss_function(x, A,mu, sigma):
                return A * np.exp(-(x - mu)**2 / (2 * sigma**2))

        def curve_fit_adv(array,nbins):
                ydata, bins  = np.histogram(array,bins=nbins)
                xdata = bins[0:nbins] + 0.5 * (bins[1]-bins[0]) #mitte der bins
                popt, pcov,infodict, mesg, ier = curve_fit(gauss_function, xdata, ydata,full_output=True)
                if ier != 1:
                    popt, pcov, xdata, ydata = curve_fit_adv(array,nbins+1)
                return popt, pcov, xdata, ydata
        
        for i,array in enumerate([gti_diff,dni_diff,dri_diff,temp_diff,wind_speed_diff]):
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
            axs[0].set_title("temp")
            axs[1].set_title("wind_speed")
            axs[2].set_title("GTI")
            axs[3].set_title("DNI")
            axs[4].set_title("DRI")
            fig.suptitle("Gauss fitted difference of forecast and historical data "+self.startDateToCalcUncertainty.strftime("%d.%m.%Y")+"-" +self.stopDateToCalcUncertainty.strftime("%d.%m.%Y"))
            plt.legend()
            plt.show()


        array_fit_parameters = np.array(array_fit_parameters)

        
        #use array_fit_parameters (mu) to correct the weather data with the most common deviation
        if correctWeather == True:
            for i, key in enumerate(self.weather_data.columns.to_numpy()):
                self.weather_data.loc[:,key] = self.weather_data.loc[:,key] - array_fit_parameters[i][0]
            #fix negative values
            mask = self.weather_data < 0
            self.weather_data[mask] = 0


        for i, key in enumerate(self.weather_data.columns.to_numpy()):
            self.weather_data.loc[:,"mu_"+key] =  array_fit_parameters[i][0]
            self.weather_data.loc[:,"sigma_"+key] = array_fit_parameters[i][1]


    def funcCalcUncertaintyPowerOutput(self):
        N=100 #number of Uncertainty Samples
        self.funcCalcUncertaintyWeather(plot=False, correctWeather=True)
        weather_cache = self.weather_data.copy(deep=True)
        powerOutputN = np.zeros((len(self.weather_data),N))

        for i in range(N):
            self.funcAddNoiseWeather(useSigmaFrame = True)
            self.weather_data = self.weather_data_noisy
            powerOutput = self.funcCreatePowerData(use_csv = False, writeOutput = False)
            powerOutputArr = powerOutput.to_numpy()
            for j in range(len(powerOutputArr)):
                powerOutputN[j][i] = powerOutputArr[j]
        self.weather_data = weather_cache

        powerOutputMu = np.zeros(len(self.weather_data))
        powerOutputSigma = np.zeros(len(self.weather_data))

        for j in range(len(powerOutputN)):
            powerOutputMu[j] = np.mean(powerOutputN[j])
            powerOutputSigma[j] = np.std(powerOutputN[j])

        self.powerOutputMu = pd.Series(powerOutputMu, index=self.weather_data.index)
        self.powerOutputSigma = pd.Series(powerOutputSigma, index=self.weather_data.index)
        


