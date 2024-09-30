#!/usr/bin/env python3.10


########################
########## PV ##########

# Using pvlib-package from python:
# https://pvlib-python.readthedocs.io/en/stable/user_guide/package_overview.html

import pvlib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


class PV():
    def __init__(self, param):
        self.param = param
        self.module = param['pv']['module']
        self.inverter = param['pv']['inverter']

        self.start = 312
        self.stop = self.start + self.param['controlParameters']['optimizationHorizon']


    def create_PV(self):

        # Latitude, longitude, name, altitude, timezone
        coordinates = [
            (32.2, -111.0, 'Tucson', 700, 'Etc/GMT+7'),
            (35.1, -106.6, 'Albuquerque', 1500, 'Etc/GMT+7'),
            (37.8, -122.4, 'San Francisco', 10, 'Etc/GMT+8'),
            (52.5, 13.4, 'Berlin', 34, 'Etc/GMT-1'),
        ]


        # Get the module and inverter specifications from SAM
        sandia_modules = pvlib.pvsystem.retrieve_sam('SandiaMod')
        sapm_inverters = pvlib.pvsystem.retrieve_sam('cecinverter')
        module = sandia_modules[self.module]
        inverter = sapm_inverters[self.inverter]
        temperature_model_parameters = pvlib.temperature.TEMPERATURE_MODEL_PARAMETERS['sapm']['open_rack_glass_glass']

        tmys = []

        for location in coordinates:
            latitude, longitude, name, altitude, timezone = location
            weather = pvlib.iotools.get_pvgis_tmy(latitude, longitude,
                                                map_variables=True)[0]
            weather.index.name = "utc_time"
            tmys.append(weather)

        system = {'module': module, 'inverter': inverter,
                'surface_azimuth': 180}


        energies = {}

        for location, weather in zip(coordinates, tmys):
            latitude, longitude, name, altitude, timezone = location
            system['surface_tilt'] = latitude
            solpos = pvlib.solarposition.get_solarposition(
                time=weather.index,
                latitude=latitude,
                longitude=longitude,
                altitude=altitude,
                temperature=weather["temp_air"],
                pressure=pvlib.atmosphere.alt2pres(altitude),
            )
            dni_extra = pvlib.irradiance.get_extra_radiation(weather.index)
            airmass = pvlib.atmosphere.get_relative_airmass(solpos['apparent_zenith'])
            pressure = pvlib.atmosphere.alt2pres(altitude)
            am_abs = pvlib.atmosphere.get_absolute_airmass(airmass, pressure)
            aoi = pvlib.irradiance.aoi(
                system['surface_tilt'],
                system['surface_azimuth'],
                solpos["apparent_zenith"],
                solpos["azimuth"],
            )
            total_irradiance = pvlib.irradiance.get_total_irradiance(
                system['surface_tilt'],
                system['surface_azimuth'],
                solpos['apparent_zenith'],
                solpos['azimuth'],
                weather['dni'],
                weather['ghi'],
                weather['dhi'],
                dni_extra=dni_extra,
                model='haydavies',
            )
            cell_temperature = pvlib.temperature.sapm_cell(
                total_irradiance['poa_global'],
                weather["temp_air"],
                weather["wind_speed"],
                **temperature_model_parameters,
            )
            effective_irradiance = pvlib.pvsystem.sapm_effective_irradiance(
                total_irradiance['poa_direct'],
                total_irradiance['poa_diffuse'],
                am_abs,
                aoi,
                module,
            )
            dc = pvlib.pvsystem.sapm(effective_irradiance, cell_temperature, module)
            ac = pvlib.inverter.sandia(dc['v_mp'], dc['p_mp'], inverter)

        ac = ac.tz_localize(None)
        index = pd.date_range(start='2016-01-01 00:00:00',end='2016-01-31 23:00:00',freq='H')

        pvData_Series = ac[index]
        self.dataRaw = pvData_Series.to_numpy()
        pv = []
        for i in range(0, len(self.dataRaw)):
            if float(self.dataRaw[i]) < 0.0:
                self.dataRaw[i] = 0.0

            pv.append(self.dataRaw[i])

        self.powerAvailable = pv[self.start:self.stop]
        self.powerAvailable.insert(0,0.0)


        #ac[index].to_excel(r"C:\Users\ne9836\Promotion_IAI\50_Daten\02_Energie\pv\pv.xlsx")
        #pvEnergy = ac[index].tolist()
        #energies = pd.Series(energies)

    def model_uncertainty(self):
        cov = np.zeros((self.param['controlParameters']['optimizationHorizon']+1,self.param['controlParameters']['optimizationHorizon']+1))
        mean = np.zeros(cov.shape[0])

        for i in range(0,cov.shape[0]):
            cov[i][i] = 1 + i*(2)
            mean[i] = self.powerAvailable[i]

        #for i in range(0,int(cov.shape[0]/24)):
        #    mean[0+i*24:(i+1)*24] = self.powerAvailable[0:24]

        pvSamples = np.random.multivariate_normal(mean,cov,100)
        for i in range(0,cov.shape[0]):
            if self.powerAvailable[i] == 0:
                for j in range(0,100):
                    pvSamples[j][i] = 0
            
        for i in range(0,cov.shape[0]):
            for j in range(0,100):
                if pvSamples[j][i] <= 0:
                    pvSamples[j][i] = 0

        self.pvSamples = pvSamples

        x = list(range(0,self.param['controlParameters']['optimizationHorizon']+1))
        for i in range(0,100):
            plt.plot(x,pvSamples[i],'--r')
 
        plt.plot(x,self.powerAvailable,'-b',linewidth=2)
        plt.show()



        #curl https://api.forecast.solar/estimate/watthours/52/12/37/0/5.67

        
