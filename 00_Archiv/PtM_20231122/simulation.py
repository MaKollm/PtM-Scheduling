#!/usr/bin/env python3.10


#############################
########## Results ##########

import gurobipy as gp
import numpy as np
import matplotlib.pyplot as plt


class Simulation():
    def __init__(self, param):
        self.update(param)


    def update(self, param):
        self.param = param
        self.time = list(range(0,self.param.param['controlParameters']['numberOfTimeSteps']+1))
        self.result = {'output': {}, 'costs': {}}
        self.constrViolationInput = []
        self.constrViolationOutput = {}

    def start_simulation(self, param, result, cf, elec, pv, pp):
        
        self.update(param)
        self.check_uncertainty_constraints(result, cf, elec, pv, pp)
        self.simulate(result, cf, elec, pv, pp)
        self.check_constraints(result, cf, elec, pv, pp)

        result.result['output'] = self.result['output']
        result.result['costs'] = self.result['costs']


    def simulate(self, resultOpt, cf, elec, pv, pp):
        timeStep = self.param.param['controlParameters']['timeStep']
        
        # Output variables
        self.result['output']['storageH2Pressure'] = []
        self.result['output']['storageMethanolWaterFilling'] = []
        self.result['output']['massFlowMethanolOut'] = []
        self.result['output']['moleFractionMethaneBiogasOut'] = []
        self.result['output']['powerPlantABSDES_MEOHSYN'] = []
        self.result['output']['powerPlantDIS'] = []
        self.result['output']['volumeBiogasIn'] = []
        self.result['output']['volumeBiogasOut'] = []
        self.result['output']['moleFractionH2Synthesisgas'] = []
        self.result['output']['moleFractionCO2Synthesisgas'] = []
        self.result['output']['batteryCharge'] = []
        self.result['output']['storageSynthesisgasPressure'] = []
        self.result['output']['massFlowSynthesisgasIn'] = []
        self.result['output']['powerPlantMEOHSYN'] = []
        self.result['output']['massFlowMeOHWaterInCycle'] = []
        self.result['output']['massFlowSynthesisgasOut'] = []
        self.result['output']['massFlowMethanolWaterStorageOut'] = []


        for i in self.time:

            self.result['output']['batteryCharge'].append((self.param.param['battery']['initialCharge'] 
                        + gp.quicksum(resultOpt.result['input']['powerInBatteryPV'][l] for l in self.time[0:i+1]) 
                        + gp.quicksum(resultOpt.result['input']['powerInBatteryBought'][l] for l in self.time[0:i+1])
                        - gp.quicksum(resultOpt.result['input']['powerOutBattery'][l] for l in self.time[0:i+1])
                        - gp.quicksum(resultOpt.result['input']['powerOutBatterySold'][l] for l in self.time[0:i+1])))

            self.result['output']['storageH2Pressure'].append((self.param.param['storageH2']['InitialFilling']
                        + gp.quicksum(resultOpt.result['input']['powerElectrolyserRaw'][(l,n)] * resultOpt.result['input']['electrolyserModeRaw'][(l,n,3)] * self.param.param['electrolyser']['constant'] * timeStep for l in self.time[0:i+1] for n in elec.enapterModules)
                        - gp.quicksum(cf.massFlowHydrogenIn[(j)] * resultOpt.result['input']['operationPoint_ABSDES'][(l,j)] * timeStep for j in cf.ABSDESValues for l in self.time[0:i+1]) 
                        - gp.quicksum(cf.massFlowAdditionalHydrogen[(j)] * resultOpt.result['input']['operationPoint_ABSDES'][(l,j)] * timeStep for j in cf.ABSDESValues for l in self.time[0:i+1])) 
                        * self.param.param['R_H2'] * (self.param.param['Tamb'] + self.param.param['T0']) / (self.param.param['storageH2']['Volume'] * 100000))
            
            self.result['output']['storageMethanolWaterFilling'].append(self.param.param['storageMethanolWater']['InitialFilling'] 
                + gp.quicksum(cf.massFlowMethanolWaterStorageInSynthesis[(j)] / self.param.param['storageMethanolWater']['InitialDensity'] * resultOpt.result['input']['operationPoint_MEOHSYN'][(l,j)] * timeStep for j in cf.synthesisgasInMethanolSynthesisValues for l in self.time[0:i+1]) 
                - gp.quicksum(cf.massFlowMethanolWaterStorageOut[(j)] / self.param.param['storageMethanolWater']['InitialDensity']  * resultOpt.result['input']['operationPoint_DIS'][(l,j)] * timeStep for j in cf.methanolWaterInDistillationValues for l in self.time[0:i+1]))

            self.result['output']['storageSynthesisgasPressure'].append((self.param.param['storageSynthesisgas']['InitialFilling']
                + gp.quicksum(cf.massFlowSynthesisgasIn[(j)] * resultOpt.result['input']['operationPoint_ABSDES'][(l,j)] * timeStep for j in cf.ABSDESValues for l in self.time[0:i+1])
                - gp.quicksum(cf.massFlowSynthesisgasOut[(j)] * resultOpt.result['input']['operationPoint_MEOHSYN'][(l,j)] * timeStep for j in cf.synthesisgasInMethanolSynthesisValues for l in self.time[0:i+1]))
                * self.param.param['R_Synthesisgas'] * (self.param.param['Tamb'] + self.param.param['T0']) / (self.param.param['storageSynthesisgas']['Volume'] * 100000))    

            self.result['output']['massFlowSynthesisgasIn'].append(gp.quicksum(cf.massFlowSynthesisgasIn[(j)] * resultOpt.result['input']['operationPoint_ABSDES'][(i,j)] * timeStep for j in cf.ABSDESValues))
            self.result['output']['massFlowSynthesisgasOut'].append(gp.quicksum(cf.massFlowSynthesisgasOut[(j)] * resultOpt.result['input']['operationPoint_MEOHSYN'][(i,j)] * timeStep for j in cf.synthesisgasInMethanolSynthesisValues))
            self.result['output']['massFlowMethanolWaterStorageOut'].append(gp.quicksum(cf.massFlowMethanolWaterStorageOut[(j)] * resultOpt.result['input']['operationPoint_DIS'][(i,j)] * timeStep for j in cf.methanolWaterInDistillationValues))
            self.result['output']['massFlowMethanolOut'].append(gp.quicksum(cf.massFlowMethanolOut[(j)] * resultOpt.result['input']['operationPoint_DIS'][(i,j)] * timeStep for j in cf.methanolWaterInDistillationValues))
            self.result['output']['moleFractionMethaneBiogasOut'].append(gp.quicksum(cf.moleFractionMethaneBiogasOut[(j)] * resultOpt.result['input']['operationPoint_ABSDES'][(i,j)] for j in cf.ABSDESValues))
            self.result['output']['powerPlantABSDES_MEOHSYN'].append(gp.quicksum(cf.powerPlantComponentsUnit1[(j)] * resultOpt.result['input']['operationPoint_ABSDES'][(i,j)] * timeStep for j in cf.ABSDESValues))
            self.result['output']['powerPlantMEOHSYN'].append(gp.quicksum(cf.powerPlantComponentsUnit2[(j)] * resultOpt.result['input']['operationPoint_MEOHSYN'][(i,j)] * timeStep for j in cf.synthesisgasInMethanolSynthesisValues))
            self.result['output']['powerPlantDIS'].append(gp.quicksum(cf.powerPlantComponentsUnit3[(j)] * resultOpt.result['input']['operationPoint_DIS'][(i,j)] * timeStep for j in cf.methanolWaterInDistillationValues))        
            self.result['output']['massFlowMeOHWaterInCycle'].append(gp.quicksum(cf.massFlowMethanolWaterInCycle[(j)] * resultOpt.result['input']['operationPoint_ABSDES'][(i,j)] for j in cf.ABSDESValues))

            self.result['output']['volumeBiogasIn'].append(gp.quicksum(cf.volumeBiogasIn[(j)] * resultOpt.result['input']['operationPoint_ABSDES'][(i,j)] * timeStep for j in cf.ABSDESValues))
            self.result['output']['volumeBiogasOut'].append(gp.quicksum(cf.volumeBiogasOut[(j)] * resultOpt.result['input']['operationPoint_ABSDES'][(i,j)] * timeStep for j in cf.ABSDESValues))

            self.result['output']['moleFractionH2Synthesisgas'].append(gp.quicksum(cf.moleFractionHydrogenSynthesisgas[(j)] * resultOpt.result['input']['operationPoint_ABSDES'][(i,j)] for j in cf.ABSDESValues))
            self.result['output']['moleFractionCO2Synthesisgas'].append(gp.quicksum(cf.moleFractionCarbondioxideSynthesisgas[(j)] * resultOpt.result['input']['operationPoint_ABSDES'][(i,j)] for j in cf.ABSDESValues))

            for key in self.result['output']:
                self.result['output'][key][i] = self.result['output'][key][i].getValue()


        self.result['output']['moleRatioH2_CO2_Synthesisgas'] = []
        self.result['output']['moleRatioH2_CO2_Synthesisgas'].append(0)



        for i in self.time[1:]:
            self.result['output']['moleRatioH2_CO2_Synthesisgas'].append(self.result['output']['moleFractionH2Synthesisgas'][i] / self.result['output']['moleFractionCO2Synthesisgas'][i])

        # Costs
        self.result['costs']['methanol'] = -np.sum(self.result['output']['massFlowMethanolOut'] * self.param.param['prices']['methanol'])
        self.result['costs']['biogasOut'] = -np.sum(np.array(self.result['output']['volumeBiogasOut']) * self.param.param['methane']['brennwert'] * self.param.param['prices']['methane'])
        self.result['costs']['biogasIn'] = np.sum(np.array(self.result['output']['volumeBiogasIn']) * self.param.param['biogas']['brennwert'] * self.param.param['prices']['biogas'])

        self.result['costs']['powerBought'] = np.sum(np.dot(self.param.param['prices']['power'], resultOpt.result['input']['powerBought']))

        self.result['costs']['powerBatterySold'] = 0.0
        for i in self.time: 
            self.result['costs']['powerBatterySold'] = self.result['costs']['powerBatterySold'] - self.param.param['prices']['powerSold']*resultOpt.result['input']['powerOutBatterySold'][i]
        
        self.result['costs']['all'] = sum(self.result['costs'].values())
        self.result['costs']['allPositive'] = self.result['costs']['biogasIn'] + self.result['costs']['powerBought']
        
        # Save the data in result
        resultOpt.result['output'] = self.result['output']
        resultOpt.result['costs'] = self.result['costs']


    def check_uncertainty_constraints(self, resultOpt, cf, elec, pv, pp):
        self.constrViolationInputBool = False
        if self.param.param['controlParameters']['checkPVUncertainty'] == True:
            for i in self.time:
                if (resultOpt.result['input']['usageOfPV'][i] + resultOpt.result['input']['powerInBatteryPV'][i] - pv.powerAvailable[i]) <= 10**(-6):
                    pass
                else:
                    self.constrViolationInputBool = True
                    self.constrViolationInput.append("Time: " + str(i) + " - " + "PV available")

                    # Costs time x
                    x = 1
                    resultOpt.result['input']['powerBought'][i] = x * (resultOpt.result['input']['powerBought'][i] + resultOpt.result['input']['usageOfPV'][i] + resultOpt.result['input']['powerInBatteryPV'][i] - pv.powerAvailable[i])

                    # Switch off plant in time step
                    """
                    for j in cf.ABSDESValues:
                        resultOpt.result['input']['operationPoint_ABSDES'][(i,j)] = 0

                    for j in cf.synthesisgasInMethanolSynthesisValues:
                        resultOpt.result['input']['operationPoint_MEOHSYN'][(i,j)] = 0

                    for j in cf.methanolWaterInDistillationValues:
                        resultOpt.result['input']['operationPoint_DIS'][(i,j)] = 0


                    resultOpt.result['input']['operationPoint_ABSDES'][(i,0)] = 1
                    resultOpt.result['input']['operationPoint_MEOHSYN'][(i,0)] = 1
                    resultOpt.result['input']['operationPoint_DIS'][(i,0)] = 1

                    for j in range(0, self.param.param['electrolyser']['numberOfEnapterModules']):
                        resultOpt.result['input']['powerElectrolyserRaw'][(i,j)] = 0
                        for k in range(0,4):
                            resultOpt.result['input']['electrolyserModeRaw'][i,j,k] = 0

                        resultOpt.result['input']['electrolyserModeRaw'][i,j,3] = 1

                    resultOpt.result['input']['usageOfPV'][i] = 0
                    resultOpt.result['input']['powerInBatteryPV'][i] = 0
                    resultOpt.result['input']['powerInBatteryBought'][i] = 0
                    resultOpt.result['input']['powerOutBattery'][i] = 0
                    resultOpt.result['input']['powerOutBatterySold'][i] = 0
                    resultOpt.result['input']['powerBought'][i] = 0
                    """


        if self.constrViolationInputBool == True:
            print("PV constraint violation")


    def check_constraints(self, resultOpt, cf, elec, pv, pp):
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
        if np.abs(resultOpt.result['output']['storageH2Pressure'][0] - resultOpt.result['output']['storageH2Pressure'][self.param.param['controlParameters']['numberOfTimeSteps']]) > self.param.param['constraints']['hydrogenStorageFillEqual']['UpperBound']:
            self.constrViolationOutput["general"].append(1)

        if np.abs(resultOpt.result['output']['storageMethanolWaterFilling'][0] - resultOpt.result['output']['storageMethanolWaterFilling'][self.param.param['controlParameters']['numberOfTimeSteps']]) > self.param.param['constraints']['methanolWaterStorageFillEqual']['UpperBound']:
            self.constrViolationOutput["general"].append(2)

        if np.abs(resultOpt.result['output']['storageSynthesisgasPressure'][0] - resultOpt.result['output']['storageSynthesisgasPressure'][self.param.param['controlParameters']['numberOfTimeSteps']]) > self.param.param['constraints']['synthesisgasStorageFillEqual']['UpperBound']:
            self.constrViolationOutput["general"].append(3)
            
        if np.abs(resultOpt.result['output']['batteryCharge'][0] - resultOpt.result['output']['batteryCharge'][self.param.param['controlParameters']['numberOfTimeSteps']]) > self.param.param['constraints']['batteryChargeEqual']['UpperBound']:
            self.constrViolationOutput["general"].append(4)

        if self.param.param['controlParameters']['benchmark'] == False:
            if np.sum(self.result['output']['massFlowMethanolOut']) < self.param.param['methanol']['minimumAmountOpt']:
                self.constrViolationOutput["general"].append(5)
        else:
            if np.sum(self.result['output']['massFlowMethanolOut']) < self.param.param['methanol']['minimumAmountBenchmark']:
                self.constrViolationOutput["general"].append(5)


        for i in self.time[1:]:
            temp = []
            # Hydrogen storage constraints
            if resultOpt.result['output']['storageH2Pressure'][i] < self.param.param['storageH2']['LowerBound']:
                temp.append(10)
            elif resultOpt.result['output']['storageH2Pressure'][i] > self.param.param['storageH2']['UpperBound']:
                temp.append(11)
            
            if resultOpt.result['output']['storageMethanolWaterFilling'][i] < self.param.param['storageMethanolWater']['LowerBound']:
                temp.append(12)
            elif resultOpt.result['output']['storageMethanolWaterFilling'][i] > self.param.param['storageMethanolWater']['UpperBound']:
                temp.append(13)

            if resultOpt.result['output']['storageSynthesisgasPressure'][i] < self.param.param['storageSynthesisgas']['LowerBound']:
                temp.append(14)
            elif resultOpt.result['output']['storageSynthesisgasPressure'][i] > self.param.param['storageSynthesisgas']['UpperBound']:
                temp.append(15)

            if resultOpt.result['output']['batteryCharge'][i] < self.param.param['battery']['minCharge']:
                temp.append(16)
            elif resultOpt.result['output']['batteryCharge'][i] > self.param.param['battery']['capacity']:
                temp.append(17)


            ## Production constraints
            # Minimum amount of methane in outflowing biogas
            if resultOpt.result['output']['moleFractionMethaneBiogasOut'][i] < self.param.param['constraints']['minMoleFractionCH4BiogasOut']:
                temp.append(20)

            # Hydrogen to carbon dioxide ratio lower and upper bound
            if resultOpt.result['output']['moleRatioH2_CO2_Synthesisgas'][i] < self.param.param['constraints']['minRatioH2_CO2_Synthesisgas']:
                temp.append(21)
            elif resultOpt.result['output']['moleRatioH2_CO2_Synthesisgas'][i] > self.param.param['constraints']['maxRatioH2_CO2_Synthesisgas']:
                temp.append(22)
        
            ## Rate of change constraints
            if self.param.param['controlParameters']['rateOfChangeConstranints'] == True and i != self.param.param['controlParameters']['numberOfTimeSteps']:
                # Distillation (mass flow methanol water from storage)
                if resultOpt.result['output']['massFlowMethanolWaterStorageOut'][i+1] - resultOpt.result['output']['massFlowMethanolWaterStorageOut'][i] > self.param.param['constraints']['operationPointChange']['distillationDownwardBound'] * self.param.param['controlParameters']['timeStep']:
                    temp.append(30)
                elif resultOpt.result['output']['massFlowMethanolWaterStorageOut'][i+1] - resultOpt.result['output']['massFlowMethanolWaterStorageOut'][i] < self.param.param['constraints']['operationPointChange']['distillationUpwardBound'] * self.param.param['controlParameters']['timeStep']:
                    temp.append(31)

                # Methanol synthesis (mass flow synthesis gas)
                if resultOpt.result['output']['massFlowSynthesisgasOut'][i+1] - resultOpt.result['output']['massFlowSynthesisgasOut'][i] > self.param.param['constraints']['operationPointChange']['MeOHSynthesisDownwardBound'] * self.param.param['controlParameters']['timeStep']:
                    temp.append(32)
                elif resultOpt.result['output']['massFlowSynthesisgasOut'][i+1] - resultOpt.result['output']['massFlowSynthesisgasOut'][i] < self.param.param['constraints']['operationPointChange']['MeOHSynthesisUpwardBound'] * self.param.param['controlParameters']['timeStep']:
                    temp.append(33)

                # Absorption/Desorption (mass flow methanol water in cycle)
                if resultOpt.result['output']['massFlowMeOHWaterInCycle'][i+1] - resultOpt.result['output']['massFlowMeOHWaterInCycle'][i] > self.param.param['constraints']['operationPointChange']['MeOHWaterInCycleDownwardBound'] * self.param.param['controlParameters']['timeStep']:
                    temp.append(34)
                elif resultOpt.result['output']['massFlowMeOHWaterInCycle'][i+1] - resultOpt.result['output']['massFlowMeOHWaterInCycle'][i] < self.param.param['constraints']['operationPointChange']['MeOHWaterInCycleUpwardBound'] * self.param.param['controlParameters']['timeStep']:
                    temp.append(35)

            if len(temp):
                self.constrViolationOutput["Time step: " + str(i)] = temp