#!/usr/bin/env python3.10

import scipy.io as sio
import pandas as pd
import numpy as np
import os
import pickle
from gurobipy import GRB
from datetime import  date, datetime, timedelta

class Param():

    def __init__(self, args):

        if len(args) > 0:
            self.optimizationHorizon = args[0]
            self.timeStep = args[1]
            self.timeLimit = args[2]
            self.optimalityGap = args[3]
            self.testFeasibility = args[4]

            self.numHoursToSimulate = args[5]

            self.startTime = args[6]
            self.useRealForecast = args[7]

            self.objectiveFunction = args[8]

            self.benchmark = args[9]
            self.sameOutputAsBenchmark = args[10]

            self.rateOfChangeConstranints = args[11]
            self.transitionConstraints = args[12]
            self.powerSale = args[13]
            self.powerPurchase = args[14]
            self.considerPV = args[15]
            self.considerBattery = args[16]
            self.peakLoadCapping = args[17]


            self.strPathCharMapData = args[18]
            self.strPathCharMapDataCalc = args[19]
            self.strPathPVData = args[20]
            self.strPathPPData = args[21]
            self.strPathInitialData = args[22]
            self.strPathAdaptationData = args[23]
        
    def funcUpdateTime(self, iteration):
        self.param['controlParameters']['startTimeIteration'] = self.param['controlParameters']['startTime'] + pd.Timedelta(hours=self.param["controlParameters"]["optimizationHorizon"]*iteration)
        self.param['controlParameters']['iteration'] = iteration
        #self.param['controlParameters']['startTimeIteration'] = self.param['controlParameters']['startTimeIteration'] + timedelta(hours=self.param['controlParameters']['numHoursToSimulate'])


    def funcUpdate(self, pv, pp, ci, iteration):
        self.param['pv']['powerAvailable'] = pv.arrPowerAvailable
        self.param['prices']['power'] = pp.arrPowerPriceHourly
        self.param['carbonIntensity']['carbonIntensity'] = ci.arrCarbonIntensityHourly

        if self.param['controlParameters']['numTimeStepsToSimulate'] >= self.param['controlParameters']['numberOfTimeSteps']:
            pass
        else:
            self.funcStoreInitialData(iteration)



    def funcStoreInitialData(self, iteration):
        if os.path.isfile(self.param['controlParameters']['pathInitialData'] + "\input_data.pkl") == True:
            with open(self.param['controlParameters']['pathInitialData'] + "\input_data.pkl", 'rb') as f:
                self.param['initialData'] = pickle.load(f)

            if len(self.param['initialData']['input']) > 0 and iteration > 0:
                # Operating states
                valueFound = False
                for i in range(self.param['controlParameters']['numTimeStepsToSimulate']-1, 0, -1):
                    for j in range(np.shape(self.param['initialData']['input']['currentStateSwitchCO2CAPRaw'])[1]):
                        for k in range(np.shape(self.param['initialData']['input']['currentStateSwitchCO2CAPRaw'])[2]):
                            if int(self.param['initialData']['input']['currentStateSwitchCO2CAPRaw'][i,j,k]) == 1 and j != k and valueFound == False:
                                self.param['startValues']['stateCO2CAP'] = k
                                if k == 0:
                                    self.param['constraints']['transitionTimesStart']['minStayTimeCO2CAP'] = max(1,self.param['constraints']['transitionTimes']['minStayTimeCO2CAP_Off'][j] - (self.param['controlParameters']['numTimeStepsToSimulate'] - i))
                                    self.param['constraints']['transitionTimesStart']['maxStayTimeCO2CAP'] = self.param['constraints']['transitionTimes']['maxStayTimeCO2CAP_Off'][j] - (self.param['controlParameters']['numTimeStepsToSimulate'] - i) if np.min(self.param['constraints']['transitionTimes']['maxStayTimeCO2CAP_Off']) < self.param['controlParameters']['numberOfTimeSteps'] else self.param['controlParameters']['numberOfTimeSteps']
                                elif k == 1:
                                    self.param['constraints']['transitionTimesStart']['minStayTimeCO2CAP'] = max(1,self.param['constraints']['transitionTimes']['minStayTimeCO2CAP_Startup'][j] - (self.param['controlParameters']['numTimeStepsToSimulate'] - i))
                                    self.param['constraints']['transitionTimesStart']['maxStayTimeCO2CAP'] = self.param['constraints']['transitionTimes']['maxStayTimeCO2CAP_Startup'][j] - (self.param['controlParameters']['numTimeStepsToSimulate'] - i) if np.min(self.param['constraints']['transitionTimes']['maxStayTimeCO2CAP_Startup']) < self.param['controlParameters']['numberOfTimeSteps'] else self.param['controlParameters']['numberOfTimeSteps']
                                elif k == 2:
                                    self.param['constraints']['transitionTimesStart']['minStayTimeCO2CAP'] = max(1,self.param['constraints']['transitionTimes']['minStayTimeCO2CAP_Standby'][j] - (self.param['controlParameters']['numTimeStepsToSimulate'] - i))
                                    self.param['constraints']['transitionTimesStart']['maxStayTimeCO2CAP'] = self.param['constraints']['transitionTimes']['maxStayTimeCO2CAP_Standby'][j] - (self.param['controlParameters']['numTimeStepsToSimulate'] - i) if np.min(self.param['constraints']['transitionTimes']['maxStayTimeCO2CAP_Standby']) < self.param['controlParameters']['numberOfTimeSteps'] else self.param['controlParameters']['numberOfTimeSteps']
                                elif k == 3:
                                    self.param['constraints']['transitionTimesStart']['minStayTimeCO2CAP'] = max(1,self.param['constraints']['transitionTimes']['minStayTimeCO2CAP_On'][j] - (self.param['controlParameters']['numTimeStepsToSimulate'] - i))
                                    self.param['constraints']['transitionTimesStart']['maxStayTimeCO2CAP'] = self.param['constraints']['transitionTimes']['maxStayTimeCO2CAP_On'][j] - (self.param['controlParameters']['numTimeStepsToSimulate'] - i) if np.min(self.param['constraints']['transitionTimes']['maxStayTimeCO2CAP_On']) < self.param['controlParameters']['numberOfTimeSteps'] else self.param['controlParameters']['numberOfTimeSteps']
                                elif k == 4:
                                    self.param['constraints']['transitionTimesStart']['minStayTimeCO2CAP'] = max(1,self.param['constraints']['transitionTimes']['minStayTimeCO2CAP_Shutdown'][j] - (self.param['controlParameters']['numTimeStepsToSimulate'] - i))
                                    self.param['constraints']['transitionTimesStart']['maxStayTimeCO2CAP'] = self.param['constraints']['transitionTimes']['maxStayTimeCO2CAP_Shutdown'][j] - (self.param['controlParameters']['numTimeStepsToSimulate'] - i) if np.min(self.param['constraints']['transitionTimes']['maxStayTimeCO2CAP_Shutdown']) < self.param['controlParameters']['numberOfTimeSteps'] else self.param['controlParameters']['numberOfTimeSteps']
                                valueFound = True

                valueFound = False
                for i in range(self.param['controlParameters']['numTimeStepsToSimulate']-1, 0, -1):
                    for j in range(np.shape(self.param['initialData']['input']['currentStateSwitchSYNRaw'])[1]):
                        for k in range(np.shape(self.param['initialData']['input']['currentStateSwitchSYNRaw'])[2]):
                            if int(self.param['initialData']['input']['currentStateSwitchSYNRaw'][i,j,k]) == 1 and j != k and valueFound == False:
                                self.param['startValues']['stateSYN'] = k
                                if k == 0:
                                    self.param['constraints']['transitionTimesStart']['minStayTimeSYN'] = max(1,self.param['constraints']['transitionTimes']['minStayTimeSYN_Off'][j] - (self.param['controlParameters']['numTimeStepsToSimulate'] - i))
                                    self.param['constraints']['transitionTimesStart']['maxStayTimeSYN'] = self.param['constraints']['transitionTimes']['maxStayTimeSYN_Off'][j] - (self.param['controlParameters']['numTimeStepsToSimulate'] - i) if np.min(self.param['constraints']['transitionTimes']['maxStayTimeSYN_Off']) < self.param['controlParameters']['numberOfTimeSteps'] else self.param['controlParameters']['numberOfTimeSteps']
                                elif k == 1:
                                    self.param['constraints']['transitionTimesStart']['minStayTimeSYN'] = max(1,self.param['constraints']['transitionTimes']['minStayTimeSYN_Startup'][j] - (self.param['controlParameters']['numTimeStepsToSimulate'] - i))
                                    self.param['constraints']['transitionTimesStart']['maxStayTimeSYN'] = self.param['constraints']['transitionTimes']['maxStayTimeSYN_Startup'][j] - (self.param['controlParameters']['numTimeStepsToSimulate'] - i) if np.min(self.param['constraints']['transitionTimes']['maxStayTimeSYN_Startup']) < self.param['controlParameters']['numberOfTimeSteps'] else self.param['controlParameters']['numberOfTimeSteps']
                                elif k == 2:
                                    self.param['constraints']['transitionTimesStart']['minStayTimeSYN'] = max(1,self.param['constraints']['transitionTimes']['minStayTimeSYN_Standby'][j] - (self.param['controlParameters']['numTimeStepsToSimulate'] - i))
                                    self.param['constraints']['transitionTimesStart']['maxStayTimeSYN'] = self.param['constraints']['transitionTimes']['maxStayTimeSYN_Standby'][j] - (self.param['controlParameters']['numTimeStepsToSimulate'] - i) if np.min(self.param['constraints']['transitionTimes']['maxStayTimeSYN_Standby']) < self.param['controlParameters']['numberOfTimeSteps'] else self.param['controlParameters']['numberOfTimeSteps']
                                elif k == 3:
                                    self.param['constraints']['transitionTimesStart']['minStayTimeSYN'] = max(1,self.param['constraints']['transitionTimes']['minStayTimeSYN_On'][j] - (self.param['controlParameters']['numTimeStepsToSimulate'] - i))
                                    self.param['constraints']['transitionTimesStart']['maxStayTimeSYN'] = self.param['constraints']['transitionTimes']['maxStayTimeSYN_On'][j] - (self.param['controlParameters']['numTimeStepsToSimulate'] - i) if np.min(self.param['constraints']['transitionTimes']['maxStayTimeSYN_On']) < self.param['controlParameters']['numberOfTimeSteps'] else self.param['controlParameters']['numberOfTimeSteps']
                                elif k == 4:
                                    self.param['constraints']['transitionTimesStart']['minStayTimeSYN'] = max(1,self.param['constraints']['transitionTimes']['minStayTimeSYN_Shutdown'][j] - (self.param['controlParameters']['numTimeStepsToSimulate'] - i))
                                    self.param['constraints']['transitionTimesStart']['maxStayTimeSYN'] = self.param['constraints']['transitionTimes']['maxStayTimeSYN_Shutdown'][j] - (self.param['controlParameters']['numTimeStepsToSimulate'] - i) if np.min(self.param['constraints']['transitionTimes']['maxStayTimeSYN_Shutdown']) < self.param['controlParameters']['numberOfTimeSteps'] else self.param['controlParameters']['numberOfTimeSteps']
                                
                                valueFound = True

                valueFound = False
                for i in range(self.param['controlParameters']['numTimeStepsToSimulate']-1, 0, -1):
                    for j in range(np.shape(self.param['initialData']['input']['currentStateSwitchDISRaw'])[1]):
                        for k in range(np.shape(self.param['initialData']['input']['currentStateSwitchDISRaw'])[2]):
                            if int(self.param['initialData']['input']['currentStateSwitchDISRaw'][i,j,k]) == 1 and j != k and valueFound == False:
                                self.param['startValues']['stateDIS'] = k
                                if k == 0:
                                    self.param['constraints']['transitionTimesStart']['minStayTimeDIS'] = max(1,self.param['constraints']['transitionTimes']['minStayTimeDIS_Off'][j] - (self.param['controlParameters']['numTimeStepsToSimulate'] - i))
                                    self.param['constraints']['transitionTimesStart']['maxStayTimeDIS'] = self.param['constraints']['transitionTimes']['maxStayTimeDIS_Off'][j] - (self.param['controlParameters']['numTimeStepsToSimulate'] - i) if np.min(self.param['constraints']['transitionTimes']['maxStayTimeDIS_Off']) < self.param['controlParameters']['numberOfTimeSteps'] else self.param['controlParameters']['numberOfTimeSteps']
                                elif k == 1:
                                    self.param['constraints']['transitionTimesStart']['minStayTimeDIS'] = max(1,self.param['constraints']['transitionTimes']['minStayTimeDIS_Startup'][j] - (self.param['controlParameters']['numTimeStepsToSimulate'] - i))
                                    self.param['constraints']['transitionTimesStart']['maxStayTimeDIS'] = self.param['constraints']['transitionTimes']['maxStayTimeDIS_Startup'][j] - (self.param['controlParameters']['numTimeStepsToSimulate'] - i) if np.min(self.param['constraints']['transitionTimes']['maxStayTimeDIS_Startup']) < self.param['controlParameters']['numberOfTimeSteps'] else self.param['controlParameters']['numberOfTimeSteps']
                                elif k == 2:
                                    self.param['constraints']['transitionTimesStart']['minStayTimeDIS'] = max(1,self.param['constraints']['transitionTimes']['minStayTimeDIS_Standby'][j] - (self.param['controlParameters']['numTimeStepsToSimulate'] - i))
                                    self.param['constraints']['transitionTimesStart']['maxStayTimeDIS'] = self.param['constraints']['transitionTimes']['maxStayTimeDIS_Standby'][j] - (self.param['controlParameters']['numTimeStepsToSimulate'] - i) if np.min(self.param['constraints']['transitionTimes']['maxStayTimeDIS_Standby']) < self.param['controlParameters']['numberOfTimeSteps'] else self.param['controlParameters']['numberOfTimeSteps']
                                elif k == 3:
                                    self.param['constraints']['transitionTimesStart']['minStayTimeDIS'] = max(1,self.param['constraints']['transitionTimes']['minStayTimeDIS_On'][j] - (self.param['controlParameters']['numTimeStepsToSimulate'] - i))
                                    self.param['constraints']['transitionTimesStart']['maxStayTimeDIS'] = self.param['constraints']['transitionTimes']['maxStayTimeDIS_On'][j] - (self.param['controlParameters']['numTimeStepsToSimulate'] - i) if np.min(self.param['constraints']['transitionTimes']['maxStayTimeDIS_On']) < self.param['controlParameters']['numberOfTimeSteps'] else self.param['controlParameters']['numberOfTimeSteps']
                                elif k == 4:
                                    self.param['constraints']['transitionTimesStart']['minStayTimeDIS'] = max(1,self.param['constraints']['transitionTimes']['minStayTimeDIS_Shutdown'][j] - (self.param['controlParameters']['numTimeStepsToSimulate'] - i))
                                    self.param['constraints']['transitionTimesStart']['maxStayTimeDIS'] = self.param['constraints']['transitionTimes']['maxStayTimeDIS_Shutdown'][j] - (self.param['controlParameters']['numTimeStepsToSimulate'] - i) if np.min(self.param['constraints']['transitionTimes']['maxStayTimeDIS_Shutdown']) < self.param['controlParameters']['numberOfTimeSteps'] else self.param['controlParameters']['numberOfTimeSteps']
                                
                                valueFound = True
                
                for j in range(np.shape(self.param['initialData']['input']['modeElectrolyserRaw'])[1]):
                    for k in range(np.shape(self.param['initialData']['input']['modeElectrolyserRaw'])[2]):
                        if int(self.param['initialData']['input']['modeElectrolyserRaw'][self.param['controlParameters']['numTimeStepsToSimulate']-1,j,k]) == 1:
                            self.param['startValues']['modeElectrolyser'][j] = k 

                # Operating points
                for j in range(np.shape(self.param['initialData']['input']['operationPoint_CO2CAP'])[1]):
                    if int(self.param['initialData']['input']['operationPoint_CO2CAP'][self.param['controlParameters']['numTimeStepsToSimulate'],j]) == 1:
                        self.param['startValues']['operatingPointCO2CAP'] = j
                        print(j)
                
                for j in range(np.shape(self.param['initialData']['input']['operationPoint_SYN'])[1]):
                    if int(self.param['initialData']['input']['operationPoint_SYN'][self.param['controlParameters']['numTimeStepsToSimulate'],j]) == 1:
                        self.param['startValues']['operatingPointSYN'] = j  
                        print(j)

                for j in range(np.shape(self.param['initialData']['input']['operationPoint_DIS'])[1]):
                    if int(self.param['initialData']['input']['operationPoint_DIS'][self.param['controlParameters']['numTimeStepsToSimulate'],j]) == 1:
                        self.param['startValues']['operatingPointDIS'] = j
                        print(j)

                # Storages
                self.param['storageH2']['InitialPressure'] = self.param['initialData']["output_Scheduling"]['storageH2Pressure'][self.param['controlParameters']['numTimeStepsToSimulate']-1]
                self.param['storageH2']['InitialFilling'] = self.param['storageH2']['InitialPressure']*100000*self.param['storageH2']['Volume'] / (self.param['R_H2']*(self.param['Tamb'] + self.param['T0']))
                self.param['storageMethanolWater']['InitialFilling'] = self.param['initialData']["output_Scheduling"]['storageMethanolWaterFilling'][self.param['controlParameters']['numTimeStepsToSimulate']-1]
                self.param['battery']['initialCharge'] = self.param['initialData']["output_Scheduling"]['batteryCharge'][self.param['controlParameters']['numTimeStepsToSimulate']-1] * self.param['battery']['power'] / 100 # Umrechnen von Prozent in Kapazität


                # Methanol produced 
                for i in range(0,self.param['controlParameters']['numTimeStepsToSimulate']):
                    self.param['controlParameters']['prodMethanolLastTimeInterval'] = self.param['controlParameters']['prodMethanolLastTimeInterval'] + self.param['initialData']['output_Scheduling']['massFlowMethanolOut'][i]
            
                self.param['controlParameters']['currStartTimeLastOptHorizon'] = int((iteration % (self.param['controlParameters']['numberOfTimeSteps'] / self.param['controlParameters']['numTimeStepsToSimulate'])) * self.param['controlParameters']['numTimeStepsToSimulate'])
                self.param['controlParameters']['numTimeStepsToHorizonEnd'] = self.param['controlParameters']['numberOfTimeSteps'] - self.param['controlParameters']['currStartTimeLastOptHorizon']
                
                # Storage filling level change
                self.param['constraints']['hydrogenStorageEqualTime'] = self.param['controlParameters']['numTimeStepsToHorizonEnd'] - 1
                self.param['constraints']['methanolWaterStorageEqualTime'] = self.param['controlParameters']['numTimeStepsToHorizonEnd'] - 1
                self.param['constraints']['batteryChargeEqualTime'] = self.param['controlParameters']['numTimeStepsToHorizonEnd'] - 1

                if self.param['controlParameters']['currStartTimeLastOptHorizon'] == 0:
                    self.param['controlParameters']['prodMethanolLastTimeInterval'] = 0
                    self.param['constraints']['hydrogenStorageEqualTime'] = self.param['controlParameters']['numberOfTimeSteps'] - 1


        
    def funcGet(self, j):

        ## Parameter
        self.param = {}

        # Production constants
        self.param['production'] = {}
        self.param['production']['minMethanolBenchmark'] = 10
        self.param['production']['minMethanolOpt'] = 50 #113.75 #108.065
        self.param['production']['methanol'] = 0      
        
        
        ## Methanol
        self.param['methanol'] = {}

    
        ## Methane   
        self.param['methane'] = {}
        self.param['methane']['brennwert'] = 11.1
    

        ## Control parameters
        self.param['controlParameters'] = {}
        self.param['controlParameters']['optimizationHorizon'] = self.optimizationHorizon
        self.param['controlParameters']['timeStep'] = self.timeStep
        self.param['controlParameters']['numberOfTimeSteps'] = int(self.optimizationHorizon / self.timeStep)
        self.param['controlParameters']['timeLimit'] = self.timeLimit
        self.param['controlParameters']['optimalityGap'] = self.optimalityGap
        self.param['controlParameters']['testFeasibility'] = self.testFeasibility
        self.param['controlParameters']['numHoursToSimulate'] = self.numHoursToSimulate
        self.param['controlParameters']['numTimeStepsToSimulate'] = int(self.numHoursToSimulate / self.timeStep)
        self.param['controlParameters']['numTimeStepsToHorizonEnd'] = int(self.numHoursToSimulate / self.timeStep)
        self.param['controlParameters']['startTime'] = self.startTime
        self.param['controlParameters']['startTimeIteration'] = self.param['controlParameters']['startTime']
        self.param['controlParameters']['useRealForecast'] = self.useRealForecast
        self.param['controlParameters']['objectiveFunction'] = self.objectiveFunction
        self.param['controlParameters']['benchmark'] = self.benchmark
        self.param['controlParameters']['sameOutputAsBenchmark'] = self.sameOutputAsBenchmark
        self.param['controlParameters']['rateOfChangeConstranints'] = self.rateOfChangeConstranints
        self.param['controlParameters']['transitionConstraints'] = self.transitionConstraints
        self.param['controlParameters']['powerSale'] = self.powerSale
        self.param['controlParameters']['powerPurchase'] = self.powerPurchase
        self.param['controlParameters']['considerPV'] = self.considerPV
        self.param['controlParameters']['considerBattery'] = self.considerBattery
        self.param['controlParameters']['peakLoadCapping'] = self.peakLoadCapping
        self.param['controlParameters']['pathCharMapData'] = self.strPathCharMapData
        self.param['controlParameters']['pathCharMapDataCalc'] = self.strPathCharMapDataCalc
        self.param['controlParameters']['pathPVData'] = self.strPathPVData 
        self.param['controlParameters']['pathPPData'] = self.strPathPPData
        self.param['controlParameters']['pathInitialData'] = self.strPathInitialData
        self.param['controlParameters']['pathAdaptationData'] = self.strPathAdaptationData

        self.param['controlParameters']['currStartTimeLastOptHorizon'] = 0
        self.param['controlParameters']['prodMethanolLastTimeInterval'] = 0

        self.param['controlParameters']['iteration'] = 0


        ## Characteristic field indices
        self.param['charMap'] = {}

        # Characteristic field indices CO2CAP
        self.param['charMap']['CO2CAP'] = {}
        self.param['charMap']['CO2CAP']['index'] = {}
        self.param['charMap']['CO2CAP']['index']['massFlowHydrogenIn'] = 3
        self.param['charMap']['CO2CAP']['index']['massFlowBiogasIn'] = 2
        self.param['charMap']['CO2CAP']['index']['massFlowBiogasOut'] = 9
        self.param['charMap']['CO2CAP']['index']['moleFractionMethaneBiogasOut'] = 7
        self.param['charMap']['CO2CAP']['index']['moleFractionCO2BiogasOut'] = 8
        self.param['charMap']['CO2CAP']['index']['massFlowSynthesisgasIn'] = 6
        self.param['charMap']['CO2CAP']['index']['moleFractionH2Synthesisgas'] = 4
        self.param['charMap']['CO2CAP']['index']['moleFractionCO2Synthesisgas'] = 5
        self.param['charMap']['CO2CAP']['index']['powerPlantComponentsUnit1'] = 19
        self.param['charMap']['CO2CAP']['numVars'] = 9

        # Characteristic field indices SYN
        self.param['charMap']['SYN'] = {}
        self.param['charMap']['SYN']['index'] = {}
        self.param['charMap']['SYN']['index']['massFlowSynthesisgasIn'] = 2
        self.param['charMap']['SYN']['index']['massFlowHydrogenIn'] = 3
        self.param['charMap']['SYN']['index']['massFlowMethanolWaterStorageIn'] = 5
        self.param['charMap']['SYN']['index']['densityMethanolWaterStorageIn'] = 4
        self.param['charMap']['SYN']['index']['massFlowSynthesisPurge'] = 7
        self.param['charMap']['SYN']['index']['moleFractionCO2SynthesisPurge'] = 6
        self.param['charMap']['SYN']['index']['powerPlantComponentsUnit2'] = 20
        self.param['charMap']['SYN']['numVars'] = 7

        # Characteristic field indices DIS
        self.param['charMap']['DIS'] = {}
        self.param['charMap']['DIS']['index'] = {}
        self.param['charMap']['DIS']['index']['massFlowMethanolWaterStorageOut'] = 2
        self.param['charMap']['DIS']['index']['massFlowMethanolOut'] = 5
        self.param['charMap']['DIS']['index']['moleFractionMethanolOut'] = 18
        self.param['charMap']['DIS']['index']['powerPlantComponentsUnit3'] = 17
        self.param['charMap']['DIS']['numVars'] = 4



        ## Biogas parameters
        self.param['biogas'] = {}
        self.param['biogas']['temperatureIn'] = 253.15
        self.param['biogas']['temperatureOut'] = 253.15
        self.param['biogas']['pressureIn'] = 3
        self.param['biogas']['pressureOut'] = 3
        self.param['biogas']['densityIn'] = 3.73426
        self.param['biogas']['brennwert'] = 6.5
        self.param['biogas']['minimumMoleFractionMethane'] = 0.94



        ## Thermodynamic and chemical parameters
        self.param['p0'] = 1.013
        self.param['T0'] = 273.15
        self.param['Tamb'] = 21
        self.param['R_H2'] = 4124.3              # http://www.thermodynamik-online.de/Tabellen/Naturkonstanten,%20Umrechnungen,%20kritische%20Gro%CC%88%C3%9Fen.pdf
        self.param['R_CO2'] = 188.92             # http://www.thermodynamik-online.de/Tabellen/Naturkonstanten,%20Umrechnungen,%20kritische%20Gro%CC%88%C3%9Fen.pdf
        self.param['R_MEOH'] = 259.5             # http://www.thermodynamik-online.de/Tabellen/Naturkonstanten,%20Umrechnungen,%20kritische%20Gro%CC%88%C3%9Fen.pdf
        self.param['R_H2O'] = 461.53             # http://www.thermodynamik-online.de/Tabellen/Naturkonstanten,%20Umrechnungen,%20kritische%20Gro%CC%88%C3%9Fen.pdf
        self.param['R_CH4'] = 518.26             # http://www.thermodynamik-online.de/Tabellen/Naturkonstanten,%20Umrechnungen,%20kritische%20Gro%CC%88%C3%9Fen.pdf

        self.param['fractionSynthesisgasCH4'] = 0.00372
        self.param['fractionSynthesisgasH2O'] = 0.00045
        self.param['fractionSynthesisgasMEOH'] = 0.00971
        self.param['fractionSynthesisgasCO2'] = 0.86698
        self.param['fractionSynthesisgasH2'] = 0.11914
        self.param['R_Synthesisgas'] = self.param['fractionSynthesisgasH2'] * self.param['R_H2'] \
                                    + self.param['fractionSynthesisgasCO2'] * self.param['R_CO2'] \
                                    + self.param['fractionSynthesisgasMEOH'] * self.param['R_MEOH'] \
                                    + self.param['fractionSynthesisgasH2O'] * self.param['R_H2O'] \
                                    + self.param['fractionSynthesisgasCH4'] * self.param['R_CH4']



        ## Cost function
        self.param['costFunction'] = {}
        self.param['costFunction']['economicFactor'] = 1
        self.param['costFunction']['ecologicalFactor'] = 0



        ## Prices of products
        self.param['prices'] = {}
        self.param['prices']['biogas'] = 0.2
        self.param['prices']['methane'] = 0.2
        self.param['prices']['methanol'] = 1
        self.param['prices']['powerSold'] = 0.238
        self.param['prices']['numberOfUncertaintySamples'] = 100



        ## Peak load capping
        self.param['peakLoadCapping'] = {}
        self.param['peakLoadCapping']['maximumLoad'] = 0.8 * 50         # with 50kW being the maximum power input of the whole plant


        
        ## Carbon intensity
        self.param['carbonIntensity'] = {}
        self.param['carbonIntensity']['numberOfUncertaintySamples'] = 100



        ## PV
        self.param['pv'] = {}
        self.param['pv']['module'] = 'Canadian_Solar_CS5P_220M___2009_'
        self.param['pv']['inverter'] = 'ABB__PVI_3_0_OUTD_S_US__208V_'#'ABB__MICRO_0_25_I_OUTD_US_208__208V_'
        self.param['pv']['powerOfModule'] = 0.22
        self.param['pv']['powerOfSystem'] = 200
        self.param['pv']['numberOfUncertaintySamples'] = 100
        self.param['pv']['alpha'] = 0.9
        self.param['pv']['covariance'] = 8
        self.param["pv"]["strPvLat"] = "49.09"
        self.param["pv"]["strPvLon"] = "8.44"



        ## Battery
        self.param['battery'] = {}                                                   # https://www.bsl-battery.com/100kwh-commercial-solar-battery-storage.html
        self.param['battery']['power'] = 300#50             # kWh
        self.param['battery']['voltage'] = 512#562          # V  
        self.param['battery']['capacity'] = self.param['battery']['power'] * 1000 / self.param['battery']['voltage']             # Ah
        self.param['battery']['minCharge'] = self.param['battery']['power'] * 0.05#0.01
        self.param['battery']['efficiency'] = 0.9#1
        self.param['battery']['maxChargeRate'] = self.param['battery']['power'] * 0.5#10          # kW
        self.param['battery']['minChargeRate'] = self.param['battery']['power'] * 0.01#1          # kW                # Annahme (aktuell nicht genutzt)
        self.param['battery']['maxDischargeRate'] = self.param['battery']['power'] * 0.5#10        # kW
        self.param['battery']['minDischargeRate'] = self.param['battery']['power'] * 0.01#1       # kW                # Annahme (aktuell nicht genutzt)
        self.param['battery']['initialCharge'] = 0.5*self.param['battery']['capacity'] * self.param['battery']['voltage'] / 1000



        ## Electrolyser
        self.param['electrolyser'] = {}
        self.param['electrolyser']['constant'] = 0.0187239583
        self.param['electrolyser']['numberOfEnapterModules'] = 8
        self.param['electrolyser']['powerLowerBound'] = 1.44
        self.param['electrolyser']['powerUpperBound'] = 2.4
        self.param['electrolyser']['standbyPower'] = 0.1
        self.param['electrolyser']['benchmarkPower'] = self.param['electrolyser']['powerUpperBound']

        self.param['electrolyser']['numberOperationPoints'] = 41
        self.param['electrolyser']['conversionValues'] = []

        for i in range(0, self.param['electrolyser']['numberOperationPoints']):
            self.param['electrolyser']['conversionValues'].append(self.param['electrolyser']['powerLowerBound'] + (self.param['electrolyser']['powerUpperBound'] - self.param['electrolyser']['powerLowerBound']) * i / (self.param['electrolyser']['numberOperationPoints'] - 1))



        ## Storages
        self.param['storageH2'] = {}
        self.param['storageMethanolWater'] = {}
        self.param['storageSynthesisgas'] = {}

        self.param['storageH2']['Volume'] = 1.7 #* 1.5
        self.param['storageMethanolWater']['Volume'] = 0.2 #* 1.5
        self.param['storageSynthesisgas']['Volume'] = 1.7 #* 1.5

        self.param['storageH2']['LowerBound'] = 15
        self.param['storageH2']['UpperBound'] = 35
        self.param['storageMethanolWater']['LowerBound'] = 0.01
        self.param['storageMethanolWater']['UpperBound'] = self.param['storageMethanolWater']['Volume']

        self.param['storageH2']['InitialFillingFactor'] = 0.5
        self.param['storageMethanolWater']['InitialFillingFactor'] = 0.5
        self.param['storageH2']['InitialPressure'] = self.param['storageH2']['InitialFillingFactor']*(self.param['storageH2']['UpperBound'] - self.param['storageH2']['LowerBound']) + self.param['storageH2']['LowerBound']
        self.param['storageH2']['InitialFilling'] = self.param['storageH2']['InitialPressure']*100000*self.param['storageH2']['Volume'] / (self.param['R_H2']*(self.param['Tamb'] + self.param['T0']))
        self.param['storageMethanolWater']['InitialFilling'] = self.param['storageMethanolWater']['InitialFillingFactor']*(self.param['storageMethanolWater']['UpperBound'] - self.param['storageMethanolWater']['LowerBound']) + self.param['storageMethanolWater']['LowerBound']
        self.param['storageMethanolWater']['InitialDensity'] = 731.972

        self.param['storageSynthesisgas']['LowerBound'] = 15
        self.param['storageSynthesisgas']['UpperBound'] = 35

        self.param['storageSynthesisgas']['InitialFillingFactor'] = 0.5
        self.param['storageSynthesisgas']['InitialPressure'] = self.param['storageSynthesisgas']['InitialFillingFactor']*(self.param['storageSynthesisgas']['UpperBound'] - self.param['storageSynthesisgas']['LowerBound']) + self.param['storageSynthesisgas']['LowerBound']
        self.param['storageSynthesisgas']['InitialFilling'] = self.param['storageSynthesisgas']['InitialPressure']*100000*self.param['storageSynthesisgas']['Volume'] / (self.param['R_Synthesisgas']*(self.param['Tamb'] + self.param['T0']))



        ## Start values
        self.param['startValues'] = {}
        self.param['startValues']['stateCO2CAP'] = 0            # off
        self.param['startValues']['stateSYN'] = 0               # off
        self.param['startValues']['stateDIS'] = 0               # off
        self.param['startValues']['modeElectrolyser'] = np.ones(self.param['electrolyser']['numberOfEnapterModules']) * 2       # off
        self.param['startValues']['operatingPointCO2CAP'] = 0   # off
        self.param['startValues']['operatingPointSYN'] = 0      # off
        self.param['startValues']['operatingPointDIS'] = 0      # off


        ## Storage constraints
        self.param['constraints'] = {}
        self.param['constraints']['storagesFactorFillEqualLower'] = 0.1

        if self.param['controlParameters']['benchmark'] == True:
            self.param['constraints']['storagesFactorFillEqualLower'] = 0.05
            self.param['constraints']['storagesFactorFillEqualUpper'] = 0.05
        else:
            self.param['constraints']['storagesFactorFillEqualLower'] = 0.05
            self.param['constraints']['storagesFactorFillEqualUpper'] = 0.05

        self.param['constraints']['methanolWaterStorageFillEqual'] = {}
        self.param['constraints']['methanolWaterStorageEqualValue'] =  self.param['storageMethanolWater']['InitialFilling']
        self.param['constraints']['methanolWaterStorageEqualTime'] =  self.param['controlParameters']['numberOfTimeSteps'] - 1
        self.param['constraints']['methanolWaterStorageFillEqual']['LowerBound'] = self.param['storageMethanolWater']['InitialFilling']*self.param['constraints']['storagesFactorFillEqualLower']
        self.param['constraints']['methanolWaterStorageFillEqual']['UpperBound'] = -self.param['storageMethanolWater']['InitialFilling']*self.param['constraints']['storagesFactorFillEqualUpper']

        self.param['constraints']['hydrogenStorageFillEqual'] = {}
        self.param['constraints']['hydrogenStorageEqualValue'] =  self.param['storageH2']['InitialPressure']
        self.param['constraints']['hydrogenStorageEqualTime'] =  self.param['controlParameters']['numberOfTimeSteps'] - 1
        self.param['constraints']['hydrogenStorageFillEqual']['LowerBound'] = self.param['storageH2']['InitialPressure']*self.param['constraints']['storagesFactorFillEqualLower']
        self.param['constraints']['hydrogenStorageFillEqual']['UpperBound'] = -self.param['storageH2']['InitialPressure']*self.param['constraints']['storagesFactorFillEqualUpper']

        self.param['constraints']['batteryChargeEqual'] = {}
        self.param['constraints']['batteryChargeEqualValue'] =  self.param['battery']['initialCharge']
        self.param['constraints']['batteryChargeEqualTime'] =  self.param['controlParameters']['numberOfTimeSteps'] - 1
        self.param['constraints']['batteryChargeEqual']['LowerBound'] = self.param['battery']['initialCharge']*self.param['constraints']['storagesFactorFillEqualLower']
        self.param['constraints']['batteryChargeEqual']['UpperBound'] = -self.param['battery']['initialCharge']*self.param['constraints']['storagesFactorFillEqualUpper']


        ## Transition times constraints
        self.param['constraints']['transitionTimes'] = {}
        self.param['constraints']['transitionTimes']['minStayTimeCO2CAP_Off'] = [int(1 / self.param['controlParameters']['timeStep']),
                                                                                         int(1 / self.param['controlParameters']['timeStep']),
                                                                                         int(1 / self.param['controlParameters']['timeStep']),
                                                                                         int(1 / self.param['controlParameters']['timeStep']),
                                                                                         int(1 / self.param['controlParameters']['timeStep'])]
        self.param['constraints']['transitionTimes']['minStayTimeCO2CAP_Startup'] = [int(6 / self.param['controlParameters']['timeStep']), #6
                                                                                             int(1 / self.param['controlParameters']['timeStep']),
                                                                                             int(2 / self.param['controlParameters']['timeStep']), #2
                                                                                             int(1 / self.param['controlParameters']['timeStep']),
                                                                                             int(1 / self.param['controlParameters']['timeStep'])]
        self.param['constraints']['transitionTimes']['minStayTimeCO2CAP_Standby'] = [int(1 / self.param['controlParameters']['timeStep']),
                                                                                             int(1 / self.param['controlParameters']['timeStep']),
                                                                                             int(1 / self.param['controlParameters']['timeStep']),
                                                                                             int(1 / self.param['controlParameters']['timeStep']),
                                                                                             int(1 / self.param['controlParameters']['timeStep'])]
        self.param['constraints']['transitionTimes']['minStayTimeCO2CAP_On'] = [int(1 / self.param['controlParameters']['timeStep']),
                                                                                        int(1 / self.param['controlParameters']['timeStep']),
                                                                                        int(1 / self.param['controlParameters']['timeStep']),
                                                                                        int(1 / self.param['controlParameters']['timeStep']),
                                                                                        int(1 / self.param['controlParameters']['timeStep'])]
        self.param['constraints']['transitionTimes']['minStayTimeCO2CAP_Shutdown'] = [int(1 / self.param['controlParameters']['timeStep']),
                                                                                        int(1 / self.param['controlParameters']['timeStep']),
                                                                                        int(4 / self.param['controlParameters']['timeStep']),   #4
                                                                                        int(6 / self.param['controlParameters']['timeStep']),   #6
                                                                                        int(1 / self.param['controlParameters']['timeStep'])]
        
        self.param['constraints']['transitionTimes']['minStayTimeSYN_Off'] = [int(1 / self.param['controlParameters']['timeStep']),
                                                                                         int(1 / self.param['controlParameters']['timeStep']),
                                                                                         int(1 / self.param['controlParameters']['timeStep']),
                                                                                         int(1 / self.param['controlParameters']['timeStep']),
                                                                                         int(1 / self.param['controlParameters']['timeStep'])]
        self.param['constraints']['transitionTimes']['minStayTimeSYN_Startup'] = [int(12 / self.param['controlParameters']['timeStep']), #12
                                                                                             int(1 / self.param['controlParameters']['timeStep']),
                                                                                             int(4 / self.param['controlParameters']['timeStep']), #4
                                                                                             int(1 / self.param['controlParameters']['timeStep']),
                                                                                             int(1 / self.param['controlParameters']['timeStep'])]
        self.param['constraints']['transitionTimes']['minStayTimeSYN_Standby'] = [int(1 / self.param['controlParameters']['timeStep']),
                                                                                             int(1 / self.param['controlParameters']['timeStep']),
                                                                                             int(1 / self.param['controlParameters']['timeStep']),
                                                                                             int(1 / self.param['controlParameters']['timeStep']),
                                                                                             int(1 / self.param['controlParameters']['timeStep'])]
        self.param['constraints']['transitionTimes']['minStayTimeSYN_On'] = [int(1 / self.param['controlParameters']['timeStep']),
                                                                                        int(1 / self.param['controlParameters']['timeStep']),
                                                                                        int(1 / self.param['controlParameters']['timeStep']),
                                                                                        int(1 / self.param['controlParameters']['timeStep']),
                                                                                        int(1 / self.param['controlParameters']['timeStep'])]
        self.param['constraints']['transitionTimes']['minStayTimeSYN_Shutdown'] = [int(1 / self.param['controlParameters']['timeStep']),
                                                                                        int(1 / self.param['controlParameters']['timeStep']),
                                                                                        int(8 / self.param['controlParameters']['timeStep']),   #8
                                                                                        int(10 / self.param['controlParameters']['timeStep']),   #10
                                                                                        int(1 / self.param['controlParameters']['timeStep'])]

        self.param['constraints']['transitionTimes']['minStayTimeDIS_Off'] = [int(1 / self.param['controlParameters']['timeStep']),
                                                                                    int(1 / self.param['controlParameters']['timeStep']),
                                                                                    int(1 / self.param['controlParameters']['timeStep']),
                                                                                    int(1 / self.param['controlParameters']['timeStep']),
                                                                                    int(1 / self.param['controlParameters']['timeStep'])]
        self.param['constraints']['transitionTimes']['minStayTimeDIS_Startup'] = [int(6 / self.param['controlParameters']['timeStep']),     #6
                                                                                        int(1 / self.param['controlParameters']['timeStep']),
                                                                                        int(3 / self.param['controlParameters']['timeStep']),   #3
                                                                                        int(1 / self.param['controlParameters']['timeStep']),
                                                                                        int(1 / self.param['controlParameters']['timeStep'])]
        self.param['constraints']['transitionTimes']['minStayTimeDIS_Standby'] = [int(1 / self.param['controlParameters']['timeStep']),
                                                                                        int(1 / self.param['controlParameters']['timeStep']),
                                                                                        int(1 / self.param['controlParameters']['timeStep']),
                                                                                        int(1 / self.param['controlParameters']['timeStep']),
                                                                                        int(1 / self.param['controlParameters']['timeStep'])]
        self.param['constraints']['transitionTimes']['minStayTimeDIS_On'] = [int(1 / self.param['controlParameters']['timeStep']),
                                                                                    int(1 / self.param['controlParameters']['timeStep']),
                                                                                    int(1 / self.param['controlParameters']['timeStep']),
                                                                                    int(1 / self.param['controlParameters']['timeStep']),
                                                                                    int(1 / self.param['controlParameters']['timeStep'])]
        self.param['constraints']['transitionTimes']['minStayTimeDIS_Shutdown'] = [int(1 / self.param['controlParameters']['timeStep']),
                                                                                        int(1 / self.param['controlParameters']['timeStep']),
                                                                                        int(2 / self.param['controlParameters']['timeStep']),   #2
                                                                                        int(4 / self.param['controlParameters']['timeStep']),   #4
                                                                                        int(1 / self.param['controlParameters']['timeStep'])]
        
        self.param['constraints']['transitionTimes']['maxStayTimeCO2CAP_Off'] = [self.param['controlParameters']['numberOfTimeSteps'],
                                                                                         self.param['controlParameters']['numberOfTimeSteps'],
                                                                                         self.param['controlParameters']['numberOfTimeSteps'],
                                                                                         self.param['controlParameters']['numberOfTimeSteps'],
                                                                                         self.param['controlParameters']['numberOfTimeSteps']]
        self.param['constraints']['transitionTimes']['maxStayTimeCO2CAP_Startup'] = [int(12 / self.param['controlParameters']['timeStep']),
                                                                                            self.param['controlParameters']['numberOfTimeSteps'],
                                                                                            int(4 / self.param['controlParameters']['timeStep']),
                                                                                            self.param['controlParameters']['numberOfTimeSteps'],
                                                                                            self.param['controlParameters']['numberOfTimeSteps']]
        self.param['constraints']['transitionTimes']['maxStayTimeCO2CAP_Standby'] = [self.param['controlParameters']['numberOfTimeSteps'],
                                                                                            self.param['controlParameters']['numberOfTimeSteps'],
                                                                                            self.param['controlParameters']['numberOfTimeSteps'],
                                                                                            self.param['controlParameters']['numberOfTimeSteps'],
                                                                                            self.param['controlParameters']['numberOfTimeSteps']]
        self.param['constraints']['transitionTimes']['maxStayTimeCO2CAP_On'] = [self.param['controlParameters']['numberOfTimeSteps'],
                                                                                                self.param['controlParameters']['numberOfTimeSteps'],
                                                                                                self.param['controlParameters']['numberOfTimeSteps'],
                                                                                                self.param['controlParameters']['numberOfTimeSteps'],
                                                                                                self.param['controlParameters']['numberOfTimeSteps']]
        self.param['constraints']['transitionTimes']['maxStayTimeCO2CAP_Shutdown'] = [self.param['controlParameters']['numberOfTimeSteps'],
                                                                                                self.param['controlParameters']['numberOfTimeSteps'],
                                                                                                int(4 / self.param['controlParameters']['timeStep']),
                                                                                                int(6 / self.param['controlParameters']['timeStep']),
                                                                                                self.param['controlParameters']['numberOfTimeSteps']]
        
        self.param['constraints']['transitionTimes']['maxStayTimeSYN_Off'] = [self.param['controlParameters']['numberOfTimeSteps'],
                                                                                         self.param['controlParameters']['numberOfTimeSteps'],
                                                                                         self.param['controlParameters']['numberOfTimeSteps'],
                                                                                         self.param['controlParameters']['numberOfTimeSteps'],
                                                                                         self.param['controlParameters']['numberOfTimeSteps']]
        self.param['constraints']['transitionTimes']['maxStayTimeSYN_Startup'] = [int(12 / self.param['controlParameters']['timeStep']),
                                                                                            self.param['controlParameters']['numberOfTimeSteps'],
                                                                                            int(4 / self.param['controlParameters']['timeStep']),
                                                                                            self.param['controlParameters']['numberOfTimeSteps'],
                                                                                            self.param['controlParameters']['numberOfTimeSteps']]
        self.param['constraints']['transitionTimes']['maxStayTimeSYN_Standby'] = [self.param['controlParameters']['numberOfTimeSteps'],
                                                                                            self.param['controlParameters']['numberOfTimeSteps'],
                                                                                            self.param['controlParameters']['numberOfTimeSteps'],
                                                                                            self.param['controlParameters']['numberOfTimeSteps'],
                                                                                            self.param['controlParameters']['numberOfTimeSteps']]
        self.param['constraints']['transitionTimes']['maxStayTimeSYN_On'] = [self.param['controlParameters']['numberOfTimeSteps'],
                                                                                                self.param['controlParameters']['numberOfTimeSteps'],
                                                                                                self.param['controlParameters']['numberOfTimeSteps'],
                                                                                                self.param['controlParameters']['numberOfTimeSteps'],
                                                                                                self.param['controlParameters']['numberOfTimeSteps']]
        self.param['constraints']['transitionTimes']['maxStayTimeSYN_Shutdown'] = [self.param['controlParameters']['numberOfTimeSteps'],
                                                                                                self.param['controlParameters']['numberOfTimeSteps'],
                                                                                                int(4 / self.param['controlParameters']['timeStep']),
                                                                                                int(6 / self.param['controlParameters']['timeStep']),
                                                                                                self.param['controlParameters']['numberOfTimeSteps']]

        self.param['constraints']['transitionTimes']['maxStayTimeDIS_Off'] = [self.param['controlParameters']['numberOfTimeSteps'],
                                                                                    self.param['controlParameters']['numberOfTimeSteps'],
                                                                                    self.param['controlParameters']['numberOfTimeSteps'],
                                                                                    self.param['controlParameters']['numberOfTimeSteps'],
                                                                                    self.param['controlParameters']['numberOfTimeSteps']]
        self.param['constraints']['transitionTimes']['maxStayTimeDIS_Startup'] = [int(6 / self.param['controlParameters']['timeStep']),
                                                                                        self.param['controlParameters']['numberOfTimeSteps'],
                                                                                        int(3 / self.param['controlParameters']['timeStep']),
                                                                                        self.param['controlParameters']['numberOfTimeSteps'],
                                                                                        self.param['controlParameters']['numberOfTimeSteps']]
        self.param['constraints']['transitionTimes']['maxStayTimeDIS_Standby'] = [self.param['controlParameters']['numberOfTimeSteps'],
                                                                                         self.param['controlParameters']['numberOfTimeSteps'],
                                                                                         self.param['controlParameters']['numberOfTimeSteps'],
                                                                                         self.param['controlParameters']['numberOfTimeSteps'],
                                                                                         self.param['controlParameters']['numberOfTimeSteps']]
        self.param['constraints']['transitionTimes']['maxStayTimeDIS_On'] = [self.param['controlParameters']['numberOfTimeSteps'],
                                                                                    self.param['controlParameters']['numberOfTimeSteps'],
                                                                                    self.param['controlParameters']['numberOfTimeSteps'],
                                                                                    self.param['controlParameters']['numberOfTimeSteps'],
                                                                                    self.param['controlParameters']['numberOfTimeSteps']]
        self.param['constraints']['transitionTimes']['maxStayTimeDIS_Shutdown'] = [self.param['controlParameters']['numberOfTimeSteps'],
                                                                                        self.param['controlParameters']['numberOfTimeSteps'],
                                                                                        int(2 / self.param['controlParameters']['timeStep']),
                                                                                        int(4 / self.param['controlParameters']['timeStep']),
                                                                                        self.param['controlParameters']['numberOfTimeSteps']]
        
        
        ## Start Values constraints
        self.param['constraints']['transitionTimesStart'] = {}
        self.param['constraints']['transitionTimesStart']['minStayTimeCO2CAP'] = 1
        self.param['constraints']['transitionTimesStart']['minStayTimeSYN'] =  1
        self.param['constraints']['transitionTimesStart']['minStayTimeDIS'] = 1

        self.param['constraints']['transitionTimesStart']['maxStayTimeCO2CAP'] = self.param['controlParameters']['numberOfTimeSteps']
        self.param['constraints']['transitionTimesStart']['maxStayTimeSYN'] = self.param['controlParameters']['numberOfTimeSteps']
        self.param['constraints']['transitionTimesStart']['maxStayTimeDIS'] = self.param['controlParameters']['numberOfTimeSteps']