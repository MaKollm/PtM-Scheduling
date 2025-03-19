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
        self.iStartInit = 24*1 
        self.iStart = self.iStartInit
        self.iStop = self.param.param['controlParameters']['numberOfTimeSteps']

        self.iNumberUncertaintySamples = self.param.param['prices']['numberOfUncertaintySamples']

        self.arrCarbonIntensityHourly = []

        # Carbon intensity
        DataFrameCarbonIntensityCharts = pd.read_csv(self.param.param['controlParameters']['pathPPData'] + "\DE_carbon_intensity_2023_hourly.csv")
        arrCarbonIntensityCharts = DataFrameCarbonIntensityCharts.to_numpy()

        self.arrCarbonIntensityAll = []
        for i in range(0, len(arrCarbonIntensityCharts)):
           self.arrCarbonIntensityAll.append(arrCarbonIntensityCharts[i][4])
    


    def funcUpdate(self, param, iteration):
        self.param = param
        self.iStart = self.iStartInit + self.param.param['controlParameters']['numHoursToSimulate']*iteration#24*7*iteration#25#iteration
        self.iStop = self.iStart + self.param.param['controlParameters']['numberOfTimeSteps']

        self.arrCarbonIntensityHourly = []
        self.arrCarbonIntensityHourly.append(0)

        for i in range(self.iStart, self.iStop):
            self.arrCarbonIntensityHourly.append(self.arrCarbonIntensityAll[int(self.iStart + self.param.param['controlParameters']['timeStep']*(i-self.iStart))])

        #self.funcAddUncertainty()
        self.iNumberUncertaintySamples = self.param.param['carbonIntensity']['numberOfUncertaintySamples']


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

        """
        x = list(range(0,len(self.arrPowerPriceHourly)))
        for i in range(0, self.iNumberUncertaintySamples):
            plt.plot(x,self.arrCarbonIntensitySamples[i],'--r')

        plt.plot(x,self.arrPowerPriceHourly,'-b',linewidth=2)
        plt.show()
        """

        
    def funcGetRealData(self):
        driver = webdriver.Edge()

        driver.get("https://www.nordpoolgroup.com/en/Market-data1/Dayahead/Area-Prices/de-lu/hourly/?view=table")