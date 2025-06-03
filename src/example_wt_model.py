from params_clone import*
from wt_model import*

#create Param object and PV object
param = Param()
wt = WT(param)


#EXAMPLE with online weather data

#get online weather data
wt.funcGetOnlineData()
print(wt.online_weather_data)


#calculate appropiate uncertainties and deviation between forecast and historical data and add them to dataframe
wt.funcCalcUncertaintyWeather(plot = False,correctWeather = True ) #if correctWeather == True mu is subtracted from corresponding weather quantity
print(wt.online_weather_data)

#add noise with the uncertainty calculated above, saved in dataframe wt.online_weather_data_noisy
wt.funcAddNoiseWeather(useSigmaFrame = True) #if useSigmaFrame == False, use the covWeatherData dict specified in param
print(wt.online_weather_data_noisy)

#calculate powerData
wt.funcCreatePowerData(weatherKey = "online_noisy") #possible keys are "online"(default), "online_noisy", "csv"(not implemented yet)
print(wt.powerOutput)

#plot power with and without noise in
if False:
	wt.funcCreatePowerData(weatherKey = "online_noisy")
	wt.powerOutput.plot()
	wt.funcCreatePowerData(weatherKey = "online")
	wt.powerOutput.plot()
	plt.show()

#one can also add noise directly to the powerOutput
if False:
	wt.funcAddNoisePowerOutput() #saves data with noise in wt.powerOutputNoisy
	wt.powerOutputNoisy.plot()
	wt.powerOutput.plot()
	plt.show()
