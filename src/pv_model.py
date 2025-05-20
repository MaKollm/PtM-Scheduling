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

########################
########## PV ##########

# This class creates the data for the pv module. It uses the pvlib-package from python and calculates the power of a specific pv-system
# at a chosen loaction with historic weather data such as wind, irradiation and temperature. It also takes a lot of other factors into
# account. For more information visit https://pvlib-python.readthedocs.io/en/stable/user_guide/package_overview.html

# Quelle re.jrc.ec.europa.eu

class PV():
    def __init__(self, param):
        self.param = param
        self.strModule = self.param.param['pv']['module']
        self.strInverter = self.param.param['pv']['inverter']
        self.strPvLat = self.param.param["pv"]["strPvLat"]
        self.strPvLon = self.param.param["pv"]["strPvLon"]
        self.iNumberUncertaintySamples = self.param.param['pv']['numberOfUncertaintySamples']
        self.fAlpha = self.param.param['pv']['alpha']
        self.fCovValue = self.param.param['pv']['covariance']

        self.funcLoadCSV()


    def funcUpdate(self, param, iteration):
        self.param = param

        self.funcGetOnlineData()
        self.funcCreatePowerData(use_csv=self.param.param['controlParameters']['useRealForecast'])

        #timestamps are saved in param
        start = self.param.param["controlParameters"]["startTimeIteration"]
        end = start + pd.Timedelta(hours = self.param.param["controlParameters"]["optimizationHorizon"])

        index = self.csv_poa_data.index
        
        self.iStart = index.searchsorted(start)
        self.iStop  = index.searchsorted(end, side="right")

        if param.param["controlParameters"]["considerPV"] == True:
            self.arrPowerAvailable = self.pvdata[self.iStart:self.iStop]

        else:
            self.arrPowerAvailable = np.zeros(self.iStop-self.iStart)

        self.iNumberUncertaintySamples = self.param.param['pv']['numberOfUncertaintySamples']
        self.fAlpha = self.param.param['pv']['alpha']
        self.iCovValue = self.param.param['pv']['covariance']
        #self.funcAddUncertainty()


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
        self.csv_poa_data = poa_data


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
        self.online_poa_data = hourly_dataframe


    def funcCreatePowerData(self, use_csv = False):

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

        if use_csv == True:
            modelChain.run_model_from_poa(self.csv_poa_data)

        else:
            modelChain.run_model_from_poa(self.online_poa_data)


        pvData_Series = modelChain.results.ac
        self.dataRaw = pvData_Series.to_numpy()
        self.pvdata = []
        for i in range(0, len(self.dataRaw)):
            if float(self.dataRaw[i]) < 0.0:
                self.dataRaw[i] = 0.0

            self.pvdata.append(self.dataRaw[i] * self.param.param['pv']['powerOfSystem'] / self.param.param['pv']['powerOfModule'] / 1000)


    def funcAddUncertainty(self):
        arrCov = np.zeros((len(self.arrPowerAvailable),len(self.arrPowerAvailable)))
        arrMean = np.zeros(arrCov.shape[0])

        for i in range(0,arrCov.shape[0]):
            arrCov[i][i] = 1 + i*(self.fCovValue)
            arrMean[i] = self.arrPowerAvailable[i]

        np.random.seed(1)
        arrPvSamples = np.random.multivariate_normal(arrMean,arrCov,self.iNumberUncertaintySamples)
        for i in range(0,arrCov.shape[0]):
            if self.arrPowerAvailable[i] == 0:
                for j in range(0,self.iNumberUncertaintySamples):
                    arrPvSamples[j][i] = 0
            
        for i in range(0,arrCov.shape[0]):
            for j in range(0,self.iNumberUncertaintySamples):
                if arrPvSamples[j][i] <= 0:
                    arrPvSamples[j][i] = 0

        self.arrPvSamples = arrPvSamples

        
