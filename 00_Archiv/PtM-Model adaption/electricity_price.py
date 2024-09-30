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
        self.startInit = 24*5 #+ 24*7*25
        self.start = self.startInit
        self.stop = self.param.param['controlParameters']['numberOfTimeSteps']

        self.numberUncertaintySamples = self.param.param['prices']['numberOfUncertaintySamples']

        self.powerPriceHourly = []

        # Energy price
        energyCharts_DataFrame = pd.read_excel(r'C:\PROJEKTE\PTX\Max\50_Daten\02_Energie\energy-charts_Stromproduktion_und_Börsenstrompreise_in_Deutschland_2022.xlsx')
        energyCharts = energyCharts_DataFrame.to_numpy()
        #powerPriceQuarterHourly = energyCharts[:,5] / 1000
        #self.powerPriceHourlyAll = []
        #for i in range(0, len(powerPriceQuarterHourly)-1,4):
        #    self.powerPriceHourlyAll.append(np.mean(powerPriceQuarterHourly[i:i+3]))
    
        self.powerPriceHourlyAll = energyCharts[1:,4] / 1000
        self.update(param, 0)


    def update(self, param, iteration):
        self.param = param
        self.start = self.startInit + 24*7*iteration
        self.stop = self.start + self.param.param['controlParameters']['numberOfTimeSteps']

        self.powerPriceHourly = []
        self.powerPriceHourly.append(0)

        for i in range(self.start, self.stop):
            self.powerPriceHourly.append(self.powerPriceHourlyAll[int(self.start + self.param.param['controlParameters']['timeStep']*(i-self.start))])

        self.uncertainty()
        self.numberUncertaintySamples = self.param.param['prices']['numberOfUncertaintySamples']

        #x = list(range(0,len(self.powerPriceHourly)))
        #plt.plot(x,self.powerPriceHourly,'-b',linewidth=2)
        #plt.show()
        #time.sleep(5)
        #plt.close('all')

    def uncertainty(self):
        cov = np.zeros((len(self.powerPriceHourly),len(self.powerPriceHourly)))
        mean = np.zeros(cov.shape[0])

        covValues = [0,2,4,6,8,10,12]
        #covValues = [0,2*10,4*10,6*10,8*10,10*10,12*10]        
        covValues = [i * 0.0001 for i in covValues]
        counter = 0

        for i in range(0,cov.shape[0]-1,int(24/self.param.param['controlParameters']['timeStep'])):
            for j in range(i,i+int(24/self.param.param['controlParameters']['timeStep'])):
                cov[j][j] = covValues[counter]
            
            counter = counter + 1

        for i in range(0,cov.shape[0]):
            mean[i] = self.powerPriceHourly[i]

        np.random.seed(1)
        self.powerPriceSamples = np.random.multivariate_normal(mean,cov, self.numberUncertaintySamples)

        for i in range(0,cov.shape[0]):
            for j in range(0, self.numberUncertaintySamples):
                if self.powerPriceSamples[j][i] <= 0:
                    self.powerPriceSamples[j][i] = 0

                self.powerPriceSamples[j][0] = 0

        """
        x = list(range(0,len(self.powerPriceHourly)))
        for i in range(0, self.numberUncertaintySamples):
            plt.plot(x,self.powerPriceSamples[i],'--r')

        plt.plot(x,self.powerPriceHourly,'-b',linewidth=2)
        plt.show()
        """

        



    def get_real_data(self):
        driver = webdriver.Edge()

        driver.get("https://www.nordpoolgroup.com/en/Market-data1/Dayahead/Area-Prices/de-lu/hourly/?view=table")
