#!/usr/bin/env python3.10

from characteristic_fields import *

import gurobipy as gp
from gurobipy import GRB
from gurobipy import *

class Optimization_Model():

    def __init__(self, param):
        self.funcUpdate(param)


    def funcUpdate(self, param):
        self.param = param
        self.arrTime = list(range(0,self.param.param['controlParameters']['numberOfTimeSteps']+1))


    def funcCreateOptimizationModel(self, cm, elec, pv, pp):

        self.m = gp.Model('ptm')
        self.m.ModelSense = GRB.MINIMIZE

        self.funcCreateVariables(cm, elec, pv, pp)
        self.funcCreateConstraints(cm, elec, pv, pp)
        self.funcCreateCostFunction(cm, elec, pv, pp)

        self.m.update()



    def funcRunOptimization(self):
        self.m.Params.TimeLimit = self.param.param['controlParameters']['timeLimit']
        self.m.Params.MIPGap = self.param.param['controlParameters']['optimalityGap']
        self.m.Params.LogToConsole = 1
        if self.param.param['controlParameters']['testFeasibility'] == True:
            self.m.computeIIS()
            self.m.write("model.ilp")
        
        self.m.optimize()



    ########## Variables ##########
    def funcCreateVariables(self, cm, elec, pv, pp):
        self.OptVarOperationPointABSDES = self.m.addVars(self.arrTime,cm.arrOperationPointsABSDES, vtype=GRB.BINARY)
        self.OptVarOperationPointMEOHSYN = self.m.addVars(self.arrTime,cm.arrOperationPointsMEOHSYN, vtype=GRB.BINARY)
        self.OptVarOperationPointDIS = self.m.addVars(self.arrTime,cm.arrOperationPointsDIS, vtype=GRB.BINARY)
        self.OptVarOperationPointSwitch = self.m.addVars(self.arrTime,[1,2,3],vtype=GRB.BINARY)

        self.OptVarPowerElectrolyser = self.m.addVars(self.arrTime,self.param.param['electrolyser']['numberOfEnapterModules'],lb=self.param.param['electrolyser']['powerLowerBound'], ub=self.param.param['electrolyser']['powerUpperBound'],vtype=GRB.CONTINUOUS)
        self.OptVarElectrolyserMode = self.m.addVars(self.arrTime,self.param.param['electrolyser']['numberOfEnapterModules'],4, vtype=GRB.BINARY)
        self.OptVarUsageOfPV = self.m.addVars(self.arrTime,lb=0.0,ub=1000,vtype=GRB.CONTINUOUS)
        self.OptVarPowerInBatteryPV = self.m.addVars(self.arrTime,lb=0,ub=self.param.param['battery']['maxChargeRate'], vtype=GRB.CONTINUOUS)
        self.OptVarPowerInBatteryBought = self.m.addVars(self.arrTime,lb=0,ub=self.param.param['battery']['maxChargeRate'], vtype=GRB.CONTINUOUS)
        self.OptVarPowerOutBattery = self.m.addVars(self.arrTime,lb=0,ub=self.param.param['battery']['maxDischargeRate'], vtype=GRB.CONTINUOUS)
        self.OptVarPowerOutBatterySold = self.m.addVars(self.arrTime,lb=0,ub=self.param.param['battery']['maxDischargeRate'], vtype=GRB.CONTINUOUS)
        self.OptVarPowerBought = self.m.addVars(self.arrTime,lb=0.0,ub=100,vtype=GRB.CONTINUOUS)

        if self.param.param['controlParameters']['uncertaintyPV'] == True:
            self.OptVarIndicatorPV = self.m.addVars(range(0,pv.iNumberUncertaintySamples),vtype=GRB.BINARY)

        if self.param.param['controlParameters']['uncertaintyPP'] == True:
            self.OptVarPowerInBatteryBought = self.m.addVars(self.arrTime,range(0,pp.iNumberUncertaintySamples),lb=0,ub=self.param.param['battery']['maxChargeRate'], vtype=GRB.CONTINUOUS)
            self.OptVarPowerOutBattery = self.m.addVars(self.arrTime,range(0,pp.iNumberUncertaintySamples),lb=0,ub=self.param.param['battery']['maxDischargeRate'], vtype=GRB.CONTINUOUS)
            self.OptVarPowerOutBatterySold = self.m.addVars(self.arrTime,range(0,pp.iNumberUncertaintySamples),lb=0,ub=self.param.param['battery']['maxDischargeRate'], vtype=GRB.CONTINUOUS)
            self.OptVarPowerBought = self.m.addVars(self.arrTime,range(0,pp.iNumberUncertaintySamples),lb=0.0,ub=100,vtype=GRB.CONTINUOUS)



    ########## Cost function ##########
    def funcCreateCostFunction(self, cm, elec, pv, pp):
        fTimeStep = self.param.param['controlParameters']['timeStep']

        if self.param.param['controlParameters']['uncertaintyPP'] == False:
            print(cm.massFlowMethanolOut)
            self.m.setObjective(0
                    - gp.quicksum(cm.massFlowMethanolOut[(j)] * self.OptVarOperationPointDIS[(i,j)] * self.param.param['prices']['methanol'] * fTimeStep for i in self.arrTime for j in cm.arrOperationPointsDIS)
                    - gp.quicksum(cm.volumeBiogasOut[(j)] * self.OptVarOperationPointABSDES[(i,j)] * self.param.param['methane']['brennwert'] * self.param.param['prices']['methane'] * fTimeStep for i in self.arrTime for j in cm.arrOperationPointsABSDES)
                    + gp.quicksum(cm.volumeBiogasIn[(j)] * self.OptVarOperationPointABSDES[(i,j)] * self.param.param['biogas']['brennwert'] * self.param.param['prices']['biogas'] * fTimeStep for i in self.arrTime for j in cm.arrOperationPointsABSDES)
                    + gp.quicksum(self.param.param['prices']['power'][i] * self.OptVarPowerBought[i] for i in self.arrTime)
                    - gp.quicksum(self.param.param['prices']['powerSold'] * self.OptVarPowerOutBatterySold[i] for i in self.arrTime))
        
        else:
            self.m.setObjective(- gp.quicksum(cm.massFlowMethanolOut[(j)] * self.OptVarOperationPointDIS[(i,j)] * self.param.param['prices']['methanol'] * fTimeStep for i in self.arrTime for j in cm.arrOperationPointsDIS)
                - gp.quicksum(cm.volumeBiogasOut[(j)] * self.OptVarOperationPointABSDES[(i,j)] * self.param.param['methane']['brennwert'] * self.param.param['prices']['methane'] * fTimeStep for i in self.arrTime for j in cm.arrOperationPointsABSDES)
                + gp.quicksum(cm.volumeBiogasIn[(j)] * self.OptVarOperationPointABSDES[(i,j)] * self.param.param['biogas']['brennwert'] * self.param.param['prices']['biogas'] * fTimeStep for i in self.arrTime for j in cm.arrOperationPointsABSDES)
                + gp.quicksum(pp.powerPriceSamples[r,i] * self.OptVarPowerBought[i,r] * 1/pp.iNumberUncertaintySamples for i in self.arrTime for r in range(0,pp.iNumberUncertaintySamples))
                - gp.quicksum(self.param.param['prices']['powerSold'] * self.OptVarPowerOutBatterySold[i,r] * 1/pp.iNumberUncertaintySamples for i in self.arrTime for r in range(0,pp.iNumberUncertaintySamples)))



    ########## Constraints ##########
    def funcCreateConstraints(self, cm, elec, pv, pp):
        fTimeStep = self.param.param['controlParameters']['timeStep']

        if self.param.param['controlParameters']['benchmark'] == False:
            if self.param.param['controlParameters']['sameOutputAsBenchmark'] == False:
                self.m.addConstr(
                    (gp.quicksum(cm.massFlowMethanolOut[(j)] * self.OptVarOperationPointDIS[(t,j)] * fTimeStep for j in cm.arrOperationPointsDIS for t in self.arrTime) >= self.param.param['methanol']['minimumAmountOpt']), "Minimum amount methanol produced")    
            else:
                self.m.addConstr(
                    (gp.quicksum(cm.massFlowMethanolOut[(j)] * self.OptVarOperationPointDIS[(t,j)] * fTimeStep for j in cm.arrOperationPointsDIS for t in self.arrTime) <= self.param.param['methanol']['sameAmountBenchmark']*1.01), "Amount methanol produced is same as benchmark upper bound") 
                self.m.addConstr(
                    (gp.quicksum(cm.massFlowMethanolOut[(j)] * self.OptVarOperationPointDIS[(t,j)] * fTimeStep for j in cm.arrOperationPointsDIS for t in self.arrTime) >= self.param.param['methanol']['sameAmountBenchmark']), "Amount methanol produced is same as benchmark lower bound")    
                self.m.addConstr(
                    (gp.quicksum(cm.volumeBiogasOut[(j)] * self.OptVarOperationPointABSDES[(t,j)] * fTimeStep for j in cm.arrOperationPointsABSDES for t in self.arrTime) <= self.param.param['methane']['sameAmountVolumeBenchmark']*1.01), "Amount methane (volume) produced is same as benchmark upper bound")    
                self.m.addConstr(
                    (gp.quicksum(cm.volumeBiogasOut[(j)] * self.OptVarOperationPointABSDES[(t,j)] * fTimeStep for j in cm.arrOperationPointsABSDES for t in self.arrTime) >= self.param.param['methane']['sameAmountVolumeBenchmark']), "Amount methane (volume) produced is same as benchmark lower bound") 

        if self.param.param['controlParameters']['benchmark'] == True:
            # Minimum amount of methanol which has to be produced
            self.m.addConstr(
                (gp.quicksum(cm.massFlowMethanolOut[(j)] * self.OptVarOperationPointDIS[(t,j)] * fTimeStep for j in cm.arrOperationPointsDIS for t in self.arrTime) >= self.param.param['methanol']['minimumAmountBenchmark']), "Minimum amount methanol produced benchmark")
            # The same operation point for absorption and desorption for every time step
            self.m.addConstrs(
                (self.OptVarOperationPointABSDES[(t-1,j)] == self.OptVarOperationPointABSDES[(t,j)] for t in self.arrTime[2:] for j in cm.arrOperationPointsABSDES), "Benchmark operation point absorption, desorption and methanolsynthesis")
            # The same operation point for distillation for every time step
            self.m.addConstrs(
                (self.OptVarOperationPointDIS[(t-1,j)] == self.OptVarOperationPointDIS[(t,j)] for t in self.arrTime[2:] for j in cm.arrOperationPointsDIS), "Benchmark operation point distillation")
            # The same operation point for methanol synthesis for every time step
            self.m.addConstrs(
                (self.OptVarOperationPointMEOHSYN[(t-1,j)] == self.OptVarOperationPointMEOHSYN[(t,j)] for t in self.arrTime[2:] for j in cm.arrOperationPointsMEOHSYN), "Benchmark operation point methanol synthesis")
            # The same power in electrolyser for every time step
            self.m.addConstrs(
                (self.OptVarPowerElectrolyser[(t-1,n)] == self.OptVarPowerElectrolyser[(t,n)] for t in self.arrTime[2:] for n in elec.arrEnapterModules), "Benchmark power electrolyser")
            self.m.addConstrs(
                (self.OptVarElectrolyserMode[(t-1,n,m)] == self.OptVarElectrolyserMode[(t,n,m)] for t in self.arrTime[3:] for n in elec.arrEnapterModules for m in elec.arrModes), "Benchmark power electrolyser")

            
        if self.param.param['controlParameters']['benchmark'] == False:
            if self.param.param['controlParameters']['transitionConstraints'] == True:
                ## Minimum stay time per mode constraints
                self.m.addConstrs(
                    (gp.quicksum(self.OptVarOperationPointABSDES[(i,j)] for i in self.arrTime[t:t+self.param.param['constraints']['transitionTimes']['minimumStayTimeABSDES']] for j in cm.arrOperationPointsABSDES[1:]) >= self.OptVarOperationPointSwitch[(t,1)]*self.param.param['constraints']['transitionTimes']['minimumStayTimeABSDES'] for t in self.arrTime[1:]), "Mode switching minimum stay constraint ABSDES")
                self.m.addConstrs(
                    (gp.quicksum(self.OptVarOperationPointMEOHSYN[(i,j)] for i in self.arrTime[t:t+self.param.param['constraints']['transitionTimes']['minimumStayTimeMEOHSYN']] for j in cm.arrOperationPointsMEOHSYN[1:]) >= self.OptVarOperationPointSwitch[(t,2)]*self.param.param['constraints']['transitionTimes']['minimumStayTimeMEOHSYN'] for t in self.arrTime[1:]), "Mode switching minimum stay constraint MEOHSYN")
                self.m.addConstrs(
                    (gp.quicksum(self.OptVarOperationPointDIS[(i,j)] for i in self.arrTime[t:t+self.param.param['constraints']['transitionTimes']['minimumStayTimeDIS']] for j in cm.arrOperationPointsDIS[1:]) >= self.OptVarOperationPointSwitch[(t,3)]*self.param.param['constraints']['transitionTimes']['minimumStayTimeDIS'] for t in self.arrTime[1:]), "Mode switching minimum stay constraint DIS")
                
                
                ## Maximum stay time per mode constraints
                self.m.addConstrs(
                    ((1 - gp.quicksum(self.OptVarOperationPointABSDES[(t+self.param.param['constraints']['transitionTimes']['maximumStayTimeABSDES'],j)] for j in cm.arrOperationPointsABSDES[1:])) >= self.OptVarOperationPointSwitch[(t,1)] - gp.quicksum(self.OptVarOperationPointABSDES[(t+i,0,0)] for i in range(self.param.param['constraints']['transitionTimes']['minimumStayTimeABSDES'],self.param.param['constraints']['transitionTimes']['maximumStayTimeABSDES'])) for t in self.arrTime[1:-(self.param.param['constraints']['transitionTimes']['maximumStayTimeABSDES'])]), "Mode switching maximum stay constraint mode ABSDES")
                self.m.addConstrs(
                    ((1 - gp.quicksum(self.OptVarOperationPointMEOHSYN[(t+self.param.param['constraints']['transitionTimes']['maximumStayTimeMEOHSYN'],j)] for j in cm.arrOperationPointsMEOHSYN[1:])) >= self.OptVarOperationPointSwitch[(t,2)] - gp.quicksum(self.OptVarOperationPointMEOHSYN[(t+i,0)] for i in range(self.param.param['constraints']['transitionTimes']['minimumStayTimeMEOHSYN'],self.param.param['constraints']['transitionTimes']['maximumStayTimeMEOHSYN'])) for t in self.arrTime[1:-(self.param.param['constraints']['transitionTimes']['maximumStayTimeMEOHSYN'])]), "Mode switching maximum stay constraint mode MEOHSYN")
                self.m.addConstrs(
                    ((1 - gp.quicksum(self.OptVarOperationPointDIS[(t+self.param.param['constraints']['transitionTimes']['maximumStayTimeDIS'],j)] for j in cm.arrOperationPointsDIS[1:])) >= self.OptVarOperationPointSwitch[(t,3)] - gp.quicksum(self.OptVarOperationPointDIS[(t+i,0)] for i in range(self.param.param['constraints']['transitionTimes']['minimumStayTimeDIS'],self.param.param['constraints']['transitionTimes']['maximumStayTimeDIS'])) for t in self.arrTime[1:-(self.param.param['constraints']['transitionTimes']['maximumStayTimeDIS'])]), "Mode switching maximum stay constraint mode DIS")


            ## Mode switching constraints
            self.m.addConstrs(
                (self.OptVarOperationPointABSDES[(t-1,0)] >= self.OptVarOperationPointSwitch[(t,1)] for t in self.arrTime[1:]), "Mode switching ABSDES 1")
            self.m.addConstrs(
                (gp.quicksum(self.OptVarOperationPointABSDES[(t,j)] for j in cm.arrOperationPointsABSDES[1:]) >= self.OptVarOperationPointSwitch[(t,1)] for t in self.arrTime[0:]), "Mode switching ABSDES 2")
            self.m.addConstrs(
                (self.OptVarOperationPointABSDES[(t-1,0)] + gp.quicksum(self.OptVarOperationPointABSDES[(t,j)] for j in cm.arrOperationPointsABSDES[1:]) - 1 <= self.OptVarOperationPointSwitch[(t,1)] for t in self.arrTime[1:]), "Mode switching ABSDES 3")

            self.m.addConstrs(
                (self.OptVarOperationPointMEOHSYN[(t-1,0)] >= self.OptVarOperationPointSwitch[(t,2)] for t in self.arrTime[1:]), "Mode switching MEOHSYN 1")
            self.m.addConstrs(
                (gp.quicksum(self.OptVarOperationPointMEOHSYN[(t,j)] for j in cm.arrOperationPointsMEOHSYN[1:]) >= self.OptVarOperationPointSwitch[(t,2)] for t in self.arrTime[0:]), "Mode switching MEOHSYN 2")
            self.m.addConstrs(
                (self.OptVarOperationPointMEOHSYN[(t-1,0)] + gp.quicksum(self.OptVarOperationPointMEOHSYN[(t,j)] for j in cm.arrOperationPointsMEOHSYN[1:]) - 1 <= self.OptVarOperationPointSwitch[(t,2)] for t in self.arrTime[1:]), "Mode switching MEOHSYN 3")

            self.m.addConstrs(
                (self.OptVarOperationPointDIS[(t-1,0)] >= self.OptVarOperationPointSwitch[(t,3)] for t in self.arrTime[1:]), "Mode switching DIS 1")
            self.m.addConstrs(
                (gp.quicksum(self.OptVarOperationPointDIS[(t,j)] for j in cm.arrOperationPointsDIS[1:]) >= self.OptVarOperationPointSwitch[(t,3)] for t in self.arrTime[0:]), "Mode switching DIS 2")
            self.m.addConstrs(
                (self.OptVarOperationPointDIS[(t-1,0)] + gp.quicksum(self.OptVarOperationPointDIS[(t,j)] for j in cm.arrOperationPointsDIS[1:]) - 1 <= self.OptVarOperationPointSwitch[(t,3)] for t in self.arrTime[1:]), "Mode switching DIS 3")

        ## PV considered
        if self.param.param['controlParameters']['considerPV'] == False:
            self.m.addConstrs(
                self.OptVarUsageOfPV[t] == 0 for t in self.arrTime)
            self.m.addConstrs(
                self.OptVarPowerInBatteryPV[t] == 0 for t in self.arrTime)

        ## Battery considered
        if self.param.param['controlParameters']['considerBattery'] == False:
            self.m.addConstrs(
                self.OptVarPowerInBatteryBought[t] == 0 for t in self.arrTime)
            self.m.addConstrs(
                self.OptVarPowerInBatteryPV[t] == 0 for t in self.arrTime)
            self.m.addConstrs(
                self.OptVarPowerOutBattery[t] == 0 for t in self.arrTime)
            self.m.addConstrs(
                self.OptVarPowerOutBatterySold[t] == 0 for t in self.arrTime)
            
        ## Power Constraints

        if self.param.param['controlParameters']['uncertaintyPP'] == True:
            # power from battery and PV and grid to electrolyser and components must equal to needed power
            self.m.addConstrs(
                (self.OptVarPowerOutBattery[t,r] + self.OptVarUsageOfPV[t] + self.OptVarPowerBought[t,r] - self.OptVarPowerInBatteryBought[t,r] == (
                gp.quicksum(self.OptVarPowerElectrolyser[(t,n)] * self.OptVarElectrolyserMode[(t,n,3)] * fTimeStep for n in elec.arrEnapterModules)
                + gp.quicksum(elec.dictPowerElectrolyserMode[(n,m)] * self.OptVarElectrolyserMode[(t,n,m)] * fTimeStep for n in elec.arrEnapterModules for m in elec.arrModes[:-1])
                + gp.quicksum(cm.powerPlantComponentsUnit1[(j)] * self.OptVarOperationPointABSDES[(t,j)] * fTimeStep for j in cm.arrOperationPointsABSDES)
                + gp.quicksum(cm.powerPlantComponentsUnit2[(j)] * self.OptVarOperationPointMEOHSYN[(t,j)] * fTimeStep for j in cm.arrOperationPointsMEOHSYN)
                + gp.quicksum(cm.powerPlantComponentsUnit3[(j)] * self.OptVarOperationPointDIS[(t,j)] * fTimeStep for j in cm.arrOperationPointsDIS))
                for t in self.arrTime[1:] for r in range(0,pp.iNumberUncertaintySamples)), "Battery output maximum")

            # Power to battery has always to be smaller than power bought
            self.m.addConstrs(
                (self.OptVarPowerInBatteryBought[t,r] <= self.OptVarPowerBought[t,r] for t in self.arrTime[1:] for r in range(0,pp.iNumberUncertaintySamples)), "Power to battery has always to be smaller than power bought")

            # Power can not be sold and bought at the same time
            self.m.addConstrs(
                (self.OptVarPowerBought[t,r] * self.OptVarPowerOutBatterySold[t,r] == 0 for t in self.arrTime[1:] for r in range(0,pp.iNumberUncertaintySamples)), "Power can not be sold and bought at the same time")
        
            # Battery can not be discharged and charged at the same time
            self.m.addConstrs(
                (self.OptVarPowerInBatteryBought[t,r] * self.OptVarPowerOutBattery[t,r] == 0 for t in self.arrTime[1:] for r in range(0,pp.iNumberUncertaintySamples)), "Battery charge and discharge time 1")
            self.m.addConstrs(
                (self.OptVarPowerInBatteryPV[t] * self.OptVarPowerOutBattery[t,r] == 0 for t in self.arrTime[1:] for r in range(0,pp.iNumberUncertaintySamples)), "Battery charge and discharge time 2")
            self.m.addConstrs(
                (self.OptVarPowerInBatteryPV[t] * self.OptVarPowerOutBatterySold[t,r] == 0 for t in self.arrTime[1:] for r in range(0,pp.iNumberUncertaintySamples)), "Battery charge and discharge time 3")
            
            # Charge and discharge rate have to be smaller than maximum rate
            self.m.addConstrs(
                (self.OptVarPowerInBatteryBought[t,r] + self.OptVarPowerInBatteryPV[t] <= self.param.param['battery']['maxChargeRate'] for t in self.arrTime[1:] for r in range(0,pp.iNumberUncertaintySamples)), "Battery charge rate")
            self.m.addConstrs(
                (self.OptVarPowerOutBattery[t,r] + self.OptVarPowerOutBatterySold[t,r] <= self.param.param['battery']['maxDischargeRate'] for t in self.arrTime[1:] for r in range(0,pp.iNumberUncertaintySamples)), "Battery discharge rate")
            
             # Power cannot be sold
            if self.param.param['controlParameters']['powerSale'] == False:
                self.m.addConstrs(
                    (self.OptVarPowerOutBatterySold[t,r] == 0 for t in self.arrTime[1:] for r in range(0,pp.iNumberUncertaintySamples)), "No power can be sold")
            
        else:
            # power from battery and PV and grid to electrolyser and components must equal to needed power
            self.m.addConstrs(
                (self.OptVarPowerOutBattery[t] + self.OptVarUsageOfPV[t] + self.OptVarPowerBought[t] - self.OptVarPowerInBatteryBought[t] == (
                gp.quicksum(self.OptVarPowerElectrolyser[(t,n)] * self.OptVarElectrolyserMode[(t,n,3)] * fTimeStep for n in elec.arrEnapterModules)
                + gp.quicksum(elec.dictPowerElectrolyserMode[(n,m)] * self.OptVarElectrolyserMode[(t,n,m)] * fTimeStep for n in elec.arrEnapterModules for m in elec.arrModes[:-1])
                + gp.quicksum(cm.powerPlantComponentsUnit1[(j)] * self.OptVarOperationPointABSDES[(t,j)] * fTimeStep for j in cm.arrOperationPointsABSDES)
                + gp.quicksum(cm.powerPlantComponentsUnit2[(j)] * self.OptVarOperationPointMEOHSYN[(t,j)] * fTimeStep for j in cm.arrOperationPointsMEOHSYN)
                + gp.quicksum(cm.powerPlantComponentsUnit3[(j)] * self.OptVarOperationPointDIS[(t,j)] * fTimeStep for j in cm.arrOperationPointsDIS))
                for t in self.arrTime[1:]), "Battery output maximum")

            # Power to battery has always to be smaller than power bought
            self.m.addConstrs(
                (self.OptVarPowerInBatteryBought[t] <= self.OptVarPowerBought[t] for t in self.arrTime[1:]), "Power to battery has always to be smaller than power bought")

            # Power can not be sold and bought at the same time
            self.m.addConstrs(
                (self.OptVarPowerBought[t] * self.OptVarPowerOutBatterySold[t] == 0 for t in self.arrTime[1:]), "Power can not be sold and bought at the same time")
            
            # Battery can not be discharged and charged at the same time
            self.m.addConstrs(
                (self.OptVarPowerInBatteryBought[t] * self.OptVarPowerOutBattery[t] == 0 for t in self.arrTime[1:]), "Battery charge and discharge time 1")
            self.m.addConstrs(
                (self.OptVarPowerInBatteryPV[t] * self.OptVarPowerOutBattery[t] == 0 for t in self.arrTime[1:]), "Battery charge and discharge time 2")
            self.m.addConstrs(
                (self.OptVarPowerInBatteryPV[t] * self.OptVarPowerOutBatterySold[t] == 0 for t in self.arrTime[1:]), "Battery charge and discharge time 3")
            
            # Charge and discharge rate have to be smaller than maximum rate
            self.m.addConstrs(
                (self.OptVarPowerInBatteryBought[t] + self.OptVarPowerInBatteryPV[t] <= self.param.param['battery']['maxChargeRate'] for t in self.arrTime[1:]), "Battery charge rate")
            self.m.addConstrs(
                (self.OptVarPowerOutBattery[t] + self.OptVarPowerOutBatterySold[t] <= self.param.param['battery']['maxDischargeRate'] for t in self.arrTime[1:]), "Battery discharge rate")
            
             # Power cannot be sold
            if self.param.param['controlParameters']['powerSale'] == False:
                self.m.addConstrs(
                    (self.OptVarPowerOutBatterySold[t] == 0 for t in self.arrTime[1:]), "No power can be sold")
                

        # Power used from PV and stored in battery from PV must be equal or smaller than power available from PV
        if self.param.param['controlParameters']['uncertaintyPV'] == True:
            self.m.addConstrs(
                (self.OptVarUsageOfPV[i] + self.OptVarPowerInBatteryPV[i] <= pv.pvSamples[r,i] + 1000*(1-self.OptVarIndicatorPV[r]) for i in self.arrTime[1:] for r in range(0,pv.iNumberUncertaintySamples)), "PV upper bound available")
            self.m.addConstr(
                (gp.quicksum(self.OptVarIndicatorPV[r] for r in range(0,pv.iNumberUncertaintySamples)) >= pv.alpha*pv.iNumberUncertaintySamples), 'Indicator PV')
        else:
            self.m.addConstrs(
                (self.OptVarUsageOfPV[i] + self.OptVarPowerInBatteryPV[i] <= pv.arrPowerAvailable[i] for i in self.arrTime[1:]), "PV upper bound available")



        ## Minimum operation point/operation mode constraint
        # Exactly one operation point for absorption, desorption and methanol synthesis has to be selected in every time step
        self.m.addConstrs(
            (self.OptVarOperationPointABSDES.sum(t,'*','*') == 1.0 for t in self.arrTime), "Exactly one operation point for absorption, desorption and methanol synthesis per time step")
        # Exactly one operation point for methanol synthesis has to be selected every time step
        self.m.addConstrs(
            (self.OptVarOperationPointMEOHSYN.sum(t,'*') == 1.0 for t in self.arrTime), "Exactly one operation point for methanol synthesis per time step")
        # Exactly one operation point for distillation has to be selected in every time step
        self.m.addConstrs(
            (self.OptVarOperationPointDIS.sum(t,'*') == 1.0 for t in self.arrTime), "Exactly one operation point for distillation per time step")
        # Exactly one operation point for electrolyser has to be selected in every time step
        self.m.addConstrs(
            (gp.quicksum(self.OptVarElectrolyserMode[(t,n,m)] for m in elec.arrModes) == 1 for t in self.arrTime for n in elec.arrEnapterModules), "one operation mode for electrolyser per time period")


        ## Initial time step constraints
        # No operation point for absorption, desorption and methanol synthesis in initial time step
        self.m.addConstr(
            (self.OptVarOperationPointABSDES[(0,0)] == 1), "No operation point for absorption, desorption and methanol synthesis in initial time step")
        # No operation point for methanol synthesis in initial time step
        self.m.addConstr(
            (self.OptVarOperationPointMEOHSYN[(0,0)] == 1), "No operation point for methanol synthesis in initial time step")
        # No operation point for distillation in initial time step
        self.m.addConstr(
            (self.OptVarOperationPointDIS[(0,0)] == 1), "No operation point for distillation in initial time step")
        # No power in electrolyser in initial time step
        self.m.addConstrs(
            (self.OptVarElectrolyserMode[(0,n,2)] == 1 for n in elec.arrEnapterModules), "Electrolyser modules are off at the beginning")
        # No input or output for battery in first time step
        self.m.addConstr(
            (self.OptVarPowerInBatteryPV[0] == 0), "PV in battery initial time step")
        
        if self.param.param['controlParameters']['uncertaintyPP'] == True:
            self.m.addConstrs(
                (self.OptVarPowerInBatteryBought[0,r] == 0 for r in range(0,pp.iNumberUncertaintySamples)), "Power bought battery initial time step")
            self.m.addConstrs(
                (self.OptVarPowerOutBattery[0,r] == 0 for r in range(0,pp.iNumberUncertaintySamples)), "power out battery initial time step")
            self.m.addConstrs(
                (self.OptVarPowerOutBatterySold[0,r] == 0 for r in range(0,pp.iNumberUncertaintySamples)), "power sold battery initial time step")
        else:
            self.m.addConstr(
                (self.OptVarPowerInBatteryBought[0] == 0), "Power bought battery initial time step")
            self.m.addConstr(
                (self.OptVarPowerOutBattery[0] == 0), "power out battery initial time step")
            self.m.addConstr(
                (self.OptVarPowerOutBatterySold[0] == 0), "power sold battery initial time step")



        ## Electrolyser constraints
        self.m.addConstrs(
            (self.OptVarElectrolyserMode[(t-1,n,0)] <= self.OptVarElectrolyserMode[(t,n,3)] for t in self.arrTime[1:] for n in elec.arrEnapterModules), "Electrolyser after off comes off or ramp-up")
        self.m.addConstrs(
            (self.OptVarElectrolyserMode[(t-1,n,1)] <= gp.quicksum(self.OptVarElectrolyserMode[(t,n,m)] for m in [2,3]) for t in self.arrTime[1:] for n in elec.arrEnapterModules), "Electrolyser after off comes off or ramp-up")
        self.m.addConstrs(
            (self.OptVarElectrolyserMode[(t-1,n,2)] <= gp.quicksum(self.OptVarElectrolyserMode[(t,n,m)] for m in [0,2]) for t in self.arrTime[1:] for n in elec.arrEnapterModules), "Electrolyser after off comes off or ramp-up")
        self.m.addConstrs(
            (self.OptVarElectrolyserMode[(t-1,n,3)] <= gp.quicksum(self.OptVarElectrolyserMode[(t,n,m)] for m in [1,2,3]) for t in self.arrTime[1:] for n in elec.arrEnapterModules), "Electrolyser after off comes off or ramp-up")


        ## Hydrogen storage constraints
        self.m.addConstrs(
            ((self.param.param['storageH2']['InitialFilling'] 
                + gp.quicksum(self.OptVarPowerElectrolyser[(l,n)] * self.OptVarElectrolyserMode[(l,n,3)] * self.param.param['electrolyser']['constant'] * fTimeStep for l in self.arrTime[0:t+1] for n in elec.arrEnapterModules)
                - gp.quicksum(cm.massFlowHydrogenIn[(j)] * self.OptVarOperationPointABSDES[(l,j)] * fTimeStep for j in cm.arrOperationPointsABSDES for l in self.arrTime[0:t+1]) 
                - gp.quicksum(cm.massFlowAdditionalHydrogen[(j)] * self.OptVarOperationPointABSDES[(l,j)] * fTimeStep for j in cm.arrOperationPointsABSDES for l in self.arrTime[0:t+1])) 
                * self.param.param['R_H2'] * (self.param.param['Tamb'] + self.param.param['T0']) / (self.param.param['storageH2']['Volume'] * 100000) <= self.param.param['storageH2']['UpperBound'] for t in self.arrTime), "Storage H2 upper bound")
        self.m.addConstrs(
            ((self.param.param['storageH2']['InitialFilling'] 
                + gp.quicksum(self.OptVarPowerElectrolyser[(l,n)] * self.OptVarElectrolyserMode[(l,n,3)] * self.param.param['electrolyser']['constant'] * fTimeStep for l in self.arrTime[0:t+1] for n in elec.arrEnapterModules)
                - gp.quicksum(cm.massFlowHydrogenIn[(j)] * self.OptVarOperationPointABSDES[(l,j)] * fTimeStep for j in cm.arrOperationPointsABSDES for l in self.arrTime[0:t+1]) 
                - gp.quicksum(cm.massFlowAdditionalHydrogen[(j)] * self.OptVarOperationPointABSDES[(l,j)] * fTimeStep for j in cm.arrOperationPointsABSDES for l in self.arrTime[0:t+1])) 
                * self.param.param['R_H2'] * (self.param.param['Tamb'] + self.param.param['T0']) / (self.param.param['storageH2']['Volume'] * 100000) >= self.param.param['storageH2']['LowerBound'] for t in self.arrTime), "Storage H2 lower bound")
        self.m.addConstr(
            ((self.param.param['storageH2']['InitialFilling'] * self.param.param['R_H2'] * (self.param.param['Tamb'] + self.param.param['T0']) / (self.param.param['storageH2']['Volume'] * 100000)) -
                (self.param.param['storageH2']['InitialFilling'] + gp.quicksum(self.OptVarPowerElectrolyser[(t,n)] * self.OptVarElectrolyserMode[(t,n,3)] * self.param.param['electrolyser']['constant'] * fTimeStep for t in self.arrTime for n in elec.arrEnapterModules)
                - gp.quicksum(cm.massFlowHydrogenIn[(j)] * self.OptVarOperationPointABSDES[(t,j)] * fTimeStep for j in cm.arrOperationPointsABSDES for t in self.arrTime) 
                - gp.quicksum(cm.massFlowAdditionalHydrogen[(j)] * self.OptVarOperationPointABSDES[(t,j)] * fTimeStep for j in cm.arrOperationPointsABSDES for t in self.arrTime)) 
                * self.param.param['R_H2'] * (self.param.param['Tamb'] + self.param.param['T0']) / (self.param.param['storageH2']['Volume'] * 100000) <= self.param.param['constraints']['hydrogenStorageFillEqual']['UpperBound']), "Storage H2 equal filling upper bound")
        self.m.addConstr(
            ((self.param.param['storageH2']['InitialFilling'] * self.param.param['R_H2'] * (self.param.param['Tamb'] + self.param.param['T0']) / (self.param.param['storageH2']['Volume'] * 100000)) -
                (self.param.param['storageH2']['InitialFilling'] + gp.quicksum(self.OptVarPowerElectrolyser[(t,n)] * self.OptVarElectrolyserMode[(t,n,3)] * self.param.param['electrolyser']['constant'] * fTimeStep for t in self.arrTime for n in elec.arrEnapterModules)
                - gp.quicksum(cm.massFlowHydrogenIn[(j)] * self.OptVarOperationPointABSDES[(t,j)] * fTimeStep for j in cm.arrOperationPointsABSDES for t in self.arrTime) 
                - gp.quicksum(cm.massFlowAdditionalHydrogen[(j)] * self.OptVarOperationPointABSDES[(t,j)] * fTimeStep for j in cm.arrOperationPointsABSDES for t in self.arrTime)) 
                * self.param.param['R_H2'] * (self.param.param['Tamb'] + self.param.param['T0']) / (self.param.param['storageH2']['Volume'] * 100000) >= self.param.param['constraints']['hydrogenStorageFillEqual']['LowerBound']), "Storage H2 equal filling lower bound")


        ## Methanol water storage constraints
        self.m.addConstrs(
            ((self.param.param['storageMethanolWater']['InitialFilling'] 
                + gp.quicksum(cm.massFlowMethanolWaterStorageInSynthesis[(i)] / self.param.param['storageMethanolWater']['InitialDensity'] * self.OptVarOperationPointMEOHSYN[(l,i)] * fTimeStep for i in cm.arrOperationPointsMEOHSYN for l in self.arrTime[0:t+1]) 
                - gp.quicksum(cm.massFlowMethanolWaterStorageOut[(i)] / self.param.param['storageMethanolWater']['InitialDensity'] * self.OptVarOperationPointDIS[(l,i)] * fTimeStep for i in cm.arrOperationPointsDIS for l in self.arrTime[0:t+1])) >= self.param.param['storageMethanolWater']['LowerBound'] for t in self.arrTime), "Storage methanol water lower bound")
        self.m.addConstrs(
            ((self.param.param['storageMethanolWater']['InitialFilling'] 
                + gp.quicksum(cm.massFlowMethanolWaterStorageInSynthesis[(i)] / cm.densityMethanolWaterStorageInSynthesis[(i)] * self.OptVarOperationPointMEOHSYN[(l,i)] * fTimeStep for i in cm.arrOperationPointsMEOHSYN for l in self.arrTime[0:t+1])  
                - gp.quicksum(cm.massFlowMethanolWaterStorageOut[(i)] / self.param.param['storageMethanolWater']['InitialDensity'] * self.OptVarOperationPointDIS[(l,i)] * fTimeStep for i in cm.arrOperationPointsDIS for l in self.arrTime[0:t+1])) <= self.param.param['storageMethanolWater']['UpperBound'] for t in self.arrTime), "Storage methanol water upper bound")
        self.m.addConstr(
            (self.param.param['storageMethanolWater']['InitialFilling'] - 
            (self.param.param['storageMethanolWater']['InitialFilling'] 
                + gp.quicksum(cm.massFlowMethanolWaterStorageInSynthesis[(i)] / cm.densityMethanolWaterStorageInSynthesis[(i)] * self.OptVarOperationPointMEOHSYN[(t,i)] * fTimeStep for i in cm.arrOperationPointsMEOHSYN for t in self.arrTime)  
                - gp.quicksum(cm.massFlowMethanolWaterStorageOut[(i)] / self.param.param['storageMethanolWater']['InitialDensity'] * self.OptVarOperationPointDIS[(t,i)] * fTimeStep for i in cm.arrOperationPointsDIS for t in self.arrTime)) <= self.param.param['constraints']['methanolWaterStorageFillEqual']['UpperBound']), "Storage methanol water equal filling upper bound")
        self.m.addConstr(
            (self.param.param['storageMethanolWater']['InitialFilling'] - 
            (self.param.param['storageMethanolWater']['InitialFilling'] 
                + gp.quicksum(cm.massFlowMethanolWaterStorageInSynthesis[(i)] / cm.densityMethanolWaterStorageInSynthesis[(i)] * self.OptVarOperationPointMEOHSYN[(t,i)] * fTimeStep for i in cm.arrOperationPointsMEOHSYN for t in self.arrTime)  
                - gp.quicksum(cm.massFlowMethanolWaterStorageOut[(i)] / self.param.param['storageMethanolWater']['InitialDensity'] * self.OptVarOperationPointDIS[(t,i)] * fTimeStep for i in cm.arrOperationPointsDIS for t in self.arrTime))  >= self.param.param['constraints']['methanolWaterStorageFillEqual']['LowerBound']), "Storage methanol water equal filling lower bound")


        ## Battery constraints
        if self.param.param['controlParameters']['uncertaintyPP'] == True:
            self.m.addConstrs(
                (self.param.param['battery']['initialCharge'] 
                + gp.quicksum(self.OptVarPowerInBatteryPV[l] for l in self.arrTime[0:t+1]) 
                + gp.quicksum(self.OptVarPowerInBatteryBought[l,r] for l in self.arrTime[0:t+1])
                - gp.quicksum(self.OptVarPowerOutBattery[l,r] for l in self.arrTime[0:t+1])
                - gp.quicksum(self.OptVarPowerOutBatterySold[l,r] for l in self.arrTime[0:t+1])
                <= self.param.param['battery']['capacity'] for t in self.arrTime for r in range(0,pp.iNumberUncertaintySamples)), "Battery upper bound")

            self.m.addConstrs(
                (self.param.param['battery']['initialCharge'] 
                + gp.quicksum(self.OptVarPowerInBatteryPV[l] for l in self.arrTime[0:t+1]) 
                + gp.quicksum(self.OptVarPowerInBatteryBought[l,r] for l in self.arrTime[0:t+1])
                - gp.quicksum(self.OptVarPowerOutBattery[l,r] for l in self.arrTime[0:t+1])
                - gp.quicksum(self.OptVarPowerOutBatterySold[l,r] for l in self.arrTime[0:t+1])
                >= self.param.param['battery']['minCharge'] for t in self.arrTime for r in range(0,pp.iNumberUncertaintySamples)), "Battery lower bound")

            self.m.addConstrs(
                (self.param.param['battery']['initialCharge'] - (self.param.param['battery']['initialCharge'] 
                + gp.quicksum(self.OptVarPowerInBatteryPV[t] for t in self.arrTime) 
                + gp.quicksum(self.OptVarPowerInBatteryBought[t,r] for t in self.arrTime)
                - gp.quicksum(self.OptVarPowerOutBattery[t,r] for t in self.arrTime)
                - gp.quicksum(self.OptVarPowerOutBatterySold[t,r] for t in self.arrTime)) <= self.param.param['constraints']['batteryChargeEqual']['UpperBound'] for r in range(0,pp.iNumberUncertaintySamples)), "Battery equal charge upper bound")

            self.m.addConstrs(
                (self.param.param['battery']['initialCharge'] - (self.param.param['battery']['initialCharge'] 
                + gp.quicksum(self.OptVarPowerInBatteryPV[t] for t in self.arrTime) 
                + gp.quicksum(self.OptVarPowerInBatteryBought[t,r] for t in self.arrTime)
                - gp.quicksum(self.OptVarPowerOutBattery[t,r] for t in self.arrTime)
                - gp.quicksum(self.OptVarPowerOutBatterySold[t,r] for t in self.arrTime)) >= self.param.param['constraints']['batteryChargeEqual']['LowerBound'] for r in range(0,pp.iNumberUncertaintySamples)), "Battery equal charge lower bound")
            
        else:
            self.m.addConstrs(
                (self.param.param['battery']['initialCharge'] 
                + gp.quicksum(self.OptVarPowerInBatteryPV[l] for l in self.arrTime[0:t+1]) 
                + gp.quicksum(self.OptVarPowerInBatteryBought[l] for l in self.arrTime[0:t+1])
                - gp.quicksum(self.OptVarPowerOutBattery[l] for l in self.arrTime[0:t+1])
                - gp.quicksum(self.OptVarPowerOutBatterySold[l] for l in self.arrTime[0:t+1])
                <= self.param.param['battery']['capacity'] for t in self.arrTime), "Battery upper bound")

            self.m.addConstrs(
                (self.param.param['battery']['initialCharge'] 
                + gp.quicksum(self.OptVarPowerInBatteryPV[l] for l in self.arrTime[0:t+1]) 
                + gp.quicksum(self.OptVarPowerInBatteryBought[l] for l in self.arrTime[0:t+1])
                - gp.quicksum(self.OptVarPowerOutBattery[l] for l in self.arrTime[0:t+1])
                - gp.quicksum(self.OptVarPowerOutBatterySold[l] for l in self.arrTime[0:t+1])
                >= self.param.param['battery']['capacity']*0.01 for t in self.arrTime), "Battery lower bound")

            self.m.addConstr(
                (self.param.param['battery']['initialCharge'] - (self.param.param['battery']['initialCharge'] 
                + gp.quicksum(self.OptVarPowerInBatteryPV[t] for t in self.arrTime) 
                + gp.quicksum(self.OptVarPowerInBatteryBought[t] for t in self.arrTime)
                - gp.quicksum(self.OptVarPowerOutBattery[t] for t in self.arrTime)
                - gp.quicksum(self.OptVarPowerOutBatterySold[t] for t in self.arrTime)) <= self.param.param['constraints']['batteryChargeEqual']['UpperBound']), "Battery equal charge upper bound")

            self.m.addConstr(
                (self.param.param['battery']['initialCharge'] - (self.param.param['battery']['initialCharge'] 
                + gp.quicksum(self.OptVarPowerInBatteryPV[t] for t in self.arrTime) 
                + gp.quicksum(self.OptVarPowerInBatteryBought[t] for t in self.arrTime)
                - gp.quicksum(self.OptVarPowerOutBattery[t] for t in self.arrTime)
                - gp.quicksum(self.OptVarPowerOutBatterySold[t] for t in self.arrTime)) >= self.param.param['constraints']['batteryChargeEqual']['LowerBound']), "Battery equal charge lower bound")

        ## Synthesisgas storage
        self.m.addConstrs(
            ((self.param.param['storageSynthesisgas']['InitialFilling'] 
                + gp.quicksum(cm.massFlowSynthesisgasIn[(j)] * self.OptVarOperationPointABSDES[(l,j)] * fTimeStep for j in cm.arrOperationPointsABSDES for l in self.arrTime[0:t+1])
                - gp.quicksum(cm.massFlowSynthesisgasOut[(i)] * self.OptVarOperationPointMEOHSYN[(l,i)] * fTimeStep for i in cm.arrOperationPointsMEOHSYN for l in self.arrTime[0:t+1]))
                * self.param.param['R_Synthesisgas'] * (self.param.param['Tamb'] + self.param.param['T0']) / (self.param.param['storageSynthesisgas']['Volume'] * 100000) >= self.param.param['storageSynthesisgas']['LowerBound'] for t in self.arrTime), "Storage synthesis gas lower bound")
        self.m.addConstrs(
            ((self.param.param['storageSynthesisgas']['InitialFilling']  
                + gp.quicksum(cm.massFlowSynthesisgasIn[(j)] * self.OptVarOperationPointABSDES[(l,j)] * fTimeStep for j in cm.arrOperationPointsABSDES for l in self.arrTime[0:t+1])
                - gp.quicksum(cm.massFlowSynthesisgasOut[(i)] * self.OptVarOperationPointMEOHSYN[(l,i)] * fTimeStep for i in cm.arrOperationPointsMEOHSYN for l in self.arrTime[0:t+1])) 
                * self.param.param['R_Synthesisgas'] * (self.param.param['Tamb'] + self.param.param['T0']) / (self.param.param['storageSynthesisgas']['Volume'] * 100000) <= self.param.param['storageSynthesisgas']['UpperBound'] for t in self.arrTime), "Storage synthesis gas upper bound")
        self.m.addConstr(
            ((self.param.param['storageSynthesisgas']['InitialFilling']  * self.param.param['R_Synthesisgas'] * (self.param.param['Tamb'] + self.param.param['T0']) / (self.param.param['storageSynthesisgas']['Volume'] * 100000)) - 
                (self.param.param['storageSynthesisgas']['InitialFilling']  
                + gp.quicksum(cm.massFlowSynthesisgasIn[(j)] * self.OptVarOperationPointABSDES[(t,j)] * fTimeStep for j in cm.arrOperationPointsABSDES for t in self.arrTime)
                - gp.quicksum(cm.massFlowSynthesisgasOut[(i)] * self.OptVarOperationPointMEOHSYN[(t,i)] * fTimeStep for i in cm.arrOperationPointsMEOHSYN for t in self.arrTime))
                * self.param.param['R_Synthesisgas'] * (self.param.param['Tamb'] + self.param.param['T0']) / (self.param.param['storageSynthesisgas']['Volume'] * 100000) <= self.param.param['constraints']['synthesisgasStorageFillEqual']['UpperBound']), "Storage synthesis gas equal filling upper bound")
        self.m.addConstr(
            ((self.param.param['storageSynthesisgas']['InitialFilling'] * self.param.param['R_Synthesisgas'] * (self.param.param['Tamb'] + self.param.param['T0']) / (self.param.param['storageSynthesisgas']['Volume'] * 100000)) - 
            (self.param.param['storageSynthesisgas']['InitialFilling'] 
                + gp.quicksum(cm.massFlowSynthesisgasIn[(j)] * self.OptVarOperationPointABSDES[(t,j)] * fTimeStep for j in cm.arrOperationPointsABSDES for t in self.arrTime)
                - gp.quicksum(cm.massFlowSynthesisgasOut[(i)] * self.OptVarOperationPointMEOHSYN[(t,i)] * fTimeStep for i in cm.arrOperationPointsMEOHSYN for t in self.arrTime))
                * self.param.param['R_Synthesisgas'] * (self.param.param['Tamb'] + self.param.param['T0']) / (self.param.param['storageSynthesisgas']['Volume'] * 100000)  >= self.param.param['constraints']['synthesisgasStorageFillEqual']['LowerBound']), "Storage synthesis gas equal filling lower bound")

            

        ## Production constraints
        # Minimum amount of methane in outflowing biogas
        self.m.addConstrs(
            (gp.quicksum(cm.moleFractionMethaneBiogasOut[(j)] * self.OptVarOperationPointABSDES[(t,j)] for j in cm.arrOperationPointsABSDES) >= self.param.param['constraints']['minMoleFractionCH4BiogasOut'] for t in self.arrTime[1:]), "Mole fraction methane biogas out")
        # Hydrogen to carbon dioxide ratio upper bound
        self.m.addConstrs(
            (gp.quicksum(cm.moleFractionHydrogenSynthesisgas[(j)] / cm.moleFractionCarbondioxideSynthesisgas[(j)] * self.OptVarOperationPointABSDES[(t,j)] for j in cm.arrOperationPointsABSDES) <= self.param.param['constraints']['maxRatioH2_CO2_Synthesisgas'] for t in self.arrTime[1:]), "Hydrogen - carbon dixoide ratio upper bound")
        # Hydrogen to carbon dioxide ratio lower bound
        self.m.addConstrs(
            (gp.quicksum(cm.moleFractionHydrogenSynthesisgas[(j)] / cm.moleFractionCarbondioxideSynthesisgas[(j)] * self.OptVarOperationPointABSDES[(t,j)] for j in cm.arrOperationPointsABSDES) >= self.param.param['constraints']['minRatioH2_CO2_Synthesisgas'] for t in self.arrTime[1:]), "Hydrogen - carbon dixoide ratio lower bound")


        ## Rate of change constraints
        if self.param.param['controlParameters']['rateOfChangeConstranints'] == True:
            # Distillation (mass flow methanol water from storage)
            self.m.addConstrs(
                ((gp.quicksum(cm.massFlowMethanolWaterStorageOut[(j)] * self.OptVarOperationPointDIS[(t-1,j)] * fTimeStep for j in cm.arrOperationPointsDIS)) - gp.quicksum((cm.massFlowMethanolWaterStorageOut[(j)] * self.OptVarOperationPointDIS[(t,j)] * fTimeStep for j in cm.arrOperationPointsDIS)) >= self.param.param['constraints']['operationPointChange']['distillationUpwardBound'] * fTimeStep for t in self.arrTime[1:]), "Operation point change distillation upward bound")
            self.m.addConstrs(
                ((gp.quicksum(cm.massFlowMethanolWaterStorageOut[(j)] * self.OptVarOperationPointDIS[(t-1,j)] * fTimeStep for j in cm.arrOperationPointsDIS)) - gp.quicksum((cm.massFlowMethanolWaterStorageOut[(j)] * self.OptVarOperationPointDIS[(t,j)] * fTimeStep for j in cm.arrOperationPointsDIS)) <= self.param.param['constraints']['operationPointChange']['distillationDownwardBound'] * fTimeStep for t in self.arrTime[1:]), "Operation point change distillation downward bound")

            # Methanol synthesis (mass flow synthesis gas)
            self.m.addConstrs(
                ((gp.quicksum(cm.massFlowSynthesisgasOut[(j)] * self.OptVarOperationPointMEOHSYN[(t-1,j)] * fTimeStep for j in cm.arrOperationPointsMEOHSYN)) - gp.quicksum((cm.massFlowSynthesisgasOut[(j)] * self.OptVarOperationPointMEOHSYN[(t,j)] * fTimeStep for j in cm.arrOperationPointsMEOHSYN)) >= self.param.param['constraints']['operationPointChange']['MeOHSynthesisUpwardBound'] * fTimeStep for t in self.arrTime[1:]), "Operation point change methanol synthesis upward bound")
            self.m.addConstrs(
                ((gp.quicksum(cm.massFlowSynthesisgasOut[(j)] * self.OptVarOperationPointMEOHSYN[(t-1,j)] * fTimeStep for j in cm.arrOperationPointsMEOHSYN)) - gp.quicksum((cm.massFlowSynthesisgasOut[(j)] * self.OptVarOperationPointMEOHSYN[(t,j)] * fTimeStep for j in cm.arrOperationPointsMEOHSYN)) <= self.param.param['constraints']['operationPointChange']['MeOHSynthesisDownwardBound'] * fTimeStep for t in self.arrTime[1:]), "Operation point change methanol synthesis upper downward")


            # Absorption/Desorption (mass flow methanol water in cycle)
            self.m.addConstrs(
                ((gp.quicksum(cm.massFlowMethanolWaterInCycle[(j)] * self.OptVarOperationPointABSDES[(t-1,j)] * fTimeStep for j in cm.arrOperationPointsABSDES)) - gp.quicksum((cm.massFlowMethanolWaterInCycle[(j)] * self.OptVarOperationPointABSDES[(t,j)] * fTimeStep for j in cm.arrOperationPointsABSDES)) >= self.param.param['constraints']['operationPointChange']['MeOHWaterInCycleUpwardBound'] * fTimeStep for t in self.arrTime[1:]), "Operation point change absorption/desorption upward bound")
            self.m.addConstrs(
                ((gp.quicksum(cm.massFlowMethanolWaterInCycle[(j)] * self.OptVarOperationPointABSDES[(t-1,j)] * fTimeStep for j in cm.arrOperationPointsABSDES)) - gp.quicksum((cm.massFlowMethanolWaterInCycle[(j)] * self.OptVarOperationPointABSDES[(t,j)] * fTimeStep for j in cm.arrOperationPointsABSDES)) <= self.param.param['constraints']['operationPointChange']['MeOHWaterInCycleDownwardBound'] * fTimeStep for t in self.arrTime[1:]), "Operation point change absorption/desorption downward bound")
