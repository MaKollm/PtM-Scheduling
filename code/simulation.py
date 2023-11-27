#!/usr/bin/env python3.10


#############################
########## Results ##########

import gurobipy as gp
import numpy as np
import matplotlib.pyplot as plt


class Simulation():
    def __init__(self, param):
        self.funcUpdate(param)


    def funcUpdate(self, param):
        self.param = param
        self.time = list(range(0,self.param.param['controlParameters']['numberOfTimeSteps']+1))
        self.dictResult = {'output': {}, 'costs': {}}
        self.dictOutput = {}
        self.dictCosts = {}
        self.constrViolationInput = []
        self.constrViolationOutput = {}

    def funcStartSimulation(self, param, resultOpt, cm, elec, pv, pp):
        
        self.funcUpdate(param)
        self.funcSimulate(resultOpt, cm, elec, pv, pp)
        self.funcCheckUncertaintyConstraints(resultOpt, cm, elec, pv, pp)
        self.funcCheckConstraints(resultOpt, cm, elec, pv, pp)

        #resultOpt.dictResult['output'] = self.dictResult['output']
        #resultOpt.dictResult['costs'] = self.dictResult['costs']

    def funcSimulate(self, resultOpt, cm, elec, pv, pp):
        timeStep = self.param.param['controlParameters']['timeStep']
        
        # Output variables
        self.dictOutput['storageH2Pressure'] = []
        self.dictOutput['storageMethanolWaterFilling'] = []
        self.dictOutput['massFlowMethanolOut'] = []
        self.dictOutput['moleFractionMethaneBiogasOut'] = []
        self.dictOutput['powerPlantABSDES_MEOHSYN'] = []
        self.dictOutput['powerPlantDIS'] = []
        self.dictOutput['volumeBiogasIn'] = []
        self.dictOutput['volumeBiogasOut'] = []
        self.dictOutput['moleFractionH2Synthesisgas'] = []
        self.dictOutput['moleFractionCO2Synthesisgas'] = []
        self.dictOutput['batteryCharge'] = []
        self.dictOutput['storageSynthesisgasPressure'] = []
        self.dictOutput['massFlowSynthesisgasIn'] = []
        self.dictOutput['powerPlantMEOHSYN'] = []
        self.dictOutput['massFlowMeOHWaterInCycle'] = []
        self.dictOutput['massFlowSynthesisgasOut'] = []
        self.dictOutput['massFlowMethanolWaterStorageOut'] = []


        for i in self.time:

            self.dictOutput['batteryCharge'].append((self.param.param['battery']['initialCharge'] 
                        + gp.quicksum(resultOpt.dictResult['input']['powerInBatteryPV'][l] for l in self.time[0:i+1]) 
                        + gp.quicksum(resultOpt.dictResult['input']['powerInBatteryBought'][l] for l in self.time[0:i+1])
                        - gp.quicksum(resultOpt.dictResult['input']['powerOutBattery'][l] for l in self.time[0:i+1])
                        - gp.quicksum(resultOpt.dictResult['input']['powerOutBatterySold'][l] for l in self.time[0:i+1])))

            self.dictOutput['storageH2Pressure'].append((self.param.param['storageH2']['InitialFilling']
                        + gp.quicksum(resultOpt.dictResult['input']['powerElectrolyserRaw'][(l,n)] * resultOpt.dictResult['input']['electrolyserModeRaw'][(l,n,3)] * self.param.param['electrolyser']['constant'] * timeStep for l in self.time[0:i+1] for n in elec.arrEnapterModules)
                        - gp.quicksum(cm.massFlowHydrogenIn[(j)] * resultOpt.dictResult['input']['operationPoint_ABSDES'][(l,j)] * timeStep for j in cm.arrOperationPointsABSDES for l in self.time[0:i+1]) 
                        - gp.quicksum(cm.massFlowAdditionalHydrogen[(j)] * resultOpt.dictResult['input']['operationPoint_ABSDES'][(l,j)] * timeStep for j in cm.arrOperationPointsABSDES for l in self.time[0:i+1])) 
                        * self.param.param['R_H2'] * (self.param.param['Tamb'] + self.param.param['T0']) / (self.param.param['storageH2']['Volume'] * 100000))
            
            self.dictOutput['storageMethanolWaterFilling'].append(self.param.param['storageMethanolWater']['InitialFilling'] 
                + gp.quicksum(cm.massFlowMethanolWaterStorageInSynthesis[(j)] / self.param.param['storageMethanolWater']['InitialDensity'] * resultOpt.dictResult['input']['operationPoint_MEOHSYN'][(l,j)] * timeStep for j in cm.arrOperationPointsMEOHSYN for l in self.time[0:i+1]) 
                - gp.quicksum(cm.massFlowMethanolWaterStorageOut[(j)] / self.param.param['storageMethanolWater']['InitialDensity']  * resultOpt.dictResult['input']['operationPoint_DIS'][(l,j)] * timeStep for j in cm.arrOperationPointsDIS for l in self.time[0:i+1]))

            self.dictOutput['storageSynthesisgasPressure'].append((self.param.param['storageSynthesisgas']['InitialFilling']
                + gp.quicksum(cm.massFlowSynthesisgasIn[(j)] * resultOpt.dictResult['input']['operationPoint_ABSDES'][(l,j)] * timeStep for j in cm.arrOperationPointsABSDES for l in self.time[0:i+1])
                - gp.quicksum(cm.massFlowSynthesisgasOut[(j)] * resultOpt.dictResult['input']['operationPoint_MEOHSYN'][(l,j)] * timeStep for j in cm.arrOperationPointsMEOHSYN for l in self.time[0:i+1]))
                * self.param.param['R_Synthesisgas'] * (self.param.param['Tamb'] + self.param.param['T0']) / (self.param.param['storageSynthesisgas']['Volume'] * 100000))    

            self.dictOutput['massFlowSynthesisgasIn'].append(gp.quicksum(cm.massFlowSynthesisgasIn[(j)] * resultOpt.dictResult['input']['operationPoint_ABSDES'][(i,j)] * timeStep for j in cm.arrOperationPointsABSDES))
            self.dictOutput['massFlowSynthesisgasOut'].append(gp.quicksum(cm.massFlowSynthesisgasOut[(j)] * resultOpt.dictResult['input']['operationPoint_MEOHSYN'][(i,j)] * timeStep for j in cm.arrOperationPointsMEOHSYN))
            self.dictOutput['massFlowMethanolWaterStorageOut'].append(gp.quicksum(cm.massFlowMethanolWaterStorageOut[(j)] * resultOpt.dictResult['input']['operationPoint_DIS'][(i,j)] * timeStep for j in cm.arrOperationPointsDIS))
            self.dictOutput['massFlowMethanolOut'].append(gp.quicksum(cm.massFlowMethanolOut[(j)] * resultOpt.dictResult['input']['operationPoint_DIS'][(i,j)] * timeStep for j in cm.arrOperationPointsDIS))
            self.dictOutput['moleFractionMethaneBiogasOut'].append(gp.quicksum(cm.moleFractionMethaneBiogasOut[(j)] * resultOpt.dictResult['input']['operationPoint_ABSDES'][(i,j)] for j in cm.arrOperationPointsABSDES))
            self.dictOutput['powerPlantABSDES_MEOHSYN'].append(gp.quicksum(cm.powerPlantComponentsUnit1[(j)] * resultOpt.dictResult['input']['operationPoint_ABSDES'][(i,j)] * timeStep for j in cm.arrOperationPointsABSDES))
            self.dictOutput['powerPlantMEOHSYN'].append(gp.quicksum(cm.powerPlantComponentsUnit2[(j)] * resultOpt.dictResult['input']['operationPoint_MEOHSYN'][(i,j)] * timeStep for j in cm.arrOperationPointsMEOHSYN))
            self.dictOutput['powerPlantDIS'].append(gp.quicksum(cm.powerPlantComponentsUnit3[(j)] * resultOpt.dictResult['input']['operationPoint_DIS'][(i,j)] * timeStep for j in cm.arrOperationPointsDIS))        
            self.dictOutput['massFlowMeOHWaterInCycle'].append(gp.quicksum(cm.massFlowMethanolWaterInCycle[(j)] * resultOpt.dictResult['input']['operationPoint_ABSDES'][(i,j)] for j in cm.arrOperationPointsABSDES))

            self.dictOutput['volumeBiogasIn'].append(gp.quicksum(cm.volumeBiogasIn[(j)] * resultOpt.dictResult['input']['operationPoint_ABSDES'][(i,j)] * timeStep for j in cm.arrOperationPointsABSDES))
            self.dictOutput['volumeBiogasOut'].append(gp.quicksum(cm.volumeBiogasOut[(j)] * resultOpt.dictResult['input']['operationPoint_ABSDES'][(i,j)] * timeStep for j in cm.arrOperationPointsABSDES))
            self.dictOutput['moleFractionH2Synthesisgas'].append(gp.quicksum(cm.moleFractionHydrogenSynthesisgas[(j)] * resultOpt.dictResult['input']['operationPoint_ABSDES'][(i,j)] for j in cm.arrOperationPointsABSDES))
            self.dictOutput['moleFractionCO2Synthesisgas'].append(gp.quicksum(cm.moleFractionCarbondioxideSynthesisgas[(j)] * resultOpt.dictResult['input']['operationPoint_ABSDES'][(i,j)] for j in cm.arrOperationPointsABSDES))

            for key in self.dictOutput:
                self.dictOutput[key][i] = self.dictOutput[key][i].getValue()


        self.dictOutput['moleRatioH2_CO2_Synthesisgas'] = []
        self.dictOutput['moleRatioH2_CO2_Synthesisgas'].append(0)



        for i in self.time[1:]:
            self.dictOutput['moleRatioH2_CO2_Synthesisgas'].append(self.dictOutput['moleFractionH2Synthesisgas'][i] / self.dictOutput['moleFractionCO2Synthesisgas'][i])

        # Costs
        self.dictCosts['methanol'] = -np.sum(self.dictOutput['massFlowMethanolOut'] * self.param.param['prices']['methanol'])
        self.dictCosts['biogasOut'] = -np.sum(np.array(self.dictOutput['volumeBiogasOut']) * self.param.param['methane']['brennwert'] * self.param.param['prices']['methane'])
        self.dictCosts['biogasIn'] = np.sum(np.array(self.dictOutput['volumeBiogasIn']) * self.param.param['biogas']['brennwert'] * self.param.param['prices']['biogas'])

        self.dictCosts['powerBought'] = np.sum(np.dot(self.param.param['prices']['power'], resultOpt.dictResult['input']['powerBought']))

        self.dictCosts['powerBatterySold'] = 0.0
        for i in self.time: 
            self.dictCosts['powerBatterySold'] = self.dictCosts['powerBatterySold'] - self.param.param['prices']['powerSold']*resultOpt.dictResult['input']['powerOutBatterySold'][i]
        
        self.dictCosts['all'] = sum(self.dictCosts.values())
        self.dictCosts['allPositive'] = self.dictCosts['biogasIn'] + self.dictCosts['powerBought']
        
        # Save the data in result
        resultOpt.dictResult['output'] = self.dictOutput
        resultOpt.dictResult['costs'] = self.dictCosts


    def funcCheckUncertaintyConstraints(self, resultOpt, cm, elec, pv, pp):
        self.constrViolationInputBool = False
        if self.param.param['controlParameters']['checkPVUncertainty'] == True:
            for i in self.time:
                if (resultOpt.dictResult['input']['usageOfPV'][i] + resultOpt.dictResult['input']['powerInBatteryPV'][i] - pv.powerAvailable[i]) <= 10**(-6):
                    pass
                else:
                    self.constrViolationInputBool = True
                    self.constrViolationInput.append("Time: " + str(i) + " - " + "PV available")

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
                            resultOpt.dictResult['input']['electrolyserModeRaw'][i,j,k] = 0

                        resultOpt.dictResult['input']['electrolyserModeRaw'][i,j,3] = 1

                    resultOpt.dictResult['input']['usageOfPV'][i] = 0
                    resultOpt.dictResult['input']['powerInBatteryPV'][i] = 0
                    resultOpt.dictResult['input']['powerInBatteryBought'][i] = 0
                    resultOpt.dictResult['input']['powerOutBattery'][i] = 0
                    resultOpt.dictResult['input']['powerOutBatterySold'][i] = 0
                    resultOpt.dictResult['input']['powerBought'][i] = 0
                    """


        if self.constrViolationInputBool == True:
            print("PV constraint violation")


    def funcCheckConstraints(self, resultOpt, cm, elec, pv, pp):
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

 

        self.constrViolationOutput["general"] = []
        if np.abs(resultOpt.dictResult['output']['storageH2Pressure'][0] - resultOpt.dictResult['output']['storageH2Pressure'][self.param.param['controlParameters']['numberOfTimeSteps']]) > self.param.param['constraints']['hydrogenStorageFillEqual']['UpperBound']:
            self.constrViolationOutput["general"].append(1)

        if np.abs(resultOpt.dictResult['output']['storageMethanolWaterFilling'][0] - resultOpt.dictResult['output']['storageMethanolWaterFilling'][self.param.param['controlParameters']['numberOfTimeSteps']]) > self.param.param['constraints']['methanolWaterStorageFillEqual']['UpperBound']:
            self.constrViolationOutput["general"].append(2)

        if np.abs(resultOpt.dictResult['output']['storageSynthesisgasPressure'][0] - resultOpt.dictResult['output']['storageSynthesisgasPressure'][self.param.param['controlParameters']['numberOfTimeSteps']]) > self.param.param['constraints']['synthesisgasStorageFillEqual']['UpperBound']:
            self.constrViolationOutput["general"].append(3)
            
        if np.abs(resultOpt.dictResult['output']['batteryCharge'][0] - resultOpt.dictResult['output']['batteryCharge'][self.param.param['controlParameters']['numberOfTimeSteps']]) > self.param.param['constraints']['batteryChargeEqual']['UpperBound']:
            self.constrViolationOutput["general"].append(4)

        if self.param.param['controlParameters']['benchmark'] == False:
            if np.sum(resultOpt.dictResult['output']['massFlowMethanolOut']) < self.param.param['methanol']['minimumAmountOpt']:
                self.constrViolationOutput["general"].append(5)
        else:
            if np.sum(resultOpt.dictResult['output']['massFlowMethanolOut']) < self.param.param['methanol']['minimumAmountBenchmark']:
                self.constrViolationOutput["general"].append(5)


        for i in self.time[1:]:
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
                self.constrViolationOutput["Time step: " + str(i)] = temp