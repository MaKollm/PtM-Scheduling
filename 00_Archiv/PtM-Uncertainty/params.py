#!/usr/bin/env python3.10

import pandas as pd 
import numpy as np

def get_params(*args):

    optimizationHorizon = args[0]
    benchmark = args[1]
    timeLimit = args[2]

    testFeasibility =args[3]

    rateOfChangeConstranints = args[4]
    transitionConstraints = args[5]
    powerSale = args[6]
    uncertainty = args[7]
    sameOutputAsBenchmark = args[8]

    ## Parameter
    param = {}

    ## Methanol
    param['methanol'] = {}
    param['methanol']['minimumAmountBenchmark'] = 10
    param['methanol']['minimumAmountOpt'] = 10
    param['methanol']['sameAmountBenchmark'] = 21.2
       


    ## Methane   
    param['methane'] = {}
    param['methane']['brennwert'] = 11.1
    
    param['methane']['sameAmountMassBenchmark'] = 200
    param['methane']['sameAmountVolumeBenchmark'] = 125.9701



    ## Control parameters
    param['controlParameters'] = {}
    param['controlParameters']['optimizationHorizon'] = optimizationHorizon
    param['controlParameters']['benchmark'] = benchmark
    param['controlParameters']['timeLimit'] = timeLimit
    param['controlParameters']['testFeasibility'] = testFeasibility
    param['controlParameters']['rateOfChangeConstranints'] = rateOfChangeConstranints
    param['controlParameters']['transitionConstraints'] = transitionConstraints
    param['controlParameters']['powerSale'] = powerSale
    param['controlParameters']['uncertainty'] = uncertainty
    param['controlParameters']['sameOutputAsBenchmark'] = sameOutputAsBenchmark



    ## Characteristic field indices
    param['charField'] = {}

    # Characteristic field indices ABSDES
    param['charField']['ABSDES'] = {}
    param['charField']['ABSDES']['index'] = {}
    param['charField']['ABSDES']['index']['massFlowHydrogenIn'] = 2
    param['charField']['ABSDES']['index']['massFlowBiogasIn'] = 3
    param['charField']['ABSDES']['index']['massFlowBiogasOut'] = 4
    param['charField']['ABSDES']['index']['densityBiogasOut'] = 6
    param['charField']['ABSDES']['index']['moleFractionMethaneBiogasOut'] = 7
    param['charField']['ABSDES']['index']['massFlowSynthesisgasIn'] = 8
    param['charField']['ABSDES']['index']['moleFractionH2Synthesisgas'] = 14
    param['charField']['ABSDES']['index']['moleFractionCO2Synthesisgas'] = 15
    param['charField']['ABSDES']['index']['massFlowMethanolWaterStorageIn'] = 16
    param['charField']['ABSDES']['index']['densityMethanolWaterStorageIn'] = 18
    param['charField']['ABSDES']['index']['massFlowMethanolWaterInCycle'] = 36
    param['charField']['ABSDES']['index']['massFlowAdditionalHydrogen'] = 37
    param['charField']['ABSDES']['index']['powerPlantComponentsUnit1'] = [25,27,28,29,31,32,34,35]

    # Characteristic field indices MEOHSYN
    param['charField']['MEOHSYN'] = {}
    param['charField']['MEOHSYN']['index'] = {}
    param['charField']['MEOHSYN']['index']['massFlowSynthesisgasOut'] = 2
    param['charField']['MEOHSYN']['index']['massFlowMethanolWaterStorageIn'] = 3
    param['charField']['MEOHSYN']['index']['densityMethanolWaterStorageIn'] = 4
    param['charField']['MEOHSYN']['index']['powerPlantComponentsUnit2'] = [10,11,12,13]

    # Characteristic field indices DIS
    param['charField']['DIS'] = {}
    param['charField']['DIS']['index'] = {}
    param['charField']['MEOHSYN']['index']['massFlowMethanolWaterStorageOut'] = 2
    param['charField']['MEOHSYN']['index']['massFlowMethanolOut'] = 3
    param['charField']['MEOHSYN']['index']['powerPlantComponentsUnit3'] = [7,8,9,10]



    ## Biogas parameters
    param['biogas'] = {}
    param['biogas']['temperatureIn'] = 253.15
    param['biogas']['temperatureOut'] = 253.15
    param['biogas']['pressureIn'] = 3
    param['biogas']['pressureOut'] = 3
    param['biogas']['densityIn'] = 3.73426
    param['biogas']['brennwert'] = 6.5
    param['biogas']['minimumMoleFractionMethane'] = 0.94



    ## Thermodynamic and chemical parameters
    param['p0'] = 1.013
    param['T0'] = 273.15
    param['Tamb'] = 21
    param['R_H2'] = 4124.3              # http://www.thermodynamik-online.de/Tabellen/Naturkonstanten,%20Umrechnungen,%20kritische%20Gro%CC%88%C3%9Fen.pdf
    param['R_CO2'] = 188.92             # http://www.thermodynamik-online.de/Tabellen/Naturkonstanten,%20Umrechnungen,%20kritische%20Gro%CC%88%C3%9Fen.pdf
    param['R_MEOH'] = 259.5             # http://www.thermodynamik-online.de/Tabellen/Naturkonstanten,%20Umrechnungen,%20kritische%20Gro%CC%88%C3%9Fen.pdf
    param['R_H2O'] = 461.53             # http://www.thermodynamik-online.de/Tabellen/Naturkonstanten,%20Umrechnungen,%20kritische%20Gro%CC%88%C3%9Fen.pdf
    param['R_CH4'] = 518.26             # http://www.thermodynamik-online.de/Tabellen/Naturkonstanten,%20Umrechnungen,%20kritische%20Gro%CC%88%C3%9Fen.pdf

    param['fractionSynthesisgasCH4'] = 0.00372
    param['fractionSynthesisgasH2O'] = 0.00045
    param['fractionSynthesisgasMEOH'] = 0.00971
    param['fractionSynthesisgasCO2'] = 0.86698
    param['fractionSynthesisgasH2'] = 0.11914
    param['R_Synthesisgas'] = param['fractionSynthesisgasH2'] * param['R_H2'] \
                                + param['fractionSynthesisgasCO2'] * param['R_CO2'] \
                                + param['fractionSynthesisgasMEOH'] * param['R_MEOH'] \
                                + param['fractionSynthesisgasH2O'] * param['R_H2O'] \
                                + param['fractionSynthesisgasCH4'] * param['R_CH4']



    ## Prices of products
    param['prices'] = {}
    param['prices']['biogas'] = 0.2
    param['prices']['methane'] = 0.2
    param['prices']['methanol'] = 1
    param['prices']['powerSold'] = 0.238

    # Energy price
    energyCharts_DataFrame = pd.read_excel(r'C:\Users\ne9836\Promotion_IAI\50_Daten\02_Energie\energy-charts_Stromproduktion_und_Börsenstrompreise_in_Deutschland_in_Woche_49_2021_Excel.xlsx')
    energyCharts = energyCharts_DataFrame.to_numpy()
    powerPriceQuarterHourly = energyCharts[:,5] / 1000
    powerPriceHourly = []
    for i in range(0, len(powerPriceQuarterHourly)-1,4):
        powerPriceHourly.append(np.mean(powerPriceQuarterHourly[i:i+3]))

    param['prices']['power'] = powerPriceHourly[0:param['controlParameters']['optimizationHorizon']]
    param['prices']['power'].insert(0,0)



    ## PV
    param['pv'] = {}
    param['pv']['module'] = 'Canadian_Solar_CS5P_220M___2009_'
    param['pv']['inverter'] = 'ABB__MICRO_0_25_I_OUTD_US_208__208V_'
    param['pv']['numberOfUncertaintySamples'] = 100
    param['pv']['alpha'] = 1
    param['pv']['covariance'] = 2




    ## Storages
    param['storageH2'] = {}
    param['storageMethanolWater'] = {}

    param['storageH2']['Volume'] = 1.7
    param['storageMethanolWater']['Volume'] = 0.2

    param['storageH2']['LowerBound'] = 15
    param['storageH2']['UpperBound'] = 35
    param['storageMethanolWater']['LowerBound'] = 0.01
    param['storageMethanolWater']['UpperBound'] = param['storageMethanolWater']['Volume']

    param['storageH2']['InitialFillingFactor'] = 0.5
    param['storageMethanolWater']['InitialFillingFactor'] = 0.5
    param['storageH2']['InitialPressure'] = param['storageH2']['InitialFillingFactor']*(param['storageH2']['UpperBound'] - param['storageH2']['LowerBound']) + param['storageH2']['LowerBound']
    param['storageH2']['InitialFilling'] = param['storageH2']['InitialPressure']*100000*param['storageH2']['Volume'] / (param['R_H2']*(param['Tamb'] + param['T0']))
    param['storageMethanolWater']['InitialFilling'] = param['storageMethanolWater']['InitialFillingFactor']*(param['storageMethanolWater']['UpperBound'] - param['storageMethanolWater']['LowerBound']) + param['storageMethanolWater']['LowerBound']
    param['storageMethanolWater']['InitialDensity'] = 804.5443


    param['storageSynthesisgas'] = {}
    param['storageSynthesisgas']['LowerBound'] = 15
    param['storageSynthesisgas']['UpperBound'] = 35

    param['storageSynthesisgas']['Volume'] = 3
    param['storageSynthesisgas']['InitialFillingFactor'] = 0.5
    param['storageSynthesisgas']['InitialPressure'] = param['storageSynthesisgas']['InitialFillingFactor']*(param['storageSynthesisgas']['UpperBound'] - param['storageSynthesisgas']['LowerBound']) + param['storageSynthesisgas']['LowerBound']
    param['storageSynthesisgas']['InitialFilling'] = param['storageSynthesisgas']['InitialPressure']*100000*param['storageSynthesisgas']['Volume'] / (param['R_Synthesisgas']*(param['Tamb'] + param['T0']))



    ## Electrolyser
    param['electrolyser'] = {}
    param['electrolyser']['constant'] = 0.0187239583
    param['electrolyser']['numberOfEnapterModules'] = 8
    param['electrolyser']['powerLowerBound'] = 1.44
    param['electrolyser']['powerUpperBound'] = 2.4
    param['electrolyser']['standbyPower'] = 0.1




    ## Battery
    param['battery'] = {}                                                   # https://www.bsl-battery.com/100kwh-commercial-solar-battery-storage.html
    param['battery']['capacity'] = 157.6                # kWh
    param['battery']['voltage'] = 562                   # V
    param['battery']['efficency'] = 0.9
    param['battery']['auxiliaryPower'] = 0.05
    param['battery']['maxChargeRate'] = 157.36         # kW
    param['battery']['minChargeRate'] = 10             # kW                # Annahme (aktuell nicht genutzt)
    param['battery']['maxDischargeRate'] = 157.36      # kW
    param['battery']['minDischargeRate'] = 10          # kW                # Annahme (aktuell nicht genutzt)
    param['battery']['initialCharge'] = 0.5*param['battery']['capacity']



    ## Constraints
    param['constraints'] = {}
    param['constraints']['storagesFactorFillEqual'] = 0.1

    param['constraints']['methanolWaterStorageFillEqual'] = {}
    param['constraints']['methanolWaterStorageFillEqual']['LowerBound'] = -param['storageMethanolWater']['InitialFilling']*param['constraints']['storagesFactorFillEqual']
    param['constraints']['methanolWaterStorageFillEqual']['UpperBound'] = param['storageMethanolWater']['InitialFilling']*param['constraints']['storagesFactorFillEqual']

    param['constraints']['hydrogenStorageFillEqual'] = {}
    param['constraints']['hydrogenStorageFillEqual']['LowerBound'] = -param['storageH2']['InitialPressure']*param['constraints']['storagesFactorFillEqual']
    param['constraints']['hydrogenStorageFillEqual']['UpperBound'] = param['storageH2']['InitialPressure']*param['constraints']['storagesFactorFillEqual']

    param['constraints']['synthesisgasStorageFillEqual'] = {}
    param['constraints']['synthesisgasStorageFillEqual']['LowerBound'] = -param['storageSynthesisgas']['InitialPressure']*param['constraints']['storagesFactorFillEqual']
    param['constraints']['synthesisgasStorageFillEqual']['UpperBound'] = param['storageSynthesisgas']['InitialPressure']*param['constraints']['storagesFactorFillEqual']

    param['constraints']['batteryChargeEqual'] = {}
    param['constraints']['batteryChargeEqual']['LowerBound'] = -1
    param['constraints']['batteryChargeEqual']['UpperBound'] = 1

    param['constraints']['minMoleFractionCH4BiogasOut'] =  param['biogas']['minimumMoleFractionMethane']
    param['constraints']['minRatioH2_CO2_Synthesisgas'] = 2.8
    param['constraints']['maxRatioH2_CO2_Synthesisgas'] = 3.2

    param['constraints']['operationPointChange'] = {}
    param['constraints']['operationPointChange']['distillationUpwardBound'] = -1
    param['constraints']['operationPointChange']['distillationDownwardBound'] = 1
    param['constraints']['operationPointChange']['MeOHSynthesisUpwardBound'] = -2
    param['constraints']['operationPointChange']['MeOHSynthesisDownwardBound'] = 2
    param['constraints']['operationPointChange']['MeOHWaterInCycleUpwardBound'] = -30
    param['constraints']['operationPointChange']['MeOHWaterInCycleDownwardBound'] = 30

    param['constraints']['transitionTimes'] = {}
    param['constraints']['transitionTimes']['minimumStayTimeABSDES'] = 3
    param['constraints']['transitionTimes']['minimumStayTimeMEOHSYN'] = 3
    param['constraints']['transitionTimes']['minimumStayTimeDIS'] = 3
    param['constraints']['transitionTimes']['maximumStayTimeABSDES'] = 8
    param['constraints']['transitionTimes']['maximumStayTimeMEOHSYN'] = 8
    param['constraints']['transitionTimes']['maximumStayTimeDIS'] = 8


    return param