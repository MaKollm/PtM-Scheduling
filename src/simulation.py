#!/usr/bin/env python3.10


#############################
########## Simulation ##########

import gurobipy as gp
import numpy as np
import matplotlib.pyplot as plt


class Simulation():
    def __init__(self, param):
        self.funcUpdate(param)


    def funcUpdate(self, param):
        self.param = param
        self.arrTime = list(range(0,self.param.param['controlParameters']['numberOfTimeSteps']+1))
        self.dictOutput = {}
        self.dictCosts = {}
        self.arrConstrViolationInput = []
        self.dictConstrViolationOutput = {}

    def funcStartSimulation(self, param, resultOpt, cm, elec, pv, pp, ci):
        
        self.funcUpdate(param)
        
        self.funcSimulate(resultOpt, cm, elec, pv, pp, ci)
        #self.funcCheckUncertaintyConstraints(resultOpt, cm, elec, pv, pp, ci)
        #self.funcCheckConstraints(resultOpt, cm, elec, pv, pp, ci)


    def funcSimulate(self, resultOpt, cm, elec, pv, pp, ci):
        fTimeStep = self.param.param['controlParameters']['timeStep']
        
        # Output variables
        self.dictOutput['massFlowHydrogenIn'] = []
        self.dictOutput['massFlowBiogasOut'] = []
        self.dictOutput['moleFractionMethaneBiogasOut'] = []
        self.dictOutput['massFlowMethanolWaterStorageIn'] = []
        self.dictOutput['massFlowMethanolWaterStorageOut'] = []
        self.dictOutput['massFlowMethanolOut'] = []
        self.dictOutput['moleFractionH2SynthesisgasIn'] = []
        self.dictOutput['moleFractionCO2SynthesisgasIn'] = []

        self.dictOutput['powerPlantCO2CAP_SYN'] = []
        self.dictOutput['powerPlantDIS'] = []

        self.dictOutput['storageH2Pressure'] = []
        self.dictOutput['storageMethanolWaterFilling'] = []
        self.dictOutput['batteryCharge'] = []



        for i in self.arrTime:#range(0,self.param.param['controlParameters']['numTimeStepsToSimulate']+1):


            self.dictOutput['massFlowHydrogenIn'].append(
                + cm.massFlowHydrogenIn[0] * resultOpt.dictResult['input']['operationPoint_CO2CAP_SYN'][i,0] * resultOpt.dictResult['input']['currentStateCO2CAP_SYNRaw'][i,0] * fTimeStep
                + cm.massFlowHydrogenIn[1] * resultOpt.dictResult['input']['operationPoint_CO2CAP_SYN'][i,1] * resultOpt.dictResult['input']['currentStateCO2CAP_SYNRaw'][i,1] * fTimeStep
                + cm.massFlowHydrogenIn[2] * resultOpt.dictResult['input']['operationPoint_CO2CAP_SYN'][i,2] * resultOpt.dictResult['input']['currentStateCO2CAP_SYNRaw'][i,2] * fTimeStep
                + gp.quicksum(cm.massFlowHydrogenIn[j] * resultOpt.dictResult['input']['operationPoint_CO2CAP_SYN'][i,j] * resultOpt.dictResult['input']['currentStateCO2CAP_SYNRaw'][i,3] * fTimeStep for j in cm.arrOperationPointsCO2CAP_SYN[4:])
                + cm.massFlowHydrogenIn[3] * resultOpt.dictResult['input']['operationPoint_CO2CAP_SYN'][i,3] * resultOpt.dictResult['input']['currentStateCO2CAP_SYNRaw'][i,4] * fTimeStep)
            
            self.dictOutput['massFlowBiogasOut'].append(
                + cm.massFlowBiogasOut[0] * resultOpt.dictResult['input']['operationPoint_CO2CAP_SYN'][i,0] * resultOpt.dictResult['input']['currentStateCO2CAP_SYNRaw'][i,0] * fTimeStep
                + cm.massFlowBiogasOut[1] * resultOpt.dictResult['input']['operationPoint_CO2CAP_SYN'][i,1] * resultOpt.dictResult['input']['currentStateCO2CAP_SYNRaw'][i,1] * fTimeStep
                + cm.massFlowBiogasOut[2] * resultOpt.dictResult['input']['operationPoint_CO2CAP_SYN'][i,2] * resultOpt.dictResult['input']['currentStateCO2CAP_SYNRaw'][i,2] * fTimeStep
                + gp.quicksum(cm.massFlowBiogasOut[j] * resultOpt.dictResult['input']['operationPoint_CO2CAP_SYN'][i,j] * resultOpt.dictResult['input']['currentStateCO2CAP_SYNRaw'][i,3] * fTimeStep for j in cm.arrOperationPointsCO2CAP_SYN[4:])
                + cm.massFlowBiogasOut[3] * resultOpt.dictResult['input']['operationPoint_CO2CAP_SYN'][i,3] * resultOpt.dictResult['input']['currentStateCO2CAP_SYNRaw'][i,4] * fTimeStep)
            
            self.dictOutput['moleFractionMethaneBiogasOut'].append(
                + cm.moleFractionMethaneBiogasOut[0] * resultOpt.dictResult['input']['operationPoint_CO2CAP_SYN'][i,0] * resultOpt.dictResult['input']['currentStateCO2CAP_SYNRaw'][i,0] * fTimeStep
                + cm.moleFractionMethaneBiogasOut[1] * resultOpt.dictResult['input']['operationPoint_CO2CAP_SYN'][i,1] * resultOpt.dictResult['input']['currentStateCO2CAP_SYNRaw'][i,1] * fTimeStep
                + cm.moleFractionMethaneBiogasOut[2] * resultOpt.dictResult['input']['operationPoint_CO2CAP_SYN'][i,2] * resultOpt.dictResult['input']['currentStateCO2CAP_SYNRaw'][i,2] * fTimeStep
                + gp.quicksum(cm.moleFractionMethaneBiogasOut[j] * resultOpt.dictResult['input']['operationPoint_CO2CAP_SYN'][i,j] * resultOpt.dictResult['input']['currentStateCO2CAP_SYNRaw'][i,3] * fTimeStep for j in cm.arrOperationPointsCO2CAP_SYN[4:])
                + cm.moleFractionMethaneBiogasOut[3] * resultOpt.dictResult['input']['operationPoint_CO2CAP_SYN'][i,3] * resultOpt.dictResult['input']['currentStateCO2CAP_SYNRaw'][i,4] * fTimeStep)
            
            self.dictOutput['massFlowMethanolWaterStorageIn'].append(
                + cm.massFlowMethanolWaterStorageIn[0] * resultOpt.dictResult['input']['operationPoint_CO2CAP_SYN'][i,0] * resultOpt.dictResult['input']['currentStateCO2CAP_SYNRaw'][i,0] * fTimeStep
                + cm.massFlowMethanolWaterStorageIn[1] * resultOpt.dictResult['input']['operationPoint_CO2CAP_SYN'][i,1] * resultOpt.dictResult['input']['currentStateCO2CAP_SYNRaw'][i,1] * fTimeStep
                + cm.massFlowMethanolWaterStorageIn[2] * resultOpt.dictResult['input']['operationPoint_CO2CAP_SYN'][i,2] * resultOpt.dictResult['input']['currentStateCO2CAP_SYNRaw'][i,2] * fTimeStep
                + gp.quicksum(cm.massFlowMethanolWaterStorageIn[j] * resultOpt.dictResult['input']['operationPoint_CO2CAP_SYN'][i,j] * resultOpt.dictResult['input']['currentStateCO2CAP_SYNRaw'][i,3] * fTimeStep for j in cm.arrOperationPointsCO2CAP_SYN[4:])
                + cm.massFlowMethanolWaterStorageIn[3] * resultOpt.dictResult['input']['operationPoint_CO2CAP_SYN'][i,3] * resultOpt.dictResult['input']['currentStateCO2CAP_SYNRaw'][i,4] * fTimeStep)
           
            self.dictOutput['massFlowMethanolWaterStorageOut'].append(
                + cm.massFlowMethanolWaterStorageOut[0] * resultOpt.dictResult['input']['operationPoint_DIS'][i,0] * resultOpt.dictResult['input']['currentStateDISRaw'][i,0] * fTimeStep
                + cm.massFlowMethanolWaterStorageOut[1] * resultOpt.dictResult['input']['operationPoint_DIS'][i,1] * resultOpt.dictResult['input']['currentStateDISRaw'][i,1] * fTimeStep
                + cm.massFlowMethanolWaterStorageOut[2] * resultOpt.dictResult['input']['operationPoint_DIS'][i,2] * resultOpt.dictResult['input']['currentStateDISRaw'][i,2] * fTimeStep
                + gp.quicksum(cm.massFlowMethanolWaterStorageOut[j] * resultOpt.dictResult['input']['operationPoint_DIS'][i,j] * resultOpt.dictResult['input']['currentStateDISRaw'][i,3] * fTimeStep for j in cm.arrOperationPointsDIS[4:])
                + cm.massFlowMethanolWaterStorageOut[3] * resultOpt.dictResult['input']['operationPoint_DIS'][i,3] * resultOpt.dictResult['input']['currentStateDISRaw'][i,4] * fTimeStep)
            
            self.dictOutput['massFlowMethanolOut'].append(
                + cm.massFlowMethanolOut[0] * resultOpt.dictResult['input']['operationPoint_DIS'][i,0] * resultOpt.dictResult['input']['currentStateDISRaw'][i,0] * fTimeStep
                + cm.massFlowMethanolOut[1] * resultOpt.dictResult['input']['operationPoint_DIS'][i,1] * resultOpt.dictResult['input']['currentStateDISRaw'][i,1] * fTimeStep
                + cm.massFlowMethanolOut[2] * resultOpt.dictResult['input']['operationPoint_DIS'][i,2] * resultOpt.dictResult['input']['currentStateDISRaw'][i,2] * fTimeStep
                + gp.quicksum(cm.massFlowMethanolOut[j] * resultOpt.dictResult['input']['operationPoint_DIS'][i,j] * resultOpt.dictResult['input']['currentStateDISRaw'][i,3] * fTimeStep for j in cm.arrOperationPointsDIS[4:])
                + cm.massFlowMethanolOut[3] * resultOpt.dictResult['input']['operationPoint_DIS'][i,3] * resultOpt.dictResult['input']['currentStateDISRaw'][i,4] * fTimeStep)
            
            self.dictOutput['moleFractionH2SynthesisgasIn'].append(
                + cm.moleFractionH2SynthesisgasIn[0] * resultOpt.dictResult['input']['operationPoint_CO2CAP_SYN'][i,0] * resultOpt.dictResult['input']['currentStateCO2CAP_SYNRaw'][i,0] * fTimeStep
                + cm.moleFractionH2SynthesisgasIn[1] * resultOpt.dictResult['input']['operationPoint_CO2CAP_SYN'][i,1] * resultOpt.dictResult['input']['currentStateCO2CAP_SYNRaw'][i,1] * fTimeStep
                + cm.moleFractionH2SynthesisgasIn[2] * resultOpt.dictResult['input']['operationPoint_CO2CAP_SYN'][i,2] * resultOpt.dictResult['input']['currentStateCO2CAP_SYNRaw'][i,2] * fTimeStep
                + gp.quicksum(cm.moleFractionH2SynthesisgasIn[j] * resultOpt.dictResult['input']['operationPoint_CO2CAP_SYN'][i,j] * resultOpt.dictResult['input']['currentStateCO2CAP_SYNRaw'][i,3] * fTimeStep for j in cm.arrOperationPointsCO2CAP_SYN[4:])
                + cm.moleFractionH2SynthesisgasIn[3] * resultOpt.dictResult['input']['operationPoint_CO2CAP_SYN'][i,3] * resultOpt.dictResult['input']['currentStateCO2CAP_SYNRaw'][i,4] * fTimeStep)
            
            self.dictOutput['moleFractionCO2SynthesisgasIn'].append(
                + cm.moleFractionCO2SynthesisgasIn[0] * resultOpt.dictResult['input']['operationPoint_CO2CAP_SYN'][i,0] * resultOpt.dictResult['input']['currentStateCO2CAP_SYNRaw'][i,0] * fTimeStep
                + cm.moleFractionCO2SynthesisgasIn[1] * resultOpt.dictResult['input']['operationPoint_CO2CAP_SYN'][i,1] * resultOpt.dictResult['input']['currentStateCO2CAP_SYNRaw'][i,1] * fTimeStep
                + cm.moleFractionCO2SynthesisgasIn[2] * resultOpt.dictResult['input']['operationPoint_CO2CAP_SYN'][i,2] * resultOpt.dictResult['input']['currentStateCO2CAP_SYNRaw'][i,2] * fTimeStep
                + gp.quicksum(cm.moleFractionCO2SynthesisgasIn[j] * resultOpt.dictResult['input']['operationPoint_CO2CAP_SYN'][i,j] * resultOpt.dictResult['input']['currentStateCO2CAP_SYNRaw'][i,3] * fTimeStep for j in cm.arrOperationPointsCO2CAP_SYN[4:])
                + cm.moleFractionCO2SynthesisgasIn[3] * resultOpt.dictResult['input']['operationPoint_CO2CAP_SYN'][i,3] * resultOpt.dictResult['input']['currentStateCO2CAP_SYNRaw'][i,4] * fTimeStep)
            
            self.dictOutput['powerPlantCO2CAP_SYN'].append(
                + cm.powerPlantComponentsUnit1[0] * resultOpt.dictResult['input']['operationPoint_CO2CAP_SYN'][i,0] * resultOpt.dictResult['input']['currentStateCO2CAP_SYNRaw'][i,0] * fTimeStep
                + cm.powerPlantComponentsUnit1[1] * resultOpt.dictResult['input']['operationPoint_CO2CAP_SYN'][i,1] * resultOpt.dictResult['input']['currentStateCO2CAP_SYNRaw'][i,1] * fTimeStep
                + cm.powerPlantComponentsUnit1[2] * resultOpt.dictResult['input']['operationPoint_CO2CAP_SYN'][i,2] * resultOpt.dictResult['input']['currentStateCO2CAP_SYNRaw'][i,2] * fTimeStep
                + gp.quicksum(cm.powerPlantComponentsUnit1[j] * resultOpt.dictResult['input']['operationPoint_CO2CAP_SYN'][i,j] * resultOpt.dictResult['input']['currentStateCO2CAP_SYNRaw'][i,3] * fTimeStep for j in cm.arrOperationPointsCO2CAP_SYN[4:])
                + cm.powerPlantComponentsUnit1[3] * resultOpt.dictResult['input']['operationPoint_CO2CAP_SYN'][i,3] * resultOpt.dictResult['input']['currentStateCO2CAP_SYNRaw'][i,4] * fTimeStep)
            
            self.dictOutput['powerPlantDIS'].append(
                + cm.powerPlantComponentsUnit2[0] * resultOpt.dictResult['input']['operationPoint_DIS'][i,0] * resultOpt.dictResult['input']['currentStateDISRaw'][i,0] * fTimeStep
                + cm.powerPlantComponentsUnit2[1] * resultOpt.dictResult['input']['operationPoint_DIS'][i,1] * resultOpt.dictResult['input']['currentStateDISRaw'][i,1] * fTimeStep
                + cm.powerPlantComponentsUnit2[2] * resultOpt.dictResult['input']['operationPoint_DIS'][i,2] * resultOpt.dictResult['input']['currentStateDISRaw'][i,2] * fTimeStep
                + gp.quicksum(cm.powerPlantComponentsUnit2[j] * resultOpt.dictResult['input']['operationPoint_DIS'][i,j] * resultOpt.dictResult['input']['currentStateDISRaw'][i,3] * fTimeStep for j in cm.arrOperationPointsDIS[4:])
                + cm.powerPlantComponentsUnit2[3] * resultOpt.dictResult['input']['operationPoint_DIS'][i,3] * resultOpt.dictResult['input']['currentStateDISRaw'][i,4] * fTimeStep)


            self.dictOutput['batteryCharge'].append((self.param.param['battery']['initialCharge'] 
                + gp.quicksum(resultOpt.dictResult['input']['actualPowerInBatteryPV'][l] * self.param.param['battery']['efficiency'] for l in self.arrTime[0:i+1])
                + gp.quicksum(resultOpt.dictResult['input']['actualPowerInBatteryBought'][l] * self.param.param['battery']['efficiency'] for l in self.arrTime[0:i+1])  
                - gp.quicksum(resultOpt.dictResult['input']['actualPowerOutBattery'][l] for l in self.arrTime[0:i+1])
                - gp.quicksum(resultOpt.dictResult['input']['actualPowerOutBatterySold'][l] for l in self.arrTime[0:i+1])))
            
            self.dictOutput['batteryCharge'][i] = self.dictOutput['batteryCharge'][i] / self.param.param['battery']['power'] * 100


            if self.param.param['controlParameters']['objectiveFunction'] == 7 or self.param.param['controlParameters']['objectiveFunction'] == 8:
                self.dictOutput['storageH2Pressure'].append((self.param.param['storageH2']['InitialFilling']
                    + gp.quicksum(cm.powerElectrolyser[j] * resultOpt.dictResult['input']['powerElectrolyserRaw'][l,j,n] * resultOpt.dictResult['input']['modeElectrolyserRaw'][l,n,3] * self.param.param['electrolyser']['constant'] * fTimeStep for l in self.arrTime[0:i+1] for n in elec.arrEnapterModules for j in cm.arrOperationPointsELEC)
                    - gp.quicksum(cm.massFlowHydrogenIn[0] * resultOpt.dictResult['input']['operationPoint_CO2CAP_SYN'][l,0] * resultOpt.dictResult['input']['currentStateCO2CAP_SYNRaw'][l,0] * fTimeStep for l in self.arrTime[0:i+1])
                    - gp.quicksum(cm.massFlowHydrogenIn[1] * resultOpt.dictResult['input']['operationPoint_CO2CAP_SYN'][l,1] * resultOpt.dictResult['input']['currentStateCO2CAP_SYNRaw'][l,1] * fTimeStep for l in self.arrTime[0:i+1])
                    - gp.quicksum(cm.massFlowHydrogenIn[2] * resultOpt.dictResult['input']['operationPoint_CO2CAP_SYN'][l,2] * resultOpt.dictResult['input']['currentStateCO2CAP_SYNRaw'][l,2] * fTimeStep for l in self.arrTime[0:i+1])
                    - gp.quicksum(cm.massFlowHydrogenIn[j] * resultOpt.dictResult['input']['operationPoint_CO2CAP_SYN'][l,j] * resultOpt.dictResult['input']['currentStateCO2CAP_SYNRaw'][l,3] * fTimeStep for j in cm.arrOperationPointsCO2CAP_SYN[4:] for l in self.arrTime[0:i+1])
                    - gp.quicksum(cm.massFlowHydrogenIn[3] * resultOpt.dictResult['input']['operationPoint_CO2CAP_SYN'][l,3] * resultOpt.dictResult['input']['currentStateCO2CAP_SYNRaw'][l,4] * fTimeStep for l in self.arrTime[0:i+1]))
                    * self.param.param['R_H2'] * (self.param.param['Tamb'] + self.param.param['T0']) / (self.param.param['storageH2']['Volume'] * 100000))                     
            else:
                self.dictOutput['storageH2Pressure'].append((self.param.param['storageH2']['InitialFilling']
                    + gp.quicksum(resultOpt.dictResult['input']['powerElectrolyserRaw'][l,n] * resultOpt.dictResult['input']['modeElectrolyserRaw'][l,n,3] * self.param.param['electrolyser']['constant'] * fTimeStep for l in self.arrTime[0:i+1] for n in elec.arrEnapterModules)
                    - gp.quicksum(cm.massFlowHydrogenIn[0] * resultOpt.dictResult['input']['operationPoint_CO2CAP_SYN'][l,0] * resultOpt.dictResult['input']['currentStateCO2CAP_SYNRaw'][l,0] * fTimeStep for l in self.arrTime[0:i+1])
                    - gp.quicksum(cm.massFlowHydrogenIn[1] * resultOpt.dictResult['input']['operationPoint_CO2CAP_SYN'][l,1] * resultOpt.dictResult['input']['currentStateCO2CAP_SYNRaw'][l,1] * fTimeStep for l in self.arrTime[0:i+1])
                    - gp.quicksum(cm.massFlowHydrogenIn[2] * resultOpt.dictResult['input']['operationPoint_CO2CAP_SYN'][l,2] * resultOpt.dictResult['input']['currentStateCO2CAP_SYNRaw'][l,2] * fTimeStep for l in self.arrTime[0:i+1])
                    - gp.quicksum(cm.massFlowHydrogenIn[j] * resultOpt.dictResult['input']['operationPoint_CO2CAP_SYN'][l,j] * resultOpt.dictResult['input']['currentStateCO2CAP_SYNRaw'][l,3] * fTimeStep for j in cm.arrOperationPointsCO2CAP_SYN[4:] for l in self.arrTime[0:i+1])
                    - gp.quicksum(cm.massFlowHydrogenIn[3] * resultOpt.dictResult['input']['operationPoint_CO2CAP_SYN'][l,3] * resultOpt.dictResult['input']['currentStateCO2CAP_SYNRaw'][l,4] * fTimeStep for l in self.arrTime[0:i+1]))
                    * self.param.param['R_H2'] * (self.param.param['Tamb'] + self.param.param['T0']) / (self.param.param['storageH2']['Volume'] * 100000))


            self.dictOutput['storageMethanolWaterFilling'].append(self.param.param['storageMethanolWater']['InitialFilling'] 
                + gp.quicksum(cm.massFlowMethanolWaterStorageIn[(0)] / self.param.param['storageMethanolWater']['InitialDensity'] * resultOpt.dictResult['input']['operationPoint_CO2CAP_SYN'][l,0] * resultOpt.dictResult['input']['currentStateCO2CAP_SYNRaw'][l,0] * fTimeStep for l in self.arrTime[0:i+1])
                + gp.quicksum(cm.massFlowMethanolWaterStorageIn[(1)] / self.param.param['storageMethanolWater']['InitialDensity'] * resultOpt.dictResult['input']['operationPoint_CO2CAP_SYN'][l,1] * resultOpt.dictResult['input']['currentStateCO2CAP_SYNRaw'][l,1] * fTimeStep for l in self.arrTime[0:i+1])
                + gp.quicksum(cm.massFlowMethanolWaterStorageIn[(2)] / self.param.param['storageMethanolWater']['InitialDensity'] * resultOpt.dictResult['input']['operationPoint_CO2CAP_SYN'][l,2] * resultOpt.dictResult['input']['currentStateCO2CAP_SYNRaw'][l,2] * fTimeStep for l in self.arrTime[0:i+1])
                + gp.quicksum(cm.massFlowMethanolWaterStorageIn[(j)] / self.param.param['storageMethanolWater']['InitialDensity'] * resultOpt.dictResult['input']['operationPoint_CO2CAP_SYN'][l,j] * resultOpt.dictResult['input']['currentStateCO2CAP_SYNRaw'][l,3] * fTimeStep for j in cm.arrOperationPointsCO2CAP_SYN[4:] for l in self.arrTime[0:i+1])
                + gp.quicksum(cm.massFlowMethanolWaterStorageIn[(3)] / self.param.param['storageMethanolWater']['InitialDensity'] * resultOpt.dictResult['input']['operationPoint_CO2CAP_SYN'][l,3] * resultOpt.dictResult['input']['currentStateCO2CAP_SYNRaw'][l,4] * fTimeStep for l in self.arrTime[0:i+1])
                - gp.quicksum(cm.massFlowMethanolWaterStorageOut[(0)] / self.param.param['storageMethanolWater']['InitialDensity'] * resultOpt.dictResult['input']['operationPoint_DIS'][l,0] * resultOpt.dictResult['input']['currentStateDISRaw'][l,0] * fTimeStep for l in self.arrTime[0:i+1])
                - gp.quicksum(cm.massFlowMethanolWaterStorageOut[(1)] / self.param.param['storageMethanolWater']['InitialDensity'] * resultOpt.dictResult['input']['operationPoint_DIS'][l,1] * resultOpt.dictResult['input']['currentStateDISRaw'][l,1] * fTimeStep for l in self.arrTime[0:i+1])
                - gp.quicksum(cm.massFlowMethanolWaterStorageOut[(2)] / self.param.param['storageMethanolWater']['InitialDensity'] * resultOpt.dictResult['input']['operationPoint_DIS'][l,2] * resultOpt.dictResult['input']['currentStateDISRaw'][l,2] * fTimeStep for l in self.arrTime[0:i+1])
                - gp.quicksum(cm.massFlowMethanolWaterStorageOut[(j)] / self.param.param['storageMethanolWater']['InitialDensity'] * resultOpt.dictResult['input']['operationPoint_DIS'][l,j] * resultOpt.dictResult['input']['currentStateDISRaw'][l,3] * fTimeStep for j in cm.arrOperationPointsDIS[4:] for l in self.arrTime[0:i+1])
                - gp.quicksum(cm.massFlowMethanolWaterStorageOut[(3)] / self.param.param['storageMethanolWater']['InitialDensity'] * resultOpt.dictResult['input']['operationPoint_DIS'][l,3] * resultOpt.dictResult['input']['currentStateDISRaw'][l,4] * fTimeStep for l in self.arrTime[0:i+1]))
            
            for key in self.dictOutput:
                self.dictOutput[key][i] = self.dictOutput[key][i].getValue()
        

        self.dictOutput['moleRatioH2_CO2_Synthesisgas'] = []
        self.dictOutput['moleRatioH2_CO2_Synthesisgas'].append(0)

        #for i in self.arrTime[1:]:
        #    self.dictOutput['moleRatioH2_CO2_Synthesisgas'].append(self.dictOutput['moleFractionH2SynthesisgasIn'][i] / self.dictOutput['moleFractionCO2SynthesisgasIn'][i])



        # Costs
        self.dictCosts['methanol'] = -np.sum(np.array(self.dictOutput['massFlowMethanolOut']) * self.param.param['prices']['methanol'])
        self.dictCosts['powerBought'] = np.sum(np.dot(self.param.param['prices']['power'], resultOpt.dictResult['input']['powerBought']))
        self.dictCosts['carbonIntensity'] = np.sum(np.dot(self.param.param['carbonIntensity']['carbonIntensity'], resultOpt.dictResult['input']['powerBought']))
        self.dictCosts['powerBatterySold'] = 0.0
        for i in self.arrTime: 
            self.dictCosts['powerBatterySold'] = self.dictCosts['powerBatterySold'] - self.param.param['prices']['powerSold']*resultOpt.dictResult['input']['actualPowerOutBatterySold'][i]
        
        self.dictCosts['all'] = sum(self.dictCosts.values())

        
        # Save the data in result
        resultOpt.dictResult['output'] = self.dictOutput
        resultOpt.dictResult['costs'] = self.dictCosts