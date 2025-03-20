#!/usr/bin/env python3.10

from characteristic_fields import *

import gurobipy as gp
from gurobipy import GRB
from gurobipy import *
import os
import pickle
import scipy.io


class Optimization_Model():

    def __init__(self, param):
        self.funcUpdate(param)


    def funcUpdate(self, param):
        self.param = param
        self.arrTime = list(range(0,self.param.param['controlParameters']['numberOfTimeSteps']+1))

        self.arrTime = [0,1,2,3,4,5,6,7,8,9,10]


    def funcCreateOptimizationModel(self, cm, elec, pv, pp, ci):
        self.m = gp.Model('ptm')
        self.m.ModelSense = GRB.MINIMIZE
        self.funcCreateVariables(cm, elec, pv, pp, ci)

        self.funcSetInitialValues(cm, elec, pv, pp, ci)
        self.funcCreateConstraints(cm, elec, pv, pp, ci)
        self.funcCreateCostFunction(cm, elec, pv, pp, ci)

        self.m.update()


    def funcRunOptimization(self):
        self.m.Params.TimeLimit = self.param.param['controlParameters']['timeLimit']
        self.m.Params.MIPGap = self.param.param['controlParameters']['optimalityGap']
        self.m.Params.LogToConsole = 1
        if self.param.param['controlParameters']['testFeasibility'] == True:
            self.m.computeIIS()
            self.m.write("model.ilp")
        self.m.optimize()



    ########## Initial Values ##########
    def funcSetInitialValues(self, cm, elec, pv, pp, ci):
        pass

    ########## Variables ##########
    def funcCreateVariables(self, cm, elec, pv, pp, ci):
        

        self.OptVarLengthTimeSteps = self.m.addVars(self.arrTime,[0,1,2],vType=GRB.CONTINUOUS)

        self.OptVarOperationPointCO2CAP_SYN = self.m.addVars(self.arrTime,cm.arrOperationPointsCO2CAP_SYN, vtype=GRB.BINARY)
        self.OptVarOperationPointDIS = self.m.addVars(self.arrTime,cm.arrOperationPointsDIS, vtype=GRB.BINARY)

        self.OptVarCurrentStateCO2CAP_SYN = self.m.addVars(self.arrTime,[0,1,2,3,4], vtype=GRB.BINARY)
        self.OptVarCurrentStateDIS = self.m.addVars(self.arrTime,[0,1,2,3,4], vtype=GRB.BINARY)
        self.OptVarCurrentStateSwitchCO2CAP_SYN = self.m.addVars(self.arrTime,[0,1,2,3,4],[0,1,2,3,4],vtype=GRB.BINARY)
        self.OptVarCurrentStateSwitchDIS = self.m.addVars(self.arrTime,[0,1,2,3,4],[0,1,2,3,4],vtype=GRB.BINARY)

        self.OptVarModeElectrolyser = self.m.addVars(self.arrTime,self.param.param['electrolyser']['numberOfEnapterModules'],4, vtype=GRB.BINARY)
        
        self.OptVarUsageOfPV = self.m.addVars(self.arrTime,lb=0.0,ub=1000,vtype=GRB.CONTINUOUS)

        #self.OptVarPowerInBatteryBought = self.m.addVars(self.arrTime,lb=self.param.param['battery']['minChargeRate'],ub=self.param.param['battery']['maxChargeRate'], vtype=GRB.CONTINUOUS)

        self.OptVarPowerInBatteryPV = self.m.addVars(self.arrTime,lb=self.param.param['battery']['minChargeRate'],ub=GRB.INFINITY, vtype=GRB.CONTINUOUS)
        self.OptVarPowerInBatteryBought = self.m.addVars(self.arrTime,lb=self.param.param['battery']['minChargeRate'],ub=GRB.INFINITY, vtype=GRB.CONTINUOUS)
        self.OptVarPowerOutBattery = self.m.addVars(self.arrTime,lb=self.param.param['battery']['minDischargeRate'],ub=GRB.INFINITY, vtype=GRB.CONTINUOUS)
        self.OptVarPowerOutBatterySold = self.m.addVars(self.arrTime,lb=self.param.param['battery']['minDischargeRate'],ub=GRB.INFINITY, vtype=GRB.CONTINUOUS)

        self.OptVarActualPowerInBatteryPV = self.m.addVars(self.arrTime,lb=0,ub=GRB.INFINITY, vtype=GRB.CONTINUOUS)
        self.OptVarActualPowerInBatteryBought = self.m.addVars(self.arrTime,lb=0,ub=GRB.INFINITY, vtype=GRB.CONTINUOUS)
        self.OptVarActualPowerOutBattery = self.m.addVars(self.arrTime,lb=0,ub=GRB.INFINITY, vtype=GRB.CONTINUOUS)
        self.OptVarActualPowerOutBatterySold = self.m.addVars(self.arrTime,lb=0,ub=GRB.INFINITY, vtype=GRB.CONTINUOUS)

        self.OptVarIndicatorBatteryCharging1 = self.m.addVars(self.arrTime,vtype=GRB.BINARY)
        self.OptVarIndicatorBatteryDischarging1 = self.m.addVars(self.arrTime,vtype=GRB.BINARY)

        self.OptVarIndicatorBatteryCharging2 = self.m.addVars(self.arrTime,vtype=GRB.BINARY)
        self.OptVarIndicatorBatteryDischarging2 = self.m.addVars(self.arrTime,vtype=GRB.BINARY)



    ########## Cost function ##########
    def funcCreateCostFunction(self, cm, elec, pv, pp, ci):
        fTimeStep = self.param.param['controlParameters']['timeStep']
        
        if self.param.param['controlParameters']['objectiveFunction'] == 1:
            self.m.setObjective(0 
                + gp.quicksum(self.param.param['prices']['power'][i] * self.OptVarPowerBought[i] for i in self.arrTime))
            
        if self.param.param['controlParameters']['objectiveFunction'] == 2:
            self.m.setObjective(0
            + gp.quicksum(self.param.param['carbonIntensity']['carbonIntensity'][i] * self.OptVarPowerBought[i] / 1000  * fTimeStep for i in self.arrTime))
        
        if self.param.param['controlParameters']['objectiveFunction'] == 3:
            self.m.setObjective(0 
                + gp.quicksum(-cm.massFlowMethanolOut[(j)] * self.OptVarOperationPointDIS[(t,j)] * fTimeStep for t in self.arrTime for j in cm.arrOperationPointsDIS))
        

    ########## Extract information from adaptation ##########
    def funcExtractInformationFromAdaptation(self, cm, elec, pv, pp, ci):
        fTimeStep = self.param.param['controlParameters']['timeStep']


    ########## Check for feasibility of operation points ##########
    def funcCheckForFeasibility(self, operationPoint, idxCharMap):
        bIsFeasible = False
            

        return bIsFeasible 


    ########## Constraints ##########
    def funcCreateConstraints(self, cm, elec, pv, pp, ci):
        fTimeStep = self.param.param['controlParameters']['timeStep']
        numSubprocesses = [0,1]

        self.m.addConstrs(
            (gp.quicksum(self.OptVarLengthTimeSteps[(t,i)] for t in self.arrTime) == 120 for i in numSubprocesses), "Time step total length")
        
        self.m.addConstrs(
            (self.OptVarLengthTimeSteps[(t,i)] > 0.167 for t in self.arrTime for i in numSubprocesses), "Time step length") # 10 Minuten
          
                
        if self.param.param['controlParameters']['benchmark'] == True:
            # Minimum amount of methanol which has to be produced
            self.m.addConstr(
                (gp.quicksum(cm.massFlowMethanolOut[(j)] * self.OptVarOperationPointDIS[(t,j)] * self.OptVarCurrentStateDIS[(t,3)] * self.OptVarLengthTimeSteps[(t,1)] for j in cm.arrOperationPointsDIS for t in self.arrTime) >= self.param.param['production']['minMethanolBenchmark']), "Minimum amount methanol produced benchmark")

            if self.param.param['controlParameters']['transitionConstraints'] == True:
                self.m.addConstr(
                    (self.OptVarCurrentStateCO2CAP_SYN[(1,1)] == 1), "Benchmark operation point CO2-Capture and synthesis 1")
                self.m.addConstr(
                    (self.OptVarLengthTimeSteps[(1,0)] == self.param.param['constraints']['transitionTimes']['minStayTimeCO2CAP_SYN_Startup'][0]), "Benchmark operation point CO2-Capture and synthesis 1 time")
                self.m.addConstrs(
                    (self.OptVarCurrentStateCO2CAP_SYN[(t,3)] == 1 for t in self.arrTime[2:]), "Benchmark operation point CO2-Capture and synthesis 2")


                self.m.addConstrs(
                    (self.OptVarCurrentStateDIS[(1,1)] == 1), "Benchmark operation point Distillation 1")
                self.m.addConstr(
                    (self.OptVarLengthTimeSteps[(1,1)] == self.param.param['constraints']['transitionTimes']['minStayTimeDIS_Startup'][0]), "Benchmark operation point Distillation 1 time")
                self.m.addConstrs(
                    (self.OptVarCurrentStateDIS[(t,3)] == 1 for t in self.arrTime[2:]), "Benchmark operation point Distillation 2")        

                # The same operation point for absorption and desorption for every time step
                self.m.addConstrs(
                    (self.OptVarOperationPointCO2CAP_SYN[(t-1,j)] == self.OptVarOperationPointCO2CAP_SYN[(t,j)] for t in self.arrTime[3:] for j in cm.arrOperationsPointsCO2CAP_SYN[4:]), "Benchmark operation point CO2-Capture and synthesis 3")
                # The same operation point for distillation for every time step
                self.m.addConstrs(
                    (self.OptVarOperationPointDIS[(t-1,j)] == self.OptVarOperationPointDIS[(t,j)] for t in self.arrTime[3:] for j in cm.arrOperationPointsDIS[4:]), "Benchmark operation point Distillation 3")
                # The same power in electrolyser for every time step
                self.m.addConstrs(
                        (self.OptVarPowerElectrolyser[(t-1,n)] == self.OptVarPowerElectrolyser[(t,n)] for t in self.arrTime[2:] for n in elec.arrEnapterModules), "Benchmark power electrolyser")
                self.m.addConstrs(
                    (self.OptVarModeElectrolyser[(t-1,n,m)] == self.OptVarModeElectrolyser[(t,n,m)] for t in self.arrTime[3:] for n in elec.arrEnapterModules for m in elec.arrModes), "Benchmark power electrolyser")
            else:
                # The same operation point for absorption and desorption for every time step
                self.m.addConstrs(
                        (self.OptVarOperationPointCO2CAP_SYN[(t-1,j)] == self.OptVarOperationPointCO2CAP_SYN[(t,j)] for t in self.arrTime[2:] for j in cm.arrOperationPointsCO2CAP_SYN[4:]), "Benchmark operation point CO2-Capture and synthesis 3")
                # The same operation point for distillation for every time step
                self.m.addConstrs(
                        (self.OptVarOperationPointDIS[(t-1,j)] == self.OptVarOperationPointDIS[(t,j)] for t in self.arrTime[2:] for j in cm.arrOperationPointsDIS[4:]), "Benchmark operation point Distillation 3")
                # The same power in electrolyser for every time step
                self.m.addConstrs(
                    (self.OptVarPowerElectrolyser[(t-1,n)] == self.OptVarPowerElectrolyser[(t,n)] for t in self.arrTime[2:] for n in elec.arrEnapterModules), "Benchmark power electrolyser")
                self.m.addConstrs(
                    (self.OptVarModeElectrolyser[(t-1,n,m)] == self.OptVarModeElectrolyser[(t,n,m)] for t in self.arrTime[3:] for n in elec.arrEnapterModules for m in elec.arrModes), "Benchmark power electrolyser")


 
        if self.param.param['controlParameters']['benchmark'] == False:
            if self.param.param['controlParameters']['sameOutputAsBenchmark'] == False:

                #if self.param.param['controlParameters']['currStartTimeLastOptHorizon'] > 0:
                #    self.m.addConstr(
                #        (gp.quicksum(cm.massFlowMethanolOut[(j)] * self.OptVarOperationPointDIS[(t,j)] * self.OptVarCurrentStateDIS[(t,3)] * self.OptVarLengthTimeSteps[(t,1)] for j in cm.arrOperationPointsDIS[4:] for t in self.arrTime) 
                #        - gp.quicksum(cm.massFlowMethanolOut[(j)] * self.OptVarOperationPointDIS[(t,j)] * self.OptVarCurrentStateDIS[(t,3)] * self.OptVarLengthTimeSteps[(t,1)] for j in cm.arrOperationPointsDIS[4:] for t in self.arrTime[-self.param.param['controlParameters']['currStartTimeLastOptHorizon']:]) >= self.param.param['production']['minMethanolOpt'] - self.param.param['controlParameters']['prodMethanolLastTimeInterval']), "Minimum amount methanol produced 1")
                
                self.m.addConstr(
                    (gp.quicksum(cm.massFlowMethanolOut[(j)] * self.OptVarOperationPointDIS[(t,j)] * self.OptVarCurrentStateDIS[(t,3)] * self.OptVarLengthTimeSteps[(t,1)] for j in cm.arrOperationPointsDIS[4:] for t in self.arrTime) >= self.param.param['production']['minMethanolOpt']), "Minimum amount methanol produced 2")     
            
            else:
                self.m.addConstr(
                    (gp.quicksum(cm.massFlowMethanolOut[(j)] * self.OptVarOperationPointDIS[(t,j)] * self.OptVarCurrentStateDIS[(t,3)] * self.OptVarLengthTimeSteps[(t,1)] for j in cm.arrOperationPointsDIS for t in self.arrTime) <= self.param.param['production']['methanol']*1.01), "Amount methanol produced is same as benchmark upper bound") 
                self.m.addConstr(
                    (gp.quicksum(cm.massFlowMethanolOut[(j)] * self.OptVarOperationPointDIS[(t,j)] * self.OptVarCurrentStateDIS[(t,3)] * self.OptVarLengthTimeSteps[(t,1)] for j in cm.arrOperationPointsDIS for t in self.arrTime) >= self.param.param['production']['methanol']), "Amount methanol produced is same as benchmark lower bound")    







        if self.param.param['controlParameters']['transitionConstraints'] == True:
            ## Minimum stay time per mode
            self.m.addConstrs(
                (self.OptVarCurrentStateSwitchCO2CAP_SYN[(t,k,0)] * self.OptVarLengthTimeSteps[(t,0)] >= self.param.param['constraints']['transitionTimes']['minStayTimeCO2CAP_SYN_Off'][k] * self.OptVarCurrentStateSwitchCO2CAP_SYN[(t,k,0)] for t in self.arrTime[1:] for k in [0,1,2,3,4]), "Mode switching min stay constraint CO2CAP_SYN off")
            self.m.addConstrs(
                (self.OptVarCurrentStateSwitchCO2CAP_SYN[(t,k,1)] * self.OptVarLengthTimeSteps[(t,0)] >= self.param.param['constraints']['transitionTimes']['minStayTimeCO2CAP_SYN_Startup'][k] * self.OptVarCurrentStateSwitchCO2CAP_SYN[(t,k,1)] for t in self.arrTime[1:] for k in [0,1,2,3,4]), "Mode switching min stay constraint CO2CAP_SYN startup")
            self.m.addConstrs(
                (self.OptVarCurrentStateSwitchCO2CAP_SYN[(t,k,2)] * self.OptVarLengthTimeSteps[(t,0)] >= self.param.param['constraints']['transitionTimes']['minStayTimeCO2CAP_SYN_Standby'][k] * self.OptVarCurrentStateSwitchCO2CAP_SYN[(t,k,2)] for t in self.arrTime[1:] for k in [0,1,2,3,4]), "Mode switching min stay constraint CO2CAP_SYN standby")
            self.m.addConstrs(
                (self.OptVarCurrentStateSwitchCO2CAP_SYN[(t,k,3)] * self.OptVarLengthTimeSteps[(t,0)] >= self.param.param['constraints']['transitionTimes']['minStayTimeCO2CAP_SYN_On'][k] * self.OptVarCurrentStateSwitchCO2CAP_SYN[(t,k,3)] for t in self.arrTime[1:] for k in [0,1,2,3,4]), "Mode switching min stay constraint CO2CAP_SYN on")
            self.m.addConstrs(
                (self.OptVarCurrentStateSwitchCO2CAP_SYN[(t,k,4)] * self.OptVarLengthTimeSteps[(t,0)] >= self.param.param['constraints']['transitionTimes']['minStayTimeCO2CAP_SYN_Shutdown'][k] * self.OptVarCurrentStateSwitchCO2CAP_SYN[(t,k,4)] for t in self.arrTime[1:] for k in [0,1,2,3,4]), "Mode switching min stay constraint CO2CAP_SYN shutdown")

            self.m.addConstrs(
                (self.OptVarCurrentStateSwitchDIS[(t,k,0)] * self.OptVarLengthTimeSteps[(t,1)] >= self.param.param['constraints']['transitionTimes']['minStayTimeDIS_Off'][k] * self.OptVarCurrentStateSwitchDIS[(t,k,0)] for t in self.arrTime[1:] for k in [0,1,2,3,4]), "Mode switching min stay constraint DIS off")
            self.m.addConstrs(
                (self.OptVarCurrentStateSwitchDIS[(t,k,1)] * self.OptVarLengthTimeSteps[(t,1)] >= self.param.param['constraints']['transitionTimes']['minStayTimeDIS_Startup'][k] * self.OptVarCurrentStateSwitchDIS[(t,k,1)] for t in self.arrTime[1:] for k in [0,1,2,3,4]), "Mode switching min stay constraint DIS startup")
            self.m.addConstrs(
                (self.OptVarCurrentStateSwitchDIS[(t,k,2)] * self.OptVarLengthTimeSteps[(t,1)] >= self.param.param['constraints']['transitionTimes']['minStayTimeDIS_Standby'][k] * self.OptVarCurrentStateSwitchDIS[(t,k,2)] for t in self.arrTime[1:] for k in [0,1,2,3,4]), "Mode switching min stay constraint DIS standby")
            self.m.addConstrs(
                (self.OptVarCurrentStateSwitchDIS[(t,k,3)] * self.OptVarLengthTimeSteps[(t,1)] >= self.param.param['constraints']['transitionTimes']['minStayTimeDIS_On'][k] * self.OptVarCurrentStateSwitchDIS[(t,k,3)] for t in self.arrTime[1:] for k in [0,1,2,3,4]), "Mode switching min stay constraint DIS on")
            self.m.addConstrs(
                (self.OptVarCurrentStateSwitchDIS[(t,k,4)] * self.OptVarLengthTimeSteps[(t,1)] >= self.param.param['constraints']['transitionTimes']['minStayTimeDIS_Shutdown'][k] * self.OptVarCurrentStateSwitchDIS[(t,k,4)] for t in self.arrTime[1:] for k in [0,1,2,3,4]), "Mode switching min stay constraint DIS shutdown")
           
            ## Maximum stay time per mode

            """
            for j in [1,2,3,4]:
                self.m.addConstrs(
                    ((1 - self.OptVarCurrentStateCO2CAP_SYN[(t+self.param.param['constraints']['transitionTimes']['maxStayTimeCO2CAP_SYN_Off'][j]+1,0)]) >= self.OptVarCurrentStateSwitchCO2CAP_SYN[(t,j,0)] - gp.quicksum(self.OptVarCurrentStateSwitchCO2CAP_SYN[(t+i,k,0)] for i in range(self.param.param['constraints']['transitionTimes']['minStayTimeCO2CAP_SYN_Off'][j],self.param.param['constraints']['transitionTimes']['maxStayTimeCO2CAP_SYN_Off'][j]) for k in [1,2,3,4]) for t in self.arrTime[1:-(self.param.param['constraints']['transitionTimes']['maxStayTimeCO2CAP_SYN_Off'][j]+1)]), "Mode switching max stay constraint CO2CAP_SYN off")
                self.m.addConstrs(
                    ((1 - self.OptVarCurrentStateDIS[(t+self.param.param['constraints']['transitionTimes']['maxStayTimeDIS_Off'][j]+1,0)]) >= self.OptVarCurrentStateSwitchDIS[(t,j,0)] - gp.quicksum(self.OptVarCurrentStateSwitchDIS[(t+i,k,0)] for i in range(self.param.param['constraints']['transitionTimes']['minStayTimeDIS_Off'][j],self.param.param['constraints']['transitionTimes']['maxStayTimeDIS_Off'][j]) for k in [1,2,3,4]) for t in self.arrTime[1:-(self.param.param['constraints']['transitionTimes']['maxStayTimeDIS_Off'][j]+1)]), "Mode switching max stay constraint DIS off")

            for j in [0,2,3,4]:
                self.m.addConstrs(
                    ((1 - self.OptVarCurrentStateCO2CAP_SYN[(t+self.param.param['constraints']['transitionTimes']['maxStayTimeCO2CAP_SYN_Startup'][j]+1,1)]) >= self.OptVarCurrentStateSwitchCO2CAP_SYN[(t,j,1)] - gp.quicksum(self.OptVarCurrentStateSwitchCO2CAP_SYN[(t+i,k,1)] for i in range(self.param.param['constraints']['transitionTimes']['minStayTimeCO2CAP_SYN_Startup'][j],self.param.param['constraints']['transitionTimes']['maxStayTimeCO2CAP_SYN_Startup'][j]) for k in [0,2,3,4]) for t in self.arrTime[1:-(self.param.param['constraints']['transitionTimes']['maxStayTimeCO2CAP_SYN_Startup'][j]+1)]), "Mode switching max stay constraint CO2CAP_SYN startup")
                self.m.addConstrs(
                    ((1 - self.OptVarCurrentStateDIS[(t+self.param.param['constraints']['transitionTimes']['maxStayTimeDIS_Startup'][j]+1,1)]) >= self.OptVarCurrentStateSwitchDIS[(t,j,1)] - gp.quicksum(self.OptVarCurrentStateSwitchDIS[(t+i,k,1)] for i in range(self.param.param['constraints']['transitionTimes']['minStayTimeDIS_Startup'][j],self.param.param['constraints']['transitionTimes']['maxStayTimeDIS_Startup'][j]) for k in [0,2,3,4]) for t in self.arrTime[1:-(self.param.param['constraints']['transitionTimes']['maxStayTimeDIS_Startup'][j]+1)]), "Mode switching max stay constraint DIS startup")

            for j in [0,1,3,4]:
                self.m.addConstrs(
                    ((1 - self.OptVarCurrentStateCO2CAP_SYN[(t+self.param.param['constraints']['transitionTimes']['maxStayTimeCO2CAP_SYN_Standby'][j]+1,2)]) >= self.OptVarCurrentStateSwitchCO2CAP_SYN[(t,j,2)] - gp.quicksum(self.OptVarCurrentStateSwitchCO2CAP_SYN[(t+i,k,2)] for i in range(self.param.param['constraints']['transitionTimes']['minStayTimeCO2CAP_SYN_Standby'][j],self.param.param['constraints']['transitionTimes']['maxStayTimeCO2CAP_SYN_Standby'][j]) for k in [0,1,3,4]) for t in self.arrTime[1:-(self.param.param['constraints']['transitionTimes']['maxStayTimeCO2CAP_SYN_Standby'][j]+1)]), "Mode switching max stay constraint CO2CAP_SYN standby")  
                self.m.addConstrs(
                    ((1 - self.OptVarCurrentStateDIS[(t+self.param.param['constraints']['transitionTimes']['maxStayTimeDIS_Standby'][j]+1,2)]) >= self.OptVarCurrentStateSwitchDIS[(t,j,2)] - gp.quicksum(self.OptVarCurrentStateSwitchDIS[(t+i,k,2)] for i in range(self.param.param['constraints']['transitionTimes']['minStayTimeDIS_Standby'][j],self.param.param['constraints']['transitionTimes']['maxStayTimeDIS_Standby'][j]) for k in [0,1,3,4]) for t in self.arrTime[1:-(self.param.param['constraints']['transitionTimes']['maxStayTimeDIS_Off'][j]+1)]), "Mode switching max stay constraint DIS standby")

            for j in [0,1,2,4]:
                self.m.addConstrs(
                    ((1 - self.OptVarCurrentStateCO2CAP_SYN[(t+self.param.param['constraints']['transitionTimes']['maxStayTimeCO2CAP_SYN_On'][j]+1,3)]) >= self.OptVarCurrentStateSwitchCO2CAP_SYN[(t,j,3)] - gp.quicksum(self.OptVarCurrentStateSwitchCO2CAP_SYN[(t+i,k,3)] for i in range(self.param.param['constraints']['transitionTimes']['minStayTimeCO2CAP_SYN_On'][j],self.param.param['constraints']['transitionTimes']['maxStayTimeCO2CAP_SYN_On'][j]) for k in [0,1,2,4]) for t in self.arrTime[1:-(self.param.param['constraints']['transitionTimes']['maxStayTimeCO2CAP_SYN_On'][j]+1)]), "Mode switching max stay constraint CO2CAP_SYN on")
                self.m.addConstrs(
                    ((1 - self.OptVarCurrentStateDIS[(t+self.param.param['constraints']['transitionTimes']['maxStayTimeDIS_On'][j]+1,3)]) >= self.OptVarCurrentStateSwitchDIS[(t,j,3)] - gp.quicksum(self.OptVarCurrentStateSwitchDIS[(t+i,k,3)] for i in range(self.param.param['constraints']['transitionTimes']['minStayTimeDIS_On'][j],self.param.param['constraints']['transitionTimes']['maxStayTimeDIS_On'][j]) for k in [0,1,2,4]) for t in self.arrTime[1:-(self.param.param['constraints']['transitionTimes']['maxStayTimeDIS_On'][j]+1)]), "Mode switching max stay constraint DIS on")
                
            for j in [0,1,2,3]:
                self.m.addConstrs(
                    ((1 - self.OptVarCurrentStateCO2CAP_SYN[(t+self.param.param['constraints']['transitionTimes']['maxStayTimeCO2CAP_SYN_Shutdown'][j]+1,4)]) >= self.OptVarCurrentStateSwitchCO2CAP_SYN[(t,j,4)] - gp.quicksum(self.OptVarCurrentStateSwitchCO2CAP_SYN[(t+i,k,4)] for i in range(self.param.param['constraints']['transitionTimes']['minStayTimeCO2CAP_SYN_Shutdown'][j],self.param.param['constraints']['transitionTimes']['maxStayTimeCO2CAP_SYN_Shutdown'][j]) for k in [0,1,2,4]) for t in self.arrTime[1:-(self.param.param['constraints']['transitionTimes']['maxStayTimeCO2CAP_SYN_Shutdown'][j]+1)]), "Mode switching max stay constraint CO2CAP_SYN shutdown")               
                self.m.addConstrs(
                    ((1 - self.OptVarCurrentStateDIS[(t+self.param.param['constraints']['transitionTimes']['maxStayTimeDIS_Shutdown'][j]+1,4)]) >= self.OptVarCurrentStateSwitchDIS[(t,j,4)] - gp.quicksum(self.OptVarCurrentStateSwitchDIS[(t+i,k,4)] for i in range(self.param.param['constraints']['transitionTimes']['minStayTimeDIS_Shutdown'][j],self.param.param['constraints']['transitionTimes']['maxStayTimeDIS_Shutdown'][j]) for k in [0,1,2,3]) for t in self.arrTime[1:-(self.param.param['constraints']['transitionTimes']['maxStayTimeDIS_Shutdown'][j]+1)]), "Mode switching max stay constraint DIS shutdown")               
            """

            ## Mode switching constraints
            # CO2-Capture and synthesis
            self.m.addConstrs(
                (self.OptVarCurrentStateCO2CAP_SYN[(t-1,i)] >= self.OptVarCurrentStateSwitchCO2CAP_SYN[(t,i,j)] for t in self.arrTime[1:] for i in range(0,5) for j in range(0,5)), "Mode switching CO2-Capture and synthesis 1")
            self.m.addConstrs(
                (self.OptVarCurrentStateCO2CAP_SYN[(t,j)] >= self.OptVarCurrentStateSwitchCO2CAP_SYN[(t,i,j)] for t in self.arrTime[0:] for i in range(0,5) for j in range(0,5)), "Mode switching CO2-Capture and synthesis 2")
            self.m.addConstrs(
                (self.OptVarCurrentStateCO2CAP_SYN[(t-1,i)] + self.OptVarCurrentStateCO2CAP_SYN[(t,j)] - 1 <= self.OptVarCurrentStateSwitchCO2CAP_SYN[(t,i,j)] for t in self.arrTime[1:] for i in range(0,5) for j in range(0,5)), "Mode switching CO2-Capture and synthesis 3")

            # DIS 
            self.m.addConstrs(
                (self.OptVarCurrentStateDIS[(t-1,i)] >= self.OptVarCurrentStateSwitchDIS[(t,i,j)] for t in self.arrTime[1:] for i in range(0,5) for j in range(0,5)), "Mode switching DIS 1")
            self.m.addConstrs(
                (self.OptVarCurrentStateDIS[(t,j)] >= self.OptVarCurrentStateSwitchDIS[(t,i,j)] for t in self.arrTime[0:] for i in range(0,5) for j in range(0,5)), "Mode switching DIS 2")
            self.m.addConstrs(
                (self.OptVarCurrentStateDIS[(t-1,i)] + self.OptVarCurrentStateDIS[(t,j)] - 1 <= self.OptVarCurrentStateSwitchDIS[(t,i,j)] for t in self.arrTime[1:] for i in range(0,5) for j in range(0,5)), "Mode switching DIS 3")

            
            # Forbidden transitions
            self.m.addConstrs(
                (self.OptVarCurrentStateSwitchCO2CAP_SYN[(t,0,j)] == 0 for t in self.arrTime for j in [2,3,4]), 'Forbidden transition from state off CO2CAP_SYN')
            self.m.addConstrs(
                (self.OptVarCurrentStateSwitchCO2CAP_SYN[(t,1,j)] == 0 for t in self.arrTime for j in [0,4]), 'Forbidden transition from state startup CO2CAP_SYN')
            self.m.addConstrs(
                (self.OptVarCurrentStateSwitchCO2CAP_SYN[(t,2,j)] == 0 for t in self.arrTime for j in [0,3]), 'Forbidden transition from state standby CO2CAP_SYN')
            self.m.addConstrs(
                (self.OptVarCurrentStateSwitchCO2CAP_SYN[(t,3,j)] == 0 for t in self.arrTime for j in [0,1,2]), 'Forbidden transition from state on CO2CAP_SYN')
            self.m.addConstrs(
                (self.OptVarCurrentStateSwitchCO2CAP_SYN[(t,4,j)] == 0 for t in self.arrTime for j in [1,3]), 'Forbidden transition from state shutdown CO2CAP_SYN')
            
            self.m.addConstrs(
                (self.OptVarCurrentStateSwitchDIS[(t,0,j)] == 0 for t in self.arrTime for j in [2,3,4]), 'Forbidden transition from state off DIS')
            self.m.addConstrs(
                (self.OptVarCurrentStateSwitchDIS[(t,1,j)] == 0 for t in self.arrTime for j in [0,4]), 'Forbidden transition from state startup DIS')
            self.m.addConstrs(
                (self.OptVarCurrentStateSwitchDIS[(t,2,j)] == 0 for t in self.arrTime for j in [0,3]), 'Forbidden transition from state standby DIS')
            self.m.addConstrs(
                (self.OptVarCurrentStateSwitchDIS[(t,3,j)] == 0 for t in self.arrTime for j in [0,1,2]), 'Forbidden transition from state on DIS')
            self.m.addConstrs(
                (self.OptVarCurrentStateSwitchDIS[(t,4,j)] == 0 for t in self.arrTime for j in [1,3]), 'Forbidden transition from state shutdown DIS')
            

            ## Transitional states
            self.m.addConstrs(
                (self.OptVarCurrentStateSwitchCO2CAP_SYN[(t-1,2,4)] == self.OptVarCurrentStateSwitchCO2CAP_SYN[(t,4,0)] for t in self.arrTime), 'Forbidden transition from state standby CO2CAP SYN')
            self.m.addConstrs(
                (self.OptVarCurrentStateSwitchDIS[(t-1,2,4)] == self.OptVarCurrentStateSwitchDIS[(t,4,0)] for t in self.arrTime), 'Forbidden transition from state standby DIS')
    

        ## Operating points per case
        self.m.addConstrs(
            (self.OptVarCurrentStateCO2CAP_SYN[(t,0)] == self.OptVarOperationPointCO2CAP_SYN[(t,0)] for t in self.arrTime), 'One operation point in case off for CO2CAP_SYN')
        self.m.addConstrs(
            (self.OptVarCurrentStateDIS[(t,0)] == self.OptVarOperationPointDIS[(t,0)] for t in self.arrTime), 'One operation point in case off for DIS')

        self.m.addConstrs(
            (self.OptVarCurrentStateCO2CAP_SYN[(t,1)] == self.OptVarOperationPointCO2CAP_SYN[(t,1)] for t in self.arrTime), 'One operation point in case startup for CO2CAP_SYN')
        self.m.addConstrs(
            (self.OptVarCurrentStateDIS[(t,1)] == self.OptVarOperationPointDIS[(t,1)] for t in self.arrTime), 'One operation point in case startup for DIS')

        self.m.addConstrs(
            (self.OptVarCurrentStateCO2CAP_SYN[(t,2)] == self.OptVarOperationPointCO2CAP_SYN[(t,2)] for t in self.arrTime), 'One operation point in case standby for CO2CAP_SYN')
        self.m.addConstrs(
            (self.OptVarCurrentStateDIS[(t,2)] == self.OptVarOperationPointDIS[(t,2)] for t in self.arrTime), 'One operation point in case standby for DIS')
        
        self.m.addConstrs(
            (self.OptVarCurrentStateCO2CAP_SYN[(t,3)] == gp.quicksum(self.OptVarOperationPointCO2CAP_SYN[(t,j)] for j in cm.arrOperationPointsCO2CAP_SYN[4:]) for t in self.arrTime), 'One operation point in case on for CO2CAP_SYN')
        self.m.addConstrs(
            (self.OptVarCurrentStateDIS[(t,3)] == gp.quicksum(self.OptVarOperationPointDIS[(t,j)] for j in cm.arrOperationPointsDIS[4:]) for t in self.arrTime), 'One operation point in case on for DIS')
        
        self.m.addConstrs(
            (self.OptVarCurrentStateCO2CAP_SYN[(t,4)] == self.OptVarOperationPointCO2CAP_SYN[(t,3)] for t in self.arrTime), 'One operation point in case shutdown for CO2CAP_SYN')
        self.m.addConstrs(
            (self.OptVarCurrentStateDIS[(t,4)] == self.OptVarOperationPointDIS[(t,3)] for t in self.arrTime), 'One operation point in case shutdown for DIS')
        



        ## PV considered
        if self.param.param['controlParameters']['considerPV'] == False:
            self.m.addConstrs(
                self.OptVarUsageOfPV[t] == 0 for t in self.arrTime)

        ## Battery considered
        if self.param.param['controlParameters']['considerBattery'] == False:
            self.m.addConstrs(
                self.OptVarActualPowerInBatteryPV[t] == 0 for t in self.arrTime)
            self.m.addConstrs(
                self.OptVarActualPowerInBatteryBought[t] == 0 for t in self.arrTime)
            self.m.addConstrs(
                self.OptVarActualPowerOutBattery[t] == 0 for t in self.arrTime)
            self.m.addConstrs(
                self.OptVarActualPowerOutBatterySold[t] == 0 for t in self.arrTime)
            self.m.addConstrs(
                self.OptVarIndicatorBatteryCharging1[t] == 0 for t in self.arrTime)
            self.m.addConstrs(
                self.OptVarIndicatorBatteryDischarging1[t] == 0 for t in self.arrTime)
            self.m.addConstrs(
                self.OptVarIndicatorBatteryCharging2[t] == 0 for t in self.arrTime)
            self.m.addConstrs(
                self.OptVarIndicatorBatteryDischarging2[t] == 0 for t in self.arrTime)            
        
        
        ## Power Constraints
        # Power from battery and PV and grid to electrolyser and components must equal to needed power
        self.m.addConstrs(
            (self.OptVarActualPowerOutBattery[t] * self.param.param['battery']['efficiency'] + self.OptVarUsageOfPV[t] + self.OptVarPowerBought[t] - self.OptVarActualPowerInBatteryBought[t] == 
            gp.quicksum(self.OptVarPowerElectrolyser[(t,n)] * self.OptVarModeElectrolyser[(t,n,3)] * self.OptVarLengthTimeSteps[(t,2)] for n in elec.arrEnapterModules)
            + gp.quicksum(elec.dictPowerElectrolyserMode[(n,m)] * self.OptVarModeElectrolyser[(t,n,m)] * self.OptVarLengthTimeSteps[(t,1)] for n in elec.arrEnapterModules for m in elec.arrModes[:-1])
            + cm.powerPlantComponentsUnit1[0] * self.OptVarOperationPointCO2CAP_SYN[(t,0)] * self.OptVarCurrentStateCO2CAP_SYN[(t,0)] * self.OptVarLengthTimeSteps[(t,0)]
            + cm.powerPlantComponentsUnit1[1] * self.OptVarOperationPointCO2CAP_SYN[(t,1)] * self.OptVarCurrentStateCO2CAP_SYN[(t,1)] * self.OptVarLengthTimeSteps[(t,0)] 
            + cm.powerPlantComponentsUnit1[2] * self.OptVarOperationPointCO2CAP_SYN[(t,2)] * self.OptVarCurrentStateCO2CAP_SYN[(t,2)] * self.OptVarLengthTimeSteps[(t,0)] 
            + gp.quicksum(cm.powerPlantComponentsUnit1[(j)] * self.OptVarOperationPointCO2CAP_SYN[(t,j)] * self.OptVarCurrentStateCO2CAP_SYN[(t,3)] * self.OptVarLengthTimeSteps[(t,0)] for j in cm.arrOperationPointsCO2CAP_SYN[4:])
            + cm.powerPlantComponentsUnit1[3] * self.OptVarOperationPointCO2CAP_SYN[(t,3)] * self.OptVarCurrentStateCO2CAP_SYN[(t,4)] * self.OptVarLengthTimeSteps[(t,0)]
            + cm.powerPlantComponentsUnit2[0] * self.OptVarOperationPointDIS[(t,0)] * self.OptVarCurrentStateDIS[(t,0)] * self.OptVarLengthTimeSteps[(t,1)]
            + cm.powerPlantComponentsUnit2[1] * self.OptVarOperationPointDIS[(t,1)] * self.OptVarCurrentStateDIS[(t,1)] * self.OptVarLengthTimeSteps[(t,1)]
            + cm.powerPlantComponentsUnit2[2] * self.OptVarOperationPointDIS[(t,2)] * self.OptVarCurrentStateDIS[(t,2)] * self.OptVarLengthTimeSteps[(t,1)]
            + gp.quicksum(cm.powerPlantComponentsUnit2[(j)] * self.OptVarOperationPointDIS[(t,j)] * self.OptVarCurrentStateDIS[(t,3)] * self.OptVarLengthTimeSteps[(t,1)] for j in cm.arrOperationPointsDIS[4:])
            + cm.powerPlantComponentsUnit2[3] * self.OptVarOperationPointDIS[(t,3)] * self.OptVarCurrentStateDIS[(t,4)] * self.OptVarLengthTimeSteps[(t,1)]
            for t in self.arrTime[1:]), "Battery output maximum")

        # Power to battery has always to be smaller than power bought
        self.m.addConstrs(
            (self.OptVarActualPowerInBatteryBought[t] <= self.OptVarPowerBought[t] for t in self.arrTime[1:]), "Power to battery has always to be smaller than power bought")
        
        # Power can not be sold and bought at the same time
        self.m.addConstrs(
            (self.OptVarPowerBought[t] * self.OptVarActualPowerOutBatterySold[t] == 0 for t in self.arrTime[1:]), "Power can not be sold and bought at the same time")
        

        
        # Actual power in and out the battery
        self.m.addConstrs(
            (self.OptVarActualPowerInBatteryPV[t] == self.OptVarIndicatorBatteryCharging1[t] * self.OptVarPowerInBatteryPV[t] for t in self.arrTime[1:]), "Battery actual charging power from pv")      
        self.m.addConstrs(
            (self.OptVarActualPowerInBatteryPV[t] <= self.OptVarPowerInBatteryPV[t] - (1 - self.OptVarIndicatorBatteryCharging1[t]) * self.param.param['battery']['minChargeRate'] for t in self.arrTime[1:]), "Battery actual charging power min rate from pv 1")
        self.m.addConstrs(
            (self.OptVarActualPowerInBatteryPV[t] >= self.OptVarPowerInBatteryPV[t] - (1 - self.OptVarIndicatorBatteryCharging1[t]) * self.param.param['battery']['maxChargeRate'] for t in self.arrTime[1:]), "Battery actual charging power min rate from pv 2")
        
        self.m.addConstrs(
            (self.OptVarActualPowerInBatteryBought[t] == self.OptVarIndicatorBatteryCharging2[t] * self.OptVarPowerInBatteryBought[t] for t in self.arrTime[1:]), "Battery actual charging power from power bought")      
        self.m.addConstrs(
            (self.OptVarActualPowerInBatteryBought[t] <= self.OptVarPowerInBatteryBought[t] - (1 - self.OptVarIndicatorBatteryCharging2[t]) * self.param.param['battery']['minChargeRate'] for t in self.arrTime[1:]), "Battery actual charging power min rate from power bought 1")
        self.m.addConstrs(
            (self.OptVarActualPowerInBatteryBought[t] >= self.OptVarPowerInBatteryBought[t] - (1 - self.OptVarIndicatorBatteryCharging2[t]) * self.param.param['battery']['maxChargeRate'] for t in self.arrTime[1:]), "Battery actual charging power min rate from power bought 2")
        
        self.m.addConstrs(
            (self.OptVarActualPowerOutBattery[t] == self.OptVarIndicatorBatteryDischarging1[t] * self.OptVarPowerOutBattery[t] for t in self.arrTime[1:]), "Battery actual discharging power")     
        self.m.addConstrs(
            (self.OptVarActualPowerOutBattery[t] <= self.OptVarPowerOutBattery[t] - (1 - self.OptVarIndicatorBatteryDischarging1[t]) * self.param.param['battery']['minChargeRate'] for t in self.arrTime[1:]), "Battery actual discharging power min rate 1")
        self.m.addConstrs(
            (self.OptVarActualPowerOutBattery[t] >= self.OptVarPowerOutBattery[t] - (1 - self.OptVarIndicatorBatteryDischarging1[t]) * self.param.param['battery']['maxChargeRate'] for t in self.arrTime[1:]), "Battery actual discharging power min rate 2")
        
        self.m.addConstrs(
            (self.OptVarActualPowerOutBatterySold[t] == self.OptVarIndicatorBatteryDischarging2[t] * self.OptVarPowerOutBatterySold[t] for t in self.arrTime[1:]), "Battery actual discharging power from power sold")     
        self.m.addConstrs(
            (self.OptVarActualPowerOutBatterySold[t] <= self.OptVarPowerOutBatterySold[t] - (1 - self.OptVarIndicatorBatteryDischarging2[t]) * self.param.param['battery']['minChargeRate'] for t in self.arrTime[1:]), "Battery actual discharging power min rate from power sold 1")
        self.m.addConstrs(
            (self.OptVarActualPowerOutBatterySold[t] >= self.OptVarPowerOutBatterySold[t] - (1 - self.OptVarIndicatorBatteryDischarging2[t]) * self.param.param['battery']['maxChargeRate'] for t in self.arrTime[1:]), "Battery actual discharging power min rate from power sold 2")
        
        self.m.addConstrs(
            (self.OptVarIndicatorBatteryCharging1[t] + self.OptVarIndicatorBatteryDischarging1[t] <= 1 for t in self.arrTime[1:]), "Battery charging and discharging")
        self.m.addConstrs(
            (self.OptVarIndicatorBatteryCharging1[t] + self.OptVarIndicatorBatteryDischarging2[t] <= 1 for t in self.arrTime[1:]), "Battery charging and discharging") 
        self.m.addConstrs(
            (self.OptVarIndicatorBatteryCharging2[t] + self.OptVarIndicatorBatteryDischarging1[t] <= 1 for t in self.arrTime[1:]), "Battery charging and discharging")
        self.m.addConstrs(
            (self.OptVarIndicatorBatteryCharging2[t] + self.OptVarIndicatorBatteryDischarging2[t] <= 1 for t in self.arrTime[1:]), "Battery charging and discharging")
        
        
        # Charge and discharge rate have to be smaller than maximum rate
        self.m.addConstrs(
            (self.OptVarActualPowerInBatteryBought[t] + self.OptVarActualPowerInBatteryPV[t] <= self.param.param['battery']['maxChargeRate'] for t in self.arrTime), "Battery max charge rate")
        self.m.addConstrs(
            (self.OptVarActualPowerOutBattery[t] + self.OptVarActualPowerOutBatterySold[t] <= self.param.param['battery']['maxDischargeRate'] for t in self.arrTime), "Battery max discharge rate")        

        
        # Power cannot be sold
        if self.param.param['controlParameters']['powerSale'] == False:
            self.m.addConstrs(
                (self.OptVarActualPowerOutBatterySold[t] == 0 for t in self.arrTime[1:]), "No power can be sold")
        # Power cannot be bought
        if self.param.param['controlParameters']['powerPurchase'] == False:
            self.m.addConstrs(
                (self.OptVarPowerBought[t] == 0 for t in self.arrTime[1:]), "Power can not be bought")
        # Peak load capping
        if self.param.param['controlParameters']['peakLoadCapping'] == True:
            self.m.addConstrs(
                (self.OptVarPowerBought[t] <= self.param['peakLoadCapping']['maximumLoad'] for t in self.arrTime[1:]), "Peak load capping")
            

        # Power used from PV and stored in battery from PV must be equal or smaller than power available from PV
        self.m.addConstrs(
            (self.OptVarUsageOfPV[t] + self.OptVarActualPowerInBatteryPV[t] <= self.param.param['pv']['powerAvailable'][t] for t in self.arrTime[1:]), "PV upper bound available")


        ## Minimum operation point/operation mode constraint
        # Exactly one operation point for CO2-Capture and synthesis has to be selected in every time step
        self.m.addConstrs(
            (self.OptVarOperationPointCO2CAP_SYN.sum(t,'*') == 1 for t in self.arrTime), "Exactly one operation point for CO2-Capture and synthesis per time step")
        # Exactly one operation point for distillation has to be selected in every time step
        self.m.addConstrs(
            (self.OptVarOperationPointDIS.sum(t,'*') == 1 for t in self.arrTime), "Exactly one operation point for distillation per time step")
        # Exactly one state of CO2-Capture and synthesis in every time step
        self.m.addConstrs(
            (self.OptVarCurrentStateCO2CAP_SYN.sum(t,'*') == 1 for t in self.arrTime), "Exactly one state for CO2-Capture and synthesis per time step")
        # Exactly one state of distillation in every time step
        self.m.addConstrs(
            (self.OptVarCurrentStateDIS.sum(t,'*') == 1 for t in self.arrTime), "Exactly one state for distillation per time step")    
        # Exactly one operation point for electrolyser has to be selected in every time step
        self.m.addConstrs(
            (gp.quicksum(self.OptVarModeElectrolyser[(t,n,m)] for m in elec.arrModes) == 1 for t in self.arrTime for n in elec.arrEnapterModules), "One operation mode for electrolyser per time period")





        ## Initial time step constraints
        # No operation point for CO2-Capture and synthesis in initial time step
        self.m.addConstr(
            (self.OptVarOperationPointCO2CAP_SYN[(0,0)] == 1), "No operation point for CO2-Capture and synthesis in initial time step")
        # No operation point for distillation in initial time step
        self.m.addConstr(
            (self.OptVarOperationPointDIS[(0,0)] == 1), "No operation point for distillation in initial time step")
        # CO2-Capture and synthesis are off in initial time step
        self.m.addConstr(
            (self.OptVarCurrentStateCO2CAP_SYN[(0,0)] == 1), "State is off for CO2-Capture and synthesis in initial time step")
        # Distillation is off in initial time step
        self.m.addConstr(
            (self.OptVarCurrentStateDIS[(0,0)] == 1), "State is off for distillation in initial time step")     
        # No power in electrolyser in initial time step
        self.m.addConstrs(
            (self.OptVarModeElectrolyser[(0,n,2)] == 1 for n in elec.arrEnapterModules), "Electrolyser modules are off at the beginning")
        # No input or output for battery in first time step
        self.m.addConstr(
            (self.OptVarActualPowerInBatteryPV[0] == 0), "PV in battery initial time step")
        self.m.addConstr(
            (self.OptVarActualPowerInBatteryBought[0] == 0), "Power bought battery initial time step")
        self.m.addConstr(
            (self.OptVarActualPowerOutBattery[0] == 0), "power out battery initial time step")
        self.m.addConstr(
            (self.OptVarActualPowerOutBatterySold[0] == 0), "power sold battery initial time step")


        ## Electrolyser constraints
        self.m.addConstrs(
            (self.OptVarModeElectrolyser[(t-1,n,0)] <= self.OptVarModeElectrolyser[(t,n,3)] for t in self.arrTime[1:] for n in elec.arrEnapterModules), "Electrolyser after off comes off or ramp-up")
        self.m.addConstrs(
            (self.OptVarModeElectrolyser[(t-1,n,1)] <= gp.quicksum(self.OptVarModeElectrolyser[(t,n,m)] for m in [2,3]) for t in self.arrTime[1:] for n in elec.arrEnapterModules), "Electrolyser after off comes off or ramp-up")
        self.m.addConstrs(
            (self.OptVarModeElectrolyser[(t-1,n,2)] <= gp.quicksum(self.OptVarModeElectrolyser[(t,n,m)] for m in [0,2]) for t in self.arrTime[1:] for n in elec.arrEnapterModules), "Electrolyser after off comes off or ramp-up")
        self.m.addConstrs(
            (self.OptVarModeElectrolyser[(t-1,n,3)] <= gp.quicksum(self.OptVarModeElectrolyser[(t,n,m)] for m in [1,2,3]) for t in self.arrTime[1:] for n in elec.arrEnapterModules), "Electrolyser after off comes off or ramp-up")
        


        ## Hydrogen storage constraints
        electrolyser_constant = self.param.param['electrolyser']['constant'] * fTimeStep
        R_H2_Tamb_T0 = self.param.param['R_H2'] * (self.param.param['Tamb'] + self.param.param['T0'])
        storage_volume_factor = 1 / (self.param.param['storageH2']['Volume'] * 100000)

        electrolyser_sum = 0
        hydrogen_in_sum = 0
        
        for t in self.arrTime:
        # Precompute constant terms

            # Calculate intermediate expressions
            electrolyser_sum = electrolyser_sum + gp.quicksum(self.OptVarPowerElectrolyser[(t,n)] * self.OptVarModeElectrolyser[(t,n,3)] * electrolyser_constant for n in elec.arrEnapterModules)
            hydrogen_in_sum = hydrogen_in_sum + (cm.massFlowHydrogenIn[0] * self.OptVarOperationPointCO2CAP_SYN[(t,0)] * self.OptVarCurrentStateCO2CAP_SYN[(t,0)] * fTimeStep
                                                + cm.massFlowHydrogenIn[1] * self.OptVarOperationPointCO2CAP_SYN[(t,1)] * self.OptVarCurrentStateCO2CAP_SYN[(t,1)] * fTimeStep
                                                + cm.massFlowHydrogenIn[2] * self.OptVarOperationPointCO2CAP_SYN[(t,2)] * self.OptVarCurrentStateCO2CAP_SYN[(t,2)] * fTimeStep
                                                + gp.quicksum(cm.massFlowHydrogenIn[j] * self.OptVarOperationPointCO2CAP_SYN[(t,j)] * self.OptVarCurrentStateCO2CAP_SYN[(t,3)] * fTimeStep for j in cm.arrOperationPointsCO2CAP_SYN[4:])
                                                + cm.massFlowHydrogenIn[3] * self.OptVarOperationPointCO2CAP_SYN[(t,3)] * self.OptVarCurrentStateCO2CAP_SYN[(t,4)] * fTimeStep)        


            # Create the constraint
            self.m.addConstr(
                (self.param.param['storageH2']['InitialFilling'] + electrolyser_sum - hydrogen_in_sum) * R_H2_Tamb_T0 * storage_volume_factor <= self.param.param['storageH2']['UpperBound'], f"Storage H2 upper bound at time {t}")
        
            self.m.addConstr(
                (self.param.param['storageH2']['InitialFilling'] + electrolyser_sum - hydrogen_in_sum) * R_H2_Tamb_T0 * storage_volume_factor >= self.param.param['storageH2']['LowerBound'], f"Storage H2 lower bound at time {t}")
        
        print("############################")
        self.m.addConstr(
            ((self.param.param['storageH2']['InitialFilling'] * self.param.param['R_H2'] * (self.param.param['Tamb'] + self.param.param['T0']) / (self.param.param['storageH2']['Volume'] * 100000)) -
                (self.param.param['storageH2']['InitialFilling'] + gp.quicksum(self.OptVarPowerElectrolyser[(t,n)] * self.OptVarModeElectrolyser[(t,n,3)] * self.param.param['electrolyser']['constant'] * fTimeStep for t in self.arrTime for n in elec.arrEnapterModules)
                - gp.quicksum(cm.massFlowHydrogenIn[0] * self.OptVarOperationPointCO2CAP_SYN[(t,0)] * self.OptVarCurrentStateCO2CAP_SYN[(t,0)] * fTimeStep for t in self.arrTime)
                - gp.quicksum(cm.massFlowHydrogenIn[1] * self.OptVarOperationPointCO2CAP_SYN[(t,1)] * self.OptVarCurrentStateCO2CAP_SYN[(t,1)] * fTimeStep for t in self.arrTime)
                - gp.quicksum(cm.massFlowHydrogenIn[2] * self.OptVarOperationPointCO2CAP_SYN[(t,2)] * self.OptVarCurrentStateCO2CAP_SYN[(t,2)] * fTimeStep for t in self.arrTime)
                - gp.quicksum(cm.massFlowHydrogenIn[j] * self.OptVarOperationPointCO2CAP_SYN[(t,j)] * self.OptVarCurrentStateCO2CAP_SYN[(t,3)] * fTimeStep for j in cm.arrOperationPointsCO2CAP_SYN[4:] for t in self.arrTime)
                - gp.quicksum(cm.massFlowHydrogenIn[3] * self.OptVarOperationPointCO2CAP_SYN[(t,3)] * self.OptVarCurrentStateCO2CAP_SYN[(t,4)] * fTimeStep for t in self.arrTime)) 
                * self.param.param['R_H2'] * (self.param.param['Tamb'] + self.param.param['T0']) / (self.param.param['storageH2']['Volume'] * 100000) <= self.param.param['constraints']['hydrogenStorageFillEqual']['LowerBound']), "Storage H2 equal filling upper bound")
        self.m.addConstr(
            ((self.param.param['storageH2']['InitialFilling'] * self.param.param['R_H2'] * (self.param.param['Tamb'] + self.param.param['T0']) / (self.param.param['storageH2']['Volume'] * 100000)) -
                (self.param.param['storageH2']['InitialFilling'] + gp.quicksum(self.OptVarPowerElectrolyser[(t,n)] * self.OptVarModeElectrolyser[(t,n,3)] * self.param.param['electrolyser']['constant'] * fTimeStep for t in self.arrTime for n in elec.arrEnapterModules)
                - gp.quicksum(cm.massFlowHydrogenIn[0] * self.OptVarOperationPointCO2CAP_SYN[(t,0)] * self.OptVarCurrentStateCO2CAP_SYN[(t,0)] * fTimeStep for t in self.arrTime)
                - gp.quicksum(cm.massFlowHydrogenIn[1] * self.OptVarOperationPointCO2CAP_SYN[(t,1)] * self.OptVarCurrentStateCO2CAP_SYN[(t,1)] * fTimeStep for t in self.arrTime)
                - gp.quicksum(cm.massFlowHydrogenIn[2] * self.OptVarOperationPointCO2CAP_SYN[(t,2)] * self.OptVarCurrentStateCO2CAP_SYN[(t,2)] * fTimeStep for t in self.arrTime)
                - gp.quicksum(cm.massFlowHydrogenIn[j] * self.OptVarOperationPointCO2CAP_SYN[(t,j)] * self.OptVarCurrentStateCO2CAP_SYN[(t,3)] * fTimeStep for j in cm.arrOperationPointsCO2CAP_SYN[4:] for t in self.arrTime)
                - gp.quicksum(cm.massFlowHydrogenIn[3] * self.OptVarOperationPointCO2CAP_SYN[(t,3)] * self.OptVarCurrentStateCO2CAP_SYN[(t,4)] * fTimeStep for t in self.arrTime))  
                * self.param.param['R_H2'] * (self.param.param['Tamb'] + self.param.param['T0']) / (self.param.param['storageH2']['Volume'] * 100000) >= self.param.param['constraints']['hydrogenStorageFillEqual']['UpperBound']), "Storage H2 equal filling lower bound")

    
        ## Methanol water storage constraints
        methanol_water_mass_flow_in = 0
        methanol_water_mass_flow_out = 0
        
        for t in self.arrTime:
        # Precompute constant terms

            # Calculate intermediate expressions
            methanol_water_mass_flow_in = methanol_water_mass_flow_in + (cm.massFlowMethanolWaterStorageIn[(0)] / self.param.param['storageMethanolWater']['InitialDensity'] * self.OptVarOperationPointCO2CAP_SYN[(t,0)] * self.OptVarCurrentStateCO2CAP_SYN[(t,0)] * fTimeStep
                                                                        + cm.massFlowMethanolWaterStorageIn[(1)] / self.param.param['storageMethanolWater']['InitialDensity'] * self.OptVarOperationPointCO2CAP_SYN[(t,1)] * self.OptVarCurrentStateCO2CAP_SYN[(t,1)] * fTimeStep
                                                                        + cm.massFlowMethanolWaterStorageIn[(2)] / self.param.param['storageMethanolWater']['InitialDensity'] * self.OptVarOperationPointCO2CAP_SYN[(t,2)] * self.OptVarCurrentStateCO2CAP_SYN[(t,2)] * fTimeStep
                                                                        + gp.quicksum(cm.massFlowMethanolWaterStorageIn[(j)] / self.param.param['storageMethanolWater']['InitialDensity'] * self.OptVarOperationPointCO2CAP_SYN[(t,j)] * self.OptVarCurrentStateCO2CAP_SYN[(t,3)] * fTimeStep for j in cm.arrOperationPointsCO2CAP_SYN[4:])
                                                                        + cm.massFlowMethanolWaterStorageIn[(3)] / self.param.param['storageMethanolWater']['InitialDensity'] * self.OptVarOperationPointCO2CAP_SYN[(t,3)] * self.OptVarCurrentStateCO2CAP_SYN[(t,4)] * fTimeStep)
            
            methanol_water_mass_flow_out = methanol_water_mass_flow_out + (cm.massFlowMethanolWaterStorageOut[(0)] / self.param.param['storageMethanolWater']['InitialDensity'] * self.OptVarOperationPointDIS[(t,0)] * self.OptVarCurrentStateDIS[(t,0)] * fTimeStep
                                                                        + cm.massFlowMethanolWaterStorageOut[(1)] / self.param.param['storageMethanolWater']['InitialDensity'] * self.OptVarOperationPointDIS[(t,1)] * self.OptVarCurrentStateDIS[(t,1)] * fTimeStep
                                                                        + cm.massFlowMethanolWaterStorageOut[(2)] / self.param.param['storageMethanolWater']['InitialDensity'] * self.OptVarOperationPointDIS[(t,2)] * self.OptVarCurrentStateDIS[(t,2)] * fTimeStep
                                                                        + gp.quicksum(cm.massFlowMethanolWaterStorageOut[(j)] / self.param.param['storageMethanolWater']['InitialDensity'] * self.OptVarOperationPointDIS[(t,j)] * self.OptVarCurrentStateDIS[(t,3)] * fTimeStep for j in cm.arrOperationPointsDIS[4:])
                                                                        + cm.massFlowMethanolWaterStorageOut[(3)] / self.param.param['storageMethanolWater']['InitialDensity'] * self.OptVarOperationPointDIS[(t,3)] * self.OptVarCurrentStateDIS[(t,4)] * fTimeStep)

            # Create the constraint
            self.m.addConstr(
                self.param.param['storageMethanolWater']['InitialFilling'] + methanol_water_mass_flow_in - methanol_water_mass_flow_out <= self.param.param['storageMethanolWater']['UpperBound'], f"Storage methanol water upper bound at time {t}")
        
            self.m.addConstr(
                self.param.param['storageMethanolWater']['InitialFilling'] + methanol_water_mass_flow_in - methanol_water_mass_flow_out >= self.param.param['storageMethanolWater']['LowerBound'], f"Storage methanol water lower bound at time {t}")
        
        self.m.addConstr(
            (self.param.param['storageMethanolWater']['InitialFilling'] - 
            (self.param.param['storageMethanolWater']['InitialFilling'] 
                + gp.quicksum(cm.massFlowMethanolWaterStorageIn[(0)] / self.param.param['storageMethanolWater']['InitialDensity'] * self.OptVarOperationPointCO2CAP_SYN[(t,0)] * self.OptVarCurrentStateCO2CAP_SYN[(t,0)] * fTimeStep for t in self.arrTime)
                + gp.quicksum(cm.massFlowMethanolWaterStorageIn[(1)] / self.param.param['storageMethanolWater']['InitialDensity'] * self.OptVarOperationPointCO2CAP_SYN[(t,1)] * self.OptVarCurrentStateCO2CAP_SYN[(t,1)] * fTimeStep for t in self.arrTime)
                + gp.quicksum(cm.massFlowMethanolWaterStorageIn[(2)] / self.param.param['storageMethanolWater']['InitialDensity'] * self.OptVarOperationPointCO2CAP_SYN[(t,2)] * self.OptVarCurrentStateCO2CAP_SYN[(t,2)] * fTimeStep for t in self.arrTime)
                + gp.quicksum(cm.massFlowMethanolWaterStorageIn[(j)] / self.param.param['storageMethanolWater']['InitialDensity'] * self.OptVarOperationPointCO2CAP_SYN[(t,j)] * self.OptVarCurrentStateCO2CAP_SYN[(t,3)] * fTimeStep for j in cm.arrOperationPointsCO2CAP_SYN[4:] for t in self.arrTime)
                + gp.quicksum(cm.massFlowMethanolWaterStorageIn[(3)] / self.param.param['storageMethanolWater']['InitialDensity'] * self.OptVarOperationPointCO2CAP_SYN[(t,3)] * self.OptVarCurrentStateCO2CAP_SYN[(t,4)] * fTimeStep for t in self.arrTime)
                - gp.quicksum(cm.massFlowMethanolWaterStorageOut[(0)] / self.param.param['storageMethanolWater']['InitialDensity'] * self.OptVarOperationPointDIS[(t,0)] * self.OptVarCurrentStateDIS[(t,0)] * fTimeStep for t in self.arrTime)
                - gp.quicksum(cm.massFlowMethanolWaterStorageOut[(1)] / self.param.param['storageMethanolWater']['InitialDensity'] * self.OptVarOperationPointDIS[(t,1)] * self.OptVarCurrentStateDIS[(t,1)] * fTimeStep for t in self.arrTime)
                - gp.quicksum(cm.massFlowMethanolWaterStorageOut[(2)] / self.param.param['storageMethanolWater']['InitialDensity'] * self.OptVarOperationPointDIS[(t,2)] * self.OptVarCurrentStateDIS[(t,2)] * fTimeStep for t in self.arrTime)
                - gp.quicksum(cm.massFlowMethanolWaterStorageOut[(j)] / self.param.param['storageMethanolWater']['InitialDensity'] * self.OptVarOperationPointDIS[(t,j)] * self.OptVarCurrentStateDIS[(t,3)] * fTimeStep for j in cm.arrOperationPointsDIS[4:] for t in self.arrTime)
                - gp.quicksum(cm.massFlowMethanolWaterStorageOut[(3)] / self.param.param['storageMethanolWater']['InitialDensity'] * self.OptVarOperationPointDIS[(t,3)] * self.OptVarCurrentStateDIS[(t,4)] * fTimeStep for t in self.arrTime)) 
                <= self.param.param['constraints']['methanolWaterStorageFillEqual']['LowerBound']), "Storage methanol water equal filling upper bound")
        self.m.addConstr(
            (self.param.param['storageMethanolWater']['InitialFilling'] - 
            (self.param.param['storageMethanolWater']['InitialFilling'] 
                + gp.quicksum(cm.massFlowMethanolWaterStorageIn[(0)] / self.param.param['storageMethanolWater']['InitialDensity'] * self.OptVarOperationPointCO2CAP_SYN[(t,0)] * self.OptVarCurrentStateCO2CAP_SYN[(t,0)] * fTimeStep for t in self.arrTime)
                + gp.quicksum(cm.massFlowMethanolWaterStorageIn[(1)] / self.param.param['storageMethanolWater']['InitialDensity'] * self.OptVarOperationPointCO2CAP_SYN[(t,1)] * self.OptVarCurrentStateCO2CAP_SYN[(t,1)] * fTimeStep for t in self.arrTime)
                + gp.quicksum(cm.massFlowMethanolWaterStorageIn[(2)] / self.param.param['storageMethanolWater']['InitialDensity'] * self.OptVarOperationPointCO2CAP_SYN[(t,2)] * self.OptVarCurrentStateCO2CAP_SYN[(t,2)] * fTimeStep for t in self.arrTime)
                + gp.quicksum(cm.massFlowMethanolWaterStorageIn[(j)] / self.param.param['storageMethanolWater']['InitialDensity'] * self.OptVarOperationPointCO2CAP_SYN[(t,j)] * self.OptVarCurrentStateCO2CAP_SYN[(t,3)] * fTimeStep for j in cm.arrOperationPointsCO2CAP_SYN[4:] for t in self.arrTime)
                + gp.quicksum(cm.massFlowMethanolWaterStorageIn[(3)] / self.param.param['storageMethanolWater']['InitialDensity'] * self.OptVarOperationPointCO2CAP_SYN[(t,3)] * self.OptVarCurrentStateCO2CAP_SYN[(t,4)] * fTimeStep for t in self.arrTime)
                - gp.quicksum(cm.massFlowMethanolWaterStorageOut[(0)] / self.param.param['storageMethanolWater']['InitialDensity'] * self.OptVarOperationPointDIS[(t,0)] * self.OptVarCurrentStateDIS[(t,0)] * fTimeStep for t in self.arrTime)
                - gp.quicksum(cm.massFlowMethanolWaterStorageOut[(1)] / self.param.param['storageMethanolWater']['InitialDensity'] * self.OptVarOperationPointDIS[(t,1)] * self.OptVarCurrentStateDIS[(t,1)] * fTimeStep for t in self.arrTime)
                - gp.quicksum(cm.massFlowMethanolWaterStorageOut[(2)] / self.param.param['storageMethanolWater']['InitialDensity'] * self.OptVarOperationPointDIS[(t,2)] * self.OptVarCurrentStateDIS[(t,2)] * fTimeStep for t in self.arrTime)
                - gp.quicksum(cm.massFlowMethanolWaterStorageOut[(j)] / self.param.param['storageMethanolWater']['InitialDensity'] * self.OptVarOperationPointDIS[(t,j)] * self.OptVarCurrentStateDIS[(t,3)] * fTimeStep for j in cm.arrOperationPointsDIS[4:] for t in self.arrTime)
                - gp.quicksum(cm.massFlowMethanolWaterStorageOut[(3)] / self.param.param['storageMethanolWater']['InitialDensity'] * self.OptVarOperationPointDIS[(t,3)] * self.OptVarCurrentStateDIS[(t,4)] * fTimeStep for t in self.arrTime)) 
                >= self.param.param['constraints']['methanolWaterStorageFillEqual']['UpperBound']), "Storage methanol water equal filling lower bound")



        battery_power = self.param.param['battery']['power']
        battery_min_charge = self.param.param['battery']['minCharge']
        battery_initial_charge = self.param.param['battery']['initialCharge']
        battery_fill_equal_lb = battery_initial_charge*self.param.param['constraints']['storagesFactorFillEqualLower']
        battery_fill_equal_ub = -battery_initial_charge*self.param.param['constraints']['storagesFactorFillEqualUpper'] 

        
        ## Battery constraints
        self.m.addConstrs(
            (battery_initial_charge 
            + gp.quicksum(self.OptVarActualPowerInBatteryPV[l] * self.param.param['battery']['efficiency'] for l in self.arrTime[0:t+1])
            + gp.quicksum(self.OptVarActualPowerInBatteryBought[l] * self.param.param['battery']['efficiency'] for l in self.arrTime[0:t+1])  
            - gp.quicksum(self.OptVarActualPowerOutBattery[l] for l in self.arrTime[0:t+1])
            - gp.quicksum(self.OptVarActualPowerOutBatterySold[l] for l in self.arrTime[0:t+1])
            <= battery_power for t in self.arrTime), "Battery upper bound")

        self.m.addConstrs(
            (battery_initial_charge 
            + gp.quicksum(self.OptVarActualPowerInBatteryPV[l] * self.param.param['battery']['efficiency'] for l in self.arrTime[0:t+1])
            + gp.quicksum(self.OptVarActualPowerInBatteryBought[l] * self.param.param['battery']['efficiency'] for l in self.arrTime[0:t+1])  
            - gp.quicksum(self.OptVarActualPowerOutBattery[l] for l in self.arrTime[0:t+1])
            - gp.quicksum(self.OptVarActualPowerOutBatterySold[l] for l in self.arrTime[0:t+1])
            >= battery_min_charge for t in self.arrTime), "Battery lower bound")

        self.m.addConstr(
            (battery_initial_charge - (battery_initial_charge 
            + gp.quicksum(self.OptVarActualPowerInBatteryPV[t] * self.param.param['battery']['efficiency'] for t in self.arrTime)
            + gp.quicksum(self.OptVarActualPowerInBatteryBought[t] * self.param.param['battery']['efficiency'] for t in self.arrTime)  
            - gp.quicksum(self.OptVarActualPowerOutBattery[t] for t in self.arrTime)
            - gp.quicksum(self.OptVarActualPowerOutBatterySold[t] for t in self.arrTime)) <= battery_fill_equal_lb), "Battery equal charge upper bound")

        self.m.addConstr(
            (battery_initial_charge - (battery_initial_charge 
            + gp.quicksum(self.OptVarActualPowerInBatteryPV[t] * self.param.param['battery']['efficiency'] for t in self.arrTime)
            + gp.quicksum(self.OptVarActualPowerInBatteryBought[t] * self.param.param['battery']['efficiency'] for t in self.arrTime)  
            - gp.quicksum(self.OptVarActualPowerOutBattery[t] for t in self.arrTime)
            - gp.quicksum(self.OptVarActualPowerOutBatterySold[t] for t in self.arrTime)) >= battery_fill_equal_ub), "Battery equal charge lower bound")
        

        