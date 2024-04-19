#!/usr/bin/env python3.10


#############################
########## Results ##########

import gurobipy as gp
import numpy as np
import matplotlib.pyplot as plt
from gurobipy import GRB
from gurobipy import *
from scipy.io import savemat
from datetime import datetime
import pickle


class Result():
    def __init__(self, param):
        self.funcUpdate(param)


    def funcUpdate(self, param):
        self.param = param
        self.arrTime = list(range(0,self.param.param['controlParameters']['numberOfTimeSteps']+1))
        self.dictResult = {'input': {}, 'output': {}, 'costs': {}, 'param': {}}
        self.dictResult['param'] = self.param


    def funcGetResult(self, optModel, cm, elec, pv, pp):
    
        self.funcCalculateInputs(optModel, cm, elec, pv, pp)

    def funcCalculateInputs(self, optModel, cm, elec, pv, pp):
        
        # Input variables
        if optModel.m.Status == GRB.OPTIMAL or optModel.m.Status == GRB.TIME_LIMIT:
            solution = optModel.m.getAttr('X', optModel.OptVarOperationPointABSDES)
            self.dictResult['input']['operationPoint_ABSDES'] = np.empty(shape=(len(self.arrTime),len(cm.arrOperationPointsABSDES)))
            self.dictResult['input']['hydrogenInput'] = []
            self.dictResult['input']['biogasInput'] = []
            for i in self.arrTime:
                for j in cm.arrOperationPointsABSDES:
                    self.dictResult['input']['operationPoint_ABSDES'][i,j] = solution[i,j]
                    if solution[i,j] == 1:
                        self.dictResult['input']['hydrogenInput'].append(cm.arrHydrogenInValuesConversion[j])
                        self.dictResult['input']['biogasInput'].append(cm.arrBiogasInValuesConversion[j])


            solution = optModel.m.getAttr('X', optModel.OptVarOperationPointMEOHSYN)
            self.dictResult['input']['operationPoint_MEOHSYN'] = np.empty(shape=(len(self.arrTime),len(cm.arrOperationPointsMEOHSYN)))
            self.dictResult['input']['synthesisgasInMethanolSynthesis'] = []
            for i in self.arrTime:
                for j in cm.arrOperationPointsMEOHSYN:
                    self.dictResult['input']['operationPoint_MEOHSYN'][i,j] = solution[i,j]
                    if solution[i,j] == 1:
                        self.dictResult['input']['synthesisgasInMethanolSynthesis'].append(cm.arrSynthesisgasInMethanolSynthesisValuesConversion[j])


            solution = optModel.m.getAttr('X', optModel.OptVarOperationPointDIS)
            self.dictResult['input']['operationPoint_DIS'] = np.empty(shape=(len(self.arrTime),len(cm.arrOperationPointsDIS)))
            self.dictResult['input']['methanolWaterInDistillation'] = []
            for i in self.arrTime:
                for j in cm.arrOperationPointsDIS:
                    self.dictResult['input']['operationPoint_DIS'][i,j] = solution[i,j]
                    if int(solution[i,j]) == 1:
                        self.dictResult['input']['methanolWaterInDistillation'].append(cm.arrMethanolWaterInDistillationValuesConversion[j])


            solution = optModel.m.getAttr('X', optModel.OptVarOperationPointSwitch)
            self.dictResult['input']['operationPointSwitch'] = np.empty(shape=(len(self.arrTime),6))
            self.dictResult['input']['operationPointSwitchABSDES'] = []
            for i in self.arrTime:
                if solution[i,4] == 1:
                    self.dictResult['input']['operationPointSwitchABSDES'].append(1)
                else:
                    self.dictResult['input']['operationPointSwitchABSDES'].append(0)
                
                for j in range(0,6):
                    self.dictResult['input']['operationPointSwitch'][i,j] = solution[i,j+1]


            self.dictResult['input']['electrolyserMode'] = {}
            for i in range(0, self.param.param['electrolyser']['numberOfEnapterModules']):
                self.dictResult['input']['electrolyserMode'][(i)] = []

            self.dictResult['input']['powerElectrolyser'] = []

            powerElectrolyserRaw = optModel.m.getAttr('X', optModel.OptVarPowerElectrolyser)
            self.dictResult['input']['powerElectrolyserRaw'] = np.empty(shape=(len(self.arrTime),self.param.param['electrolyser']['numberOfEnapterModules']))
            modeElectrolyserRaw = optModel.m.getAttr('X', optModel.OptVarModeElectrolyser)
            self.dictResult['input']['modeElectrolyserRaw'] = np.empty(shape=(len(self.arrTime),self.param.param['electrolyser']['numberOfEnapterModules'],4))

            for i in self.arrTime:
                temp = 0
                for n in elec.arrEnapterModules:
                    if modeElectrolyserRaw[i,n,0] == 1:
                        temp = temp + self.param.param['electrolyser']['powerLowerBound'] + (self.param.param['electrolyser']['powerUpperBound'] - self.param.param['electrolyser']['powerLowerBound']) / 2
                        self.dictResult['input']['electrolyserMode'][(n)].append("ramp-up")
                    elif modeElectrolyserRaw[i,n,1] == 1:
                        temp = temp + 0.3
                        self.dictResult['input']['electrolyserMode'][(n)].append("standby")
                    elif modeElectrolyserRaw[i,n,2] == 1:
                        temp = temp + 0
                        self.dictResult['input']['electrolyserMode'][(n)].append("off")
                    elif modeElectrolyserRaw[i,n,3] == 1:
                        temp = temp + powerElectrolyserRaw[i,n]
                        self.dictResult['input']['electrolyserMode'][(n)].append("on")

                    self.dictResult['input']['powerElectrolyserRaw'][i,n] = powerElectrolyserRaw[i,n]
                    for k in range(0,4):
                        self.dictResult['input']['modeElectrolyserRaw'][i,n,k] = modeElectrolyserRaw[i,n,k]
                        
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
        """
        ########## Input ##########
        print('Input variables')
        print('')
        for key in self.dictResult['input']:
            if (key != 'operationPoint_ABSDES' and key != 'operationPoint_MEOHSYN' and key != 'operationPoint_DIS' and key != 'modeElectrolyserRaw' and 
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

        print('Production')
        print('')
        print('Methanol: ', np.sum(self.dictResult['output']['massFlowMethanolOut']))
        print('Methan: ' , np.sum(self.dictResult['output']['volumeBiogasOut']))
        print('Biogas: ', np.sum(self.dictResult['output']['volumeBiogasIn']))
        """

        print('')
        print('Methanol: ', np.sum(self.dictResult['output']['massFlowMethanolOut'][:self.param.param['controlParameters']['numTimeStepsToSimulate']]))

    def funcSaveResult(self, optModel, text):

        ###############################
        ########## Save data ##########

        if self.param.param['controlParameters']['benchmark'] == True:
            string = "benchmark"
        else:
            string = "opt"

        resultSave = self.dictResult
        self.param.param['optimization'] = {}
        self.param.param['optimization']['runtime'] = optModel.m.Runtime
        self.param.param['optimization']['gap'] = optModel.m.MIPGap
        resultSave['param'] = self.param.param

        now = datetime.now() # current date and time
        date_time = now.strftime("%Y%m%d_%H%M%S")
        
        savemat("data_" + string + "_" + text + ".mat", resultSave)
        savemat("data_" + string + "_" + text + "_" + date_time + ".mat", resultSave)

        with open('input_data.pkl','wb') as f:
            pickle.dump(self.dictResult,f)

    
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