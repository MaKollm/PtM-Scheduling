#!/usr/bin/env python3.10


import pvlib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests
import json
from scipy.io import savemat

from pvlib.location import Location
from pvlib.modelchain import ModelChain
from pvlib.temperature import TEMPERATURE_MODEL_PARAMETERS
from pvlib.pvsystem import PVSystem

########################
########## PV ##########

# This class creates the data for the pv module. It uses the pvlib-package from python and calculates the power of a specific pv-system
# at a chosen loaction with historic weather data such as wind, irradiation and temperature. It also takes a lot of other factors into
# account. For more information visit https://pvlib-python.readthedocs.io/en/stable/user_guide/package_overview.html

class PV():
    def __init__(self, param):
        self.param = param
        self.startInit = 24*5 #+ 24*7*25   #312
        self.module = self.param.param['pv']['module']
        self.inverter = self.param.param['pv']['inverter']
        self.pvLat = "49.09"
        self.pvLon = "8.44"
        self.numberUncertaintySamples = self.param.param['pv']['numberOfUncertaintySamples']
        self.alpha = self.param.param['pv']['alpha']
        self.covValue = self.param.param['pv']['covariance']

        self.create_data()
        self.update(param, 0)


    def update(self, param, iteration):
        self.param = param

        self.start = self.startInit + 24*7*iteration
        self.stop = self.start + self.param.param['controlParameters']['numberOfTimeSteps']

        self.powerAvailable = []
        self.powerAvailable.append(0)

        for i in range(self.start, self.stop):
            if param.param['controlParameters']['considerPV'] == True:
                self.powerAvailable.append(self.pvdata[int(self.start + self.param.param['controlParameters']['timeStep']*(i-self.start))] * self.param.param['controlParameters']['timeStep'])
            else:
                self.powerAvailable.append(0)
    
        
        self.uncertainty()
        self.numberUncertaintySamples = self.param.param['pv']['numberOfUncertaintySamples']
        self.alpha = self.param.param['pv']['alpha']
        self.covValue = self.param.param['pv']['covariance']

    def create_data(self):

        # Weather
        global_2020 = pd.read_csv(r'C:\PROJEKTE\PTX\Max\50_Daten\05_PV\pvgis_global_2020.csv', skiprows=8, nrows = 8784,index_col=0)
        components_2020 = pd.read_csv(r'C:\PROJEKTE\PTX\Max\50_Daten\05_PV\pvgis_components_2020.csv', skiprows=8, nrows = 8784,index_col=0)
    

        poa_data_2020 = pd.DataFrame(columns=[
            'poa_global','poa_direct','poa_diffuse','temp_air','wind_speed'],
            index=global_2020.index)
        
        poa_data_2020['poa_global'] = global_2020['G(i)']
        poa_data_2020['poa_direct'] = components_2020['Gb(i)']
        poa_data_2020['poa_diffuse'] = components_2020['Gd(i)'] + components_2020['Gr(i)']
        poa_data_2020['temp_air'] = components_2020['T2m']
        poa_data_2020['wind_speed'] = components_2020['WS10m']
        poa_data_2020.index = pd.to_datetime(poa_data_2020.index, format="%Y%m%d:%H%M")
        
        poa_data_2020.to_csv('C:/PROJEKTE/PTX/Max/50_Daten/05_PV/poa_data_2020.csv')

        # PV
        location = Location(latitude=49.09, longitude=8.44,tz='Europe/Berlin',altitude=110, name='KIT Campus Nord')

        sandia_modules = pvlib.pvsystem.retrieve_sam('SandiaMod')
        sapm_inverters = pvlib.pvsystem.retrieve_sam('cecinverter')

        module = sandia_modules[self.module]
        inverter = sapm_inverters[self.inverter]

        temperature_parameters = pvlib.temperature.TEMPERATURE_MODEL_PARAMETERS['sapm']['open_rack_glass_glass']

        system = PVSystem(surface_tilt=45, surface_azimuth=180,
                          module_parameters=module, inverter_parameters=inverter,
                          temperature_model_parameters=temperature_parameters,
                          modules_per_string=1,strings_per_inverter=1)
        
        modelChain = ModelChain(system, location)

        poa_data_2020_Used = pd.read_csv(r'C:/PROJEKTE/PTX/Max/50_Daten/05_PV/poa_data_2020.csv', index_col=0)
        poa_data_2020_Used.index = pd.to_datetime((poa_data_2020.index))

        modelChain.run_model_from_poa(poa_data_2020_Used)

        pvData_Series = modelChain.results.ac
        self.dataRaw = pvData_Series.to_numpy()
        self.pvdata = []
        for i in range(0, len(self.dataRaw)):
            if float(self.dataRaw[i]) < 0.0:
                self.dataRaw[i] = 0.0

            self.pvdata.append(self.dataRaw[i] * self.param.param['pv']['powerOfSystem'] / self.param.param['pv']['powerOfModule'] / 1000)

        #pvData = {"pv": self.pvdata}
        #savemat('C:/PROJEKTE/PTX/Max/50_Daten/05_PV/pv_data_2020.mat', pvData)


        #modelChain.results.ac.plot(figsize=(16,9))
        #plt.show()

    def uncertainty(self):
        cov = np.zeros((len(self.powerAvailable),len(self.powerAvailable)))
        mean = np.zeros(cov.shape[0])

        for i in range(0,cov.shape[0]):
            cov[i][i] = 1 + i*(self.covValue)
            mean[i] = self.powerAvailable[i]

        np.random.seed(1)
        pvSamples = np.random.multivariate_normal(mean,cov,self.numberUncertaintySamples)
        for i in range(0,cov.shape[0]):
            if self.powerAvailable[i] == 0:
                for j in range(0,self.numberUncertaintySamples):
                    pvSamples[j][i] = 0
            
        for i in range(0,cov.shape[0]):
            for j in range(0,self.numberUncertaintySamples):
                if pvSamples[j][i] <= 0:
                    pvSamples[j][i] = 0

        self.pvSamples = pvSamples

        """
        x = list(range(0,len(self.powerAvailable)))
        for i in range(0,self.numberUncertaintySamples):
            plt.plot(x,pvSamples[i],'--r')
 
        plt.plot(x,self.powerAvailable,'-b',linewidth=2)
        plt.xlabel("time in h")
        plt.ylabel("power in kWh")
        plt.show()
        """
        

    def get_real_data(self):
        
        locationCheck = "https://api.forecast.solar/check/" + self.pvLat + "/" + self.pvLon
        location = requests.get(locationCheck)

        my_json = location.content.decode('utf8')

        a = json.loads(my_json)
        print(a)
        print(a["result"])
        print(a["result"]["place"])

        response = requests.get("https://api.forecast.solar/estimate/watthours/52/12/37/0/5.67")
        #print(response)
        #print(response.content)

        with open(r"C:\Users\ne9836\Promotion_IAI\50_Daten\05_PV\pvData.json","w") as outfile:
            json.dump(a, outfile)

        #curl https://api.forecast.solar/estimate/watthours/52/12/37/0/5.67
