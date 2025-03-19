#!/usr/bin/env python3.10


#############################
########## Check Simulation Results ##########

from result import *

import gurobipy as gp
import numpy as np
import matplotlib.pyplot as plt
from copy import deepcopy


class CheckSimulationResults():
    def __init__(self, param):
        self.funcUpdate(param)


    def funcUpdate(self, param):
        self.param = param
        self.arrTime = list(range(0,self.param.param['controlParameters']['numberOfTimeSteps']+1))
        self.dictResult = {'output': {}, 'costs': {}}
        self.arrConstrViolationInput = []
        self.dictConstrViolationOutput = {}

    def funcStartCheck(self, param, resultOpt, cm, elec, pv, pp, ci, simulation):
        
        self.funcUpdate(param)
    
        self.funcCheckUncertainty(resultOpt, cm, elec, pv, pp, ci, simulation)
        #self.funcCheckUncertaintyConstraints(resultOpt, cm, elec, pv, pp, ci)
        self.funcCheckConstraints(resultOpt, cm, elec, pv, pp, ci)


    # Check scenarios with price uncertainty if pv uncertainty is not considered
    def funcCheckUncertainty(self, resultOpt, cm, elec, pv, pp, ci, simulation):
        if self.param.param['controlParameters']['checkPPUncertainty'] == True:
            meanCosts = 0
            resultTemp = Result(self.param)
            for i in range(0, pp.iNumberUncertaintySamples):
                print(i)
                pp.arrPowerPriceHourly = pp.arrPowerPriceSamples[i]
                self.param.funcUpdate(pv,pp)
                resultOpt.dictResult["input"]["powerBought"] = resultOpt.dictResult["input"]["powerBoughtRaw"][i]
                resultOpt.dictResult["input"]["powerInBatteryBought"] = resultOpt.dictResult["input"]["powerInBatteryBoughtRaw"][i]
                resultOpt.dictResult["input"]["powerOutBattery"] = resultOpt.dictResult["input"]["powerOutBatteryRaw"][i]
                resultOpt.dictResult["input"]["powerOutBatterySold"] = resultOpt.dictResult["input"]["powerOutBatterySoldRaw"][i]
                resultTemp = deepcopy(resultOpt)
                simulation.funcStartSimulation(self.param, resultTemp, cm, elec, pv, pp, ci)
                self.funcCheckUncertaintyConstraints(resultTemp, cm, elec, pv, pp, ci)

                print("costs: " + str(resultTemp.result['costs']['all']))
                print(simulation.constrViolationOutput)
                meanCosts = meanCosts + resultTemp.dictResult['costs']['all']

            meanCosts = meanCosts / pv.iNumberUncertaintySamples
            print(meanCosts)

        elif self.param.param['controlParameters']['checkPVUncertainty'] == True:
            maxPowerBought = [0] * (self.param.param['controlParameters']['numberOfTimeSteps']+1)
            numberOfConstrViolations = 0
            meanCosts = 0
            resultTemp = Result(self.fparam)
            for i in range(0, pv.iNumberUncertaintySamples):
                pv.arrPowerAvailable = pv.arrPvSamples[i]
                self.param.funcUpdate(pv,pp)
                resultTemp = deepcopy(resultOpt)
                simulation.funcStartSimulation(self.param, resultTemp, cm, elec, pv, pp, ci)
                self.funcCheckUncertaintyConstraints(resultTemp, cm, elec, pv, pp, ci)

                if simulation.bConstrViolationInput == True:
                    numberOfConstrViolations = numberOfConstrViolations + 1
                print(simulation.dictConstrViolationOutput)

                for t in range(0, self.param.param['controlParameters']['numberOfTimeSteps']+1):
                    if resultTemp.dictResult['input']['powerBought'][t] >= maxPowerBought[t]:
                        maxPowerBought[t] = resultTemp.dictResult['input']['powerBought'][t]

                meanCosts = meanCosts + resultTemp.dictResult['costs']['all']

            maxPowerBoughtPrice = [i*j for i,j in zip(maxPowerBought, self.param.param['prices']['power'])]
            meanCosts = meanCosts / pv.iNumberUncertaintySamples
            print(np.sum(maxPowerBoughtPrice))
            print("Mean costs: " + meanCosts)
            print("Number of constraints violations: " + numberOfConstrViolations)
        


    def funcCheckUncertaintyConstraints(self, resultOpt, cm, elec, pv, pp, ci):
        self.bConstrViolationInput = False
        if self.param.param['controlParameters']['checkPVUncertainty'] == True:
            for i in self.arrTime:
                if (resultOpt.dictResult['input']['usageOfPV'][i] + resultOpt.dictResult['input']['powerInBatteryPV'][i] - pv.arrPowerAvailable[i]) <= 10**(-6):
                    pass
                else:
                    self.bConstrViolationInput = True
                    self.arrConstrViolationInput.append("Time: " + str(i) + " - " + "PV available")

                    # Costs time x
                    x = 1
                    resultOpt.dictResult['input']['powerBought'][i] = x * (resultOpt.dictResult['input']['powerBought'][i] + resultOpt.dictResult['input']['usageOfPV'][i] + resultOpt.dictResult['input']['powerInBatteryPV'][i] - pv.powerAvailable[i])

                    # Switch off plant in time step
                    """
                    for j in cm.arrOperationPointsABSDES:
                        resultOpt.dictResult['input']['operationPoint_ABSDES'][(i,j)] = 0

                    for j in cm.arrOperationPointsMEOHSYN:
                        resultOpt.dictResult['input']['operationPoint_MEOHSYN'][(i,j)] = 0

                    for j in cm.arrOperationPointsDIS:
                        resultOpt.dictResult['input']['operationPoint_DIS'][(i,j)] = 0


                    resultOpt.dictResult['input']['operationPoint_ABSDES'][(i,0)] = 1
                    resultOpt.dictResult['input']['operationPoint_MEOHSYN'][(i,0)] = 1
                    resultOpt.dictResult['input']['operationPoint_DIS'][(i,0)] = 1

                    for j in range(0, self.param.param['electrolyser']['numberOfEnapterModules']):
                        resultOpt.dictResult['input']['powerElectrolyserRaw'][(i,j)] = 0
                        for k in range(0,4):
                            resultOpt.dictResult['input']['modeElectrolyserRaw'][i,j,k] = 0

                        resultOpt.dictResult['input']['modeElectrolyserRaw'][i,j,3] = 1

                    resultOpt.dictResult['input']['usageOfPV'][i] = 0
                    resultOpt.dictResult['input']['powerInBatteryPV'][i] = 0
                    resultOpt.dictResult['input']['powerInBatteryBought'][i] = 0
                    resultOpt.dictResult['input']['powerOutBattery'][i] = 0
                    resultOpt.dictResult['input']['powerOutBatterySold'][i] = 0
                    resultOpt.dictResult['input']['powerBought'][i] = 0
                    """


        if self.bConstrViolationInput == True:
            print("PV constraint violation")


    def funcCheckConstraints(self, resultOpt, cm, elec, pv, pp, ci):
        # Constraint violation
        # 1: Hydrogen storage equal pressure violation
        # 2: Methanol water storage equal level violation
        # 3: Synthesisgas storage equal pressure violation
        # 4: Battery equal charge violation
        # 5: Minimum amount of methanol produced violation

        # 10: Hydrogen storage min pressure violation
        # 11: Hydrogen storage max pressure violation
        # 12: Methanol water storage min filling level violation
        # 13: Methanol water storage max filling level violation
        # 14: Synthesisgas storage min pressure violation
        # 15: Synthesisgas storage max pressure violation
        # 16: Battery min charge violation
        # 17: Battery max charge violation

        # 20: Minimum amount of methane of outflowing biogas violation
        # 21: Synthesisgas min ratio hydrogen to carbon dioxide violation
        # 22: Synthesisgas max ratio hydrogen to carbon dioxide violation

        # 30: Rate of operation point change distillation upward violation
        # 31: Rate of operation point change distillation downward violation
        # 32: Rate of operation point change methanol synthesis upward violation
        # 33: Rate of operation point change methanol synthesis downward violation
        # 34: Rate of operation point change absorption/desorption upward violation
        # 35: Rate of operation point change absorption/desorption downward violation

 

        self.dictConstrViolationOutput["general"] = []
        if np.abs(resultOpt.dictResult['output']['storageH2Pressure'][0] - resultOpt.dictResult['output']['storageH2Pressure'][self.param.param['controlParameters']['numberOfTimeSteps']]) > self.param.param['constraints']['hydrogenStorageFillEqual']['UpperBound']:
            self.dictConstrViolationOutput["general"].append(1)

        if np.abs(resultOpt.dictResult['output']['storageMethanolWaterFilling'][0] - resultOpt.dictResult['output']['storageMethanolWaterFilling'][self.param.param['controlParameters']['numberOfTimeSteps']]) > self.param.param['constraints']['methanolWaterStorageFillEqual']['UpperBound']:
            self.dictConstrViolationOutput["general"].append(2)

        if np.abs(resultOpt.dictResult['output']['storageSynthesisgasPressure'][0] - resultOpt.dictResult['output']['storageSynthesisgasPressure'][self.param.param['controlParameters']['numberOfTimeSteps']]) > self.param.param['constraints']['synthesisgasStorageFillEqual']['UpperBound']:
            self.dictConstrViolationOutput["general"].append(3)
            
        if np.abs(resultOpt.dictResult['output']['batteryCharge'][0] - resultOpt.dictResult['output']['batteryCharge'][self.param.param['controlParameters']['numberOfTimeSteps']]) > self.param.param['constraints']['batteryChargeEqual']['UpperBound']:
            self.dictConstrViolationOutput["general"].append(4)

        if self.param.param['controlParameters']['benchmark'] == False:
            if np.sum(resultOpt.dictResult['output']['massFlowMethanolOut']) < self.param.param['production']['minMethanolOpt']:
                self.dictConstrViolationOutput["general"].append(5)
        else:
            if np.sum(resultOpt.dictResult['output']['massFlowMethanolOut']) < self.param.param['production']['minMethanolBenchmark']:
                self.dictConstrViolationOutput["general"].append(5)


        for i in self.arrTime[1:]:
            temp = []
            # Hydrogen storage constraints
            if resultOpt.dictResult['output']['storageH2Pressure'][i] < self.param.param['storageH2']['LowerBound']:
                temp.append(10)
            elif resultOpt.dictResult['output']['storageH2Pressure'][i] > self.param.param['storageH2']['UpperBound']:
                temp.append(11)
            
            if resultOpt.dictResult['output']['storageMethanolWaterFilling'][i] < self.param.param['storageMethanolWater']['LowerBound']:
                temp.append(12)
            elif resultOpt.dictResult['output']['storageMethanolWaterFilling'][i] > self.param.param['storageMethanolWater']['UpperBound']:
                temp.append(13)

            if resultOpt.dictResult['output']['storageSynthesisgasPressure'][i] < self.param.param['storageSynthesisgas']['LowerBound']:
                temp.append(14)
            elif resultOpt.dictResult['output']['storageSynthesisgasPressure'][i] > self.param.param['storageSynthesisgas']['UpperBound']:
                temp.append(15)

            if resultOpt.dictResult['output']['batteryCharge'][i] < self.param.param['battery']['minCharge']:
                temp.append(16)
            elif resultOpt.dictResult['output']['batteryCharge'][i] > self.param.param['battery']['capacity']:
                temp.append(17)


            ## Production constraints
            # Minimum amount of methane in outflowing biogas
            if resultOpt.dictResult['output']['moleFractionMethaneBiogasOut'][i] < self.param.param['constraints']['minMoleFractionCH4BiogasOut']:
                temp.append(20)

            # Hydrogen to carbon dioxide ratio lower and upper bound
            if resultOpt.dictResult['output']['moleRatioH2_CO2_Synthesisgas'][i] < self.param.param['constraints']['minRatioH2_CO2_Synthesisgas']:
                temp.append(21)
            elif resultOpt.dictResult['output']['moleRatioH2_CO2_Synthesisgas'][i] > self.param.param['constraints']['maxRatioH2_CO2_Synthesisgas']:
                temp.append(22)
        
            ## Rate of change constraints
            if self.param.param['controlParameters']['rateOfChangeConstranints'] == True and i != self.param.param['controlParameters']['numberOfTimeSteps']:
                # Distillation (mass flow methanol water from storage)
                if resultOpt.dictResult['output']['massFlowMethanolWaterStorageOut'][i+1] - resultOpt.dictResult['output']['massFlowMethanolWaterStorageOut'][i] > self.param.param['constraints']['operationPointChange']['distillationDownwardBound'] * self.param.param['controlParameters']['timeStep']:
                    temp.append(30)
                elif resultOpt.dictResult['output']['massFlowMethanolWaterStorageOut'][i+1] - resultOpt.dictResult['output']['massFlowMethanolWaterStorageOut'][i] < self.param.param['constraints']['operationPointChange']['distillationUpwardBound'] * self.param.param['controlParameters']['timeStep']:
                    temp.append(31)

                # Methanol synthesis (mass flow synthesis gas)
                if resultOpt.dictResult['output']['massFlowSynthesisgasOut'][i+1] - resultOpt.dictResult['output']['massFlowSynthesisgasOut'][i] > self.param.param['constraints']['operationPointChange']['MeOHSynthesisDownwardBound'] * self.param.param['controlParameters']['timeStep']:
                    temp.append(32)
                elif resultOpt.dictResult['output']['massFlowSynthesisgasOut'][i+1] - resultOpt.dictResult['output']['massFlowSynthesisgasOut'][i] < self.param.param['constraints']['operationPointChange']['MeOHSynthesisUpwardBound'] * self.param.param['controlParameters']['timeStep']:
                    temp.append(33)

                # Absorption/Desorption (mass flow methanol water in cycle)
                if resultOpt.dictResult['output']['massFlowMeOHWaterInCycle'][i+1] - resultOpt.dictResult['output']['massFlowMeOHWaterInCycle'][i] > self.param.param['constraints']['operationPointChange']['MeOHWaterInCycleDownwardBound'] * self.param.param['controlParameters']['timeStep']:
                    temp.append(34)
                elif resultOpt.dictResult['output']['massFlowMeOHWaterInCycle'][i+1] - resultOpt.dictResult['output']['massFlowMeOHWaterInCycle'][i] < self.param.param['constraints']['operationPointChange']['MeOHWaterInCycleUpwardBound'] * self.param.param['controlParameters']['timeStep']:
                    temp.append(35)

            if len(temp):
                self.dictConstrViolationOutput["Time step: " + str(i)] = temp
