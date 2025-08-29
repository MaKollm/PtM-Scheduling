#!/usr/bin/env python3.10


#############################
########## Results ##########

import numpy as np
import matplotlib.pyplot as plt
from gurobipy import *
from scipy.io import savemat
from datetime import datetime
import pickle
import tkinter as tk

from vis import visu, createGif


class Result():
    def __init__(self, param):
        self.funcUpdate(param)


    def funcUpdate(self, param):
        self.param = param
        self.dictResult = {'input': {}, 'output_Scheduling': {}, 'output_Sim': {}, 'costs': {}, 'param': {}}
        self.arrTime = list(range(0,self.param.param['controlParameters']['numberOfTimeSteps']))
        self.dictResult['param'] = self.param


    def funcGetResult(self, optModel, cm, elec, pv, wt, pp, ci):
    
        self.funcCalculateInputs(optModel, cm, elec, pv, wt, pp, ci)

    def funcCalculateInputs(self, optModel, cm, elec, pv, wt, pp, ci):
        
        # Input variables
        if optModel.m.Status == GRB.OPTIMAL or (optModel.m.Status == GRB.TIME_LIMIT and optModel.m.SolCount > 0):
            solution = optModel.m.getAttr('X', optModel.OptVarOperationPointCO2CAP)
            self.dictResult['input']['operationPoint_CO2CAP'] = np.empty(shape=(len(self.arrTime),len(cm.arrOperationPointsCO2CAP)))
            self.dictResult['input']['massFlowBiogasIn'] = []
            for i in self.arrTime:
                for j in cm.arrOperationPointsCO2CAP:
                    self.dictResult['input']['operationPoint_CO2CAP'][i,j] = solution[i,j]
                    if solution[i,j] == 1:
                        self.dictResult['input']['massFlowBiogasIn'].append(cm.arrBiogasInValuesConversion[j])

            solution = optModel.m.getAttr('X', optModel.OptVarOperationPointCO2CAP)
            self.dictResult['input']['operationPoint_CO2CAP'] = np.empty(shape=(len(self.arrTime),len(cm.arrOperationPointsCO2CAP)))
            self.dictResult['input']['massFlowHydrogenIn'] = []
            for i in self.arrTime:
                for j in cm.arrOperationPointsCO2CAP:
                    self.dictResult['input']['operationPoint_CO2CAP'][i,j] = solution[i,j]
                    if solution[i,j] == 1:
                        self.dictResult['input']['massFlowHydrogenIn'].append(cm.arrHydrogenInValuesConversion[j])

            solution = optModel.m.getAttr('X', optModel.OptVarOperationPointSYN)
            self.dictResult['input']['operationPoint_SYN'] = np.empty(shape=(len(self.arrTime),len(cm.arrOperationPointsSYN)))
            self.dictResult['input']['massFlowSynthesisgasIn'] = []
            for i in self.arrTime:
                for j in cm.arrOperationPointsSYN:
                    self.dictResult['input']['operationPoint_SYN'][i,j] = solution[i,j]
                    if int(solution[i,j]) == 1:
                        self.dictResult['input']['massFlowSynthesisgasIn'].append(cm.arrSynthesisgasInValuesConversion[j])
                    
            solution = optModel.m.getAttr('X', optModel.OptVarOperationPointDIS)
            self.dictResult['input']['operationPoint_DIS'] = np.empty(shape=(len(self.arrTime),len(cm.arrOperationPointsDIS)))
            self.dictResult['input']['volFlowMethanolWaterStorage'] = []
            for i in self.arrTime:
                for j in cm.arrOperationPointsDIS:
                    self.dictResult['input']['operationPoint_DIS'][i,j] = solution[i,j]
                    if int(solution[i,j]) == 1:
                        self.dictResult['input']['volFlowMethanolWaterStorage'].append(cm.arrMethanolWaterInDistillationValuesConversion[j])


            solution = optModel.m.getAttr('X', optModel.OptVarCurrentStateCO2CAP)
            self.dictResult['input']['currentStateCO2CAPRaw'] = np.empty(shape=(len(self.arrTime),5))
            self.dictResult['input']['currentStateCO2CAP'] = []
            for i in self.arrTime:
                for j in range(0,5):
                    if solution[i,j] == 1:
                        self.dictResult['input']['currentStateCO2CAP'].append(j)

                    self.dictResult['input']['currentStateCO2CAPRaw'][i,j] = solution[i,j]

            solution = optModel.m.getAttr('X', optModel.OptVarCurrentStateSYN)
            self.dictResult['input']['currentStateSYNRaw'] = np.empty(shape=(len(self.arrTime),5))
            self.dictResult['input']['currentStateSYN'] = []
            for i in self.arrTime:
                for j in range(0,5):
                    if solution[i,j] == 1:
                        self.dictResult['input']['currentStateSYN'].append(j)

                    self.dictResult['input']['currentStateSYNRaw'][i,j] = solution[i,j]

            solution = optModel.m.getAttr('X', optModel.OptVarCurrentStateDIS)
            self.dictResult['input']['currentStateDISRaw'] = np.empty(shape=(len(self.arrTime),5))
            self.dictResult['input']['currentStateDIS'] = []
            for i in self.arrTime:
                for j in range(0,5):
                    if solution[i,j] == 1:
                        self.dictResult['input']['currentStateDIS'].append(j)

                    self.dictResult['input']['currentStateDISRaw'][i,j] = solution[i,j]


            solution = optModel.m.getAttr('X', optModel.OptVarCurrentStateSwitchCO2CAP)
            self.dictResult['input']['currentStateSwitchCO2CAPRaw'] = np.empty(shape=(len(self.arrTime),5,5))
            self.dictResult['input']['currentStateSwitchCO2CAP'] = []
            for i in self.arrTime:
                for j in range(0,5):
                    for k in range(0,5):
                        if solution[i,j,k] == 1:
                            self.dictResult['input']['currentStateSwitchCO2CAP'].append((j,k))
                        else:
                            self.dictResult['input']['currentStateSwitchCO2CAP'].append((-1,-1))

                        self.dictResult['input']['currentStateSwitchCO2CAPRaw'][i,j,k] = solution[i,j,k]
                        

            solution = optModel.m.getAttr('X', optModel.OptVarCurrentStateSwitchSYN)
            self.dictResult['input']['currentStateSwitchSYNRaw'] = np.empty(shape=(len(self.arrTime),5,5))
            self.dictResult['input']['currentStateSwitchSYN'] = []
            for i in self.arrTime:
                for j in range(0,5):
                    for k in range(0,5):
                        if solution[i,j,k] == 1:
                            self.dictResult['input']['currentStateSwitchSYN'].append((j,k))
                        else:
                            self.dictResult['input']['currentStateSwitchSYN'].append((-1,-1))

                        self.dictResult['input']['currentStateSwitchSYNRaw'][i,j,k] = solution[i,j,k]


            solution = optModel.m.getAttr('X', optModel.OptVarCurrentStateSwitchDIS)
            self.dictResult['input']['currentStateSwitchDISRaw'] = np.empty(shape=(len(self.arrTime),5,5))
            self.dictResult['input']['currentStateSwitchDIS'] = []
            for i in self.arrTime:
                for j in range(0,5):
                    for k in range(0,5):
                        if solution[i,j,k] == 1:
                            self.dictResult['input']['currentStateSwitchDIS'].append((j,k))
                        else:
                            self.dictResult['input']['currentStateSwitchDIS'].append((-1,-1))

                        self.dictResult['input']['currentStateSwitchDISRaw'][i,j,k] = solution[i,j,k]


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

            self.dictResult['input']['usageOfWind'] = []
            solution = optModel.m.getAttr('X', optModel.OptVarUsageOfWind)
            for i in self.arrTime:
                self.dictResult['input']['usageOfWind'].append(solution[i])

            self.dictResult['input']['powerInBatteryPV'] = []
            solution = optModel.m.getAttr('X', optModel.OptVarPowerInBatteryPV)
            for i in self.arrTime:
               self.dictResult['input']['powerInBatteryPV'].append(solution[i])

            self.dictResult['input']['powerInBatteryWind'] = []
            solution = optModel.m.getAttr('X', optModel.OptVarPowerInBatteryWind)
            for i in self.arrTime:
                self.dictResult['input']['powerInBatteryWind'].append(solution[i])

            self.dictResult['input']['powerInBatteryGrid'] = []
            solution = optModel.m.getAttr('X', optModel.OptVarPowerInBatteryGrid)
            for i in self.arrTime:
                self.dictResult['input']['powerInBatteryGrid'].append(solution[i])
             
            self.dictResult['input']['powerOutBattery'] = []
            solution = optModel.m.getAttr('X', optModel.OptVarPowerOutBattery)
            for i in self.arrTime:
                self.dictResult['input']['powerOutBattery'].append(solution[i])

            self.dictResult['input']['powerOutBatterySold'] = []
            solution = optModel.m.getAttr('X', optModel.OptVarPowerOutBatterySold)
            for i in self.arrTime:
                self.dictResult['input']['powerOutBatterySold'].append(solution[i])
 
            self.dictResult['input']['powerGrid'] = []
            solution = optModel.m.getAttr('X', optModel.OptVarPowerGrid)
            for i in self.arrTime:
                self.dictResult['input']['powerGrid'].append(solution[i]) 
      
            
            self.dictResult['input']['indicatorBatteryCharging1'] = []
            solution = optModel.m.getAttr('X', optModel.OptVarIndicatorBatteryCharging1)
            for i in self.arrTime:
                self.dictResult['input']['indicatorBatteryCharging1'].append(solution[i]) 

            self.dictResult['input']['indicatorBatteryDischarging1'] = []
            solution = optModel.m.getAttr('X', optModel.OptVarIndicatorBatteryDischarging1)
            for i in self.arrTime:
                self.dictResult['input']['indicatorBatteryDischarging1'].append(solution[i]) 

            self.dictResult['input']['indicatorBatteryCharging2'] = []
            solution = optModel.m.getAttr('X', optModel.OptVarIndicatorBatteryCharging2)
            for i in self.arrTime:
                self.dictResult['input']['indicatorBatteryCharging2'].append(solution[i]) 

            self.dictResult['input']['indicatorBatteryDischarging2'] = []
            solution = optModel.m.getAttr('X', optModel.OptVarIndicatorBatteryDischarging2)
            for i in self.arrTime:
                self.dictResult['input']['indicatorBatteryDischarging2'].append(solution[i])

            self.dictResult['input']['indicatorBatteryCharging3'] = []
            solution = optModel.m.getAttr('X', optModel.OptVarIndicatorBatteryCharging3)
            for i in self.arrTime:
                self.dictResult['input']['indicatorBatteryCharging3'].append(solution[i])


            self.dictResult['input']['actualPowerInBatteryPV'] = []
            solution = optModel.m.getAttr('X', optModel.OptVarActualPowerInBatteryPV)
            for i in self.arrTime:
                self.dictResult['input']['actualPowerInBatteryPV'].append(solution[i])

            self.dictResult['input']['actualPowerInBatteryWind'] = []
            solution = optModel.m.getAttr('X', optModel.OptVarActualPowerInBatteryWind)
            for i in self.arrTime:
                self.dictResult['input']['actualPowerInBatteryWind'].append(solution[i])

            self.dictResult['input']['actualPowerInBatteryGrid'] = []
            solution = optModel.m.getAttr('X', optModel.OptVarActualPowerInBatteryGrid)
            for i in self.arrTime:
                self.dictResult['input']['actualPowerInBatteryGrid'].append(solution[i]) 

            self.dictResult['input']['actualPowerOutBattery'] = []
            solution = optModel.m.getAttr('X', optModel.OptVarActualPowerOutBattery)
            for i in self.arrTime:
                self.dictResult['input']['actualPowerOutBattery'].append(solution[i]) 

            self.dictResult['input']['actualPowerOutBatterySold'] = []
            solution = optModel.m.getAttr('X', optModel.OptVarActualPowerOutBatterySold)
            for i in self.arrTime:
                self.dictResult['input']['actualPowerOutBatterySold'].append(solution[i])


            
            self.dictResult['input']['usedOperationPointCO2CAP'] = 0
            self.dictResult['input']['usedOperationPointCO2CAPRaw'] = []
            solution = optModel.m.getAttr('X', optModel.OptVarUsedOperationPointCO2CAP)
            for i in cm.arrOperationPointsCO2CAP[4:]:
                self.dictResult['input']['usedOperationPointCO2CAPRaw'].append(solution[i])
                if solution[i] == 1:     
                    self.dictResult['input']['usedOperationPointCO2CAP'] = i

            self.dictResult['input']['usedOperationPointSYN'] = 0
            self.dictResult['input']['usedOperationPointSYNRaw'] = []
            solution = optModel.m.getAttr('X', optModel.OptVarUsedOperationPointSYN)
            for i in cm.arrOperationPointsSYN[4:]:
                self.dictResult['input']['usedOperationPointSYNRaw'].append(solution[i])
                if solution[i] == 1:     
                    self.dictResult['input']['usedOperationPointSYN'] = i

            self.dictResult['input']['usedOperationPointDIS'] = 0
            self.dictResult['input']['usedOperationPointDISRaw'] = []
            solution = optModel.m.getAttr('X', optModel.OptVarUsedOperationPointDIS)
            for i in cm.arrOperationPointsDIS[4:]:
                self.dictResult['input']['usedOperationPointDISRaw'].append(solution[i])
                if solution[i] == 1:     
                    self.dictResult['input']['usedOperationPointDIS'] = i

            self.dictResult['input']['UsedOperationPointElec'] = []
            solution = optModel.m.getAttr('X', optModel.OptVarUsedOperationPointElectrolyser)
            for n in elec.arrEnapterModules: 
                self.dictResult['input']['UsedOperationPointElec'].append(solution[n])

      

    def funcPrintResult(self, optModel, cm, elec, pv, wt, pp, ci):
        

        # Create the main window
        root = tk.Tk()
        root.title("Setpoints")

  
        # Example variables
        vol = self.dictResult['input']['massFlowBiogasIn'][0] / (44.01 * 0.35 + 28.013 * 0.65) * 1000 * 22.414 / 60
        carbon_dioxide = 0#0.35 * vol
        nitrogen = 0#0.65 * vol
        biogas = self.dictResult['input']['massFlowBiogasIn'][0] / (44.01 * 0.35 + 16.04 * 0.65) * 1000 * 22.414 / 60
        hydrogen = self.dictResult['input']['massFlowHydrogenIn'][0] / 2.016 * 1000 * 22.414 / 60


        elec_mode = []
        elec_rate = []
        for n in elec.arrEnapterModules:
            elec_mode = self.dictResult['input']['electrolyserMode'][(n)][0]
            elec_rate = self.dictResult['input']['powerElectrolyserRaw'][0,n] / self.param.param['electrolyser']['powerUpperBound'] * 100 * self.dictResult['input']['modeElectrolyserRaw'][0,n,3]
                
        data = [
            ("Volume flow of nitrogen (FIC-5014) [Nl/min]:", f"{nitrogen:.2f}"),
            ("Volume flow of carbon dioxide (FIC-5026) [Nl/min]:", f"{carbon_dioxide:.2f}"),
            ("Volume flow of biogas (FIC-5007) [Nl/min]:", f"{biogas:.2f}"),
            ("Volume flow of hydrogen (FIC-5036) [Nl/min]:", f"{hydrogen:.2f}")
        ]

        for n in elec.arrEnapterModules:
            data.append(("Mode of Electrolyser " + str(n+1) + ":", elec_mode))
            data.append(("Production rate [%] of Electrolyser " + str(n+1) + ":", f"{elec_rate:.2f}"))

        # Daten anzeigen in zwei Spalten
        for i, (label_text, value_text) in enumerate(data, start=1):
            label = tk.Label(root, text=label_text, font=("Arial", 12), anchor="w", padx=10)
            value = tk.Label(root, text=value_text, font=("Arial", 12), anchor="e", padx=10)
            label.grid(row=i, column=0, sticky="w")
            value.grid(row=i, column=1, sticky="e")


        # Run the GUI loop
        root.mainloop()


        ########## Input ##########
        print('Input variables')
        print('')
        for key in self.dictResult['input']:
                print(key)
                print(self.dictResult['input'][key])
                print('----------')

        ########## Output ###########
        print('Output variables')
        print('')
        for key in self.dictResult['output_Scheduling']:
            print(key + ': ', self.dictResult['output_Scheduling'][key]) 
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
        print('')
        print("##########")
        print('Costs')
        print('')
        for key in self.dictResult['costs']:
            print(key + ': ', self.dictResult['costs'][key])
        print('')
        print('#########')

        print('Production')
        print('')
        print('Methanol: ', np.sum(self.dictResult['output_Scheduling']['volFlowMethanolOut']))
        print('Methanol-Water: ', np.sum(self.dictResult['output_Scheduling']['producedMethanolWater']))
        print('Methan: ' , np.sum(self.dictResult['output_Scheduling']['massFlowBiogasOut']))

        print('')
        print('Methanol in last Simulation Step: ', np.sum(self.dictResult['output_Scheduling']['volFlowMethanolOut'][0:self.param.param['controlParameters']['numTimeStepsToSimulate']]))
        print('Methanol-Water in last Simulation Step: ', np.sum(self.dictResult['output_Scheduling']['producedMethanolWater'][0:self.param.param['controlParameters']['numTimeStepsToSimulate']]))
        print('')
        print('##########')

        print("Consumption")
        print('Biogas: ', np.sum(self.dictResult['input']['massFlowBiogasIn']))     
        print('Hydrogen: ', np.sum(self.dictResult['output_Scheduling']['massFlowHydrogenIn']))     
        print('Electrical power: ', np.sum(self.dictResult['input']['powerGrid']))


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
        self.param.param['optimization']['status'] = optModel.m.status
        resultSave['param'] = self.param.param

        now = datetime.now() # current date and time
        date_time = now.strftime("%Y%m%d_%H%M%S")
        
        savemat("data_" + string + "_" + text + ".mat", resultSave)
        savemat("data_" + string + "_" + text + "_" + date_time + ".mat", resultSave)


        with open('input_data.pkl','wb') as f:
            pickle.dump(self.dictResult,f)

        with open('input_data_' + date_time + '.pkl', 'wb') as f:
            pickle.dump(self.dictResult,f)

    
    def funcVisualizationResult(self, OptModel, cm, elec, pv, wt, pp, ci):

        ###################################
        ########## Visualization ########## 

        visu(self.dictResult)
        pass
    