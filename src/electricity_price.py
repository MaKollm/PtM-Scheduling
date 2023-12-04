#!/usr/bin/env python3.10

import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from selenium import webdriver
from datetime import datetime

##################################
########## Electricity price ##########


class PowerPrice():

    def __init__(self, param):
        self.param = param
        self.iStartInit = 24*5 
        self.iStart = self.iStartInit
        self.iStop = self.param.param['controlParameters']['numberOfTimeSteps']

        self.iNumberUncertaintySamples = self.param.param['prices']['numberOfUncertaintySamples']

        self.arrPowerPriceHourly = []

        # Energy price
        DataFrameEnergyCharts = pd.read_excel(r'C:\PROJEKTE\PTX\Max\50_Daten\02_Energie\energy-charts_Stromproduktion_und_Börsenstrompreise_in_Deutschland_2022.xlsx')
        arrEnergyCharts = DataFrameEnergyCharts.to_numpy()
    
        self.arrPowerPriceHourlyAll = arrEnergyCharts[1:,4] / 1000
        self.funcUpdate(param, 0)


    def funcUpdate(self, param, iteration):
        self.param = param
        self.iStart = self.iStartInit + 24*7*iteration
        self.iStop = self.iStart + self.param.param['controlParameters']['numberOfTimeSteps']

        self.arrPowerPriceHourly = []
        self.arrPowerPriceHourly.append(0)

        for i in range(self.iStart, self.iStop):
            self.arrPowerPriceHourly.append(self.arrPowerPriceHourlyAll[int(self.iStart + self.param.param['controlParameters']['timeStep']*(i-self.iStart))])

        self.funcAddUncertainty()
        self.iNumberUncertaintySamples = self.param.param['prices']['numberOfUncertaintySamples']


    def funcAddUncertainty(self):
        arrCov = np.zeros((len(self.arrPowerPriceHourly),len(self.arrPowerPriceHourly)))
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
            arrMean[i] = self.arrPowerPriceHourly[i]

        np.random.seed(1)
        self.arrPowerPriceSamples = np.random.multivariate_normal(arrMean,arrCov, self.iNumberUncertaintySamples)

        for i in range(0,arrCov.shape[0]):
            for j in range(0, self.iNumberUncertaintySamples):
                if self.arrPowerPriceSamples[j][i] <= 0:
                    self.arrPowerPriceSamples[j][i] = 0

                self.arrPowerPriceSamples[j][0] = 0

        """
        x = list(range(0,len(self.arrPowerPriceHourly)))
        for i in range(0, self.iNumberUncertaintySamples):
            plt.plot(x,self.arrPowerPriceSamples[i],'--r')

        plt.plot(x,self.arrPowerPriceHourly,'-b',linewidth=2)
        plt.show()
        """

        
    def funcGetRealData(self):
        driver = webdriver.Edge()

        driver.get("https://www.nordpoolgroup.com/en/Market-data1/Dayahead/Area-Prices/de-lu/hourly/?view=table")
