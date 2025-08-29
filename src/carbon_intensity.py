import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from selenium import webdriver
from datetime import datetime

##################################
########## Carbon intensity ##########

# Quelle: electricitymaps.com

class CarbonIntensity():

    def __init__(self, param):
        self.param = param
        self.funcLoadCSV()

    def funcUpdate(self, param, iteration):
        self.param = param
        if param.param['controlParameters']['useRealForecast'] == True:
            self.iStart = 0
            self.iStop  = self.param.param["controlParameters"]["optimizationHorizon"]
            self.arrCarbonIntensityHourly = np.zeros(self.iStop-self.iStart)
        else:
            self.funcUpdateCSV(param)

    def funcLoadCSV(self):
        self.DataFrameEnergyCharts = pd.read_csv(self.param.param['controlParameters']['pathPPData'] + r"\\DE_carbon_intensity_2023_hourly.csv",dtype = str)
        self.DataFrameEnergyCharts = self.DataFrameEnergyCharts.set_index("Datetime (UTC)", drop = True)
        self.DataFrameEnergyCharts.index = pd.to_datetime(self.DataFrameEnergyCharts.index, utc=True).tz_convert("Europe/Berlin").tz_localize(None)
        self.DataFrameEnergyCharts = self.DataFrameEnergyCharts[["Carbon Intensity gCO₂eq/kWh (direct)"]]
        self.DataFrameEnergyCharts["Carbon Intensity gCO₂eq/kWh (direct)"] = self.DataFrameEnergyCharts["Carbon Intensity gCO₂eq/kWh (direct)"].astype(float)

        self.arrCarbonIntensityHourlyAll = self.DataFrameEnergyCharts["Carbon Intensity gCO₂eq/kWh (direct)"].to_numpy()

    def funcUpdateCSV(self, param):
        start = self.param.param["controlParameters"]["startTimeIteration"]
        end = start + pd.Timedelta(hours = self.param.param["controlParameters"]["optimizationHorizon"] - 1)

        index = self.DataFrameEnergyCharts.index
        
        self.iStart = index.searchsorted(start)
        self.iStop  = index.searchsorted(end, side="right")

        self.arrCarbonIntensityHourly = self.arrCarbonIntensityHourlyAll[self.iStart:self.iStop]

        ## Repeat carbon intensity depending on time step
        self.arrCarbonIntensityHourly = [x for x in self.arrCarbonIntensityHourly for _ in range(int(1 / self.param.param['controlParameters']['timeStep']))]


    def funcAddUncertainty(self):
        arrCov = np.zeros((len(self.arrCarbonIntensityHourly),len(self.arrCarbonIntensityHourly)))
        arrMean = np.zeros(arrCov.shape[0])

        arrCovValues = [0,2,4,6,8,10,12]
        #arrCovValues = [0,2*10,4*10,6*10,8*10,10*10,12*10]        
        arrCovValues = [i * 0.0001 for i in arrCovValues]
        iCounter = 0

        for i in range(0,arrCov.shape[0]-1,int(24/self.param.param['controlParameters']['timeStep'])):
            for j in range(i,i+int(24/self.param.param['controlParameters']['timeStep'])):
                arrCov[j][j] = arrCovValues[iCounter]
            
            iCounter = iCounter + 1

        for i in range(0,arrCov.shape[0]):
            arrMean[i] = self.arrCarbonIntensityHourly[i]

        np.random.seed(1)
        self.arrCarbonIntensitySamples = np.random.multivariate_normal(arrMean,arrCov, self.iNumberUncertaintySamples)

        for i in range(0,arrCov.shape[0]):
            for j in range(0, self.iNumberUncertaintySamples):
                if self.arrCarbonIntensitySamples[j][i] <= 0:
                    self.arrCarbonIntensitySamples[j][i] = 0

                self.arrCarbonIntensitySamples[j][0] = 0
