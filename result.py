#!/usr/bin/env python3.10


#############################
########## Results ##########

import gurobipy as gp
import numpy as np
import matplotlib.pyplot as plt
from gurobipy import GRB
from gurobipy import *
from scipy.io import savemat


class Result():
    def __init__(self, param):
        self.update(param)


    def update(self, param):
        self.param = param
        self.time = list(range(0,self.param.param['controlParameters']['numberOfTimeSteps']+1))
        self.result = {'input': {}, 'output': {}, 'costs': {}}


    def get_results(self, optModel, cf, elec, pv, pp):
    
        self.input(optModel, cf, elec, pv, pp)

    def input(self, optModel, cf, elec, pv, pp):
        
        # Input variables
        if optModel.m.Status == GRB.OPTIMAL or optModel.m.Status == GRB.TIME_LIMIT:
            solution = optModel.m.getAttr('X', optModel.operationPoint_ABSDES)
            self.result['input']['operationPoint_ABSDES'] = solution
            self.result['input']['hydrogenInput'] = []
            self.result['input']['biogasInput'] = []
            for i in self.time:
                for j in cf.ABSDESValues:
                    if solution[i,j] == 1:
                        self.result['input']['hydrogenInput'].append(cf.hydrogenInValuesConversion[j])
                        self.result['input']['biogasInput'].append(cf.biogasInValuesConversion[j])

            solution = optModel.m.getAttr('X', optModel.operationPoint_MEOHSYN)
            self.result['input']['operationPoint_MEOHSYN'] = solution
            self.result['input']['synthesisgasInMethanolSynthesis'] = []
            for i in self.time:
                for j in cf.synthesisgasInMethanolSynthesisValues:
                    if solution[i,j] == 1:
                        self.result['input']['synthesisgasInMethanolSynthesis'].append(cf.synthesisgasInMethanolSynthesisValuesConversion[j])

            solution = optModel.m.getAttr('X', optModel.operationPoint_DIS)
            self.result['input']['operationPoint_DIS'] = solution
            self.result['input']['methanolWaterInDistillation'] = []
            for i in self.time:
                for j in cf.methanolWaterInDistillationValues:
                    if solution[i,j] == 1:
                        self.result['input']['methanolWaterInDistillation'].append(cf.methanolWaterInDistillationValuesConversion[j])

            solution = optModel.m.getAttr('X', optModel.operationPointSwitch)

            self.result['input']['electrolyserMode'] = {}
            for i in range(0, self.param.param['electrolyser']['numberOfEnapterModules']):
                self.result['input']['electrolyserMode'][(i)] = []

            solution = optModel.m.getAttr('X', optModel.powerElectrolyser)
            self.result['input']['powerElectrolyserRaw'] = solution
            print(solution)
            solution = optModel.m.getAttr('X', optModel.electrolyserMode)
            self.result['input']['electrolyserModeRaw'] = solution
            self.result['input']['powerElectrolyser'] = []

            for i in self.time:
                temp = 0
                for n in elec.enapterModules:
                    if self.result['input']['electrolyserModeRaw'][i,n,0] == 1:
                        temp = temp + self.param.param['electrolyser']['powerLowerBound'] + (self.param.param['electrolyser']['powerUpperBound'] - self.param.param['electrolyser']['powerLowerBound']) / 2
                        self.result['input']['electrolyserMode'][(n)].append("ramp-up")
                    elif self.result['input']['electrolyserModeRaw'][i,n,1] == 1:
                        temp = temp + 0.3
                        self.result['input']['electrolyserMode'][(n)].append("standby")
                    elif self.result['input']['electrolyserModeRaw'][i,n,2] == 1:
                        temp = temp + 0
                        self.result['input']['electrolyserMode'][(n)].append("off")
                    elif self.result['input']['electrolyserModeRaw'][i,n,3] == 1:
                        temp = temp + self.result['input']['powerElectrolyserRaw'][i,n]
                        self.result['input']['electrolyserMode'][(n)].append("on")
                        
                self.result['input']['powerElectrolyser'].append(temp)

            self.result['input']['usageOfPV'] = []
            solution = optModel.m.getAttr('X', optModel.usageOfPV)
            for i in self.time:
                self.result['input']['usageOfPV'].append(solution[i])   
            
            self.result['input']['powerInBatteryPV'] = []
            solution = optModel.m.getAttr('X', optModel.powerInBatteryPV)
            for i in self.time:
               self.result['input']['powerInBatteryPV'].append(solution[i])

            if self.param.param['controlParameters']['uncertaintyPV'] == True:
                solution = optModel.m.getAttr('X', optModel.indicatorPV)
                self.result['input']['indicatorPV'] = []
                for i in range(0,pv.numberUncertaintySamples):
                    self.result['input']['indicatorPV'].append(solution[i])


            #self.result['input']['powerInBatteryBought'] = []
            self.result['input']['powerInBatteryBoughtRaw'] = []
            solution = optModel.m.getAttr('X', optModel.powerInBatteryBought)
            if self.param.param['controlParameters']['uncertaintyPP'] == False:
                for j in range(0,pp.numberUncertaintySamples):
                    self.result['input']['powerInBatteryBoughtRaw'].append([])
                    for i in self.time:
                        self.result['input']['powerInBatteryBoughtRaw'][j].append(solution[i])
                self.result['input']['powerInBatteryBought'] = self.result['input']['powerInBatteryBoughtRaw'][0]
            else:
                for j in range(0,pp.numberUncertaintySamples):
                    self.result['input']['powerInBatteryBoughtRaw'].append([])
                    for i in self.time:
                       self.result['input']['powerInBatteryBoughtRaw'][j].append(solution[i,j])


            #self.result['input']['powerOutBattery'] = []
            self.result['input']['powerOutBatteryRaw'] = []
            solution = optModel.m.getAttr('X', optModel.powerOutBattery)
            if self.param.param['controlParameters']['uncertaintyPP'] == False:
                for j in range(0,pp.numberUncertaintySamples):
                    self.result['input']['powerOutBatteryRaw'].append([])
                    for i in self.time:
                        self.result['input']['powerOutBatteryRaw'][j].append(solution[i])
                self.result['input']['powerOutBattery'] = self.result['input']['powerOutBatteryRaw'][0]
            else:
                for j in range(0,pp.numberUncertaintySamples):
                    self.result['input']['powerOutBatteryRaw'].append([])
                    for i in self.time:
                        self.result['input']['powerOutBatteryRaw'][j].append(solution[i,j])


            #self.result['input']['powerOutBatterySold'] = []
            self.result['input']['powerOutBatterySoldRaw'] = []
            solution = optModel.m.getAttr('X', optModel.powerOutBatterySold)
            if self.param.param['controlParameters']['uncertaintyPP'] == False:
                for j in range(0,pp.numberUncertaintySamples):
                    self.result['input']['powerOutBatterySoldRaw'].append([])
                    for i in self.time:
                        self.result['input']['powerOutBatterySoldRaw'][j].append(solution[i])
                self.result['input']['powerOutBatterySold'] = self.result['input']['powerOutBatterySoldRaw'][0]
            else:
                for j in range(0,pp.numberUncertaintySamples):
                    self.result['input']['powerOutBatterySoldRaw'].append([])
                    for i in self.time:
                        self.result['input']['powerOutBatterySoldRaw'][j].append(solution[i,j])


            #self.result['input']['powerBought'] = []
            self.result['input']['powerBoughtRaw'] = []
            solution = optModel.m.getAttr('X', optModel.powerBought)
            if self.param.param['controlParameters']['uncertaintyPP'] == False:
                for j in range(0,pp.numberUncertaintySamples):
                    self.result['input']['powerBoughtRaw'].append([])
                    for i in self.time:
                        self.result['input']['powerBoughtRaw'][j].append(solution[i]) 
                self.result['input']['powerBought'] = self.result['input']['powerBoughtRaw'][0]
            else:
                for j in range(0,pp.numberUncertaintySamples):
                    self.result['input']['powerBoughtRaw'].append([])
                    for i in self.time:
                        self.result['input']['powerBoughtRaw'][j].append(solution[i,j])

    def print(self, optModel, cf, elec, pv, pp):

        ########## Input ##########
        print('Input variables')
        print('')
        for key in self.result['input']:
            if (key != 'operationPoint_ABSDES' and key != 'operationPoint_MEOHSYN' and key != 'operationPoint_DIS' and key != 'electrolyserModeRaw' and 
                key != 'powerElectrolyserRaw' and key != "powerBoughtRaw" and key != 'powerOutBatterySoldRaw' and key != 'powerOutBatteryRaw' and key != 'powerInBatteryBoughtRaw'):
                print(key)
                print(self.result['input'][key])
                print('----------')

        ########## Output ###########
        print('Output variables')
        print('')
        for key in self.result['output']:
            print(key + ': ', self.result['output'][key]) 
            print('----------')

        print('#########')
        print('')
        print('Price power')
        print(self.param.param['prices']['power'])
        print('')
        print('#########')

        print('#########')
        print('')
        print('PV available')
        print(self.param.param['pv']['powerAvailable'])
        print('')
        print('#########')
        

        ########## Optimization ##########
        print('')
        print("Runtime:")
        print(optModel.m.Runtime)

        print('')
        print('##########')
        print('Feasibility:')
        print(optModel.m.printQuality())

        print('')
        print('##########')
        print('Optimality Gap:')
        print(optModel.m.MIPGap)


        ########## Costs ##########
        print('Costs')
        print('')
        for key in self.result['costs']:
            print(key + ': ', self.result['costs'][key])
        print('')
        print('#########')

        if self.param.param['controlParameters']['benchmark'] == True:
            print('Benchmark')
            print('')
            print('Methanol: ', np.sum(self.result['output']['massFlowMethanolOut']))
            print('Methan: ' , np.sum(self.result['output']['volumeBiogasOut']))

    def save_data(self, optModel, cf, elec, pv, pp, iteration):

        ###############################
        ########## Save data ##########

        if self.param.param['controlParameters']['benchmark'] == True:
            string = "benchmark"
        else:
            string = "opt"

        resultSave = self.result
        resultSave['param'] = self.param.param

        savemat("data_" + string + "_" + str(iteration) + ".mat", resultSave)

    
    def visualization(self, OptModel, cf, elec, pv, pp):

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