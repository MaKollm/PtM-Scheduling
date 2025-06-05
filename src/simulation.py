#!/usr/bin/env python3.10


#############################
########## Simulation ##########

import gurobipy as gp
import numpy as np
import matplotlib.pyplot as plt
import copy


class Simulation:
    def __init__(self, param):
        self.funcUpdate(param)


    def funcUpdate(self, param):
        self.param = param
        self.arrTime = list(range(0,self.param.param['controlParameters']['numberOfTimeSteps']))
        self.dictOutput_Scheduling = {}
        self.dictOutput_Sim = {}
        self.dictCosts = {}
        self.arrConstrViolationInput = []
        self.dictConstrViolationOutput = {}

    def funcStartSimulation(self, param, resultOpt, cm, elec, pv, wt, pp, ci):
        
        self.funcUpdate(param)
        
        self.funcSimulate(resultOpt, cm, elec, pv, wt, pp, ci)
        self.funcCalculateCosts(resultOpt, cm, elec, pv, wt, pp, ci)


    def funcSimulate(self, resultOpt, cm, elec, pv, wt, pp, ci):
        fTimeStep = self.param.param['controlParameters']['timeStep']
        
        # Output variables
        self.dictOutput_Scheduling['massFlowHydrogenIn'] = []
        self.dictOutput_Scheduling['massFlowBiogasOut'] = []
        self.dictOutput_Scheduling['moleFractionMethaneBiogasOut'] = []
        self.dictOutput_Scheduling['massFlowMethanolWaterStorageIn'] = []
        self.dictOutput_Scheduling['massFlowMethanolWaterStorageOut'] = []
        self.dictOutput_Scheduling['massFlowMethanolOut'] = []
        self.dictOutput_Scheduling['moleFractionH2SynthesisgasIn'] = []
        self.dictOutput_Scheduling['moleFractionCO2SynthesisgasIn'] = []

        self.dictOutput_Scheduling['powerPlantCO2CAP'] = []
        self.dictOutput_Scheduling['powerPlantSYN'] = []
        self.dictOutput_Scheduling['powerPlantDIS'] = []

        self.dictOutput_Scheduling['storageH2Pressure'] = []
        self.dictOutput_Scheduling['storageMethanolWaterFilling'] = []
        self.dictOutput_Scheduling['batteryCharge'] = []



        for i in self.arrTime:#range(0,self.param.param['controlParameters']['numTimeStepsToSimulate']+1):


            self.dictOutput_Scheduling['massFlowHydrogenIn'].append(
                + cm.massFlowHydrogenInCO2CAP[0] * resultOpt.dictResult['input']['operationPoint_CO2CAP'][i,0] * resultOpt.dictResult['input']['currentStateCO2CAPRaw'][i,0] * fTimeStep
                + cm.massFlowHydrogenInCO2CAP[1] * resultOpt.dictResult['input']['operationPoint_CO2CAP'][i,1] * resultOpt.dictResult['input']['currentStateCO2CAPRaw'][i,1] * fTimeStep
                + cm.massFlowHydrogenInCO2CAP[2] * resultOpt.dictResult['input']['operationPoint_CO2CAP'][i,2] * resultOpt.dictResult['input']['currentStateCO2CAPRaw'][i,2] * fTimeStep
                + gp.quicksum(cm.massFlowHydrogenInCO2CAP[j] * resultOpt.dictResult['input']['operationPoint_CO2CAP'][i,j] * resultOpt.dictResult['input']['currentStateCO2CAPRaw'][i,3] * fTimeStep for j in cm.arrOperationPointsCO2CAP[4:])
                + cm.massFlowHydrogenInCO2CAP[3] * resultOpt.dictResult['input']['operationPoint_CO2CAP'][i,3] * resultOpt.dictResult['input']['currentStateCO2CAPRaw'][i,4] * fTimeStep
                + cm.massFlowHydrogenInSYN[0] * resultOpt.dictResult['input']['operationPoint_SYN'][i,0] * resultOpt.dictResult['input']['currentStateSYNRaw'][i,0] * fTimeStep
                + cm.massFlowHydrogenInSYN[1] * resultOpt.dictResult['input']['operationPoint_SYN'][i,1] * resultOpt.dictResult['input']['currentStateSYNRaw'][i,1] * fTimeStep
                + cm.massFlowHydrogenInSYN[2] * resultOpt.dictResult['input']['operationPoint_SYN'][i,2] * resultOpt.dictResult['input']['currentStateSYNRaw'][i,2] * fTimeStep
                + gp.quicksum(cm.massFlowHydrogenInSYN[j] * resultOpt.dictResult['input']['operationPoint_SYN'][i,j] * resultOpt.dictResult['input']['currentStateSYNRaw'][i,3] * fTimeStep for j in cm.arrOperationPointsSYN[4:])
                + cm.massFlowHydrogenInSYN[3] * resultOpt.dictResult['input']['operationPoint_SYN'][i,3] * resultOpt.dictResult['input']['currentStateSYNRaw'][i,4] * fTimeStep)
            
            self.dictOutput_Scheduling['massFlowBiogasOut'].append(
                + cm.massFlowBiogasOut[0] * resultOpt.dictResult['input']['operationPoint_CO2CAP'][i,0] * resultOpt.dictResult['input']['currentStateCO2CAPRaw'][i,0] * fTimeStep
                + cm.massFlowBiogasOut[1] * resultOpt.dictResult['input']['operationPoint_CO2CAP'][i,1] * resultOpt.dictResult['input']['currentStateCO2CAPRaw'][i,1] * fTimeStep
                + cm.massFlowBiogasOut[2] * resultOpt.dictResult['input']['operationPoint_CO2CAP'][i,2] * resultOpt.dictResult['input']['currentStateCO2CAPRaw'][i,2] * fTimeStep
                + gp.quicksum(cm.massFlowBiogasOut[j] * resultOpt.dictResult['input']['operationPoint_CO2CAP'][i,j] * resultOpt.dictResult['input']['currentStateCO2CAPRaw'][i,3] * fTimeStep for j in cm.arrOperationPointsCO2CAP[4:])
                + cm.massFlowBiogasOut[3] * resultOpt.dictResult['input']['operationPoint_CO2CAP'][i,3] * resultOpt.dictResult['input']['currentStateCO2CAPRaw'][i,4] * fTimeStep)
            
            self.dictOutput_Scheduling['moleFractionMethaneBiogasOut'].append(
                + cm.moleFractionMethaneBiogasOut[0] * resultOpt.dictResult['input']['operationPoint_CO2CAP'][i,0] * resultOpt.dictResult['input']['currentStateCO2CAPRaw'][i,0] * fTimeStep
                + cm.moleFractionMethaneBiogasOut[1] * resultOpt.dictResult['input']['operationPoint_CO2CAP'][i,1] * resultOpt.dictResult['input']['currentStateCO2CAPRaw'][i,1] * fTimeStep
                + cm.moleFractionMethaneBiogasOut[2] * resultOpt.dictResult['input']['operationPoint_CO2CAP'][i,2] * resultOpt.dictResult['input']['currentStateCO2CAPRaw'][i,2] * fTimeStep
                + gp.quicksum(cm.moleFractionMethaneBiogasOut[j] * resultOpt.dictResult['input']['operationPoint_CO2CAP'][i,j] * resultOpt.dictResult['input']['currentStateCO2CAPRaw'][i,3] * fTimeStep for j in cm.arrOperationPointsCO2CAP[4:])
                + cm.moleFractionMethaneBiogasOut[3] * resultOpt.dictResult['input']['operationPoint_CO2CAP'][i,3] * resultOpt.dictResult['input']['currentStateCO2CAPRaw'][i,4] * fTimeStep)
            
            self.dictOutput_Scheduling['massFlowMethanolWaterStorageIn'].append(
                + cm.massFlowMethanolWaterStorageIn[0] * resultOpt.dictResult['input']['operationPoint_SYN'][i,0] * resultOpt.dictResult['input']['currentStateSYNRaw'][i,0] * fTimeStep
                + cm.massFlowMethanolWaterStorageIn[1] * resultOpt.dictResult['input']['operationPoint_SYN'][i,1] * resultOpt.dictResult['input']['currentStateSYNRaw'][i,1] * fTimeStep
                + cm.massFlowMethanolWaterStorageIn[2] * resultOpt.dictResult['input']['operationPoint_SYN'][i,2] * resultOpt.dictResult['input']['currentStateSYNRaw'][i,2] * fTimeStep
                + gp.quicksum(cm.massFlowMethanolWaterStorageIn[j] * resultOpt.dictResult['input']['operationPoint_SYN'][i,j] * resultOpt.dictResult['input']['currentStateSYNRaw'][i,3] * fTimeStep for j in cm.arrOperationPointsSYN[4:])
                + cm.massFlowMethanolWaterStorageIn[3] * resultOpt.dictResult['input']['operationPoint_SYN'][i,3] * resultOpt.dictResult['input']['currentStateSYNRaw'][i,4] * fTimeStep)
           
            self.dictOutput_Scheduling['massFlowMethanolWaterStorageOut'].append(
                + cm.massFlowMethanolWaterStorageOut[0] * resultOpt.dictResult['input']['operationPoint_DIS'][i,0] * resultOpt.dictResult['input']['currentStateDISRaw'][i,0] * fTimeStep
                + cm.massFlowMethanolWaterStorageOut[1] * resultOpt.dictResult['input']['operationPoint_DIS'][i,1] * resultOpt.dictResult['input']['currentStateDISRaw'][i,1] * fTimeStep
                + cm.massFlowMethanolWaterStorageOut[2] * resultOpt.dictResult['input']['operationPoint_DIS'][i,2] * resultOpt.dictResult['input']['currentStateDISRaw'][i,2] * fTimeStep
                + gp.quicksum(cm.massFlowMethanolWaterStorageOut[j] * resultOpt.dictResult['input']['operationPoint_DIS'][i,j] * resultOpt.dictResult['input']['currentStateDISRaw'][i,3] * fTimeStep for j in cm.arrOperationPointsDIS[4:])
                + cm.massFlowMethanolWaterStorageOut[3] * resultOpt.dictResult['input']['operationPoint_DIS'][i,3] * resultOpt.dictResult['input']['currentStateDISRaw'][i,4] * fTimeStep)
            
            self.dictOutput_Scheduling['massFlowMethanolOut'].append(
                + cm.massFlowMethanolOut[0] * resultOpt.dictResult['input']['operationPoint_DIS'][i,0] * resultOpt.dictResult['input']['currentStateDISRaw'][i,0] * fTimeStep
                + cm.massFlowMethanolOut[1] * resultOpt.dictResult['input']['operationPoint_DIS'][i,1] * resultOpt.dictResult['input']['currentStateDISRaw'][i,1] * fTimeStep
                + cm.massFlowMethanolOut[2] * resultOpt.dictResult['input']['operationPoint_DIS'][i,2] * resultOpt.dictResult['input']['currentStateDISRaw'][i,2] * fTimeStep
                + gp.quicksum(cm.massFlowMethanolOut[j] * resultOpt.dictResult['input']['operationPoint_DIS'][i,j] * resultOpt.dictResult['input']['currentStateDISRaw'][i,3] * fTimeStep for j in cm.arrOperationPointsDIS[4:])
                + cm.massFlowMethanolOut[3] * resultOpt.dictResult['input']['operationPoint_DIS'][i,3] * resultOpt.dictResult['input']['currentStateDISRaw'][i,4] * fTimeStep)
            
            self.dictOutput_Scheduling['moleFractionH2SynthesisgasIn'].append(
                + cm.moleFractionH2SynthesisgasIn[0] * resultOpt.dictResult['input']['operationPoint_CO2CAP'][i,0] * resultOpt.dictResult['input']['currentStateCO2CAPRaw'][i,0] * fTimeStep
                + cm.moleFractionH2SynthesisgasIn[1] * resultOpt.dictResult['input']['operationPoint_CO2CAP'][i,1] * resultOpt.dictResult['input']['currentStateCO2CAPRaw'][i,1] * fTimeStep
                + cm.moleFractionH2SynthesisgasIn[2] * resultOpt.dictResult['input']['operationPoint_CO2CAP'][i,2] * resultOpt.dictResult['input']['currentStateCO2CAPRaw'][i,2] * fTimeStep
                + gp.quicksum(cm.moleFractionH2SynthesisgasIn[j] * resultOpt.dictResult['input']['operationPoint_CO2CAP'][i,j] * resultOpt.dictResult['input']['currentStateCO2CAPRaw'][i,3] * fTimeStep for j in cm.arrOperationPointsCO2CAP[4:])
                + cm.moleFractionH2SynthesisgasIn[3] * resultOpt.dictResult['input']['operationPoint_CO2CAP'][i,3] * resultOpt.dictResult['input']['currentStateCO2CAPRaw'][i,4] * fTimeStep)
            
            self.dictOutput_Scheduling['moleFractionCO2SynthesisgasIn'].append(
                + cm.moleFractionCO2SynthesisgasIn[0] * resultOpt.dictResult['input']['operationPoint_CO2CAP'][i,0] * resultOpt.dictResult['input']['currentStateCO2CAPRaw'][i,0] * fTimeStep
                + cm.moleFractionCO2SynthesisgasIn[1] * resultOpt.dictResult['input']['operationPoint_CO2CAP'][i,1] * resultOpt.dictResult['input']['currentStateCO2CAPRaw'][i,1] * fTimeStep
                + cm.moleFractionCO2SynthesisgasIn[2] * resultOpt.dictResult['input']['operationPoint_CO2CAP'][i,2] * resultOpt.dictResult['input']['currentStateCO2CAPRaw'][i,2] * fTimeStep
                + gp.quicksum(cm.moleFractionCO2SynthesisgasIn[j] * resultOpt.dictResult['input']['operationPoint_CO2CAP'][i,j] * resultOpt.dictResult['input']['currentStateCO2CAPRaw'][i,3] * fTimeStep for j in cm.arrOperationPointsCO2CAP[4:])
                + cm.moleFractionCO2SynthesisgasIn[3] * resultOpt.dictResult['input']['operationPoint_CO2CAP'][i,3] * resultOpt.dictResult['input']['currentStateCO2CAPRaw'][i,4] * fTimeStep)
            
            self.dictOutput_Scheduling['powerPlantCO2CAP'].append(
                + cm.powerPlantComponentsUnit1[0] * resultOpt.dictResult['input']['operationPoint_CO2CAP'][i,0] * resultOpt.dictResult['input']['currentStateCO2CAPRaw'][i,0] * fTimeStep
                + cm.powerPlantComponentsUnit1[1] * resultOpt.dictResult['input']['operationPoint_CO2CAP'][i,1] * resultOpt.dictResult['input']['currentStateCO2CAPRaw'][i,1] * fTimeStep
                + cm.powerPlantComponentsUnit1[2] * resultOpt.dictResult['input']['operationPoint_CO2CAP'][i,2] * resultOpt.dictResult['input']['currentStateCO2CAPRaw'][i,2] * fTimeStep
                + gp.quicksum(cm.powerPlantComponentsUnit1[j] * resultOpt.dictResult['input']['operationPoint_CO2CAP'][i,j] * resultOpt.dictResult['input']['currentStateCO2CAPRaw'][i,3] * fTimeStep for j in cm.arrOperationPointsCO2CAP[4:])
                + cm.powerPlantComponentsUnit1[3] * resultOpt.dictResult['input']['operationPoint_CO2CAP'][i,3] * resultOpt.dictResult['input']['currentStateCO2CAPRaw'][i,4] * fTimeStep)

            self.dictOutput_Scheduling['powerPlantSYN'].append(
                + cm.powerPlantComponentsUnit2[0] * resultOpt.dictResult['input']['operationPoint_SYN'][i,0] * resultOpt.dictResult['input']['currentStateSYNRaw'][i,0] * fTimeStep
                + cm.powerPlantComponentsUnit2[1] * resultOpt.dictResult['input']['operationPoint_SYN'][i,1] * resultOpt.dictResult['input']['currentStateSYNRaw'][i,1] * fTimeStep
                + cm.powerPlantComponentsUnit2[2] * resultOpt.dictResult['input']['operationPoint_SYN'][i,2] * resultOpt.dictResult['input']['currentStateSYNRaw'][i,2] * fTimeStep
                + gp.quicksum(cm.powerPlantComponentsUnit2[j] * resultOpt.dictResult['input']['operationPoint_SYN'][i,j] * resultOpt.dictResult['input']['currentStateSYNRaw'][i,3] * fTimeStep for j in cm.arrOperationPointsSYN[4:])
                + cm.powerPlantComponentsUnit2[3] * resultOpt.dictResult['input']['operationPoint_SYN'][i,3] * resultOpt.dictResult['input']['currentStateSYNRaw'][i,4] * fTimeStep)
                       
            self.dictOutput_Scheduling['powerPlantDIS'].append(
                + cm.powerPlantComponentsUnit3[0] * resultOpt.dictResult['input']['operationPoint_DIS'][i,0] * resultOpt.dictResult['input']['currentStateDISRaw'][i,0] * fTimeStep
                + cm.powerPlantComponentsUnit3[1] * resultOpt.dictResult['input']['operationPoint_DIS'][i,1] * resultOpt.dictResult['input']['currentStateDISRaw'][i,1] * fTimeStep
                + cm.powerPlantComponentsUnit3[2] * resultOpt.dictResult['input']['operationPoint_DIS'][i,2] * resultOpt.dictResult['input']['currentStateDISRaw'][i,2] * fTimeStep
                + gp.quicksum(cm.powerPlantComponentsUnit3[j] * resultOpt.dictResult['input']['operationPoint_DIS'][i,j] * resultOpt.dictResult['input']['currentStateDISRaw'][i,3] * fTimeStep for j in cm.arrOperationPointsDIS[4:])
                + cm.powerPlantComponentsUnit3[3] * resultOpt.dictResult['input']['operationPoint_DIS'][i,3] * resultOpt.dictResult['input']['currentStateDISRaw'][i,4] * fTimeStep)


            self.dictOutput_Scheduling['batteryCharge'].append((self.param.param['battery']['initialCharge'] 
                + gp.quicksum(resultOpt.dictResult['input']['actualPowerInBatteryPV'][l] * self.param.param['battery']['efficiency'] for l in self.arrTime[0:i+1])
                + gp.quicksum(resultOpt.dictResult['input']['actualPowerInBatteryWind'][l] * self.param.param['battery']['efficiency'] for l in self.arrTime[0:i+1])
                + gp.quicksum(resultOpt.dictResult['input']['actualPowerInBatteryBought'][l] * self.param.param['battery']['efficiency'] for l in self.arrTime[0:i+1])  
                - gp.quicksum(resultOpt.dictResult['input']['actualPowerOutBattery'][l] for l in self.arrTime[0:i+1])
                - gp.quicksum(resultOpt.dictResult['input']['actualPowerOutBatterySold'][l] for l in self.arrTime[0:i+1])))
            
            self.dictOutput_Scheduling['batteryCharge'][i] = self.dictOutput_Scheduling['batteryCharge'][i] / self.param.param['battery']['power'] * 100


            self.dictOutput_Scheduling['storageH2Pressure'].append((self.param.param['storageH2']['InitialFilling']
                + gp.quicksum(resultOpt.dictResult['input']['powerElectrolyserRaw'][l,n] * resultOpt.dictResult['input']['modeElectrolyserRaw'][l,n,3] * self.param.param['electrolyser']['constant'] * fTimeStep for l in self.arrTime[0:i+1] for n in elec.arrEnapterModules)
                - gp.quicksum(cm.massFlowHydrogenInCO2CAP[0] * resultOpt.dictResult['input']['operationPoint_CO2CAP'][l,0] * resultOpt.dictResult['input']['currentStateCO2CAPRaw'][l,0] * fTimeStep for l in self.arrTime[0:i+1])
                - gp.quicksum(cm.massFlowHydrogenInCO2CAP[1] * resultOpt.dictResult['input']['operationPoint_CO2CAP'][l,1] * resultOpt.dictResult['input']['currentStateCO2CAPRaw'][l,1] * fTimeStep for l in self.arrTime[0:i+1])
                - gp.quicksum(cm.massFlowHydrogenInCO2CAP[2] * resultOpt.dictResult['input']['operationPoint_CO2CAP'][l,2] * resultOpt.dictResult['input']['currentStateCO2CAPRaw'][l,2] * fTimeStep for l in self.arrTime[0:i+1])
                - gp.quicksum(cm.massFlowHydrogenInCO2CAP[j] * resultOpt.dictResult['input']['operationPoint_CO2CAP'][l,j] * resultOpt.dictResult['input']['currentStateCO2CAPRaw'][l,3] * fTimeStep for j in cm.arrOperationPointsCO2CAP[4:] for l in self.arrTime[0:i+1])
                - gp.quicksum(cm.massFlowHydrogenInCO2CAP[3] * resultOpt.dictResult['input']['operationPoint_CO2CAP'][l,3] * resultOpt.dictResult['input']['currentStateCO2CAPRaw'][l,4] * fTimeStep for l in self.arrTime[0:i+1])
                - gp.quicksum(cm.massFlowHydrogenInSYN[0] * resultOpt.dictResult['input']['operationPoint_SYN'][l,0] * resultOpt.dictResult['input']['currentStateSYNRaw'][l,0] * fTimeStep for l in self.arrTime[0:i+1])
                - gp.quicksum(cm.massFlowHydrogenInSYN[1] * resultOpt.dictResult['input']['operationPoint_SYN'][l,1] * resultOpt.dictResult['input']['currentStateSYNRaw'][l,1] * fTimeStep for l in self.arrTime[0:i+1])
                - gp.quicksum(cm.massFlowHydrogenInSYN[2] * resultOpt.dictResult['input']['operationPoint_SYN'][l,2] * resultOpt.dictResult['input']['currentStateSYNRaw'][l,2] * fTimeStep for l in self.arrTime[0:i+1])
                - gp.quicksum(cm.massFlowHydrogenInSYN[j] * resultOpt.dictResult['input']['operationPoint_SYN'][l,j] * resultOpt.dictResult['input']['currentStateSYNRaw'][l,3] * fTimeStep for j in cm.arrOperationPointsSYN[4:] for l in self.arrTime[0:i+1])
                - gp.quicksum(cm.massFlowHydrogenInSYN[3] * resultOpt.dictResult['input']['operationPoint_SYN'][l,3] * resultOpt.dictResult['input']['currentStateSYNRaw'][l,4] * fTimeStep for l in self.arrTime[0:i+1]))
                * self.param.param['R_H2'] * (self.param.param['Tamb'] + self.param.param['T0']) / (self.param.param['storageH2']['Volume'] * 100000))


            self.dictOutput_Scheduling['storageMethanolWaterFilling'].append(self.param.param['storageMethanolWater']['InitialFilling'] 
                + gp.quicksum(cm.massFlowMethanolWaterStorageIn[(0)] / self.param.param['storageMethanolWater']['InitialDensity'] * resultOpt.dictResult['input']['operationPoint_SYN'][l,0] * resultOpt.dictResult['input']['currentStateSYNRaw'][l,0] * fTimeStep for l in self.arrTime[0:i+1])
                + gp.quicksum(cm.massFlowMethanolWaterStorageIn[(1)] / self.param.param['storageMethanolWater']['InitialDensity'] * resultOpt.dictResult['input']['operationPoint_SYN'][l,1] * resultOpt.dictResult['input']['currentStateSYNRaw'][l,1] * fTimeStep for l in self.arrTime[0:i+1])
                + gp.quicksum(cm.massFlowMethanolWaterStorageIn[(2)] / self.param.param['storageMethanolWater']['InitialDensity'] * resultOpt.dictResult['input']['operationPoint_SYN'][l,2] * resultOpt.dictResult['input']['currentStateSYNRaw'][l,2] * fTimeStep for l in self.arrTime[0:i+1])
                + gp.quicksum(cm.massFlowMethanolWaterStorageIn[(j)] / self.param.param['storageMethanolWater']['InitialDensity'] * resultOpt.dictResult['input']['operationPoint_SYN'][l,j] * resultOpt.dictResult['input']['currentStateSYNRaw'][l,3] * fTimeStep for j in cm.arrOperationPointsSYN[4:] for l in self.arrTime[0:i+1])
                + gp.quicksum(cm.massFlowMethanolWaterStorageIn[(3)] / self.param.param['storageMethanolWater']['InitialDensity'] * resultOpt.dictResult['input']['operationPoint_SYN'][l,3] * resultOpt.dictResult['input']['currentStateSYNRaw'][l,4] * fTimeStep for l in self.arrTime[0:i+1])
                - gp.quicksum(cm.massFlowMethanolWaterStorageOut[(0)] / self.param.param['storageMethanolWater']['InitialDensity'] * resultOpt.dictResult['input']['operationPoint_DIS'][l,0] * resultOpt.dictResult['input']['currentStateDISRaw'][l,0] * fTimeStep for l in self.arrTime[0:i+1])
                - gp.quicksum(cm.massFlowMethanolWaterStorageOut[(1)] / self.param.param['storageMethanolWater']['InitialDensity'] * resultOpt.dictResult['input']['operationPoint_DIS'][l,1] * resultOpt.dictResult['input']['currentStateDISRaw'][l,1] * fTimeStep for l in self.arrTime[0:i+1])
                - gp.quicksum(cm.massFlowMethanolWaterStorageOut[(2)] / self.param.param['storageMethanolWater']['InitialDensity'] * resultOpt.dictResult['input']['operationPoint_DIS'][l,2] * resultOpt.dictResult['input']['currentStateDISRaw'][l,2] * fTimeStep for l in self.arrTime[0:i+1])
                - gp.quicksum(cm.massFlowMethanolWaterStorageOut[(j)] / self.param.param['storageMethanolWater']['InitialDensity'] * resultOpt.dictResult['input']['operationPoint_DIS'][l,j] * resultOpt.dictResult['input']['currentStateDISRaw'][l,3] * fTimeStep for j in cm.arrOperationPointsDIS[4:] for l in self.arrTime[0:i+1])
                - gp.quicksum(cm.massFlowMethanolWaterStorageOut[(3)] / self.param.param['storageMethanolWater']['InitialDensity'] * resultOpt.dictResult['input']['operationPoint_DIS'][l,3] * resultOpt.dictResult['input']['currentStateDISRaw'][l,4] * fTimeStep for l in self.arrTime[0:i+1]))
            
            for key in self.dictOutput_Scheduling:
                self.dictOutput_Scheduling[key][i] = self.dictOutput_Scheduling[key][i].getValue()
        

        #self.dictOutput_Scheduling['moleRatioH2_CO2_Synthesisgas'] = []
        #self.dictOutput_Scheduling['moleRatioH2_CO2_Synthesisgas']
        #for i in self.arrTime[1:]:
        #    self.dictOutput_Scheduling['moleRatioH2_CO2_Synthesisgas'].append(self.dictOutput_Scheduling['moleFractionH2SynthesisgasIn'][i] / self.dictOutput_Scheduling['moleFractionCO2SynthesisgasIn'][i])

        self.dictOutput_Sim = copy.deepcopy(self.dictOutput_Scheduling)
        for key in self.dictOutput_Sim:
            del self.dictOutput_Sim[key][self.param.param['controlParameters']['numTimeStepsToSimulate']:]

        resultOpt.dictResult['output_Scheduling'] = self.dictOutput_Scheduling
        resultOpt.dictResult['output_Sim'] = self.dictOutput_Sim


    def funcCalculateCosts(self, resultOpt, cm, elec, pv, wt, pp, ci):

        # Costs
        self.dictCosts['methanol'] = -np.sum(np.array(self.dictOutput_Scheduling['massFlowMethanolOut']) * self.param.param['prices']['methanol'])
        self.dictCosts['powerBought'] = np.sum(np.dot(self.param.param['prices']['power'], resultOpt.dictResult['input']['powerBought']))
        self.dictCosts['carbonIntensity'] = np.sum(np.dot(self.param.param['carbonIntensity']['carbonIntensity'], resultOpt.dictResult['input']['powerBought']))
        self.dictCosts['powerBatterySold'] = -np.sum(self.param.param['prices']['powerSold'] * np.array(resultOpt.dictResult['input']['actualPowerOutBatterySold']))
        
        self.dictCosts['all'] = sum(self.dictCosts.values())

        
        # Save the data in result
        resultOpt.dictResult['costs'] = self.dictCosts