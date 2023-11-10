#!/usr/bin/env python3.10

import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt


class Param():

    def __init__(self, *args):

        if len(args) > 0:
            self.optimizationHorizon = args[0]
            self.timeStep = args[1]
            self.timeLimit = args[2]
            self.optimalityGap = args[3]
            self.testFeasibility =args[4]

            self.benchmark = args[5]
            self.sameOutputAsBenchmark = args[6]

            self.rateOfChangeConstranints = args[7]
            self.transitionConstraints = args[8]
            self.powerSale = args[9]
            self.uncertaintyPV = args[10]
            self.uncertaintyPP = args[11]

            self.checkPVUncertainty = args[12]
            self.checkPPUncertainty = args[13]

            self.considerPV = args[14]
            self.considerBattery = args[15]
        

    def update(self, pv, pp):
        self.param['pv']['powerAvailable'] = pv.powerAvailable
        self.param['prices']['power'] = pp.powerPriceHourly

        self.param['constraints']['methanolWaterStorageFillEqual']['LowerBound'] = -self.param['storageMethanolWater']['InitialFilling']*self.param['constraints']['storagesFactorFillEqual']
        self.param['constraints']['methanolWaterStorageFillEqual']['UpperBound'] = self.param['storageMethanolWater']['InitialFilling']*self.param['constraints']['storagesFactorFillEqual']

        self.param['constraints']['hydrogenStorageFillEqual']['LowerBound'] = -self.param['storageH2']['InitialPressure']*self.param['constraints']['storagesFactorFillEqual']
        self.param['constraints']['hydrogenStorageFillEqual']['UpperBound'] = self.param['storageH2']['InitialPressure']*self.param['constraints']['storagesFactorFillEqual']

        self.param['constraints']['synthesisgasStorageFillEqual']['LowerBound'] = -self.param['storageSynthesisgas']['InitialPressure']*self.param['constraints']['storagesFactorFillEqual']
        self.param['constraints']['synthesisgasStorageFillEqual']['UpperBound'] = self.param['storageSynthesisgas']['InitialPressure']*self.param['constraints']['storagesFactorFillEqual']

        self.param['constraints']['batteryChargeEqual']['LowerBound'] = -self.param['battery']['initialCharge']*self.param['constraints']['storagesFactorFillEqual']
        self.param['constraints']['batteryChargeEqual']['UpperBound'] = self.param['battery']['initialCharge']*self.param['constraints']['storagesFactorFillEqual']

    def get(self):

        ## Parameter
        self.param = {}

        ## Methanol
        self.param['methanol'] = {}
        self.param['methanol']['minimumAmountBenchmark'] = 5
        self.param['methanol']['minimumAmountOpt'] = 37.876913040000005
        self.param['methanol']['sameAmountBenchmark'] = 37.876913040000005
        


        ## Methane   
        self.param['methane'] = {}
        self.param['methane']['brennwert'] = 11.1
        
        self.param['methane']['sameAmountMassBenchmark'] = 200
        self.param['methane']['sameAmountVolumeBenchmark'] = 300.7298414902889



        ## Control parameters
        self.param['controlParameters'] = {}
        self.param['controlParameters']['optimizationHorizon'] = self.optimizationHorizon
        self.param['controlParameters']['timeStep'] = self.timeStep
        self.param['controlParameters']['numberOfTimeSteps'] = int(self.optimizationHorizon / self.timeStep)
        self.param['controlParameters']['timeLimit'] = self.timeLimit
        self.param['controlParameters']['optimalityGap'] = self.optimalityGap
        self.param['controlParameters']['testFeasibility'] = self.testFeasibility
        self.param['controlParameters']['benchmark'] = self.benchmark
        self.param['controlParameters']['sameOutputAsBenchmark'] = self.sameOutputAsBenchmark
        self.param['controlParameters']['rateOfChangeConstranints'] = self.rateOfChangeConstranints
        self.param['controlParameters']['transitionConstraints'] = self.transitionConstraints
        self.param['controlParameters']['powerSale'] = self.powerSale
        self.param['controlParameters']['uncertaintyPV'] = self.uncertaintyPV
        self.param['controlParameters']['uncertaintyPP'] = self.uncertaintyPP
        self.param['controlParameters']['checkPVUncertainty'] = self.checkPVUncertainty
        self.param['controlParameters']['checkPPUncertainty'] = self.checkPPUncertainty
        self.param['controlParameters']['considerPV'] = self.considerPV
        self.param['controlParameters']['considerBattery'] = self.considerBattery



        ## Characteristic field indices
        self.param['charField'] = {}

        # Characteristic field indices ABSDES
        self.param['charField']['ABSDES'] = {}
        self.param['charField']['ABSDES']['index'] = {}
        self.param['charField']['ABSDES']['index']['massFlowHydrogenIn'] = 2
        self.param['charField']['ABSDES']['index']['massFlowBiogasIn'] = 3
        self.param['charField']['ABSDES']['index']['massFlowBiogasOut'] = 4
        self.param['charField']['ABSDES']['index']['densityBiogasOut'] = 6
        self.param['charField']['ABSDES']['index']['moleFractionMethaneBiogasOut'] = 7
        self.param['charField']['ABSDES']['index']['massFlowSynthesisgasIn'] = 8
        self.param['charField']['ABSDES']['index']['moleFractionH2Synthesisgas'] = 14
        self.param['charField']['ABSDES']['index']['moleFractionCO2Synthesisgas'] = 15
        self.param['charField']['ABSDES']['index']['massFlowMethanolWaterStorageIn'] = 16
        self.param['charField']['ABSDES']['index']['densityMethanolWaterStorageIn'] = 18
        self.param['charField']['ABSDES']['index']['massFlowMethanolWaterInCycle'] = 36
        self.param['charField']['ABSDES']['index']['massFlowAdditionalHydrogen'] = 37
        self.param['charField']['ABSDES']['index']['powerPlantComponentsUnit1'] = [25,27,28,29,31,32,34,35]

        # Characteristic field indices MEOHSYN
        self.param['charField']['MEOHSYN'] = {}
        self.param['charField']['MEOHSYN']['index'] = {}
        self.param['charField']['MEOHSYN']['index']['massFlowSynthesisgasOut'] = 2
        self.param['charField']['MEOHSYN']['index']['massFlowMethanolWaterStorageIn'] = 3
        self.param['charField']['MEOHSYN']['index']['densityMethanolWaterStorageIn'] = 4
        self.param['charField']['MEOHSYN']['index']['powerPlantComponentsUnit2'] = [10,11,12,13]

        # Characteristic field indices DIS
        self.param['charField']['DIS'] = {}
        self.param['charField']['DIS']['index'] = {}
        self.param['charField']['MEOHSYN']['index']['massFlowMethanolWaterStorageOut'] = 2
        self.param['charField']['MEOHSYN']['index']['massFlowMethanolOut'] = 3
        self.param['charField']['MEOHSYN']['index']['powerPlantComponentsUnit3'] = [7,8,9,10]



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




        ## Prices of products
        self.param['prices'] = {}
        self.param['prices']['biogas'] = 0.2
        self.param['prices']['methane'] = 0.2
        self.param['prices']['methanol'] = 1
        self.param['prices']['powerSold'] = 0.238
        self.param['prices']['numberOfUncertaintySamples'] = 100




        ## PV
        self.param['pv'] = {}
        self.param['pv']['module'] = 'Canadian_Solar_CS5P_220M___2009_'
        self.param['pv']['inverter'] = 'ABB__PVI_3_0_OUTD_S_US__208V_'#'ABB__MICRO_0_25_I_OUTD_US_208__208V_'
        self.param['pv']['powerOfModule'] = 0.22
        self.param['pv']['powerOfSystem'] = 30
        self.param['pv']['numberOfUncertaintySamples'] = 100
        self.param['pv']['alpha'] = 0.9
        self.param['pv']['covariance'] = 8



        ## Storages
        self.param['storageH2'] = {}
        self.param['storageMethanolWater'] = {}

        self.param['storageH2']['Volume'] = 1.7 #+ 0.85
        self.param['storageMethanolWater']['Volume'] = 0.2

        self.param['storageH2']['LowerBound'] = 15
        self.param['storageH2']['UpperBound'] = 35
        self.param['storageMethanolWater']['LowerBound'] = 0.01
        self.param['storageMethanolWater']['UpperBound'] = self.param['storageMethanolWater']['Volume']

        self.param['storageH2']['InitialFillingFactor'] = 0.5
        self.param['storageMethanolWater']['InitialFillingFactor'] = 0.5
        self.param['storageH2']['InitialPressure'] = self.param['storageH2']['InitialFillingFactor']*(self.param['storageH2']['UpperBound'] - self.param['storageH2']['LowerBound']) + self.param['storageH2']['LowerBound']
        self.param['storageH2']['InitialFilling'] = self.param['storageH2']['InitialPressure']*100000*self.param['storageH2']['Volume'] / (self.param['R_H2']*(self.param['Tamb'] + self.param['T0']))
        self.param['storageMethanolWater']['InitialFilling'] = self.param['storageMethanolWater']['InitialFillingFactor']*(self.param['storageMethanolWater']['UpperBound'] - self.param['storageMethanolWater']['LowerBound']) + self.param['storageMethanolWater']['LowerBound']
        self.param['storageMethanolWater']['InitialDensity'] = 804.5443


        self.param['storageSynthesisgas'] = {}
        self.param['storageSynthesisgas']['LowerBound'] = 15
        self.param['storageSynthesisgas']['UpperBound'] = 35

        self.param['storageSynthesisgas']['Volume'] = 3
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




        ## Battery
        self.param['battery'] = {}                                                   # https://www.bsl-battery.com/100kwh-commercial-solar-battery-storage.html
        self.param['battery']['capacity'] = 50                # kWh
        self.param['battery']['minCharge'] = self.param['battery']['capacity']*0.01
        self.param['battery']['voltage'] = 562                   # V
        self.param['battery']['efficency'] = 0.9
        self.param['battery']['auxiliaryPower'] = 0.05
        self.param['battery']['maxChargeRate'] = self.param['battery']['capacity']          # kW
        self.param['battery']['minChargeRate'] = 1                                          # kW                # Annahme (aktuell nicht genutzt)
        self.param['battery']['maxDischargeRate'] = self.param['battery']['capacity']       # kW
        self.param['battery']['minDischargeRate'] = 1                                       # kW                # Annahme (aktuell nicht genutzt)
        self.param['battery']['initialCharge'] = 0.5*self.param['battery']['capacity']



        ## Constraints
        self.param['constraints'] = {}
        self.param['constraints']['storagesFactorFillEqual'] = 0.05

        self.param['constraints']['methanolWaterStorageFillEqual'] = {}
        self.param['constraints']['methanolWaterStorageFillEqual']['LowerBound'] = -self.param['storageMethanolWater']['InitialFilling']*self.param['constraints']['storagesFactorFillEqual']
        self.param['constraints']['methanolWaterStorageFillEqual']['UpperBound'] = self.param['storageMethanolWater']['InitialFilling']*self.param['constraints']['storagesFactorFillEqual']

        self.param['constraints']['hydrogenStorageFillEqual'] = {}
        self.param['constraints']['hydrogenStorageFillEqual']['LowerBound'] = -self.param['storageH2']['InitialPressure']*self.param['constraints']['storagesFactorFillEqual']
        self.param['constraints']['hydrogenStorageFillEqual']['UpperBound'] = self.param['storageH2']['InitialPressure']*self.param['constraints']['storagesFactorFillEqual']

        self.param['constraints']['synthesisgasStorageFillEqual'] = {}
        self.param['constraints']['synthesisgasStorageFillEqual']['LowerBound'] = -self.param['storageSynthesisgas']['InitialPressure']*self.param['constraints']['storagesFactorFillEqual']
        self.param['constraints']['synthesisgasStorageFillEqual']['UpperBound'] = self.param['storageSynthesisgas']['InitialPressure']*self.param['constraints']['storagesFactorFillEqual']

        self.param['constraints']['batteryChargeEqual'] = {}
        self.param['constraints']['batteryChargeEqual']['LowerBound'] = -self.param['battery']['initialCharge']*self.param['constraints']['storagesFactorFillEqual']
        self.param['constraints']['batteryChargeEqual']['UpperBound'] = self.param['battery']['initialCharge']*self.param['constraints']['storagesFactorFillEqual']

        self.param['constraints']['minMoleFractionCH4BiogasOut'] =  self.param['biogas']['minimumMoleFractionMethane']
        self.param['constraints']['minRatioH2_CO2_Synthesisgas'] = 2.8
        self.param['constraints']['maxRatioH2_CO2_Synthesisgas'] = 3.2

        self.param['constraints']['operationPointChange'] = {}
        self.param['constraints']['operationPointChange']['distillationUpwardBound'] = -0.1 * self.param['controlParameters']['timeStep']
        self.param['constraints']['operationPointChange']['distillationDownwardBound'] = 0.1 * self.param['controlParameters']['timeStep']
        self.param['constraints']['operationPointChange']['MeOHSynthesisUpwardBound'] = -2 * self.param['controlParameters']['timeStep']
        self.param['constraints']['operationPointChange']['MeOHSynthesisDownwardBound'] = 2 * self.param['controlParameters']['timeStep']
        self.param['constraints']['operationPointChange']['MeOHWaterInCycleUpwardBound'] = -30 * self.param['controlParameters']['timeStep']
        self.param['constraints']['operationPointChange']['MeOHWaterInCycleDownwardBound'] = 30 * self.param['controlParameters']['timeStep']

        self.param['constraints']['transitionTimes'] = {}
        self.param['constraints']['transitionTimes']['minimumStayTimeABSDES'] = 5
        self.param['constraints']['transitionTimes']['minimumStayTimeMEOHSYN'] = 5
        self.param['constraints']['transitionTimes']['minimumStayTimeDIS'] = 10
        self.param['constraints']['transitionTimes']['maximumStayTimeABSDES'] = self.optimizationHorizon
        self.param['constraints']['transitionTimes']['maximumStayTimeMEOHSYN'] = self.optimizationHorizon
        self.param['constraints']['transitionTimes']['maximumStayTimeDIS'] = self.optimizationHorizon
        