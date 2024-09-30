#!/usr/bin/env python3.10


#############################
########## Results ##########

import gurobipy as gp
import numpy as np
import matplotlib.pyplot as plt
from gurobipy import GRB
from gurobipy import *
from scipy.io import savemat


class Results():
    def __init__(self, param, OptModel, cf, elec, pv):
        self.param = param
        self.OptModel = OptModel
        self.cf = cf
        self.elec = elec
        self.pv = pv
        self.time = OptModel.time

        self.result = {'input': {}, 'output': {}, 'costs': {}, 'input default': {}}

    

    def input(self):
        m = self.OptModel.m
        OptModel = self.OptModel
        cf = self.cf
        param = self.param
        elec = self.elec
        
        # Input variables
        if m.Status == GRB.OPTIMAL or m.Status == GRB.TIME_LIMIT:
            solution = m.getAttr('X', OptModel.operationPoint_ABSDES)
            self.result['input default']['operationPoint_ABSDES'] = solution
            self.result['input']['hydrogenInput'] = []
            self.result['input']['biogasInput'] = []
            for i in self.time:
                for j in cf.ABSDESValues:
                    if solution[i,j] == 1:
                        self.result['input']['hydrogenInput'].append(cf.hydrogenInValuesConversion[j])
                        self.result['input']['biogasInput'].append(cf.biogasInValuesConversion[j])

            solution = m.getAttr('X', OptModel.operationPoint_MEOHSYN)
            self.result['input default']['operationPoint_MEOHSYN'] = solution
            self.result['input']['synthesisgasInMethanolSynthesis'] = []
            for i in self.time:
                for j in cf.synthesisgasInMethanolSynthesisValues:
                    if solution[i,j] == 1:
                        self.result['input']['synthesisgasInMethanolSynthesis'].append(cf.synthesisgasInMethanolSynthesisValuesConversion[j])

            solution = m.getAttr('X', OptModel.operationPoint_DIS)
            self.result['input default']['operationPoint_DIS'] = solution
            self.result['input']['methanolWaterInDistillation'] = []
            for i in self.time:
                for j in cf.methanolWaterInDistillationValues:
                    if solution[i,j] == 1:
                        self.result['input']['methanolWaterInDistillation'].append(cf.methanolWaterInDistillationValuesConversion[j])

            solution = m.getAttr('X', OptModel.operationPointSwitch)
            print(solution)

            self.result['input']['electrolyserMode'] = {}
            for i in range(0, param['electrolyser']['numberOfEnapterModules']):
                self.result['input']['electrolyserMode'][(i)] = []

            solution = m.getAttr('X', OptModel.powerElectrolyser)
            solution1 = m.getAttr('X', OptModel.electrolyserMode)
            self.result['input']['powerElectrolyser'] = []
            self.result['input default']['powerElectrolyser'] = solution
            self.result['input default']['electrolyserMode'] = solution1
            for i in self.time:
                temp = 0
                for n in elec.enapterModules:
                    if solution1[i,n,0] == 1:
                        temp = temp + param['electrolyser']['powerLowerBound'] + (param['electrolyser']['powerUpperBound'] - param['electrolyser']['powerLowerBound']) / 2
                        self.result['input']['electrolyserMode'][(n)].append("ramp-up")
                    elif solution1[i,n,1] == 1:
                        temp = temp + 0.3
                        self.result['input']['electrolyserMode'][(n)].append("standby")
                    elif solution1[i,n,2] == 1:
                        temp = temp + 0
                        self.result['input']['electrolyserMode'][(n)].append("off")
                    elif solution1[i,n,3] == 1:
                        temp = temp + solution[i,n]
                        self.result['input']['electrolyserMode'][(n)].append("on")
                        
                self.result['input']['powerElectrolyser'].append(temp)

            self.result['input']['usageOfPV'] = []
            solution = m.getAttr('X', OptModel.usageOfPV)
            for i in self.time:
                self.result['input']['usageOfPV'].append(solution[i])   
            
            self.result['input']['powerInBatteryPV'] = []
            solution = m.getAttr('X', OptModel.powerInBatteryPV)
            for i in self.time:
               self.result['input']['powerInBatteryPV'].append(solution[i])

            self.result['input']['powerInBatteryBought'] = []
            solution = m.getAttr('X', OptModel.powerInBatteryBought)
            for i in self.time:
                self.result['input']['powerInBatteryBought'].append(solution[i])

            self.result['input']['powerOutBattery'] = []
            solution = m.getAttr('X', OptModel.powerOutBattery)
            for i in self.time:
                self.result['input']['powerOutBattery'].append(solution[i])

            self.result['input']['powerOutBatterySold'] = []
            solution = m.getAttr('X', OptModel.powerOutBatterySold)
            for i in self.time:
                self.result['input']['powerOutBatterySold'].append(solution[i])

            self.result['input']['powerBought'] = []
            solution = m.getAttr('X', OptModel.powerBought)
            for i in self.time:
                self.result['input']['powerBought'].append(solution[i])

        print('Input variables')
        print('')
        for key in self.result['input']:
            print(key + ': ', self.result['input'][key]) 
            print(len(self.result['input'][key]))
            print('----------')

    
    def output(self):
        m = self.OptModel.m
        time = self.OptModel.time
        OptModel = self.OptModel
        cf = self.cf
        param = self.param
        pv = self.pv
        elec = self.elec
        
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

        param['pv']['powerAvailable'] = []

        for i in time:

            self.result['output']['batteryCharge'].append((param['battery']['initialCharge'] 
                        + gp.quicksum(self.result['input']['powerInBatteryPV'][l] for l in time[0:i+1]) 
                        + gp.quicksum(self.result['input']['powerInBatteryBought'][l] for l in time[0:i+1])
                        - gp.quicksum(self.result['input']['powerOutBattery'][l] for l in time[0:i+1])
                        - gp.quicksum(self.result['input']['powerOutBatterySold'][l] for l in time[0:i+1])))

            self.result['output']['storageH2Pressure'].append((param['storageH2']['InitialFilling']
                        + gp.quicksum(self.result['input default']['powerElectrolyser'][(l,n)] * self.result['input default']['electrolyserMode'][(l,n,3)] * param['electrolyser']['constant'] for l in time[0:i+1] for n in elec.enapterModules)
                        - gp.quicksum(cf.massFlowHydrogenIn[(j)] * self.result['input default']['operationPoint_ABSDES'][(l,j)] for j in cf.ABSDESValues for l in time[0:i+1]) 
                        - gp.quicksum(cf.massFlowAdditionalHydrogen[(j)] * self.result['input default']['operationPoint_ABSDES'][(l,j)] for j in cf.ABSDESValues for l in time[0:i+1])) 
                        * param['R_H2'] * (param['Tamb'] + param['T0']) / (param['storageH2']['Volume'] * 100000))
            
            self.result['output']['storageMethanolWaterFilling'].append(param['storageMethanolWater']['InitialFilling'] 
                + gp.quicksum(cf.massFlowMethanolWaterStorageInSynthesis[(j)] / param['storageMethanolWater']['InitialDensity'] * self.result['input default']['operationPoint_MEOHSYN'][(l,j)] for j in cf.synthesisgasInMethanolSynthesisValues for l in time[0:i+1]) 
                - gp.quicksum(cf.massFlowMethanolWaterStorageOut[(j)] / param['storageMethanolWater']['InitialDensity']  * self.result['input default']['operationPoint_DIS'][(l,j)] for j in cf.methanolWaterInDistillationValues for l in time[0:i+1]))

            self.result['output']['storageSynthesisgasPressure'].append((param['storageSynthesisgas']['InitialFilling']
                + gp.quicksum(cf.massFlowSynthesisgasIn[(j)] * self.result['input default']['operationPoint_ABSDES'][(l,j)] for j in cf.ABSDESValues for l in time[0:i+1])
                - gp.quicksum(cf.massFlowSynthesisgasOut[(j)] * self.result['input default']['operationPoint_MEOHSYN'][(l,j)] for j in cf.synthesisgasInMethanolSynthesisValues for l in time[0:i+1]))
                * param['R_Synthesisgas'] * (param['Tamb'] + param['T0']) / (param['storageSynthesisgas']['Volume'] * 100000))    

            self.result['output']['massFlowSynthesisgasIn'].append(gp.quicksum(cf.massFlowSynthesisgasIn[(j)] * self.result['input default']['operationPoint_ABSDES'][(i,j)] for j in cf.ABSDESValues))
            self.result['output']['massFlowMethanolOut'].append(gp.quicksum(cf.massFlowMethanolOut[(j)] * self.result['input default']['operationPoint_DIS'][(i,j)] for j in cf.methanolWaterInDistillationValues))
            self.result['output']['moleFractionMethaneBiogasOut'].append(gp.quicksum(cf.moleFractionMethaneBiogasOut[(j)] * self.result['input default']['operationPoint_ABSDES'][(i,j)] for j in cf.ABSDESValues))
            self.result['output']['powerPlantABSDES_MEOHSYN'].append(gp.quicksum(cf.powerPlantComponentsUnit1[(j)] * self.result['input default']['operationPoint_ABSDES'][(i,j)] for j in cf.ABSDESValues))
            self.result['output']['powerPlantDIS'].append(gp.quicksum(cf.powerPlantComponentsUnit3[(j)] * self.result['input default']['operationPoint_DIS'][(i,j)] for j in cf.methanolWaterInDistillationValues))
            self.result['output']['powerPlantMEOHSYN'].append(gp.quicksum(cf.powerPlantComponentsUnit2[(j)] * self.result['input default']['operationPoint_MEOHSYN'][(i,j)] for j in cf.synthesisgasInMethanolSynthesisValues))        
            self.result['output']['massFlowMeOHWaterInCycle'].append(gp.quicksum(cf.massFlowMethanolWaterInCycle[(j)] * self.result['input default']['operationPoint_ABSDES'][(i,j)] for j in cf.ABSDESValues))

            self.result['output']['volumeBiogasIn'].append(gp.quicksum(cf.volumeBiogasIn[(j)] * self.result['input default']['operationPoint_ABSDES'][(i,j)] for j in cf.ABSDESValues))
            self.result['output']['volumeBiogasOut'].append(gp.quicksum(cf.volumeBiogasOut[(j)] * self.result['input default']['operationPoint_ABSDES'][(i,j)] for j in cf.ABSDESValues))

            self.result['output']['moleFractionH2Synthesisgas'].append(gp.quicksum(cf.moleFractionHydrogenSynthesisgas[(j)] * self.result['input default']['operationPoint_ABSDES'][(i,j)] for j in cf.ABSDESValues))
            self.result['output']['moleFractionCO2Synthesisgas'].append(gp.quicksum(cf.moleFractionCarbondioxideSynthesisgas[(j)] * self.result['input default']['operationPoint_ABSDES'][(i,j)] for j in cf.ABSDESValues))

            param['pv']['powerAvailable'].append(pv.powerAvailable[i])

            for key in self.result['output']:
                self.result['output'][key][i] = self.result['output'][key][i].getValue()


        self.result['output']['moleRatioH2_CO2_Synthesisgas'] = []
        self.result['output']['moleRatioH2_CO2_Synthesisgas'].append(0)

        for i in time[1:]:
            self.result['output']['moleRatioH2_CO2_Synthesisgas'].append(self.result['output']['moleFractionH2Synthesisgas'][i] / self.result['output']['moleFractionCO2Synthesisgas'][i])

        # Costs
        self.result['costs']['methanol'] = -np.sum(self.result['output']['massFlowMethanolOut'] * param['prices']['methanol'])
        self.result['costs']['biogasOut'] = -np.sum(np.array(self.result['output']['volumeBiogasOut']) * param['methane']['brennwert'] * param['prices']['methane'])
        self.result['costs']['biogasIn'] = np.sum(np.array(self.result['output']['volumeBiogasIn']) * param['biogas']['brennwert'] * param['prices']['biogas'])
        self.result['costs']['powerBought'] = np.sum(np.dot(param['prices']['power'], self.result['input']['powerBought']))

        temp = 0.0
        for i in time:
            temp = temp + param['prices']['powerSold']*self.result['input']['powerOutBatterySold'][i]

        self.result['costs']['powerBatterySold'] = -temp


        print('Output variables')
        print('')
        for key in self.result['output']:
            print(key + ': ', self.result['output'][key]) 
            print('----------')

        print('#########')
        print('')
        print('Price power')
        print(param['prices']['power'])
        print('')
        print('#########')

        print('#########')
        print('')
        print('PV available')
        print(param['pv']['powerAvailable'])
        print('')
        print('###################################')

        print('Costs')
        print('')
        for key in self.result['costs']:
            print(key + ': ', self.result['costs'][key])

        self.result['costs']['all'] = sum(self.result['costs'].values())
        print(self.result['costs']['all'])

        print('')
        print("Runtime:")
        print(m.Runtime)

        print('')
        print('##########')
        print('Feasibility:')
        print(m.printQuality())

        ###############################
        ########## Save data ##########

        if param['controlParameters']['benchmark'] == True:
            string = "benchmark"
        else:
            string = "opt"

        savemat("data_param_" + string + ".mat", param)
        savemat("data_output_" + string + ".mat", self.result['output'])
        savemat("data_input_" + string + ".mat", self.result['input'])
        savemat("data_costs_" + string + ".mat", self.result['costs'])


        ###################################
        ########## Visualization ########## 

        #columns = ('methanol','biogas out','biogas in','power plant','power elect.', 'pv', 'batt. in', 'batt. out', 'batt. sold')
        columns = ('methanol','biogas out','biogas in', 'power bought', 'batt. sold')
        index = np.arange(len(columns)) + 0.3
        bar_width = 0.4

        n_rows = len(self.result['costs'])

        data = []
        for key in self.result['costs']:
            data.append(self.result['costs'][key])

        y_offset = np.zeros(len(columns))

        cell_text = []
        plt.bar(index, data[:-1], bar_width, bottom=y_offset)
        plt.axhline(y = 0, color = 'k', linestyle = '-')
        plt.ylabel('operation costs')
        numbers = [1,2,3,4,5]
        plt.xticks(index, columns)
        plt.title('Composition of operation costs')
        plt.show()