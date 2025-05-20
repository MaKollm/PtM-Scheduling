#!/usr/bin/env python3.10

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import json
import requests
from datetime import  date, datetime, timedelta

##################################
########## Electricity price ##########

# Quelle: energy-charts.info -> EPEX SPOT Börsenstrompreis


class PowerPrice():

    def __init__(self, param):
        self.param = param
        self.funcLoadCSV()

    def funcUpdate(self, param, iteration):
        self.param = param
        if param.param['controlParameters']['useRealForecast'] == True:
            data = self.funcForecastData(numWeeksToConsider=1)
            self.iStart = 0
            self.iStop  = self.param.param["controlParameters"]["optimizationHorizon"]
            data["prices"] = data["prices"].astype(float) / 1000
            self.arrPowerPriceHourly = data["prices"].to_numpy()
            self.arrPowerPriceHourly = self.arrPowerPriceHourly[self.iStart:self.iStop]
            print(len(self.arrPowerPriceHourly))
        else:
            self.funcUpdateCSV(param)


    def funcLoadCSV(self):
        self.DataFrameEnergyCharts = pd.read_csv(self.param.param['controlParameters']['pathPPData'] + r"\\energy-charts_Stromproduktion_und_Börsenstrompreise_in_Deutschland_2023.csv",dtype = str,skiprows = [1])
        self.DataFrameEnergyCharts = self.DataFrameEnergyCharts.set_index("Datum (MEZ)", drop = True)
        self.DataFrameEnergyCharts.index = pd.to_datetime(self.DataFrameEnergyCharts.index, utc=True).tz_convert("Europe/Berlin").tz_localize(None)
        self.DataFrameEnergyCharts = self.DataFrameEnergyCharts[["Day Ahead Auktion (DE-LU)"]]
        self.DataFrameEnergyCharts["Day Ahead Auktion (DE-LU)"] = self.DataFrameEnergyCharts["Day Ahead Auktion (DE-LU)"].astype(float) /1000

        self.arrPowerPriceHourlyAll = self.DataFrameEnergyCharts["Day Ahead Auktion (DE-LU)"].to_numpy()


    #trims arrPowerPriceHourlyAll to depending on start_time and numHoursToSimulate, saves trimmed array as arrPowerPriceHourly
    def funcUpdateCSV(self, param):
        start = self.param.param["controlParameters"]["startTimeIteration"]
        end = start + pd.Timedelta(hours = self.param.param["controlParameters"]["optimizationHorizon"] - 1)

        index = self.DataFrameEnergyCharts.index
        
        self.iStart = index.searchsorted(start)
        self.iStop  = index.searchsorted(end, side="right")

        self.arrPowerPriceHourly = self.arrPowerPriceHourlyAll[self.iStart:self.iStop]


    #helper method, which gets the full Day-Ahead-auction (DE/LU) prices for a specific year (returns numpy array)
    def funcGetElectricityPrice(self, year):
        url = r"https://www.energy-charts.info/charts/price_spot_market/data/de/year_"+str(year)+".json"
        response = requests.get(url)
        if response.status_code == 200:
            dataset = response.json()  #list of whole dataset - entry 6 is day ahead auction
        else:
            print("Fehler beim Abruf:", response.status_code)

        #find day-ahead-auction in dataset
        for i in range(len(dataset)):
            try:
                if dataset[i]["name"][0]["en"] == "Day Ahead Auction (DE-LU)":
                    print("Day Ahead Auction has index ",i)
                    break
            except:
                1==1

        data = np.array(dataset[i]["data"])

        return data

    #requests data from www.energy-charts.info and takes mean value of the last numWeeksToConsider weeks as forecast
    #returns dataset with timestamps as indices, columns are the prices and standard deviations
    def funcForecastData(self,numWeeksToConsider):

        #get current date and save relevant parameters
        today = date.today()
        week = today.isocalendar().week
        year = today.year
        day = today.day
        days_gone = (today - date(today.year,1,1)).days #number of days this year, excluding today


        #get data and convert to dataframe with timestamps - vll actual prices rather than day ahead prices
        if week > numWeeksToConsider:
            prices = self.funcGetElectricityPrice(year)
            time_index = pd.date_range(start=str(year)+"-01-01 00:00",periods=len(prices),freq="h",tz="Europe/Berlin").tz_localize(None) #tz="Europe/Berlin" includes summer/winter time - localize removes utc information 
            data = pd.DataFrame(index=time_index)
            data["Day Ahead Price (DE/LU)"] = prices

        else:  
            prices1 = self.funcGetElectricityPrice(year-1)
            prices2 = self.funcGetElectricityPrice(year)
            prices = np.concatenate((prices1,prices2))
            time_index = pd.date_range(start=str(year-1)+"-01-01 00:00",periods=len(prices),freq="h",tz="Europe/Berlin").tz_localize(None)
            data = pd.DataFrame(index=time_index)
            data["Day Ahead Price (DE/LU)"] = prices

        #print(data["Day Ahead Price (DE/LU)"] )


        #delete NaN values
        mask_none = data["Day Ahead Price (DE/LU)"].notna()
        data = data[mask_none]

        #evaluate mean value as "forecast" and standard deviation - forecast one week
        prices_mean = np.zeros(24*7,dtype=float)
        prices_mean_std = np.zeros(24*7,dtype=float)

        #calculate mean value of numWeeksToConsider Weeks
        #print(data["Day Ahead Price (DE/LU)"] ,len(data["Day Ahead Price (DE/LU)"]))
        prices_mean += data["Day Ahead Price (DE/LU)"].to_numpy(dtype=np.float64)[-24*7:]/numWeeksToConsider
        for i in range(1,numWeeksToConsider):
            prices_mean += data["Day Ahead Price (DE/LU)"].to_numpy(dtype=np.float64)[-24*7*(i+1):-24*7*i]/numWeeksToConsider

        #calculate standard deviation of numWeeksToConsider Weeks
        prices_mean_std += (prices_mean - data["Day Ahead Price (DE/LU)"].to_numpy(dtype=np.float64)[-24*7:])**2
        for i in range(1,numWeeksToConsider):
            prices_mean_std += (prices_mean - data["Day Ahead Price (DE/LU)"].to_numpy(dtype=np.float64)[-24*7*(i+1):-24*7*i])**2
        prices_mean_std = np.sqrt(prices_mean_std)

        start_data_forecast = data.index[-1] + timedelta(hours=1)
        times_forecast = pd.date_range(start=start_data_forecast,periods=24*7,freq="h",tz="Europe/Berlin").tz_localize(None)
        data_forecast = pd.DataFrame(index=times_forecast)
        data_forecast["prices"] = prices_mean
        data_forecast["prices_std"] = prices_mean_std



        #check if today/tomorrow is in data_forecast, if not add the existing prices from data in front of data_forecast
        if np.datetime64(today) not in data_forecast.index:
            if np.datetime64(today +timedelta(days=1)) not in data_forecast.index:
                add_time = pd.date_range(start=today,periods=48,freq="h")
                add_data = data["Day Ahead Price (DE/LU)"][-48:]
                print(len(add_time),len(add_data))
            else:
                add_time = pd.date_range(start=(today + timedelta(days=1)),periods=24,freq="h")
                add_data = data["Day Ahead Price (DE/LU)"][-24:]


            data_forecast_total = pd.DataFrame(index = pd.concat([pd.Series(add_time),pd.Series(data_forecast.index)]))
            data_forecast_total["prices"] = pd.concat([add_data,data_forecast["prices"]])
            data_forecast_total["prices_std"] = pd.concat([add_data*0,data_forecast["prices_std"]]) #add_data has right dimension and std of these values is zero
        else:
            data_forecast_total = data_forecast

        return data_forecast_total
    

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

