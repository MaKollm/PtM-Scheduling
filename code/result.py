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
        self.funcUpdate(param)


    def funcUpdate(self, param):
        self.param = param
        self.arrTime = list(range(0,self.param.param['controlParameters']['numberOfTimeSteps']+1))
        self.dictResult = {'input': {}, 'output': {}, 'costs': {}}


    def funcGetResult(self, optModel, cm, elec, pv, pp):
    
        self.funcCalculateInputs(optModel, cm, elec, pv, pp)

    def funcCalculateInputs(self, optModel, cm, elec, pv, pp):
        
        # Input variables
        if optModel.m.Status == GRB.OPTIMAL or optModel.m.Status == GRB.TIME_LIMIT:
            solution = optModel.m.getAttr('X', optModel.OptVarOperationPointABSDES)
            self.dictResult['input']['operationPoint_ABSDES'] = solution
            self.dictResult['input']['hydrogenInput'] = []
            self.dictResult['input']['biogasInput'] = []
            for i in self.arrTime:
                for j in cm.arrOperationPointsABSDES:
                    if solution[i,j] == 1:
                        self.dictResult['input']['hydrogenInput'].append(cm.arrHydrogenInValuesConversion[j])
                        self.dictResult['input']['biogasInput'].append(cm.arrBiogasInValuesConversion[j])

            solution = optModel.m.getAttr('X', optModel.OptVarOperationPointMEOHSYN)
            self.dictResult['input']['operationPoint_MEOHSYN'] = solution
            self.dictResult['input']['synthesisgasInMethanolSynthesis'] = []
            for i in self.arrTime:
                for j in cm.arrOperationPointsMEOHSYN:
                    if solution[i,j] == 1:
                        self.dictResult['input']['synthesisgasInMethanolSynthesis'].append(cm.arrSynthesisgasInMethanolSynthesisValuesConversion[j])

            solution = optModel.m.getAttr('X', optModel.OptVarOperationPointDIS)
            self.dictResult['input']['operationPoint_DIS'] = solution
            self.dictResult['input']['methanolWaterInDistillation'] = []
            for i in self.arrTime:
                for j in cm.arrOperationPointsDIS:
                    if solution[i,j] == 1:
                        self.dictResult['input']['methanolWaterInDistillation'].append(cm.arrMethanolWaterInDistillationValuesConversion[j])

            solution = optModel.m.getAttr('X', optModel.OptVarOperationPointSwitch)

            self.dictResult['input']['electrolyserMode'] = {}
            for i in range(0, self.param.param['electrolyser']['numberOfEnapterModules']):
                self.dictResult['input']['electrolyserMode'][(i)] = []

            solution = optModel.m.getAttr('X', optModel.OptVarPowerElectrolyser)
            self.dictResult['input']['powerElectrolyserRaw'] = solution
            solution = optModel.m.getAttr('X', optModel.OptVarElectrolyserMode)
            self.dictResult['input']['electrolyserModeRaw'] = solution
            self.dictResult['input']['powerElectrolyser'] = []

            for i in self.arrTime:
                temp = 0
                for n in elec.arrEnapterModules:
                    if self.dictResult['input']['electrolyserModeRaw'][i,n,0] == 1:
                        temp = temp + self.param.param['electrolyser']['powerLowerBound'] + (self.param.param['electrolyser']['powerUpperBound'] - self.param.param['electrolyser']['powerLowerBound']) / 2
                        self.dictResult['input']['electrolyserMode'][(n)].append("ramp-up")
                    elif self.dictResult['input']['electrolyserModeRaw'][i,n,1] == 1:
                        temp = temp + 0.3
                        self.dictResult['input']['electrolyserMode'][(n)].append("standby")
                    elif self.dictResult['input']['electrolyserModeRaw'][i,n,2] == 1:
                        temp = temp + 0
                        self.dictResult['input']['electrolyserMode'][(n)].append("off")
                    elif self.dictResult['input']['electrolyserModeRaw'][i,n,3] == 1:
                        temp = temp + self.dictResult['input']['powerElectrolyserRaw'][i,n]
                        self.dictResult['input']['electrolyserMode'][(n)].append("on")
                        
                self.dictResult['input']['powerElectrolyser'].append(temp)

            self.dictResult['input']['usageOfPV'] = []
            solution = optModel.m.getAttr('X', optModel.OptVarUsageOfPV)
            for i in self.arrTime:
                self.dictResult['input']['usageOfPV'].append(solution[i])   
            
            self.dictResult['input']['powerInBatteryPV'] = []
            solution = optModel.m.getAttr('X', optModel.OptVarPowerInBatteryPV)
            for i in self.arrTime:
               self.dictResult['input']['powerInBatteryPV'].append(solution[i])

            if self.param.param['controlParameters']['uncertaintyPV'] == True:
                solution = optModel.m.getAttr('X', optModel.OptVarIndicatorPV)
                self.dictResult['input']['indicatorPV'] = []
                for i in range(0,pv.iNumberUncertaintySamples):
                    self.dictResult['input']['indicatorPV'].append(solution[i])


            #self.dictResult['input']['powerInBatteryBought'] = []
            self.dictResult['input']['powerInBatteryBoughtRaw'] = []
            solution = optModel.m.getAttr('X', optModel.OptVarPowerInBatteryBought)
            if self.param.param['controlParameters']['uncertaintyPP'] == False:
                for j in range(0,pp.iNumberUncertaintySamples):
                    self.dictResult['input']['powerInBatteryBoughtRaw'].append([])
                    for i in self.arrTime:
                        self.dictResult['input']['powerInBatteryBoughtRaw'][j].append(solution[i])
                self.dictResult['input']['powerInBatteryBought'] = self.dictResult['input']['powerInBatteryBoughtRaw'][0]
            else:
                for j in range(0,pp.iNumberUncertaintySamples):
                    self.dictResult['input']['powerInBatteryBoughtRaw'].append([])
                    for i in self.arrTime:
                       self.dictResult['input']['powerInBatteryBoughtRaw'][j].append(solution[i,j])


            #self.dictResult['input']['powerOutBattery'] = []
            self.dictResult['input']['powerOutBatteryRaw'] = []
            solution = optModel.m.getAttr('X', optModel.OptVarPowerOutBattery)
            if self.param.param['controlParameters']['uncertaintyPP'] == False:
                for j in range(0,pp.iNumberUncertaintySamples):
                    self.dictResult['input']['powerOutBatteryRaw'].append([])
                    for i in self.arrTime:
                        self.dictResult['input']['powerOutBatteryRaw'][j].append(solution[i])
                self.dictResult['input']['powerOutBattery'] = self.dictResult['input']['powerOutBatteryRaw'][0]
            else:
                for j in range(0,pp.iNumberUncertaintySamples):
                    self.dictResult['input']['powerOutBatteryRaw'].append([])
                    for i in self.arrTime:
                        self.dictResult['input']['powerOutBatteryRaw'][j].append(solution[i,j])


            #self.dictResult['input']['powerOutBatterySold'] = []
            self.dictResult['input']['powerOutBatterySoldRaw'] = []
            solution = optModel.m.getAttr('X', optModel.OptVarPowerOutBatterySold)
            if self.param.param['controlParameters']['uncertaintyPP'] == False:
                for j in range(0,pp.iNumberUncertaintySamples):
                    self.dictResult['input']['powerOutBatterySoldRaw'].append([])
                    for i in self.arrTime:
                        self.dictResult['input']['powerOutBatterySoldRaw'][j].append(solution[i])
                self.dictResult['input']['powerOutBatterySold'] = self.dictResult['input']['powerOutBatterySoldRaw'][0]
            else:
                for j in range(0,pp.iNumberUncertaintySamples):
                    self.dictResult['input']['powerOutBatterySoldRaw'].append([])
                    for i in self.arrTime:
                        self.dictResult['input']['powerOutBatterySoldRaw'][j].append(solution[i,j])


            #self.dictResult['input']['powerBought'] = []
            self.dictResult['input']['powerBoughtRaw'] = []
            solution = optModel.m.getAttr('X', optModel.OptVarPowerBought)
            if self.param.param['controlParameters']['uncertaintyPP'] == False:
                for j in range(0,pp.iNumberUncertaintySamples):
                    self.dictResult['input']['powerBoughtRaw'].append([])
                    for i in self.arrTime:
                        self.dictResult['input']['powerBoughtRaw'][j].append(solution[i]) 
                self.dictResult['input']['powerBought'] = self.dictResult['input']['powerBoughtRaw'][0]
            else:
                for j in range(0,pp.iNumberUncertaintySamples):
                    self.dictResult['input']['powerBoughtRaw'].append([])
                    for i in self.arrTime:
                        self.dictResult['input']['powerBoughtRaw'][j].append(solution[i,j])

    def funcPrintResult(self, optModel, cm, elec, pv, pp):

        ########## Input ##########
        print('Input variables')
        print('')
        for key in self.dictResult['input']:
            if (key != 'operationPoint_ABSDES' and key != 'operationPoint_MEOHSYN' and key != 'operationPoint_DIS' and key != 'electrolyserModeRaw' and 
                key != 'powerElectrolyserRaw' and key != "powerBoughtRaw" and key != 'powerOutBatterySoldRaw' and key != 'powerOutBatteryRaw' and key != 'powerInBatteryBoughtRaw'):
                print(key)
                print(self.dictResult['input'][key])
                print('----------')

        ########## Output ###########
        print('Output variables')
        print('')
        for key in self.dictResult['output']:
            print(key + ': ', self.dictResult['output'][key]) 
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
        for key in self.dictResult['costs']:
            print(key + ': ', self.dictResult['costs'][key])
        print('')
        print('#########')

        if self.param.param['controlParameters']['benchmark'] == True:
            print('Benchmark')
            print('')
            print('Methanol: ', np.sum(self.dictResult['output']['massFlowMethanolOut']))
            print('Methan: ' , np.sum(self.dictResult['output']['volumeBiogasOut']))

    def funcSaveResult(self, optModel, cm, elec, pv, pp, iteration):

        ###############################
        ########## Save data ##########

        if self.param.param['controlParameters']['benchmark'] == True:
            string = "benchmark"
        else:
            string = "opt"

        resultSave = self.dictResult
        resultSave['param'] = self.param.param

        savemat("data_" + string + "_" + ".mat", resultSave)

    
    def funcVisualizationResult(self, OptModel, cm, elec, pv, pp):

        ###################################
        ########## Visualization ########## 

        #columns = ('methanol','biogas out','biogas in','power plant','power elect.', 'pv', 'batt. in', 'batt. out', 'batt. sold')
        columns = ('methanol','biogas out','biogas in', 'power bought', 'batt. sold')
        index = np.arange(len(columns)) + 0.3
        bar_width = 0.4

        n_rows = len(self.dictResult['costs'])

        data = []
        for key in self.dictResult['costs']:
            data.append(self.dictResult['costs'][key])

        y_offset = np.zeros(len(columns))

        cell_text = []
        plt.bar(index, data[:-1], bar_width, bottom=y_offset)
        plt.axhline(y = 0, color = 'k', linestyle = '-')
        plt.ylabel('operation costs')
        numbers = [1,2,3,4,5]
        plt.xticks(index, columns)
        plt.title('Composition of operation costs')
        plt.show()