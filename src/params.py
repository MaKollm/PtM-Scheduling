#!/usr/bin/env python3.10

import scipy.io as sio
import gurobipy as gp
import os
import pickle
from gurobipy import GRB

class Param():

    def __init__(self, args):

        if len(args) > 0:
            self.optimizationHorizon = args[0]
            self.timeStep = args[1]
            self.timeLimit = args[2]
            self.optimalityGap = args[3]
            self.testFeasibility = args[4]

            self.numHoursToSimulate = args[5]

            self.objectiveFunction = args[6]

            self.benchmark = args[7]
            self.sameOutputAsBenchmark = args[8]

            self.rateOfChangeConstranints = args[9]
            self.transitionConstraints = args[10]
            self.powerSale = args[11]
            self.powerPurchase = args[12]
            self.considerPV = args[13]
            self.considerBattery = args[14]
            self.peakLoadCapping = args[15]


            self.strPathCharMapData = args[16]
            self.strPathCharMapDataCalc = args[17]
            self.strPathPVData = args[18]
            self.strPathPPData = args[19]
            self.strPathInitialData = args[20]
            self.strPathAdaptationData = args[21]
        

    def funcUpdate(self, pv, pp, ci, iteration):
        self.param['pv']['powerAvailable'] = pv.arrPowerAvailable
        self.param['prices']['power'] = pp.arrPowerPriceHourly
        self.param['carbonIntensity']['carbonIntensity'] = ci.arrCarbonIntensityHourly
        
        """
        if iteration > 0:
            self.param['controlParameters']['currStartTimeLastOptHorizon'] = int((iteration % (self.param['controlParameters']['numberOfTimeSteps'] / self.param['controlParameters']['numTimeStepsToSimulate'])) * self.param['controlParameters']['numTimeStepsToSimulate'])
            outputData = sio.loadmat(r'C:\PROJEKTE\PTX\Max\21_Scheduling\gurobi\PtM\data_opt_trueCharMap')
            
            for i in range(0,self.param['controlParameters']['numTimeStepsToSimulate']+1):
                self.param['controlParameters']['prodMethanolLastTimeInterval'] = self.param['controlParameters']['prodMethanolLastTimeInterval'] + outputData['output']['massFlowMethanolOut'][0][0][0][i]

            if self.param['controlParameters']['currStartTimeLastOptHorizon'] >= self.param['controlParameters']['numberOfTimeSteps'] - self.param['controlParameters']['numTimeStepsToSimulate']:
                self.param['controlParameters']['currStartTimeLastOptHorizon'] = 0
                self.param['controlParameters']['prodMethanolLastTimeInterval'] = 0

                self.param['battery']['initialCharge'] = outputData['output']['batteryCharge'][0][0][0][self.param['controlParameters']['numTimeStepsToSimulate']+1]
                self.param['storageMethanolWater']['InitialFilling'] = outputData['output']['storageMethanolWaterFilling'][0][0][0][self.param['controlParameters']['numTimeStepsToSimulate']+1]
                self.param['storageH2']['InitialPressure'] = outputData['output']['storageH2Pressure'][0][0][0][self.param['controlParameters']['numTimeStepsToSimulate']+1]
                self.param['storageH2']['InitialFilling'] = self.param['storageH2']['InitialPressure']*100000*self.param['storageH2']['Volume'] / (self.param['R_H2']*(self.param['Tamb'] + self.param['T0']))
                self.param['storageSynthesisgas']['InitialPressure'] = outputData['output']['storageSynthesisgasPressure'][0][0][0][self.param['controlParameters']['numTimeStepsToSimulate']+1]
                self.param['storageSynthesisgas']['InitialFilling'] = self.param['storageSynthesisgas']['InitialPressure']*100000*self.param['storageSynthesisgas']['Volume'] / (self.param['R_Synthesisgas']*(self.param['Tamb'] + self.param['T0']))
        """

    def funcUpdateStorageParameters(self, resultOpt, optModel):
        if self.param['controlParameters']['objectiveFunction'] == 4 or self.param['controlParameters']['objectiveFunction'] == 6 or self.param['controlParameters']['objectiveFunction'] == 10:
            if optModel.m.status == GRB.INFEASIBLE:
                resultOpt.dictResult['input']['batterySize'] = self.param['battery']['power']

            self.param['battery']['power'] = resultOpt.dictResult['input']['batterySize']
            self.param['battery']['minCharge'] = resultOpt.dictResult['input']['batterySize'] * 0.05
            self.param['battery']['initialCharge'] = resultOpt.dictResult['input']['batterySize'] * 0.5
            self.param['constraints']['batteryChargeEqual']['LowerBound'] = self.param['battery']['initialCharge']*self.param['constraints']['storagesFactorFillEqualLower']
            self.param['constraints']['batteryChargeEqual']['UpperBound'] = -self.param['battery']['initialCharge']*self.param['constraints']['storagesFactorFillEqualUpper']
            self.param['battery']['maxChargeRate'] = resultOpt.dictResult['input']['batterySize'] * 0.5
            self.param['battery']['maxDischargeRate'] = resultOpt.dictResult['input']['batterySize'] * 0.5

        if self.param['controlParameters']['objectiveFunction'] == 7 or self.param['controlParameters']['objectiveFunction'] == 8:
            self.param['storageH2']['Volume'] = resultOpt.dictResult['input']['H2StorageSize']
            self.param['storageH2']['LowerBound'] = 15
            self.param['storageH2']['UpperBound'] = 35
            self.param['storageH2']['InitialFillingFactor'] = 0.5
            self.param['storageH2']['InitialPressure'] = self.param['storageH2']['InitialFillingFactor']*(self.param['storageH2']['UpperBound'] - self.param['storageH2']['LowerBound']) + self.param['storageH2']['LowerBound']
            self.param['storageH2']['InitialFilling'] = self.param['storageH2']['InitialPressure']*100000*self.param['storageH2']['Volume'] / (self.param['R_H2']*(self.param['Tamb'] + self.param['T0']))

            
            self.param['storageMethanolWater']['Volume'] = resultOpt.dictResult['input']['MeOHWaterStorageSize']
            self.param['storageMethanolWater']['LowerBound'] = 0.01
            self.param['storageMethanolWater']['UpperBound'] = self.param['storageMethanolWater']['Volume']
            self.param['storageMethanolWater']['InitialFillingFactor'] = 0.5
            self.param['storageMethanolWater']['InitialFilling'] = self.param['storageMethanolWater']['InitialFillingFactor']*(self.param['storageMethanolWater']['UpperBound'] - self.param['storageMethanolWater']['LowerBound']) + self.param['storageMethanolWater']['LowerBound']
            self.param['storageMethanolWater']['InitialDensity'] = 731.972

            self.param['constraints']['hydrogenStorageFillEqual']['LowerBound'] = self.param['storageH2']['InitialPressure']*self.param['constraints']['storagesFactorFillEqualLower']
            self.param['constraints']['hydrogenStorageFillEqual']['UpperBound'] = -self.param['storageH2']['InitialPressure']*self.param['constraints']['storagesFactorFillEqualUpper']

            self.param['constraints']['methanolWaterStorageFillEqual']['LowerBound'] = self.param['storageMethanolWater']['InitialFilling']*self.param['constraints']['storagesFactorFillEqualLower']
            self.param['constraints']['methanolWaterStorageFillEqual']['UpperBound'] = -self.param['storageMethanolWater']['InitialFilling']*self.param['constraints']['storagesFactorFillEqualUpper']


        
    def funcGet(self, j):

        ## Parameter
        self.param = {}

        # Production constants
        self.param['production'] = {}
        self.param['production']['minMethanolBenchmark'] = 100
        self.param['production']['minMethanolOpt'] = 108.065 #113.75 #108.065
        self.param['production']['methanol'] = 37.876913040000005      
        
        
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
        self.param['charMap']['SYN']['index']['massFlowHdydrogenIn'] = 3
        self.param['charMap']['SYN']['index']['massFlowMethanolWaterStorageIn'] = 5
        self.param['charMap']['SYN']['index']['densityMethanolWaterStorageIn'] = 4
        self.param['charMap']['SYN']['index']['massFlowSynthesisPurge'] = 7
        self.param['charMap']['SYN']['index']['moleFractionCO2SynthesisPurge'] = 6
        self.param['charMap']['SYN']['index']['powerPlantComponentsUnit2'] = 20
        self.param['charMap']['CO2CAP']['numVars'] = 7

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



        ## PV
        self.param['pv'] = {}
        self.param['pv']['module'] = 'Canadian_Solar_CS5P_220M___2009_'
        self.param['pv']['inverter'] = 'ABB__PVI_3_0_OUTD_S_US__208V_'#'ABB__MICRO_0_25_I_OUTD_US_208__208V_'
        self.param['pv']['powerOfModule'] = 0.22
        self.param['pv']['powerOfSystem'] = 4427 #* 1.5
        self.param['pv']['numberOfUncertaintySamples'] = 100
        self.param['pv']['alpha'] = 0.9
        self.param['pv']['covariance'] = 8

        #if j == 0 or j == 1 or j == 2 or j == 3:
        #    self.param['pv']['powerOfSystem'] = 100
        #elif j == 4 or j == 5 or j == 6:
        #    self.param['pv']['powerOfSystem'] = 500

        #pkl_files = [f for f in os.listdir(r'C:\PROJEKTE\PTX\Max\21_Scheduling\01_Scheduling_Results\01_data\results_v2\Case_99_econ') if f.endswith('.pkl')]
        #pkl_files.sort(key=lambda x: os.path.getctime(os.path.join(r'C:\PROJEKTE\PTX\Max\21_Scheduling\01_Scheduling_Results\01_data\results_v2\Case_99_econ', x)))

        #file_path = os.path.join(r'C:\PROJEKTE\PTX\Max\21_Scheduling\01_Scheduling_Results\01_data\results_v2\Case_99_econ', pkl_files[j])
        #with open(file_path, 'rb') as f:
        #    data = pickle.load(f)

        #self.param['pv']['powerOfSystem'] = data['input']['pvSize']

        



        ## Carbon intensity
        self.param['carbonIntensity'] = {}
        self.param['carbonIntensity']['numberOfUncertaintySamples'] = 100



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



        ## Electrolyser
        self.param['electrolyser'] = {}
        self.param['electrolyser']['constant'] = 0.0187239583
        self.param['electrolyser']['numberOfEnapterModules'] = 8
        self.param['electrolyser']['powerLowerBound'] = 1.44
        self.param['electrolyser']['powerUpperBound'] = 2.4
        self.param['electrolyser']['standbyPower'] = 0.1

        self.param['electrolyser']['numberOperationPoints'] = 41
        self.param['electrolyser']['conversionValues'] = []

        for i in range(0, self.param['electrolyser']['numberOperationPoints']):
            self.param['electrolyser']['conversionValues'].append(self.param['electrolyser']['powerLowerBound'] + (self.param['electrolyser']['powerUpperBound'] - self.param['electrolyser']['powerLowerBound']) * i / (self.param['electrolyser']['numberOperationPoints'] - 1))




        ## Battery
        self.param['battery'] = {}                                                   # https://www.bsl-battery.com/100kwh-commercial-solar-battery-storage.html

        #if j == 0 or j == 4:
        #    self.param['battery']['power'] = 400
        #elif j == 1 or j == 5:
        #    self.param['battery']['power'] = 600
        #elif j == 2 or j == 6:
        #    self.param['battery']['power'] = 800
        #elif j == 3:
        #    self.param['battery']['power'] = 1000

        #self.param['battery']['power'] = data['input']['batterySize']
        
        self.param['battery']['power'] = 6384#50             # kWh
        self.param['battery']['voltage'] = 512#562          # V  
        self.param['battery']['capacity'] = self.param['battery']['power'] * 1000 / self.param['battery']['voltage']             # Ah
        self.param['battery']['minCharge'] = self.param['battery']['power'] * 0.05#0.01
        self.param['battery']['efficiency'] = 0.9#1
        self.param['battery']['maxChargeRate'] = self.param['battery']['power'] * 0.5#10          # kW
        self.param['battery']['minChargeRate'] = 2#self.param['battery']['power'] * 0.01#1          # kW                # Annahme (aktuell nicht genutzt)
        self.param['battery']['maxDischargeRate'] = self.param['battery']['power'] * 0.5#10        # kW
        self.param['battery']['minDischargeRate'] = 2#self.param['battery']['power'] * 0.01#1       # kW                # Annahme (aktuell nicht genutzt)
        self.param['battery']['initialCharge'] = 0.5*self.param['battery']['capacity'] * self.param['battery']['voltage'] / 1000



        ## Constraints
        self.param['constraints'] = {}
        self.param['constraints']['storagesFactorFillEqualLower'] = 0.1

        if self.param['controlParameters']['benchmark'] == True:
            self.param['constraints']['storagesFactorFillEqualLower'] = 0.25
            self.param['constraints']['storagesFactorFillEqualUpper'] = 0.25
        else:
            self.param['constraints']['storagesFactorFillEqualLower'] = 0.05
            self.param['constraints']['storagesFactorFillEqualUpper'] = 0.05

        self.param['constraints']['methanolWaterStorageFillEqual'] = {}
        self.param['constraints']['methanolWaterStorageFillEqual']['LowerBound'] = self.param['storageMethanolWater']['InitialFilling']*self.param['constraints']['storagesFactorFillEqualLower']
        self.param['constraints']['methanolWaterStorageFillEqual']['UpperBound'] = -self.param['storageMethanolWater']['InitialFilling']*self.param['constraints']['storagesFactorFillEqualUpper']

        self.param['constraints']['hydrogenStorageFillEqual'] = {}
        self.param['constraints']['hydrogenStorageFillEqual']['LowerBound'] = self.param['storageH2']['InitialPressure']*self.param['constraints']['storagesFactorFillEqualLower']
        self.param['constraints']['hydrogenStorageFillEqual']['UpperBound'] = -self.param['storageH2']['InitialPressure']*self.param['constraints']['storagesFactorFillEqualUpper']

        self.param['constraints']['batteryChargeEqual'] = {}
        self.param['constraints']['batteryChargeEqual']['LowerBound'] = self.param['battery']['initialCharge']*self.param['constraints']['storagesFactorFillEqualLower']
        self.param['constraints']['batteryChargeEqual']['UpperBound'] = -self.param['battery']['initialCharge']*self.param['constraints']['storagesFactorFillEqualUpper']




        self.param['constraints']['transitionTimes'] = {}
        self.param['constraints']['transitionTimes']['minStayTimeCO2CAP_SYN_Off'] = [int(1 / self.param['controlParameters']['timeStep']),
                                                                                         int(1 / self.param['controlParameters']['timeStep']),
                                                                                         int(1 / self.param['controlParameters']['timeStep']),
                                                                                         int(1 / self.param['controlParameters']['timeStep']),
                                                                                         int(1 / self.param['controlParameters']['timeStep'])]
        self.param['constraints']['transitionTimes']['minStayTimeCO2CAP_SYN_Startup'] = [int(12 / self.param['controlParameters']['timeStep']), #12
                                                                                             int(1 / self.param['controlParameters']['timeStep']),
                                                                                             int(4 / self.param['controlParameters']['timeStep']), #4
                                                                                             int(1 / self.param['controlParameters']['timeStep']),
                                                                                             int(1 / self.param['controlParameters']['timeStep'])]
        self.param['constraints']['transitionTimes']['minStayTimeCO2CAP_SYN_Standby'] = [int(1 / self.param['controlParameters']['timeStep']),
                                                                                             int(1 / self.param['controlParameters']['timeStep']),
                                                                                             int(1 / self.param['controlParameters']['timeStep']),
                                                                                             int(1 / self.param['controlParameters']['timeStep']),
                                                                                             int(1 / self.param['controlParameters']['timeStep'])]
        self.param['constraints']['transitionTimes']['minStayTimeCO2CAP_SYN_On'] = [int(1 / self.param['controlParameters']['timeStep']),
                                                                                        int(1 / self.param['controlParameters']['timeStep']),
                                                                                        int(1 / self.param['controlParameters']['timeStep']),
                                                                                        int(1 / self.param['controlParameters']['timeStep']),
                                                                                        int(1 / self.param['controlParameters']['timeStep'])]
        self.param['constraints']['transitionTimes']['minStayTimeCO2CAP_SYN_Shutdown'] = [int(1 / self.param['controlParameters']['timeStep']),
                                                                                        int(1 / self.param['controlParameters']['timeStep']),
                                                                                        int(4 / self.param['controlParameters']['timeStep']),   #4
                                                                                        int(6 / self.param['controlParameters']['timeStep']),   #6
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
        
        self.param['constraints']['transitionTimes']['maxStayTimeCO2CAP_SYN_Off'] = [self.optimizationHorizon,
                                                                                         self.optimizationHorizon,
                                                                                         self.optimizationHorizon,
                                                                                         self.optimizationHorizon,
                                                                                         self.optimizationHorizon]
        self.param['constraints']['transitionTimes']['maxStayTimeCO2CAP_SYN_Startup'] = [int(12 / self.param['controlParameters']['timeStep']),
                                                                                            self.optimizationHorizon,
                                                                                            int(4 / self.param['controlParameters']['timeStep']),
                                                                                            self.optimizationHorizon,
                                                                                            self.optimizationHorizon]
        self.param['constraints']['transitionTimes']['maxStayTimeCO2CAP_SYN_Standby'] = [self.optimizationHorizon,
                                                                                            self.optimizationHorizon,
                                                                                            self.optimizationHorizon,
                                                                                            self.optimizationHorizon,
                                                                                            self.optimizationHorizon]
        self.param['constraints']['transitionTimes']['maxStayTimeCO2CAP_SYN_On'] = [self.optimizationHorizon,
                                                                                                self.optimizationHorizon,
                                                                                                self.optimizationHorizon,
                                                                                                self.optimizationHorizon,
                                                                                                self.optimizationHorizon]
        self.param['constraints']['transitionTimes']['maxStayTimeCO2CAP_SYN_Shutdown'] = [self.optimizationHorizon,
                                                                                                self.optimizationHorizon,
                                                                                                int(4 / self.param['controlParameters']['timeStep']),
                                                                                                int(6 / self.param['controlParameters']['timeStep']),
                                                                                                self.optimizationHorizon]

        self.param['constraints']['transitionTimes']['maxStayTimeDIS_Off'] = [self.optimizationHorizon,
                                                                                    self.optimizationHorizon,
                                                                                    self.optimizationHorizon,
                                                                                    self.optimizationHorizon,
                                                                                    self.optimizationHorizon]
        self.param['constraints']['transitionTimes']['maxStayTimeDIS_Startup'] = [int(6 / self.param['controlParameters']['timeStep']),
                                                                                        self.optimizationHorizon,
                                                                                        int(3 / self.param['controlParameters']['timeStep']),
                                                                                        self.optimizationHorizon,
                                                                                        self.optimizationHorizon]
        self.param['constraints']['transitionTimes']['maxStayTimeDIS_Standby'] = [self.optimizationHorizon,
                                                                                         self.optimizationHorizon,
                                                                                         self.optimizationHorizon,
                                                                                         self.optimizationHorizon,
                                                                                         self.optimizationHorizon]
        self.param['constraints']['transitionTimes']['maxStayTimeDIS_On'] = [self.optimizationHorizon,
                                                                                    self.optimizationHorizon,
                                                                                    self.optimizationHorizon,
                                                                                    self.optimizationHorizon,
                                                                                    self.optimizationHorizon]
        self.param['constraints']['transitionTimes']['maxStayTimeDIS_Shutdown'] = [self.optimizationHorizon,
                                                                                        self.optimizationHorizon,
                                                                                        int(2 / self.param['controlParameters']['timeStep']),
                                                                                        int(4 / self.param['controlParameters']['timeStep']),
                                                                                        self.optimizationHorizon]
        
        