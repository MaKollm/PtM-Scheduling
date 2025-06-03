from params_clone import*
from pv_model import*

#create Param object and PV object
param = Param()
pv = PV(param)


#EXAMPLE with online weather data

#get online weather data
pv.funcGetOnlineData()
print(pv.online_weather_data)

#calculate appropiate uncertainties and deviation between forecast and historical data and add them to dataframe
pv.funcCalcUncertaintyWeather(plot = True,correctWeather = True ) #if correctWeather == True mu is subtracted from corresponding weather quantity
print(pv.online_weather_data)

#add noise with the uncertainty calculated above, saved in dataframe pv.online_weather_data_noisy
pv.funcAddNoiseWeather(useSigmaFrame = True) #if useSigmaFrame == False, use the covWeatherData dict specified in param
print(pv.online_weather_data_noisy)

#calculate powerData
pv.funcCreatePowerData(weatherKey = "online_noisy") #possible keys are "online"(default), "online_noisy", "csv"
print(pv.powerOutput)

#plot power with and without noise in
if True:
	pv.funcCreatePowerData(weatherKey = "online")
	pv.powerOutput.plot()
	pv.funcCreatePowerData(weatherKey = "online_noisy")
	pv.powerOutput.plot()
	plt.show()

#one can also add noise directly to the powerOutput
if True:
	pv.funcAddNoisePowerOutput() #saves data with noise in pv.powerOutputNoisy
	pv.powerOutputNoisy.plot()
	pv.powerOutput.plot()
	plt.show()
