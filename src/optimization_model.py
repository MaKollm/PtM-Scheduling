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
        self.arrTime = list(range(0,self.param.param['controlParameters']['numberOfTimeSteps']))


    def funcCreateOptimizationModel(self, cm, elec, pv, pp, ci):
        self.m = gp.Model('ptm')
        self.m.ModelSense = GRB.MINIMIZE
        self.funcCreateVariables(cm, elec, pv, pp, ci)

        # Extract information from adaptation which operation points to use
        #self.funcExtractInformationFromAdaptation(cm, elec, pv, pp)

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
        if "initialData" in self.param.param:
            # Check if the time horizon of the initial data is the same as the time horizon of the current optimization
            if self.param.param['initialData']["param"]['controlParameters']['numberOfTimeSteps'] == self.param.param['controlParameters']['numberOfTimeSteps'] and self.param.param['initialData']["param"]['optimization']['status'] != GRB.INFEASIBLE:

                for t in self.arrTime:
                    for i in cm.arrOperationPointsCO2CAP:
                        self.OptVarOperationPointCO2CAP[t,i].Start = self.param.param['initialData']['input']['operationPoint_CO2CAP'][t,i]

                    for i in cm.arrOperationPointsSYN:
                        self.OptVarOperationPointSYN[t,i].Start = self.param.param['initialData']['input']['operationPoint_SYN'][t,i]

                    for i in cm.arrOperationPointsDIS:
                        self.OptVarOperationPointDIS[t,i].Start = self.param.param['initialData']['input']['operationPoint_DIS'][t,i]

                    for i in range(0,np.shape(self.param.param['initialData']['input']['currentStateCO2CAPRaw'])[1]):
                        self.OptVarCurrentStateCO2CAP[t,i].Start = self.param.param['initialData']['input']['currentStateCO2CAPRaw'][t,i]

                    for i in range(0,np.shape(self.param.param['initialData']['input']['currentStateSYNRaw'])[1]):
                        self.OptVarCurrentStateSYN[t,i].Start = self.param.param['initialData']['input']['currentStateSYNRaw'][t,i]

                    for i in range(0,np.shape(self.param.param['initialData']['input']['currentStateDISRaw'])[1]):
                        self.OptVarCurrentStateDIS[t,i].Start = self.param.param['initialData']['input']['currentStateDISRaw'][t,i]

                    for i in range(0,np.shape(self.param.param['initialData']['input']['currentStateSwitchCO2CAPRaw'])[1]):
                        for j in range(0,np.shape(self.param.param['initialData']['input']['currentStateSwitchCO2CAPRaw'])[2]):
                            self.OptVarCurrentStateSwitchCO2CAP[t,i,j].Start = self.param.param['initialData']['input']['currentStateSwitchCO2CAPRaw'][t,i,j]
                    
                    for i in range(0,np.shape(self.param.param['initialData']['input']['currentStateSwitchSYNRaw'])[1]):
                        for j in range(0,np.shape(self.param.param['initialData']['input']['currentStateSwitchSYNRaw'])[2]):
                            self.OptVarCurrentStateSwitchSYN[t,i,j].Start = self.param.param['initialData']['input']['currentStateSwitchSYNRaw'][t,i,j]

                    for i in range(0,np.shape(self.param.param['initialData']['input']['currentStateSwitchDISRaw'])[1]):
                        for j in range(0,np.shape(self.param.param['initialData']['input']['currentStateSwitchDISRaw'])[2]):
                            self.OptVarCurrentStateSwitchDIS[t,i,j].Start = self.param.param['initialData']['input']['currentStateSwitchDISRaw'][t,i,j]

                    for i in elec.arrEnapterModules:
                        self.OptVarPowerElectrolyser[t,i].Start = self.param.param['initialData']['input']['powerElectrolyserRaw'][t,i]

                    for i in elec.arrEnapterModules:
                        for j in elec.arrModes:
                            self.OptVarModeElectrolyser[t,i,j].Start = self.param.param['initialData']['input']['modeElectrolyserRaw'][t,i,j]

                    self.OptVarUsageOfPV[t].Start = self.param.param['initialData']['input']['usageOfPV'][t]       
                    self.OptVarPowerInBatteryPV[t].Start = self.param.param['initialData']['input']['powerInBatteryPV'][t]

                    self.OptVarPowerInBatteryBought[t].Start = self.param.param['initialData']['input']['powerInBatteryBought'][t]
                    self.OptVarPowerOutBattery[t].Start = self.param.param['initialData']['input']['powerOutBattery'][t]
                    self.OptVarPowerOutBatterySold[t].Start = self.param.param['initialData']['input']['powerOutBatterySold'][t]
                    self.OptVarPowerBought[t].Start = self.param.param['initialData']['input']['powerBought'][t]
        
                    self.OptVarActualPowerInBatteryPV[t].Start = self.param.param['initialData']['input']['actualPowerInBatteryPV'][t]
                    self.OptVarActualPowerInBatteryBought[t].Start = self.param.param['initialData']['input']['actualPowerInBatteryBought'][t]
                    self.OptVarActualPowerOutBattery[t].Start = self.param.param['initialData']['input']['actualPowerOutBattery'][t]
                    self.OptVarActualPowerOutBatterySold[t].Start = self.param.param['initialData']['input']['actualPowerOutBatterySold'][t]

                    self.OptVarIndicatorBatteryCharging1[t].Start = self.param.param['initialData']['input']['indicatorBatteryCharging1'][t]
                    self.OptVarIndicatorBatteryDischarging1[t].Start = self.param.param['initialData']['input']['indicatorBatteryDischarging1'][t]
                    self.OptVarIndicatorBatteryCharging2[t].Start = self.param.param['initialData']['input']['indicatorBatteryCharging2'][t]
                    self.OptVarIndicatorBatteryDischarging2[t].Start = self.param.param['initialData']['input']['indicatorBatteryDischarging2'][t]
                
                for locali, i in enumerate(cm.arrOperationPointsCO2CAP[4:]):
                    self.OptVarUsedOperationPointCO2CAP[i].Start = self.param.param['initialData']['input']['usedOperationPointCO2CAPRaw'][locali]

                for locali, i in enumerate(cm.arrOperationPointsSYN[4:]):
                    self.OptVarUsedOperationPointSYN[i].Start = self.param.param['initialData']['input']['usedOperationPointSYNRaw'][locali]

                for locali, i in enumerate(cm.arrOperationPointsDIS[4:]):
                    self.OptVarUsedOperationPointDIS[i].Start = self.param.param['initialData']['input']['usedOperationPointDISRaw'][locali]

                for i in elec.arrEnapterModules:
                     self.OptVarUsedOperationPointElectrolyser[i].Start = self.param.param['initialData']['input']['UsedOperationPointElec'][i]

            else:
                print("########## Warning ##########")
                print("Time horizon of initial data does not match with the time horizon of the current optimization. No initial start values will be set.")
        else:
            print("File with initial values not found")

    ########## Variables ##########
    def funcCreateVariables(self, cm, elec, pv, pp, ci):
        self.OptVarOperationPointCO2CAP = self.m.addVars(self.arrTime,cm.arrOperationPointsCO2CAP, vtype=GRB.BINARY)
        self.OptVarOperationPointSYN = self.m.addVars(self.arrTime,cm.arrOperationPointsSYN, vtype=GRB.BINARY)
        self.OptVarOperationPointDIS = self.m.addVars(self.arrTime,cm.arrOperationPointsDIS, vtype=GRB.BINARY)

        self.OptVarCurrentStateCO2CAP = self.m.addVars(self.arrTime,[0,1,2,3,4], vtype=GRB.BINARY)
        self.OptVarCurrentStateSYN = self.m.addVars(self.arrTime,[0,1,2,3,4], vtype=GRB.BINARY)
        self.OptVarCurrentStateDIS = self.m.addVars(self.arrTime,[0,1,2,3,4], vtype=GRB.BINARY)
        self.OptVarCurrentStateSwitchCO2CAP = self.m.addVars(self.arrTime,[0,1,2,3,4],[0,1,2,3,4],vtype=GRB.BINARY)
        self.OptVarCurrentStateSwitchSYN = self.m.addVars(self.arrTime,[0,1,2,3,4],[0,1,2,3,4],vtype=GRB.BINARY)
        self.OptVarCurrentStateSwitchDIS = self.m.addVars(self.arrTime,[0,1,2,3,4],[0,1,2,3,4],vtype=GRB.BINARY)

        self.OptVarPowerElectrolyser = self.m.addVars(self.arrTime,self.param.param['electrolyser']['numberOfEnapterModules'],lb=self.param.param['electrolyser']['powerLowerBound'], ub=self.param.param['electrolyser']['powerUpperBound'],vtype=GRB.CONTINUOUS)

        self.OptVarModeElectrolyser = self.m.addVars(self.arrTime,self.param.param['electrolyser']['numberOfEnapterModules'],4, vtype=GRB.BINARY)
        
        self.OptVarUsageOfPV = self.m.addVars(self.arrTime,lb=0.0,ub=1000,vtype=GRB.CONTINUOUS)

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

        self.OptVarPowerBought = self.m.addVars(self.arrTime,lb=0.0,ub=100,vtype=GRB.CONTINUOUS)

        # Variable for benchmark
        self.OptVarUsedOperationPointCO2CAP = self.m.addVars(cm.arrOperationPointsCO2CAP[4:], vtype=GRB.BINARY)
        self.OptVarUsedOperationPointSYN = self.m.addVars(cm.arrOperationPointsSYN[4:], vtype=GRB.BINARY)
        self.OptVarUsedOperationPointDIS = self.m.addVars(cm.arrOperationPointsDIS[4:], vtype=GRB.BINARY)
        self.OptVarUsedOperationPointElectrolyser = self.m.addVars(self.param.param['electrolyser']['numberOfEnapterModules'],lb=self.param.param['electrolyser']['powerLowerBound'], ub=self.param.param['electrolyser']['powerUpperBound'],vtype=GRB.CONTINUOUS)
        

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

          
                
        if self.param.param['controlParameters']['benchmark'] == True:
            # Minimum amount of methanol which has to be produced
            self.m.addConstr(
                (gp.quicksum(cm.massFlowMethanolOut[(j)] * self.OptVarOperationPointDIS[(t,j)] * self.OptVarCurrentStateDIS[(t,3)] * fTimeStep for j in cm.arrOperationPointsDIS for t in self.arrTime) >= self.param.param['production']['minMethanolBenchmark']), "Minimum amount methanol produced benchmark")
            

            self.m.addConstr(
                (gp.quicksum(self.OptVarUsedOperationPointCO2CAP[j] for j in cm.arrOperationPointsCO2CAP[4:]) == 1), "Benchmark operation point CO2-Capture 3_1")
            self.m.addConstrs(
                (self.OptVarOperationPointCO2CAP[(t,j)] == self.OptVarCurrentStateCO2CAP[(t,3)] * self.OptVarUsedOperationPointCO2CAP[j] for t in self.arrTime for j in cm.arrOperationPointsCO2CAP[4:]), "Benchmark operation point CO2-Capture 3_2")

            self.m.addConstr(
                (gp.quicksum(self.OptVarUsedOperationPointSYN[j] for j in cm.arrOperationPointsSYN[4:]) == 1), "Benchmark operation point Synthesis 3_1")
            self.m.addConstrs(
                (self.OptVarOperationPointSYN[(t,j)] == self.OptVarCurrentStateSYN[(t,3)] * self.OptVarUsedOperationPointSYN[j] for t in self.arrTime for j in cm.arrOperationPointsSYN[4:]), "Benchmark operation point Synthesis 3_2")
            
            self.m.addConstr(
                (gp.quicksum(self.OptVarUsedOperationPointDIS[j] for j in cm.arrOperationPointsDIS[4:]) == 1), "Benchmark operation point Distillation 3_1")
            self.m.addConstrs(
                (self.OptVarOperationPointDIS[(t,j)] == self.OptVarCurrentStateDIS[(t,3)] * self.OptVarUsedOperationPointDIS[j] for t in self.arrTime for j in cm.arrOperationPointsDIS[4:]), "Benchmark operation point Distillation 3_2")
            
            self.m.addConstrs(
                (self.OptVarPowerElectrolyser[(t,n)] >= self.param.param['electrolyser']['benchmarkPower'] * self.OptVarModeElectrolyser[(t,n,3)] for t in self.arrTime for n in elec.arrEnapterModules), "Benchmark power electrolyser")
            self.m.addConstrs(
                (self.OptVarModeElectrolyser[(t,n-1,m)] == self.OptVarModeElectrolyser[(t,n,m)] for t in self.arrTime for n in elec.arrEnapterModules[1:] for m in elec.arrModes), "fdsa")
            
            # Maximal einmal hochfahren im Benchmark
            self.m.addConstr(
                (gp.quicksum(self.OptVarCurrentStateSwitchCO2CAP[(t,0,1)] for t in self.arrTime) <= 1), "fdsa")
            self.m.addConstr(
                (gp.quicksum(self.OptVarCurrentStateSwitchSYN[(t,0,1)] for t in self.arrTime) <= 1), "fdsa")
            self.m.addConstr(
                (gp.quicksum(self.OptVarCurrentStateSwitchDIS[(t,0,1)] for t in self.arrTime) <= 1), "fdsa")
            self.m.addConstrs(
                (gp.quicksum(self.OptVarModeElectrolyser[(t,n,0)] for t in self.arrTime) <= 1 for n in elec.arrEnapterModules), "fdsa")
            
            # Kein Standby im Benchmark
            self.m.addConstr(
                (gp.quicksum(self.OptVarCurrentStateCO2CAP[(t,2)] for t in self.arrTime) == 0), "fdsa")
            self.m.addConstr(
                (gp.quicksum(self.OptVarCurrentStateSYN[(t,2)] for t in self.arrTime) == 0), "fdsa")
            self.m.addConstr(
                (gp.quicksum(self.OptVarCurrentStateDIS[(t,2)] for t in self.arrTime) == 0), "fdsa")

            """
            if self.param.param['controlParameters']['transitionConstraints'] == True:
                self.m.addConstrs(
                    (self.OptVarCurrentStateCO2CAP[(t,1)] == 1 for t in self.arrTime[1:self.param.param['constraints']['transitionTimes']['minStayTimeCO2CAP_Startup'][0]+1]), "Benchmark operation point CO2-Capture 1")
                self.m.addConstrs(
                    (self.OptVarCurrentStateCO2CAP[(t,3)] == 1 for t in self.arrTime[1+self.param.param['constraints']['transitionTimes']['minStayTimeCO2CAP_Startup'][0]:]), "Benchmark operation point CO2-Capture 2")
                self.m.addConstrs(
                    (self.OptVarCurrentStateSYN[(t,1)] == 1 for t in self.arrTime[1:self.param.param['constraints']['transitionTimes']['minStayTimeSYN_Startup'][0]+1]), "Benchmark operation point Synthesis 1")
                self.m.addConstrs(
                    (self.OptVarCurrentStateSYN[(t,3)] == 1 for t in self.arrTime[1+self.param.param['constraints']['transitionTimes']['minStayTimeSYN_Startup'][0]:]), "Benchmark operation point Synthesis 2")
                self.m.addConstrs(
                    (self.OptVarCurrentStateDIS[(t,1)] == 1 for t in self.arrTime[1:self.param.param['constraints']['transitionTimes']['minStayTimeDIS_Startup'][0]+1]), "Benchmark operation point Distillation 1")
                self.m.addConstrs(
                    (self.OptVarCurrentStateDIS[(t,3)] == 1 for t in self.arrTime[1+self.param.param['constraints']['transitionTimes']['minStayTimeDIS_Startup'][0]:]), "Benchmark operation point Distillation 2")        
                # The same operation point for absorption and desorption for every time step
                self.m.addConstrs(
                    (self.OptVarOperationPointCO2CAP[(t-1,j)] == self.OptVarOperationPointCO2CAP[(t,j)] for t in self.arrTime[2+self.param.param['constraints']['transitionTimes']['minStayTimeCO2CAP_Startup'][0]:] for j in cm.arrOperationPointsCO2CAP[4:]), "Benchmark operation point CO2-Capture 3")
                # The same operation point synthesis for every time step
                self.m.addConstrs(
                    (self.OptVarOperationPointSYN[(t-1,j)] == self.OptVarOperationPointSYN[(t,j)] for t in self.arrTime[2+self.param.param['constraints']['transitionTimes']['minStayTimeSYN_Startup'][0]:] for j in cm.arrOperationPointsSYN[4:]), "Benchmark operation point Synthesis 3")    
                # The same operation point for distillation for every time step
                self.m.addConstrs(
                    (self.OptVarOperationPointDIS[(t-1,j)] == self.OptVarOperationPointDIS[(t,j)] for t in self.arrTime[2+self.param.param['constraints']['transitionTimes']['minStayTimeDIS_Startup'][0]:] for j in cm.arrOperationPointsDIS[4:]), "Benchmark operation point Distillation 3")
                # The same power in electrolyser for every time step
                self.m.addConstrs(
                    (self.OptVarPowerElectrolyser[(t-1,n)] == self.OptVarPowerElectrolyser[(t,n)] for t in self.arrTime[2:] for n in elec.arrEnapterModules), "Benchmark power electrolyser")
                self.m.addConstrs(
                    (self.OptVarModeElectrolyser[(t-1,n,m)] == self.OptVarModeElectrolyser[(t,n,m)] for t in self.arrTime[3:] for n in elec.arrEnapterModules for m in elec.arrModes), "Benchmark power electrolyser")
            else:
                
                # The same operation point for absorption and desorption for every time step
                self.m.addConstrs(
                        (self.OptVarOperationPointCO2CAP[(t-1,j)] == self.OptVarOperationPointCO2CAP[(t,j)] for t in self.arrTime[2:] for j in cm.arrOperationPointsCO2CAP[4:]), "Benchmark operation point CO2-Capture 3")
                # The same operation point for synthesis for every time step
                self.m.addConstrs(
                        (self.OptVarOperationPointSYN[(t-1,j)] == self.OptVarOperationPointSYN[(t,j)] for t in self.arrTime[2:] for j in cm.arrOperationPointsSYN[4:]), "Benchmark operation point Synthesis 3")
                # The same operation point for distillation for every time step
                self.m.addConstrs(
                        (self.OptVarOperationPointDIS[(t-1,j)] == self.OptVarOperationPointDIS[(t,j)] for t in self.arrTime[2:] for j in cm.arrOperationPointsDIS[4:]), "Benchmark operation point Distillation 3")
                # The same power in electrolyser for every time step
                self.m.addConstrs(
                    (self.OptVarPowerElectrolyser[(t-1,n)] == self.OptVarPowerElectrolyser[(t,n)] for t in self.arrTime[2:] for n in elec.arrEnapterModules), "Benchmark power electrolyser")
                self.m.addConstrs(
                    (self.OptVarModeElectrolyser[(t-1,n,m)] == self.OptVarModeElectrolyser[(t,n,m)] for t in self.arrTime[3:] for n in elec.arrEnapterModules for m in elec.arrModes), "Benchmark power electrolyser")
                """

 
        if self.param.param['controlParameters']['benchmark'] == False:
            if self.param.param['controlParameters']['sameOutputAsBenchmark'] == False:

                if self.param.param['controlParameters']['currStartTimeLastOptHorizon'] > 0:
                    self.m.addConstr(
                        (gp.quicksum(cm.massFlowMethanolOut[(j)] * self.OptVarOperationPointDIS[(t,j)] * self.OptVarCurrentStateDIS[(t,3)] * fTimeStep for j in cm.arrOperationPointsDIS[4:] for t in self.arrTime) 
                        - gp.quicksum(cm.massFlowMethanolOut[(j)] * self.OptVarOperationPointDIS[(t,j)] * self.OptVarCurrentStateDIS[(t,3)] * fTimeStep for j in cm.arrOperationPointsDIS[4:] for t in self.arrTime[-self.param.param['controlParameters']['currStartTimeLastOptHorizon']:]) >= self.param.param['production']['minMethanolOpt'] - self.param.param['controlParameters']['prodMethanolLastTimeInterval']), "Minimum amount methanol produced 1")
                
                self.m.addConstr(
                    (gp.quicksum(cm.massFlowMethanolOut[(j)] * self.OptVarOperationPointDIS[(t,j)] * self.OptVarCurrentStateDIS[(t,3)] * fTimeStep for j in cm.arrOperationPointsDIS[4:] for t in self.arrTime) >= self.param.param['production']['minMethanolOpt']), "Minimum amount methanol produced 2")     
            
            else:
                self.m.addConstr(
                    (gp.quicksum(cm.massFlowMethanolOut[(j)] * self.OptVarOperationPointDIS[(t,j)] * self.OptVarCurrentStateDIS[(t,3)] * fTimeStep for j in cm.arrOperationPointsDIS for t in self.arrTime) <= self.param.param['production']['methanol']*1.01), "Amount methanol produced is same as benchmark upper bound") 
                self.m.addConstr(
                    (gp.quicksum(cm.massFlowMethanolOut[(j)] * self.OptVarOperationPointDIS[(t,j)] * self.OptVarCurrentStateDIS[(t,3)] * fTimeStep for j in cm.arrOperationPointsDIS for t in self.arrTime) >= self.param.param['production']['methanol']), "Amount methanol produced is same as benchmark lower bound")    



        if self.param.param['controlParameters']['transitionConstraints'] == True:
            ## Minimum and maximum stay time per mode after new schedule
            if self.param.param['controlParameters']['numTimeStepsToSimulate'] < self.param.param['controlParameters']['numberOfTimeSteps'] and self.param.param['controlParameters']['iteration'] > 0:
                for t in range(0,self.param.param['constraints']['transitionTimesStart']['minStayTimeCO2CAP']):
                    self.m.addConstr(self.OptVarCurrentStateCO2CAP[(t,self.param.param['startValues']['stateCO2CAP'])] == 1)
            
                if self.param.param['constraints']['transitionTimesStart']['maxStayTimeCO2CAP'] < self.param.param['controlParameters']['numberOfTimeSteps']:
                    self.m.addConstr(self.OptVarCurrentStateCO2CAP[(self.param.param['constraints']['transitionTimesStart']['maxStayTimeCO2CAP'],self.param.param['startValues']['stateCO2CAP'])] == 0)

                for t in range(0,self.param.param['constraints']['transitionTimesStart']['minStayTimeSYN']):
                    self.m.addConstr(self.OptVarCurrentStateSYN[(t,self.param.param['startValues']['stateSYN'])] == 1)
            
                if self.param.param['constraints']['transitionTimesStart']['maxStayTimeSYN'] < self.param.param['controlParameters']['numberOfTimeSteps']:
                    self.m.addConstr(self.OptVarCurrentStateSYN[(self.param.param['constraints']['transitionTimesStart']['maxStayTimeSYN'],self.param.param['startValues']['stateSYN'])] == 0)

                for t in range(0,self.param.param['constraints']['transitionTimesStart']['minStayTimeDIS']):
                    self.m.addConstr(self.OptVarCurrentStateDIS[(t,self.param.param['startValues']['stateDIS'])] == 1)
            
                if self.param.param['constraints']['transitionTimesStart']['maxStayTimeSYN'] < self.param.param['controlParameters']['numberOfTimeSteps']:
                    self.m.addConstr(self.OptVarCurrentStateDIS[(self.param.param['constraints']['transitionTimesStart']['maxStayTimeDIS'],self.param.param['startValues']['stateDIS'])] == 0)
    
            ## Minimum stay time per mode
        
            self.m.addConstrs(
                (gp.quicksum(self.OptVarCurrentStateCO2CAP[(i,j)] for i in self.arrTime[t:t+self.param.param['constraints']['transitionTimes']['minStayTimeCO2CAP_Off'][k]] for j in [1,2,3,4]) <= (1 - self.OptVarCurrentStateSwitchCO2CAP[(t,k,0)])*self.param.param['constraints']['transitionTimes']['minStayTimeCO2CAP_Off'][k] for t in self.arrTime[1:] for k in [1,2,3,4]), "Mode switching min stay constraint CO2CAP off")
            self.m.addConstrs(
                (gp.quicksum(self.OptVarCurrentStateCO2CAP[(i,j)] for i in self.arrTime[t:t+self.param.param['constraints']['transitionTimes']['minStayTimeCO2CAP_Startup'][k]] for j in [0,2,3,4]) <= (1 - self.OptVarCurrentStateSwitchCO2CAP[(t,k,1)])*self.param.param['constraints']['transitionTimes']['minStayTimeCO2CAP_Startup'][k] for t in self.arrTime[1:] for k in [0,2,3,4]), "Mode switching min stay constraint CO2CAP startup")
            self.m.addConstrs(
                (gp.quicksum(self.OptVarCurrentStateCO2CAP[(i,j)] for i in self.arrTime[t:t+self.param.param['constraints']['transitionTimes']['minStayTimeCO2CAP_Standby'][k]] for j in [0,1,3,4]) <= (1 - self.OptVarCurrentStateSwitchCO2CAP[(t,k,2)])*self.param.param['constraints']['transitionTimes']['minStayTimeCO2CAP_Standby'][k] for t in self.arrTime[1:] for k in [0,1,3,4]), "Mode switching min stay constraint CO2CAP standby")
            self.m.addConstrs(
                (gp.quicksum(self.OptVarCurrentStateCO2CAP[(i,j)] for i in self.arrTime[t:t+self.param.param['constraints']['transitionTimes']['minStayTimeCO2CAP_On'][k]] for j in [0,1,2,4]) <= (1 - self.OptVarCurrentStateSwitchCO2CAP[(t,k,3)])*self.param.param['constraints']['transitionTimes']['minStayTimeCO2CAP_On'][k] for t in self.arrTime[1:] for k in [0,1,2,4]), "Mode switching min stay constraint CO2CAP on")
            self.m.addConstrs(
                (gp.quicksum(self.OptVarCurrentStateCO2CAP[(i,j)] for i in self.arrTime[t:t+self.param.param['constraints']['transitionTimes']['minStayTimeCO2CAP_Shutdown'][k]] for j in [0,1,2,3]) <= (1 - self.OptVarCurrentStateSwitchCO2CAP[(t,k,4)])*self.param.param['constraints']['transitionTimes']['minStayTimeCO2CAP_Shutdown'][k] for t in self.arrTime[1:] for k in [0,1,2,3]), "Mode switching min stay constraint CO2CAP shutdown")

            self.m.addConstrs(
                (gp.quicksum(self.OptVarCurrentStateSYN[(i,j)] for i in self.arrTime[t:t+self.param.param['constraints']['transitionTimes']['minStayTimeSYN_Off'][k]] for j in [1,2,3,4]) <= (1 - self.OptVarCurrentStateSwitchSYN[(t,k,0)])*self.param.param['constraints']['transitionTimes']['minStayTimeSYN_Off'][k] for t in self.arrTime[1:] for k in [1,2,3,4]), "Mode switching min stay constraint SYN off")
            self.m.addConstrs(
                (gp.quicksum(self.OptVarCurrentStateSYN[(i,j)] for i in self.arrTime[t:t+self.param.param['constraints']['transitionTimes']['minStayTimeSYN_Startup'][k]] for j in [0,2,3,4]) <= (1 - self.OptVarCurrentStateSwitchSYN[(t,k,1)])*self.param.param['constraints']['transitionTimes']['minStayTimeSYN_Startup'][k] for t in self.arrTime[1:] for k in [0,2,3,4]), "Mode switching min stay constraint SYN startup")
            self.m.addConstrs(
                (gp.quicksum(self.OptVarCurrentStateSYN[(i,j)] for i in self.arrTime[t:t+self.param.param['constraints']['transitionTimes']['minStayTimeSYN_Standby'][k]] for j in [0,1,3,4]) <= (1 - self.OptVarCurrentStateSwitchSYN[(t,k,2)])*self.param.param['constraints']['transitionTimes']['minStayTimeSYN_Standby'][k] for t in self.arrTime[1:] for k in [0,1,3,4]), "Mode switching min stay constraint SYN standby")
            self.m.addConstrs(
                (gp.quicksum(self.OptVarCurrentStateSYN[(i,j)] for i in self.arrTime[t:t+self.param.param['constraints']['transitionTimes']['minStayTimeSYN_On'][k]] for j in [0,1,2,4]) <= (1 - self.OptVarCurrentStateSwitchSYN[(t,k,3)])*self.param.param['constraints']['transitionTimes']['minStayTimeSYN_On'][k] for t in self.arrTime[1:] for k in [0,1,2,4]), "Mode switching min stay constraint SYN on")
            self.m.addConstrs(
                (gp.quicksum(self.OptVarCurrentStateSYN[(i,j)] for i in self.arrTime[t:t+self.param.param['constraints']['transitionTimes']['minStayTimeSYN_Shutdown'][k]] for j in [0,1,2,3]) <= (1 - self.OptVarCurrentStateSwitchSYN[(t,k,4)])*self.param.param['constraints']['transitionTimes']['minStayTimeSYN_Shutdown'][k] for t in self.arrTime[1:] for k in [0,1,2,3]), "Mode switching min stay constraint SYN shutdown")
          
            self.m.addConstrs(
                (gp.quicksum(self.OptVarCurrentStateDIS[(i,j)] for i in self.arrTime[t:t+self.param.param['constraints']['transitionTimes']['minStayTimeDIS_Off'][k]] for j in [1,2,3,4]) <= (1 - self.OptVarCurrentStateSwitchDIS[(t,k,0)])*self.param.param['constraints']['transitionTimes']['minStayTimeDIS_Off'][k] for t in self.arrTime[1:] for k in [1,2,3,4]), "Mode switching min stay constraint DIS off")
            self.m.addConstrs(
                (gp.quicksum(self.OptVarCurrentStateDIS[(i,j)] for i in self.arrTime[t:t+self.param.param['constraints']['transitionTimes']['minStayTimeDIS_Startup'][k]] for j in [0,2,3,4]) <= (1 - self.OptVarCurrentStateSwitchDIS[(t,k,1)])*self.param.param['constraints']['transitionTimes']['minStayTimeDIS_Startup'][k] for t in self.arrTime[1:] for k in [0,2,3,4]), "Mode switching min stay constraint DIS startup")
            self.m.addConstrs(
                (gp.quicksum(self.OptVarCurrentStateDIS[(i,j)] for i in self.arrTime[t:t+self.param.param['constraints']['transitionTimes']['minStayTimeDIS_Standby'][k]] for j in [0,1,3,4]) <= (1 - self.OptVarCurrentStateSwitchDIS[(t,k,2)])*self.param.param['constraints']['transitionTimes']['minStayTimeDIS_Standby'][k] for t in self.arrTime[1:] for k in [0,1,3,4]), "Mode switching min stay constraint DIS standby")
            self.m.addConstrs(
                (gp.quicksum(self.OptVarCurrentStateDIS[(i,j)] for i in self.arrTime[t:t+self.param.param['constraints']['transitionTimes']['minStayTimeDIS_On'][k]] for j in [0,1,2,4]) <= (1 - self.OptVarCurrentStateSwitchDIS[(t,k,3)])*self.param.param['constraints']['transitionTimes']['minStayTimeDIS_On'][k] for t in self.arrTime[1:] for k in [0,1,2,4]), "Mode switching min stay constraint DIS on")
            self.m.addConstrs(
                (gp.quicksum(self.OptVarCurrentStateDIS[(i,j)] for i in self.arrTime[t:t+self.param.param['constraints']['transitionTimes']['minStayTimeDIS_Shutdown'][k]] for j in [0,1,2,3]) <= (1 - self.OptVarCurrentStateSwitchDIS[(t,k,4)])*self.param.param['constraints']['transitionTimes']['minStayTimeDIS_Shutdown'][k] for t in self.arrTime[1:] for k in [0,1,2,3]), "Mode switching min stay constraint DIS shutdown")
            

            ## Maximum stay time per mode
            for j in [1,2,3,4]:
                self.m.addConstrs(
                    ((1 - self.OptVarCurrentStateCO2CAP[(t+self.param.param['constraints']['transitionTimes']['maxStayTimeCO2CAP_Off'][j]+1,0)]) >= self.OptVarCurrentStateSwitchCO2CAP[(t,j,0)] - gp.quicksum(self.OptVarCurrentStateSwitchCO2CAP[(t+i,k,0)] for i in range(self.param.param['constraints']['transitionTimes']['minStayTimeCO2CAP_Off'][j],self.param.param['constraints']['transitionTimes']['maxStayTimeCO2CAP_Off'][j]) for k in [1,2,3,4]) for t in self.arrTime[1:-(self.param.param['constraints']['transitionTimes']['maxStayTimeCO2CAP_Off'][j]+1)]), "Mode switching max stay constraint CO2CAP off")
                self.m.addConstrs(
                    ((1 - self.OptVarCurrentStateSYN[(t+self.param.param['constraints']['transitionTimes']['maxStayTimeSYN_Off'][j]+1,0)]) >= self.OptVarCurrentStateSwitchSYN[(t,j,0)] - gp.quicksum(self.OptVarCurrentStateSwitchSYN[(t+i,k,0)] for i in range(self.param.param['constraints']['transitionTimes']['minStayTimeSYN_Off'][j],self.param.param['constraints']['transitionTimes']['maxStayTimeSYN_Off'][j]) for k in [1,2,3,4]) for t in self.arrTime[1:-(self.param.param['constraints']['transitionTimes']['maxStayTimeSYN_Off'][j]+1)]), "Mode switching max stay constraint SYN off")
                self.m.addConstrs(
                    ((1 - self.OptVarCurrentStateDIS[(t+self.param.param['constraints']['transitionTimes']['maxStayTimeDIS_Off'][j]+1,0)]) >= self.OptVarCurrentStateSwitchDIS[(t,j,0)] - gp.quicksum(self.OptVarCurrentStateSwitchDIS[(t+i,k,0)] for i in range(self.param.param['constraints']['transitionTimes']['minStayTimeDIS_Off'][j],self.param.param['constraints']['transitionTimes']['maxStayTimeDIS_Off'][j]) for k in [1,2,3,4]) for t in self.arrTime[1:-(self.param.param['constraints']['transitionTimes']['maxStayTimeDIS_Off'][j]+1)]), "Mode switching max stay constraint DIS off")

            for j in [0,2,3,4]:
                self.m.addConstrs(
                    ((1 - self.OptVarCurrentStateCO2CAP[(t+self.param.param['constraints']['transitionTimes']['maxStayTimeCO2CAP_Startup'][j]+1,1)]) >= self.OptVarCurrentStateSwitchCO2CAP[(t,j,1)] - gp.quicksum(self.OptVarCurrentStateSwitchCO2CAP[(t+i,k,1)] for i in range(self.param.param['constraints']['transitionTimes']['minStayTimeCO2CAP_Startup'][j],self.param.param['constraints']['transitionTimes']['maxStayTimeCO2CAP_Startup'][j]) for k in [0,2,3,4]) for t in self.arrTime[1:-(self.param.param['constraints']['transitionTimes']['maxStayTimeCO2CAP_Startup'][j]+1)]), "Mode switching max stay constraint CO2CAP startup")
                self.m.addConstrs(
                    ((1 - self.OptVarCurrentStateSYN[(t+self.param.param['constraints']['transitionTimes']['maxStayTimeSYN_Startup'][j]+1,1)]) >= self.OptVarCurrentStateSwitchSYN[(t,j,1)] - gp.quicksum(self.OptVarCurrentStateSwitchSYN[(t+i,k,1)] for i in range(self.param.param['constraints']['transitionTimes']['minStayTimeSYN_Startup'][j],self.param.param['constraints']['transitionTimes']['maxStayTimeSYN_Startup'][j]) for k in [0,2,3,4]) for t in self.arrTime[1:-(self.param.param['constraints']['transitionTimes']['maxStayTimeSYN_Startup'][j]+1)]), "Mode switching max stay constraint SYN startup")
                self.m.addConstrs(
                    ((1 - self.OptVarCurrentStateDIS[(t+self.param.param['constraints']['transitionTimes']['maxStayTimeDIS_Startup'][j]+1,1)]) >= self.OptVarCurrentStateSwitchDIS[(t,j,1)] - gp.quicksum(self.OptVarCurrentStateSwitchDIS[(t+i,k,1)] for i in range(self.param.param['constraints']['transitionTimes']['minStayTimeDIS_Startup'][j],self.param.param['constraints']['transitionTimes']['maxStayTimeDIS_Startup'][j]) for k in [0,2,3,4]) for t in self.arrTime[1:-(self.param.param['constraints']['transitionTimes']['maxStayTimeDIS_Startup'][j]+1)]), "Mode switching max stay constraint DIS startup")

            for j in [0,1,3,4]:
                self.m.addConstrs(
                    ((1 - self.OptVarCurrentStateCO2CAP[(t+self.param.param['constraints']['transitionTimes']['maxStayTimeCO2CAP_Standby'][j]+1,2)]) >= self.OptVarCurrentStateSwitchCO2CAP[(t,j,2)] - gp.quicksum(self.OptVarCurrentStateSwitchCO2CAP[(t+i,k,2)] for i in range(self.param.param['constraints']['transitionTimes']['minStayTimeCO2CAP_Standby'][j],self.param.param['constraints']['transitionTimes']['maxStayTimeCO2CAP_Standby'][j]) for k in [0,1,3,4]) for t in self.arrTime[1:-(self.param.param['constraints']['transitionTimes']['maxStayTimeCO2CAP_Standby'][j]+1)]), "Mode switching max stay constraint CO2CAP standby")  
                self.m.addConstrs(
                    ((1 - self.OptVarCurrentStateSYN[(t+self.param.param['constraints']['transitionTimes']['maxStayTimeSYN_Standby'][j]+1,2)]) >= self.OptVarCurrentStateSwitchSYN[(t,j,2)] - gp.quicksum(self.OptVarCurrentStateSwitchSYN[(t+i,k,2)] for i in range(self.param.param['constraints']['transitionTimes']['minStayTimeSYN_Standby'][j],self.param.param['constraints']['transitionTimes']['maxStayTimeSYN_Standby'][j]) for k in [0,1,3,4]) for t in self.arrTime[1:-(self.param.param['constraints']['transitionTimes']['maxStayTimeSYN_Standby'][j]+1)]), "Mode switching max stay constraint SYN standby")  
                self.m.addConstrs(
                    ((1 - self.OptVarCurrentStateDIS[(t+self.param.param['constraints']['transitionTimes']['maxStayTimeDIS_Standby'][j]+1,2)]) >= self.OptVarCurrentStateSwitchDIS[(t,j,2)] - gp.quicksum(self.OptVarCurrentStateSwitchDIS[(t+i,k,2)] for i in range(self.param.param['constraints']['transitionTimes']['minStayTimeDIS_Standby'][j],self.param.param['constraints']['transitionTimes']['maxStayTimeDIS_Standby'][j]) for k in [0,1,3,4]) for t in self.arrTime[1:-(self.param.param['constraints']['transitionTimes']['maxStayTimeDIS_Off'][j]+1)]), "Mode switching max stay constraint DIS standby")

            for j in [0,1,2,4]:
                self.m.addConstrs(
                    ((1 - self.OptVarCurrentStateCO2CAP[(t+self.param.param['constraints']['transitionTimes']['maxStayTimeCO2CAP_On'][j]+1,3)]) >= self.OptVarCurrentStateSwitchCO2CAP[(t,j,3)] - gp.quicksum(self.OptVarCurrentStateSwitchCO2CAP[(t+i,k,3)] for i in range(self.param.param['constraints']['transitionTimes']['minStayTimeCO2CAP_On'][j],self.param.param['constraints']['transitionTimes']['maxStayTimeCO2CAP_On'][j]) for k in [0,1,2,4]) for t in self.arrTime[1:-(self.param.param['constraints']['transitionTimes']['maxStayTimeCO2CAP_On'][j]+1)]), "Mode switching max stay constraint CO2CAP on")
                self.m.addConstrs(
                    ((1 - self.OptVarCurrentStateSYN[(t+self.param.param['constraints']['transitionTimes']['maxStayTimeSYN_On'][j]+1,3)]) >= self.OptVarCurrentStateSwitchSYN[(t,j,3)] - gp.quicksum(self.OptVarCurrentStateSwitchSYN[(t+i,k,3)] for i in range(self.param.param['constraints']['transitionTimes']['minStayTimeSYN_On'][j],self.param.param['constraints']['transitionTimes']['maxStayTimeSYN_On'][j]) for k in [0,1,2,4]) for t in self.arrTime[1:-(self.param.param['constraints']['transitionTimes']['maxStayTimeSYN_On'][j]+1)]), "Mode switching max stay constraint SYN on")
                self.m.addConstrs(
                    ((1 - self.OptVarCurrentStateDIS[(t+self.param.param['constraints']['transitionTimes']['maxStayTimeDIS_On'][j]+1,3)]) >= self.OptVarCurrentStateSwitchDIS[(t,j,3)] - gp.quicksum(self.OptVarCurrentStateSwitchDIS[(t+i,k,3)] for i in range(self.param.param['constraints']['transitionTimes']['minStayTimeDIS_On'][j],self.param.param['constraints']['transitionTimes']['maxStayTimeDIS_On'][j]) for k in [0,1,2,4]) for t in self.arrTime[1:-(self.param.param['constraints']['transitionTimes']['maxStayTimeDIS_On'][j]+1)]), "Mode switching max stay constraint DIS on")
                
            for j in [0,1,2,3]:
                self.m.addConstrs(
                    ((1 - self.OptVarCurrentStateCO2CAP[(t+self.param.param['constraints']['transitionTimes']['maxStayTimeCO2CAP_Shutdown'][j]+1,4)]) >= self.OptVarCurrentStateSwitchCO2CAP[(t,j,4)] - gp.quicksum(self.OptVarCurrentStateSwitchCO2CAP[(t+i,k,4)] for i in range(self.param.param['constraints']['transitionTimes']['minStayTimeCO2CAP_Shutdown'][j],self.param.param['constraints']['transitionTimes']['maxStayTimeCO2CAP_Shutdown'][j]) for k in [0,1,2,4]) for t in self.arrTime[1:-(self.param.param['constraints']['transitionTimes']['maxStayTimeCO2CAP_Shutdown'][j]+1)]), "Mode switching max stay constraint CO2CAP shutdown")               
                self.m.addConstrs(
                    ((1 - self.OptVarCurrentStateSYN[(t+self.param.param['constraints']['transitionTimes']['maxStayTimeSYN_Shutdown'][j]+1,4)]) >= self.OptVarCurrentStateSwitchSYN[(t,j,4)] - gp.quicksum(self.OptVarCurrentStateSwitchSYN[(t+i,k,4)] for i in range(self.param.param['constraints']['transitionTimes']['minStayTimeSYN_Shutdown'][j],self.param.param['constraints']['transitionTimes']['maxStayTimeSYN_Shutdown'][j]) for k in [0,1,2,4]) for t in self.arrTime[1:-(self.param.param['constraints']['transitionTimes']['maxStayTimeSYN_Shutdown'][j]+1)]), "Mode switching max stay constraint SYN shutdown")               
                self.m.addConstrs(
                    ((1 - self.OptVarCurrentStateDIS[(t+self.param.param['constraints']['transitionTimes']['maxStayTimeDIS_Shutdown'][j]+1,4)]) >= self.OptVarCurrentStateSwitchDIS[(t,j,4)] - gp.quicksum(self.OptVarCurrentStateSwitchDIS[(t+i,k,4)] for i in range(self.param.param['constraints']['transitionTimes']['minStayTimeDIS_Shutdown'][j],self.param.param['constraints']['transitionTimes']['maxStayTimeDIS_Shutdown'][j]) for k in [0,1,2,3]) for t in self.arrTime[1:-(self.param.param['constraints']['transitionTimes']['maxStayTimeDIS_Shutdown'][j]+1)]), "Mode switching max stay constraint DIS shutdown")               
               

            ## Mode switching constraints
            # CO2-Capture
            self.m.addConstrs(
                (self.OptVarCurrentStateCO2CAP[(t-1,i)] >= self.OptVarCurrentStateSwitchCO2CAP[(t,i,j)] for t in self.arrTime[1:] for i in range(0,5) for j in range(0,5)), "Mode switching CO2-Capture 1")
            self.m.addConstrs(
                (self.OptVarCurrentStateCO2CAP[(t,j)] >= self.OptVarCurrentStateSwitchCO2CAP[(t,i,j)] for t in self.arrTime[0:] for i in range(0,5) for j in range(0,5)), "Mode switching CO2-Capture 2")
            self.m.addConstrs(
                (self.OptVarCurrentStateCO2CAP[(t-1,i)] + self.OptVarCurrentStateCO2CAP[(t,j)] - 1 <= self.OptVarCurrentStateSwitchCO2CAP[(t,i,j)] for t in self.arrTime[1:] for i in range(0,5) for j in range(0,5)), "Mode switching CO2-Capture 3")
            
            # Synthesis
            self.m.addConstrs(
                (self.OptVarCurrentStateSYN[(t-1,i)] >= self.OptVarCurrentStateSwitchSYN[(t,i,j)] for t in self.arrTime[1:] for i in range(0,5) for j in range(0,5)), "Mode switching Synthesis 1")
            self.m.addConstrs(
                (self.OptVarCurrentStateSYN[(t,j)] >= self.OptVarCurrentStateSwitchSYN[(t,i,j)] for t in self.arrTime[0:] for i in range(0,5) for j in range(0,5)), "Mode switching Synthesis 2")
            self.m.addConstrs(
                (self.OptVarCurrentStateSYN[(t-1,i)] + self.OptVarCurrentStateSYN[(t,j)] - 1 <= self.OptVarCurrentStateSwitchSYN[(t,i,j)] for t in self.arrTime[1:] for i in range(0,5) for j in range(0,5)), "Mode switching Synthesis 3")

            # DIS 
            self.m.addConstrs(
                (self.OptVarCurrentStateDIS[(t-1,i)] >= self.OptVarCurrentStateSwitchDIS[(t,i,j)] for t in self.arrTime[1:] for i in range(0,5) for j in range(0,5)), "Mode switching DIS 1")
            self.m.addConstrs(
                (self.OptVarCurrentStateDIS[(t,j)] >= self.OptVarCurrentStateSwitchDIS[(t,i,j)] for t in self.arrTime[0:] for i in range(0,5) for j in range(0,5)), "Mode switching DIS 2")
            self.m.addConstrs(
                (self.OptVarCurrentStateDIS[(t-1,i)] + self.OptVarCurrentStateDIS[(t,j)] - 1 <= self.OptVarCurrentStateSwitchDIS[(t,i,j)] for t in self.arrTime[1:] for i in range(0,5) for j in range(0,5)), "Mode switching DIS 3")

            
            # Forbidden transitions
            self.m.addConstrs(
                (self.OptVarCurrentStateSwitchCO2CAP[(t,0,j)] == 0 for t in self.arrTime for j in [2,3,4]), 'Forbidden transition from state off CO2CAP')
            self.m.addConstrs(
                (self.OptVarCurrentStateSwitchCO2CAP[(t,1,j)] == 0 for t in self.arrTime for j in [0,4]), 'Forbidden transition from state startup CO2CAP')
            self.m.addConstrs(
                (self.OptVarCurrentStateSwitchCO2CAP[(t,2,j)] == 0 for t in self.arrTime for j in [0,3]), 'Forbidden transition from state standby CO2CAP')
            self.m.addConstrs(
                (self.OptVarCurrentStateSwitchCO2CAP[(t,3,j)] == 0 for t in self.arrTime for j in [0,1,2]), 'Forbidden transition from state on CO2CAP')
            self.m.addConstrs(
                (self.OptVarCurrentStateSwitchCO2CAP[(t,4,j)] == 0 for t in self.arrTime for j in [1,3]), 'Forbidden transition from state shutdown CO2CAP')
            
            self.m.addConstrs(
                (self.OptVarCurrentStateSwitchSYN[(t,0,j)] == 0 for t in self.arrTime for j in [2,3,4]), 'Forbidden transition from state off SYN')
            self.m.addConstrs(
                (self.OptVarCurrentStateSwitchSYN[(t,1,j)] == 0 for t in self.arrTime for j in [0,4]), 'Forbidden transition from state startup SYN')
            self.m.addConstrs(
                (self.OptVarCurrentStateSwitchSYN[(t,2,j)] == 0 for t in self.arrTime for j in [0,3]), 'Forbidden transition from state standby SYN')
            self.m.addConstrs(
                (self.OptVarCurrentStateSwitchSYN[(t,3,j)] == 0 for t in self.arrTime for j in [0,1,2]), 'Forbidden transition from state on SYN')
            self.m.addConstrs(
                (self.OptVarCurrentStateSwitchSYN[(t,4,j)] == 0 for t in self.arrTime for j in [1,3]), 'Forbidden transition from state shutdown SYN')
            
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
                (self.OptVarCurrentStateSwitchCO2CAP[(t-self.param.param['constraints']['transitionTimes']['minStayTimeCO2CAP_Shutdown'][2],2,4)] == self.OptVarCurrentStateSwitchCO2CAP[(t,4,0)] for t in self.arrTime[self.param.param['constraints']['transitionTimes']['minStayTimeCO2CAP_Shutdown'][2]:]), 'Forbidden transition from state standby CO2CAP SYN')
            self.m.addConstrs(
                (self.OptVarCurrentStateSwitchSYN[(t-self.param.param['constraints']['transitionTimes']['minStayTimeSYN_Shutdown'][2],2,4)] == self.OptVarCurrentStateSwitchSYN[(t,4,0)] for t in self.arrTime[self.param.param['constraints']['transitionTimes']['minStayTimeSYN_Shutdown'][2]:]), 'Forbidden transition from state standby SYN SYN')
            self.m.addConstrs(
                (self.OptVarCurrentStateSwitchDIS[(t-self.param.param['constraints']['transitionTimes']['minStayTimeDIS_Shutdown'][2],2,4)] == self.OptVarCurrentStateSwitchDIS[(t,4,0)] for t in self.arrTime[self.param.param['constraints']['transitionTimes']['minStayTimeDIS_Shutdown'][2]:]), 'Forbidden transition from state standby DIS')
    

        ## Operating points per case
        self.m.addConstrs(
            (self.OptVarCurrentStateCO2CAP[(t,0)] == self.OptVarOperationPointCO2CAP[(t,0)] for t in self.arrTime), 'One operation point in case off for CO2CAP')
        self.m.addConstrs(
            (self.OptVarCurrentStateSYN[(t,0)] == self.OptVarOperationPointSYN[(t,0)] for t in self.arrTime), 'One operation point in case off for SYN')
        self.m.addConstrs(
            (self.OptVarCurrentStateDIS[(t,0)] == self.OptVarOperationPointDIS[(t,0)] for t in self.arrTime), 'One operation point in case off for DIS')

        self.m.addConstrs(
            (self.OptVarCurrentStateCO2CAP[(t,1)] == self.OptVarOperationPointCO2CAP[(t,1)] for t in self.arrTime), 'One operation point in case startup for CO2CAP')
        self.m.addConstrs(
            (self.OptVarCurrentStateSYN[(t,1)] == self.OptVarOperationPointSYN[(t,1)] for t in self.arrTime), 'One operation point in case startup for SYN')
        self.m.addConstrs(
            (self.OptVarCurrentStateDIS[(t,1)] == self.OptVarOperationPointDIS[(t,1)] for t in self.arrTime), 'One operation point in case startup for DIS')

        self.m.addConstrs(
            (self.OptVarCurrentStateCO2CAP[(t,2)] == self.OptVarOperationPointCO2CAP[(t,2)] for t in self.arrTime), 'One operation point in case standby for CO2CAP')
        self.m.addConstrs(
            (self.OptVarCurrentStateSYN[(t,2)] == self.OptVarOperationPointSYN[(t,2)] for t in self.arrTime), 'One operation point in case standby for SYN')
        self.m.addConstrs(
            (self.OptVarCurrentStateDIS[(t,2)] == self.OptVarOperationPointDIS[(t,2)] for t in self.arrTime), 'One operation point in case standby for DIS')
        
        self.m.addConstrs(
            (self.OptVarCurrentStateCO2CAP[(t,3)] == gp.quicksum(self.OptVarOperationPointCO2CAP[(t,j)] for j in cm.arrOperationPointsCO2CAP[4:]) for t in self.arrTime), 'One operation point in case on for CO2CAP')
        self.m.addConstrs(
            (self.OptVarCurrentStateSYN[(t,3)] == gp.quicksum(self.OptVarOperationPointSYN[(t,j)] for j in cm.arrOperationPointsSYN[4:]) for t in self.arrTime), 'One operation point in case on for SYN')
        self.m.addConstrs(
            (self.OptVarCurrentStateDIS[(t,3)] == gp.quicksum(self.OptVarOperationPointDIS[(t,j)] for j in cm.arrOperationPointsDIS[4:]) for t in self.arrTime), 'One operation point in case on for DIS')
        
        self.m.addConstrs(
            (self.OptVarCurrentStateCO2CAP[(t,4)] == self.OptVarOperationPointCO2CAP[(t,3)] for t in self.arrTime), 'One operation point in case shutdown for CO2CAP')
        self.m.addConstrs(
            (self.OptVarCurrentStateSYN[(t,4)] == self.OptVarOperationPointSYN[(t,3)] for t in self.arrTime), 'One operation point in case shutdown for SYN')
        self.m.addConstrs(
            (self.OptVarCurrentStateDIS[(t,4)] == self.OptVarOperationPointDIS[(t,3)] for t in self.arrTime), 'One operation point in case shutdown for DIS')
        

        # CO2-Capture and Synthesis are connected
        self.m.addConstrs(
            (self.OptVarOperationPointCO2CAP[(t,j)] == self.OptVarOperationPointSYN[(t,j)] for j in cm.arrOperationPointsCO2CAP[4:] for t in self.arrTime), 'Coupling of CO2-Capture and Synthesis')


        ## PV considered
        if self.param.param['controlParameters']['considerPV'] == False:
            self.m.addConstrs(
                self.OptVarUsageOfPV[t] == 0 for t in self.arrTime)
            #self.m.addConstrs(
            #    self.OptVarPowerInBatteryPV[t] == 0 for t in self.arrTime)

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
            gp.quicksum(self.OptVarPowerElectrolyser[(t,n)] * self.OptVarModeElectrolyser[(t,n,3)] * fTimeStep for n in elec.arrEnapterModules)
            + gp.quicksum(elec.dictPowerElectrolyserMode[(n,m)] * self.OptVarModeElectrolyser[(t,n,m)] * fTimeStep for n in elec.arrEnapterModules for m in elec.arrModes[:-1])
            + cm.powerPlantComponentsUnit1[0] * self.OptVarOperationPointCO2CAP[(t,0)] * self.OptVarCurrentStateCO2CAP[(t,0)] * fTimeStep
            + cm.powerPlantComponentsUnit1[1] * self.OptVarOperationPointCO2CAP[(t,1)] * self.OptVarCurrentStateCO2CAP[(t,1)] * fTimeStep 
            + cm.powerPlantComponentsUnit1[2] * self.OptVarOperationPointCO2CAP[(t,2)] * self.OptVarCurrentStateCO2CAP[(t,2)] * fTimeStep 
            + gp.quicksum(cm.powerPlantComponentsUnit1[(j)] * self.OptVarOperationPointCO2CAP[(t,j)] * self.OptVarCurrentStateCO2CAP[(t,3)] * fTimeStep for j in cm.arrOperationPointsCO2CAP[4:])
            + cm.powerPlantComponentsUnit1[3] * self.OptVarOperationPointCO2CAP[(t,3)] * self.OptVarCurrentStateCO2CAP[(t,4)] * fTimeStep
            + cm.powerPlantComponentsUnit2[0] * self.OptVarOperationPointSYN[(t,0)] * self.OptVarCurrentStateSYN[(t,0)] * fTimeStep
            + cm.powerPlantComponentsUnit2[1] * self.OptVarOperationPointSYN[(t,1)] * self.OptVarCurrentStateSYN[(t,1)] * fTimeStep 
            + cm.powerPlantComponentsUnit2[2] * self.OptVarOperationPointSYN[(t,2)] * self.OptVarCurrentStateSYN[(t,2)] * fTimeStep 
            + gp.quicksum(cm.powerPlantComponentsUnit2[(j)] * self.OptVarOperationPointSYN[(t,j)] * self.OptVarCurrentStateSYN[(t,3)] * fTimeStep for j in cm.arrOperationPointsSYN[4:])
            + cm.powerPlantComponentsUnit2[3] * self.OptVarOperationPointSYN[(t,3)] * self.OptVarCurrentStateSYN[(t,4)] * fTimeStep
            + cm.powerPlantComponentsUnit3[0] * self.OptVarOperationPointDIS[(t,0)] * self.OptVarCurrentStateDIS[(t,0)] * fTimeStep
            + cm.powerPlantComponentsUnit3[1] * self.OptVarOperationPointDIS[(t,1)] * self.OptVarCurrentStateDIS[(t,1)] * fTimeStep
            + cm.powerPlantComponentsUnit3[2] * self.OptVarOperationPointDIS[(t,2)] * self.OptVarCurrentStateDIS[(t,2)] * fTimeStep
            + gp.quicksum(cm.powerPlantComponentsUnit3[(j)] * self.OptVarOperationPointDIS[(t,j)] * self.OptVarCurrentStateDIS[(t,3)] * fTimeStep for j in cm.arrOperationPointsDIS[4:])
            + cm.powerPlantComponentsUnit3[3] * self.OptVarOperationPointDIS[(t,3)] * self.OptVarCurrentStateDIS[(t,4)] * fTimeStep
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
        # Exactly one operation point for CO2-Capture has to be selected in every time step
        self.m.addConstrs(
            (self.OptVarOperationPointCO2CAP.sum(t,'*') == 1 for t in self.arrTime), "Exactly one operation point for CO2-Capture per time step")
        # Exactly one operation point for Synthesis has to be selected in every time step
        self.m.addConstrs(
            (self.OptVarOperationPointSYN.sum(t,'*') == 1 for t in self.arrTime), "Exactly one operation point for Synthesis per time step")
        # Exactly one operation point for distillation has to be selected in every time step
        self.m.addConstrs(
            (self.OptVarOperationPointDIS.sum(t,'*') == 1 for t in self.arrTime), "Exactly one operation point for distillation per time step")
        # Exactly one state of CO2-Capture in every time step
        self.m.addConstrs(
            (self.OptVarCurrentStateCO2CAP.sum(t,'*') == 1 for t in self.arrTime), "Exactly one state for CO2-Capture per time step")
        # Exactly one state of CO2-Capture and synthesis in every time step
        self.m.addConstrs(
            (self.OptVarCurrentStateSYN.sum(t,'*') == 1 for t in self.arrTime), "Exactly one state for Synthesis per time step")
        # Exactly one state of distillation in every time step
        self.m.addConstrs(
            (self.OptVarCurrentStateDIS.sum(t,'*') == 1 for t in self.arrTime), "Exactly one state for distillation per time step")    
        # Exactly one operation point for electrolyser has to be selected in every time step
        self.m.addConstrs(
            (gp.quicksum(self.OptVarModeElectrolyser[(t,n,m)] for m in elec.arrModes) == 1 for t in self.arrTime for n in elec.arrEnapterModules), "One operation mode for electrolyser per time period")





        ## Initial time step constraints

        # No operation point for Synthesis in initial time step
        self.m.addConstr(
            (self.OptVarOperationPointCO2CAP[(0,self.param.param['startValues']['operatingPointCO2CAP'])] == 1), "No operation point for CO2-Capture in initial time step")
        # No operation point for CO2-Capture in initial time step
        self.m.addConstr(
            (self.OptVarOperationPointSYN[(0,self.param.param['startValues']['operatingPointSYN'])] == 1), "No operation point for Synthesis in initial time step")
        # No operation point for distillation in initial time step
        self.m.addConstr(
            (self.OptVarOperationPointDIS[(0,self.param.param['startValues']['operatingPointDIS'])] == 1), "No operation point for distillation in initial time step")
        # CO2-Capture is off in initial time step
        self.m.addConstr(
            (self.OptVarCurrentStateCO2CAP[(0,self.param.param['startValues']['stateCO2CAP'])] == 1), "State is off for CO2-Capture in initial time step")
        # Synthesis is off in initial time step
        self.m.addConstr(
            (self.OptVarCurrentStateSYN[(0,self.param.param['startValues']['stateSYN'])] == 1), "State is off for COSynthesis in initial time step")
        # Distillation is off in initial time step
        self.m.addConstr(
            (self.OptVarCurrentStateDIS[(0,self.param.param['startValues']['stateDIS'])] == 1), "State is off for distillation in initial time step")     
        # No power in electrolyser in initial time step
        self.m.addConstrs(
            (self.OptVarModeElectrolyser[(0,n,self.param.param['startValues']['modeElectrolyser'][j])] == 1 for n in elec.arrEnapterModules), "Electrolyser modules are off at the beginning")

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
        pressure_level_storage_H2 = []
        
        for t in self.arrTime:
        # Precompute constant terms

            # Calculate intermediate expressions
            electrolyser_sum = electrolyser_sum + gp.quicksum(self.OptVarPowerElectrolyser[(t,n)] * self.OptVarModeElectrolyser[(t,n,3)] * electrolyser_constant for n in elec.arrEnapterModules)
            hydrogen_in_sum = hydrogen_in_sum + (cm.massFlowHydrogenInCO2CAP[0] * self.OptVarOperationPointCO2CAP[(t,0)] * self.OptVarCurrentStateCO2CAP[(t,0)] * fTimeStep
                                                + cm.massFlowHydrogenInCO2CAP[1] * self.OptVarOperationPointCO2CAP[(t,1)] * self.OptVarCurrentStateCO2CAP[(t,1)] * fTimeStep
                                                + cm.massFlowHydrogenInCO2CAP[2] * self.OptVarOperationPointCO2CAP[(t,2)] * self.OptVarCurrentStateCO2CAP[(t,2)] * fTimeStep
                                                + gp.quicksum(cm.massFlowHydrogenInCO2CAP[j] * self.OptVarOperationPointCO2CAP[(t,j)] * self.OptVarCurrentStateCO2CAP[(t,3)] * fTimeStep for j in cm.arrOperationPointsCO2CAP[4:])
                                                + cm.massFlowHydrogenInCO2CAP[3] * self.OptVarOperationPointCO2CAP[(t,3)] * self.OptVarCurrentStateCO2CAP[(t,4)] * fTimeStep
                                                + cm.massFlowHydrogenInSYN[0] * self.OptVarOperationPointSYN[(t,0)] * self.OptVarCurrentStateSYN[(t,0)] * fTimeStep
                                                + cm.massFlowHydrogenInSYN[1] * self.OptVarOperationPointSYN[(t,1)] * self.OptVarCurrentStateSYN[(t,1)] * fTimeStep
                                                + cm.massFlowHydrogenInSYN[2] * self.OptVarOperationPointSYN[(t,2)] * self.OptVarCurrentStateSYN[(t,2)] * fTimeStep
                                                + gp.quicksum(cm.massFlowHydrogenInSYN[j] * self.OptVarOperationPointSYN[(t,j)] * self.OptVarCurrentStateSYN[(t,3)] * fTimeStep for j in cm.arrOperationPointsSYN[4:])
                                                + cm.massFlowHydrogenInSYN[3] * self.OptVarOperationPointSYN[(t,3)] * self.OptVarCurrentStateSYN[(t,4)] * fTimeStep)

            pressure_level_storage_H2.append((self.param.param['storageH2']['InitialFilling'] + electrolyser_sum - hydrogen_in_sum) * R_H2_Tamb_T0 * storage_volume_factor)

            # Create the constraint
            self.m.addConstr(
                pressure_level_storage_H2[t] <= self.param.param['storageH2']['UpperBound'], f"Storage H2 upper bound at time {t}")
            self.m.addConstr(
                pressure_level_storage_H2[t] >= self.param.param['storageH2']['LowerBound'], f"Storage H2 lower bound at time {t}")
            #self.m.addConstr(
            #    (self.param.param['storageH2']['InitialFilling'] + electrolyser_sum - hydrogen_in_sum) * R_H2_Tamb_T0 * storage_volume_factor <= self.param.param['storageH2']['UpperBound'], f"Storage H2 upper bound at time {t}")       
            #self.m.addConstr(
            #    (self.param.param['storageH2']['InitialFilling'] + electrolyser_sum - hydrogen_in_sum) * R_H2_Tamb_T0 * storage_volume_factor >= self.param.param['storageH2']['LowerBound'], f"Storage H2 lower bound at time {t}")
        
        self.m.addConstr(
            (self.param.param['constraints']['hydrogenStorageEqualValue'] - pressure_level_storage_H2[self.param.param['constraints']['hydrogenStorageEqualTime']] <= self.param.param['constraints']['hydrogenStorageFillEqual']['LowerBound']), "Storage H2 equal filling upper bound")
        self.m.addConstr(
            (self.param.param['constraints']['hydrogenStorageEqualValue'] - pressure_level_storage_H2[self.param.param['constraints']['hydrogenStorageEqualTime']] >= self.param.param['constraints']['hydrogenStorageFillEqual']['UpperBound']), "Storage H2 equal filling lower bound")
        


        ## Methanol water storage constraints
        methanol_water_mass_flow_in = 0
        methanol_water_mass_flow_out = 0
        filling_level_storage_methanol_water = []
        
        for t in self.arrTime:
        # Precompute constant terms

            # Calculate intermediate expressions
            methanol_water_mass_flow_in = methanol_water_mass_flow_in + (cm.massFlowMethanolWaterStorageIn[(0)] / self.param.param['storageMethanolWater']['InitialDensity'] * self.OptVarOperationPointSYN[(t,0)] * self.OptVarCurrentStateSYN[(t,0)] * fTimeStep
                                                                        + cm.massFlowMethanolWaterStorageIn[(1)] / self.param.param['storageMethanolWater']['InitialDensity'] * self.OptVarOperationPointSYN[(t,1)] * self.OptVarCurrentStateSYN[(t,1)] * fTimeStep
                                                                        + cm.massFlowMethanolWaterStorageIn[(2)] / self.param.param['storageMethanolWater']['InitialDensity'] * self.OptVarOperationPointSYN[(t,2)] * self.OptVarCurrentStateSYN[(t,2)] * fTimeStep
                                                                        + gp.quicksum(cm.massFlowMethanolWaterStorageIn[(j)] / self.param.param['storageMethanolWater']['InitialDensity'] * self.OptVarOperationPointSYN[(t,j)] * self.OptVarCurrentStateSYN[(t,3)] * fTimeStep for j in cm.arrOperationPointsSYN[4:])
                                                                        + cm.massFlowMethanolWaterStorageIn[(3)] / self.param.param['storageMethanolWater']['InitialDensity'] * self.OptVarOperationPointSYN[(t,3)] * self.OptVarCurrentStateSYN[(t,4)] * fTimeStep)
            
            methanol_water_mass_flow_out = methanol_water_mass_flow_out + (cm.massFlowMethanolWaterStorageOut[(0)] / self.param.param['storageMethanolWater']['InitialDensity'] * self.OptVarOperationPointDIS[(t,0)] * self.OptVarCurrentStateDIS[(t,0)] * fTimeStep
                                                                        + cm.massFlowMethanolWaterStorageOut[(1)] / self.param.param['storageMethanolWater']['InitialDensity'] * self.OptVarOperationPointDIS[(t,1)] * self.OptVarCurrentStateDIS[(t,1)] * fTimeStep
                                                                        + cm.massFlowMethanolWaterStorageOut[(2)] / self.param.param['storageMethanolWater']['InitialDensity'] * self.OptVarOperationPointDIS[(t,2)] * self.OptVarCurrentStateDIS[(t,2)] * fTimeStep
                                                                        + gp.quicksum(cm.massFlowMethanolWaterStorageOut[(j)] / self.param.param['storageMethanolWater']['InitialDensity'] * self.OptVarOperationPointDIS[(t,j)] * self.OptVarCurrentStateDIS[(t,3)] * fTimeStep for j in cm.arrOperationPointsDIS[4:])
                                                                        + cm.massFlowMethanolWaterStorageOut[(3)] / self.param.param['storageMethanolWater']['InitialDensity'] * self.OptVarOperationPointDIS[(t,3)] * self.OptVarCurrentStateDIS[(t,4)] * fTimeStep)

            filling_level_storage_methanol_water.append(self.param.param['storageMethanolWater']['InitialFilling'] + methanol_water_mass_flow_in - methanol_water_mass_flow_out)
            
            # Create the constraint
            self.m.addConstr(
                filling_level_storage_methanol_water[t] <= self.param.param['storageMethanolWater']['UpperBound'], f"Storage methanol water upper bound at time {t}")
            self.m.addConstr(
                filling_level_storage_methanol_water[t] >= self.param.param['storageMethanolWater']['LowerBound'], f"Storage methanol water lower bound at time {t}")
            #self.m.addConstr(
            #    self.param.param['storageMethanolWater']['InitialFilling'] + methanol_water_mass_flow_in - methanol_water_mass_flow_out <= self.param.param['storageMethanolWater']['UpperBound'], f"Storage methanol water upper bound at time {t}") 
            #self.m.addConstr(
            #    self.param.param['storageMethanolWater']['InitialFilling'] + methanol_water_mass_flow_in - methanol_water_mass_flow_out >= self.param.param['storageMethanolWater']['LowerBound'], f"Storage methanol water lower bound at time {t}")
        

        self.m.addConstr(
            (self.param.param['constraints']['methanolWaterStorageEqualValue'] - filling_level_storage_methanol_water[self.param.param['constraints']['methanolWaterStorageEqualTime']] <= self.param.param['constraints']['methanolWaterStorageFillEqual']['LowerBound']), "Storage H2 equal filling upper bound")
        self.m.addConstr(
            (self.param.param['constraints']['methanolWaterStorageEqualValue'] - filling_level_storage_methanol_water[self.param.param['constraints']['methanolWaterStorageEqualTime']] >= self.param.param['constraints']['methanolWaterStorageFillEqual']['UpperBound']), "Storage H2 equal filling lower bound")



        ## Battery constraints
        battery_power = self.param.param['battery']['power']
        battery_min_charge = self.param.param['battery']['minCharge']
        battery_initial_charge = self.param.param['battery']['initialCharge']
        battery_fill_equal_lb = battery_initial_charge*self.param.param['constraints']['storagesFactorFillEqualLower']
        battery_fill_equal_ub = -battery_initial_charge*self.param.param['constraints']['storagesFactorFillEqualUpper'] 

        battery_in = 0
        battery_out = 0
        battery_charge = []
        
        for t in self.arrTime:
        # Precompute constant terms

            # Calculate intermediate expressions
            battery_in = battery_in + (self.OptVarActualPowerInBatteryPV[t] * self.param.param['battery']['efficiency']
                                    + self.OptVarActualPowerInBatteryBought[t] * self.param.param['battery']['efficiency'])
            
            battery_out = battery_out + (self.OptVarActualPowerOutBattery[t]
                                      + self.OptVarActualPowerOutBatterySold[t])
            
            battery_charge.append(battery_initial_charge + battery_in - battery_out)
            
            # Create the constraint
            self.m.addConstr(
                battery_charge[t] <= battery_power, f"Battery upper bound")
            self.m.addConstr(
                battery_charge[t] >= battery_min_charge, f"Battery lower bound")


        self.m.addConstr(
            (self.param.param['constraints']['batteryChargeEqualValue'] - battery_charge[self.param.param['constraints']['batteryChargeEqualTime']] <= battery_fill_equal_lb), "Battery equal charge upper bound")
        self.m.addConstr(
            (self.param.param['constraints']['batteryChargeEqualValue'] - battery_charge[self.param.param['constraints']['batteryChargeEqualTime']] >= battery_fill_equal_ub), "Battery equal charge lower bound")

        

        