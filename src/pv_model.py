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

# Quelle re.jrc.ec.europa.eu

class PV():
    def __init__(self, param):
        self.param = param
        self.iStartInit = 24*1 #+ 24*7*25   #312
        self.strModule = self.param.param['pv']['module']
        self.strInverter = self.param.param['pv']['inverter']
        self.strPvLat = "49.09"
        self.strPvLon = "8.44"
        self.iNumberUncertaintySamples = self.param.param['pv']['numberOfUncertaintySamples']
        self.fAlpha = self.param.param['pv']['alpha']
        self.fCovValue = self.param.param['pv']['covariance']

        self.funcCreateData()
        #self.funcUpdate(param, 0)


    def funcUpdate(self, param, iteration):
        self.param = param

        self.iStart = self.iStartInit + self.param.param['controlParameters']['numHoursToSimulate']*iteration#24*7*iteration#25#iteration
        self.iStop = self.iStart + self.param.param['controlParameters']['numberOfTimeSteps']

        self.arrPowerAvailable = []
        self.arrPowerAvailable.append(0)

        for i in range(self.iStart, self.iStop):
            if param.param['controlParameters']['considerPV'] == True:
                self.arrPowerAvailable.append(self.pvdata[int(self.iStart + self.param.param['controlParameters']['timeStep']*(i-self.iStart))] * self.param.param['controlParameters']['timeStep'])
            else:
                self.arrPowerAvailable.append(0)
        
        self.funcAddUncertainty()
        self.iNumberUncertaintySamples = self.param.param['pv']['numberOfUncertaintySamples']
        self.fAlpha = self.param.param['pv']['alpha']
        self.iCovValue = self.param.param['pv']['covariance']

    def funcCreateData(self):

        # Weather
        global_data = pd.read_csv(self.param.param['controlParameters']['pathPVData'] + "\pvgis_global_2023.csv", skiprows=10, nrows = 8751,index_col=0)
        components_data = pd.read_csv(self.param.param['controlParameters']['pathPVData'] + "\pvgis_components_2023.csv", skiprows=10, nrows = 8751,index_col=0)
    

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
        
        poa_data.to_csv(self.param.param['controlParameters']['pathPVData'] + "\poa_data.csv")

        # PV
        location = Location(latitude=49.09, longitude=8.44,tz='Europe/Berlin',altitude=110, name='KIT Campus Nord') # Karlsruhe
        # location = Location(latitude=35.341, longitude=25.115,tz='Europe/Athens',altitude=0, name='Heraklion') # Heraklion
        # location = Location(latitude=60.22, longitude=24.986,tz='Europe/Helsinki',altitude=0, name='Helsinki') # Helsinki

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

        poa_data_Used = pd.read_csv(self.param.param['controlParameters']['pathPVData'] + "\poa_data.csv", index_col=0)
        poa_data_Used.index = pd.to_datetime((poa_data.index))

        modelChain.run_model_from_poa(poa_data_Used)

        pvData_Series = modelChain.results.ac
        self.dataRaw = pvData_Series.to_numpy()
        self.pvdata = []
        for i in range(0, len(self.dataRaw)):
            if float(self.dataRaw[i]) < 0.0:
                self.dataRaw[i] = 0.0

            self.pvdata.append(self.dataRaw[i] * self.param.param['pv']['powerOfSystem'] / self.param.param['pv']['powerOfModule'] / 1000)

        """
        x = list(range(0,len(self.pvdata)))

        plt.plot(x,self.pvdata,'-b',linewidth=2)
        plt.xlabel("time in h")
        plt.ylabel("power in kWh")

        plt.show()

        plt.plot(x,pv_pvgis,'-b',linewidth=2)
        plt.xlabel("time in h")
        plt.ylabel("power in kWh")

        plt.show()
        """

        #pvData = {"pv": self.pvdata}
        #savemat('C:/PROJEKTE/PTX/Max/50_Daten/05_PV/pv_data_2020.mat', pvData)


        #modelChain.results.ac.plot(figsize=(16,9))
        #plt.show()

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

        """
        x = list(range(0,len(self.powerAvailable)))
        for i in range(0,self.numberUncertaintySamples):
            plt.plot(x,pvSamples[i],'--r')
 
        plt.plot(x,self.powerAvailable,'-b',linewidth=2)
        plt.xlabel("time in h")
        plt.ylabel("power in kWh")
        plt.show()
        """
        

    def funcGetRealData(self):
        
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
