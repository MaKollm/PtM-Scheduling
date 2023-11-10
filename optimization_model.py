#!/usr/bin/env python3.10

from characteristic_fields import *

import gurobipy as gp
from gurobipy import GRB
from gurobipy import *

class Optimization_Model():

    def __init__(self, param):
        self.update(param)


    def update(self, param):
        self.param = param
        self.time = list(range(0,self.param.param['controlParameters']['numberOfTimeSteps']+1))


    def create_optimization_model(self, cf, elec, pv, pp):

        self.m = gp.Model('ptm')
        self.m.ModelSense = GRB.MINIMIZE

        self.create_variables(cf, elec, pv, pp)
        self.create_constraints(cf, elec, pv, pp)
        self.create_cost_function(cf, elec, pv, pp)

        self.m.update()



    def run_optimization(self):
        self.m.Params.TimeLimit = self.param.param['controlParameters']['timeLimit']
        self.m.Params.MIPGap = self.param.param['controlParameters']['optimalityGap']
        self.m.Params.LogToConsole = 1
        if self.param.param['controlParameters']['testFeasibility'] == True:
            self.m.computeIIS()
            self.m.write("model.ilp")
        
        self.m.optimize()



    ########## Variables ##########
    def create_variables(self, cf, elec, pv, pp):

        self.operationPoint_ABSDES = self.m.addVars(self.time,cf.ABSDESValues, vtype=GRB.BINARY)
        self.operationPoint_MEOHSYN = self.m.addVars(self.time,cf.synthesisgasInMethanolSynthesisValues, vtype=GRB.BINARY)
        self.operationPoint_DIS = self.m.addVars(self.time,cf.methanolWaterInDistillationValues, vtype=GRB.BINARY)
        self.operationPointSwitch = self.m.addVars(self.time,[1,2,3],vtype=GRB.BINARY)

        self.powerElectrolyser = self.m.addVars(self.time,self.param.param['electrolyser']['numberOfEnapterModules'],lb=self.param.param['electrolyser']['powerLowerBound'], ub=self.param.param['electrolyser']['powerUpperBound'],vtype=GRB.CONTINUOUS)
        self.electrolyserMode = self.m.addVars(self.time,self.param.param['electrolyser']['numberOfEnapterModules'],4, vtype=GRB.BINARY)
        self.usageOfPV = self.m.addVars(self.time,lb=0.0,ub=1000,vtype=GRB.CONTINUOUS)
        self.powerInBatteryPV = self.m.addVars(self.time,lb=0,ub=self.param.param['battery']['maxChargeRate'], vtype=GRB.CONTINUOUS)
        self.powerInBatteryBought = self.m.addVars(self.time,lb=0,ub=self.param.param['battery']['maxChargeRate'], vtype=GRB.CONTINUOUS)
        self.powerOutBattery = self.m.addVars(self.time,lb=0,ub=self.param.param['battery']['maxDischargeRate'], vtype=GRB.CONTINUOUS)
        self.powerOutBatterySold = self.m.addVars(self.time,lb=0,ub=self.param.param['battery']['maxDischargeRate'], vtype=GRB.CONTINUOUS)
        self.powerBought = self.m.addVars(self.time,lb=0.0,ub=100,vtype=GRB.CONTINUOUS)

        if self.param.param['controlParameters']['uncertaintyPV'] == True:
            self.indicatorPV = self.m.addVars(range(0,pv.numberUncertaintySamples),vtype=GRB.BINARY)

        if self.param.param['controlParameters']['uncertaintyPP'] == True:
            #self.usageOfPV = self.m.addVars(self.time,range(0,pp.numberUncertaintySamples),lb=0.0,ub=1000,vtype=GRB.CONTINUOUS)
            #self.powerInBatteryPV = self.m.addVars(self.time,range(0,pp.numberUncertaintySamples),lb=0,ub=self.param.param['battery']['maxChargeRate'], vtype=GRB.CONTINUOUS)
            self.powerInBatteryBought = self.m.addVars(self.time,range(0,pp.numberUncertaintySamples),lb=0,ub=self.param.param['battery']['maxChargeRate'], vtype=GRB.CONTINUOUS)
            self.powerOutBattery = self.m.addVars(self.time,range(0,pp.numberUncertaintySamples),lb=0,ub=self.param.param['battery']['maxDischargeRate'], vtype=GRB.CONTINUOUS)
            self.powerOutBatterySold = self.m.addVars(self.time,range(0,pp.numberUncertaintySamples),lb=0,ub=self.param.param['battery']['maxDischargeRate'], vtype=GRB.CONTINUOUS)
            self.powerBought = self.m.addVars(self.time,range(0,pp.numberUncertaintySamples),lb=0.0,ub=100,vtype=GRB.CONTINUOUS)



    ########## Cost function ##########
    def create_cost_function(self, cf, elec, pv, pp):
        timeStep = self.param.param['controlParameters']['timeStep']

        if self.param.param['controlParameters']['uncertaintyPP'] == False:
            self.m.setObjective(0
                    - gp.quicksum(cf.massFlowMethanolOut[(j)] * self.operationPoint_DIS[(i,j)] * self.param.param['prices']['methanol'] * timeStep for i in self.time for j in cf.methanolWaterInDistillationValues)
                    - gp.quicksum(cf.volumeBiogasOut[(j)] * self.operationPoint_ABSDES[(i,j)] * self.param.param['methane']['brennwert'] * self.param.param['prices']['methane'] * timeStep for i in self.time for j in cf.ABSDESValues)
                    + gp.quicksum(cf.volumeBiogasIn[(j)] * self.operationPoint_ABSDES[(i,j)] * self.param.param['biogas']['brennwert'] * self.param.param['prices']['biogas'] * timeStep for i in self.time for j in cf.ABSDESValues)
                    + gp.quicksum(self.param.param['prices']['power'][i] * self.powerBought[i] for i in self.time)
                    - gp.quicksum(self.param.param['prices']['powerSold'] * self.powerOutBatterySold[i] for i in self.time))
        
        else:
            self.m.setObjective(- gp.quicksum(cf.massFlowMethanolOut[(j)] * self.operationPoint_DIS[(i,j)] * self.param.param['prices']['methanol'] * timeStep for i in self.time for j in cf.methanolWaterInDistillationValues)
                - gp.quicksum(cf.volumeBiogasOut[(j)] * self.operationPoint_ABSDES[(i,j)] * self.param.param['methane']['brennwert'] * self.param.param['prices']['methane'] * timeStep for i in self.time for j in cf.ABSDESValues)
                + gp.quicksum(cf.volumeBiogasIn[(j)] * self.operationPoint_ABSDES[(i,j)] * self.param.param['biogas']['brennwert'] * self.param.param['prices']['biogas'] * timeStep for i in self.time for j in cf.ABSDESValues)
                + gp.quicksum(pp.powerPriceSamples[r,i] * self.powerBought[i,r] * 1/pp.numberUncertaintySamples for i in self.time for r in range(0,pp.numberUncertaintySamples))
                - gp.quicksum(self.param.param['prices']['powerSold'] * self.powerOutBatterySold[i,r] * 1/pp.numberUncertaintySamples for i in self.time for r in range(0,pp.numberUncertaintySamples)))



    ########## Constraints ##########
    def create_constraints(self, cf, elec, pv, pp):
        timeStep = self.param.param['controlParameters']['timeStep']

        if self.param.param['controlParameters']['benchmark'] == False:
            if self.param.param['controlParameters']['sameOutputAsBenchmark'] == False:
                self.m.addConstr(
                    (gp.quicksum(cf.massFlowMethanolOut[(j)] * self.operationPoint_DIS[(t,j)] * timeStep for j in cf.methanolWaterInDistillationValues for t in self.time) >= self.param.param['methanol']['minimumAmountOpt']), "Minimum amount methanol produced")    
            else:
                self.m.addConstr(
                    (gp.quicksum(cf.massFlowMethanolOut[(j)] * self.operationPoint_DIS[(t,j)] * timeStep for j in cf.methanolWaterInDistillationValues for t in self.time) <= self.param.param['methanol']['sameAmountBenchmark']*1.01), "Amount methanol produced is same as benchmark upper bound") 
                self.m.addConstr(
                    (gp.quicksum(cf.massFlowMethanolOut[(j)] * self.operationPoint_DIS[(t,j)] * timeStep for j in cf.methanolWaterInDistillationValues for t in self.time) >= self.param.param['methanol']['sameAmountBenchmark']), "Amount methanol produced is same as benchmark lower bound")    
                self.m.addConstr(
                    (gp.quicksum(cf.volumeBiogasOut[(j)] * self.operationPoint_ABSDES[(t,j)] * timeStep for j in cf.ABSDESValues for t in self.time) <= self.param.param['methane']['sameAmountVolumeBenchmark']*1.01), "Amount methane (volume) produced is same as benchmark upper bound")    
                self.m.addConstr(
                    (gp.quicksum(cf.volumeBiogasOut[(j)] * self.operationPoint_ABSDES[(t,j)] * timeStep for j in cf.ABSDESValues for t in self.time) >= self.param.param['methane']['sameAmountVolumeBenchmark']), "Amount methane (volume) produced is same as benchmark lower bound") 

        if self.param.param['controlParameters']['benchmark'] == True:
            # Minimum amount of methanol which has to be produced
            self.m.addConstr(
                (gp.quicksum(cf.massFlowMethanolOut[(j)] * self.operationPoint_DIS[(t,j)] * timeStep for j in cf.methanolWaterInDistillationValues for t in self.time) >= self.param.param['methanol']['minimumAmountBenchmark']), "Minimum amount methanol produced benchmark")
            # The same operation point for absorption and desorption for every time step
            self.m.addConstrs(
                (self.operationPoint_ABSDES[(t-1,j)] == self.operationPoint_ABSDES[(t,j)] for t in self.time[2:] for j in cf.ABSDESValues), "Benchmark operation point absorption, desorption and methanolsynthesis")
            # The same operation point for distillation for every time step
            self.m.addConstrs(
                (self.operationPoint_DIS[(t-1,j)] == self.operationPoint_DIS[(t,j)] for t in self.time[2:] for j in cf.methanolWaterInDistillationValues), "Benchmark operation point distillation")
            # The same operation point for methanol synthesis for every time step
            self.m.addConstrs(
                (self.operationPoint_MEOHSYN[(t-1,j)] == self.operationPoint_MEOHSYN[(t,j)] for t in self.time[2:] for j in cf.synthesisgasInMethanolSynthesisValues), "Benchmark operation point methanol synthesis")
            # The same power in electrolyser for every time step
            self.m.addConstrs(
                (self.powerElectrolyser[(t-1,n)] == self.powerElectrolyser[(t,n)] for t in self.time[2:] for n in elec.enapterModules), "Benchmark power electrolyser")
            self.m.addConstrs(
                (self.electrolyserMode[(t-1,n,m)] == self.electrolyserMode[(t,n,m)] for t in self.time[3:] for n in elec.enapterModules for m in elec.modes), "Benchmark power electrolyser")
            """
            self.m.addConstr(
            ((self.param.param['storageH2']['InitialFilling'] * self.param.param['R_H2'] * (self.param.param['Tamb'] + self.param.param['T0']) / (self.param.param['storageH2']['Volume'] * 100000)) -
                (self.param.param['storageH2']['InitialFilling'] + gp.quicksum(self.powerElectrolyser[(t,n)] * self.electrolyserMode[(t,n,3)] * self.param.param['electrolyser']['constant'] * timeStep for t in self.time for n in elec.enapterModules)
                - gp.quicksum(cf.massFlowHydrogenIn[(j)] * self.operationPoint_ABSDES[(t,j)] * timeStep for j in cf.ABSDESValues for t in self.time) 
                - gp.quicksum(cf.massFlowAdditionalHydrogen[(j)] * self.operationPoint_ABSDES[(t,j)] * timeStep for j in cf.ABSDESValues for t in self.time)) 
                * self.param.param['R_H2'] * (self.param.param['Tamb'] + self.param.param['T0']) / (self.param.param['storageH2']['Volume'] * 100000) <= self.param.param['constraints']['hydrogenStorageFillEqual']['UpperBound']), "Storage H2 equal filling upper bound")
            self.m.addConstr(
                ((self.param.param['storageH2']['InitialFilling'] * self.param.param['R_H2'] * (self.param.param['Tamb'] + self.param.param['T0']) / (self.param.param['storageH2']['Volume'] * 100000)) -
                    (self.param.param['storageH2']['InitialFilling'] + gp.quicksum(self.powerElectrolyser[(t,n)] * self.electrolyserMode[(t,n,3)] * self.param.param['electrolyser']['constant'] * timeStep for t in self.time for n in elec.enapterModules)
                    - gp.quicksum(cf.massFlowHydrogenIn[(j)] * self.operationPoint_ABSDES[(t,j)] * timeStep for j in cf.ABSDESValues for t in self.time) 
                    - gp.quicksum(cf.massFlowAdditionalHydrogen[(j)] * self.operationPoint_ABSDES[(t,j)] * timeStep for j in cf.ABSDESValues for t in self.time)) 
                    * self.param.param['R_H2'] * (self.param.param['Tamb'] + self.param.param['T0']) / (self.param.param['storageH2']['Volume'] * 100000) >= self.param.param['constraints']['hydrogenStorageFillEqual']['LowerBound']), "Storage H2 equal filling lower bound")
            """
            
        if self.param.param['controlParameters']['benchmark'] == False:
            if self.param.param['controlParameters']['transitionConstraints'] == True:
                ## Minimum stay time per mode constraints
                self.m.addConstrs(
                    (gp.quicksum(self.operationPoint_ABSDES[(i,j)] for i in self.time[t:t+self.param.param['constraints']['transitionTimes']['minimumStayTimeABSDES']] for j in cf.ABSDESValues[1:]) >= self.operationPointSwitch[(t,1)]*self.param.param['constraints']['transitionTimes']['minimumStayTimeABSDES'] for t in self.time[1:]), "Mode switching minimum stay constraint ABSDES")
                self.m.addConstrs(
                    (gp.quicksum(self.operationPoint_MEOHSYN[(i,j)] for i in self.time[t:t+self.param.param['constraints']['transitionTimes']['minimumStayTimeMEOHSYN']] for j in cf.synthesisgasInMethanolSynthesisValues[1:]) >= self.operationPointSwitch[(t,2)]*self.param.param['constraints']['transitionTimes']['minimumStayTimeMEOHSYN'] for t in self.time[1:]), "Mode switching minimum stay constraint MEOHSYN")
                self.m.addConstrs(
                    (gp.quicksum(self.operationPoint_DIS[(i,j)] for i in self.time[t:t+self.param.param['constraints']['transitionTimes']['minimumStayTimeDIS']] for j in cf.methanolWaterInDistillationValues[1:]) >= self.operationPointSwitch[(t,3)]*self.param.param['constraints']['transitionTimes']['minimumStayTimeDIS'] for t in self.time[1:]), "Mode switching minimum stay constraint DIS")
                
                
                ## Maximum stay time per mode constraints
                self.m.addConstrs(
                    ((1 - gp.quicksum(self.operationPoint_ABSDES[(t+self.param.param['constraints']['transitionTimes']['maximumStayTimeABSDES'],j)] for j in cf.ABSDESValues[1:])) >= self.operationPointSwitch[(t,1)] - gp.quicksum(self.operationPoint_ABSDES[(t+i,0,0)] for i in range(self.param.param['constraints']['transitionTimes']['minimumStayTimeABSDES'],self.param.param['constraints']['transitionTimes']['maximumStayTimeABSDES'])) for t in self.time[1:-(self.param.param['constraints']['transitionTimes']['maximumStayTimeABSDES'])]), "Mode switching maximum stay constraint mode ABSDES")
                self.m.addConstrs(
                    ((1 - gp.quicksum(self.operationPoint_MEOHSYN[(t+self.param.param['constraints']['transitionTimes']['maximumStayTimeMEOHSYN'],j)] for j in cf.synthesisgasInMethanolSynthesisValues[1:])) >= self.operationPointSwitch[(t,2)] - gp.quicksum(self.operationPoint_MEOHSYN[(t+i,0)] for i in range(self.param.param['constraints']['transitionTimes']['minimumStayTimeMEOHSYN'],self.param.param['constraints']['transitionTimes']['maximumStayTimeMEOHSYN'])) for t in self.time[1:-(self.param.param['constraints']['transitionTimes']['maximumStayTimeMEOHSYN'])]), "Mode switching maximum stay constraint mode MEOHSYN")
                self.m.addConstrs(
                    ((1 - gp.quicksum(self.operationPoint_DIS[(t+self.param.param['constraints']['transitionTimes']['maximumStayTimeDIS'],j)] for j in cf.methanolWaterInDistillationValues[1:])) >= self.operationPointSwitch[(t,3)] - gp.quicksum(self.operationPoint_DIS[(t+i,0)] for i in range(self.param.param['constraints']['transitionTimes']['minimumStayTimeDIS'],self.param.param['constraints']['transitionTimes']['maximumStayTimeDIS'])) for t in self.time[1:-(self.param.param['constraints']['transitionTimes']['maximumStayTimeDIS'])]), "Mode switching maximum stay constraint mode DIS")


            ## Mode switching constraints
            self.m.addConstrs(
                (self.operationPoint_ABSDES[(t-1,0)] >= self.operationPointSwitch[(t,1)] for t in self.time[1:]), "Mode switching ABSDES 1")
            self.m.addConstrs(
                (gp.quicksum(self.operationPoint_ABSDES[(t,j)] for j in cf.ABSDESValues[1:]) >= self.operationPointSwitch[(t,1)] for t in self.time[0:]), "Mode switching ABSDES 2")
            self.m.addConstrs(
                (self.operationPoint_ABSDES[(t-1,0)] + gp.quicksum(self.operationPoint_ABSDES[(t,j)] for j in cf.ABSDESValues[1:]) - 1 <= self.operationPointSwitch[(t,1)] for t in self.time[1:]), "Mode switching ABSDES 3")

            self.m.addConstrs(
                (self.operationPoint_MEOHSYN[(t-1,0)] >= self.operationPointSwitch[(t,2)] for t in self.time[1:]), "Mode switching MEOHSYN 1")
            self.m.addConstrs(
                (gp.quicksum(self.operationPoint_MEOHSYN[(t,j)] for j in cf.synthesisgasInMethanolSynthesisValues[1:]) >= self.operationPointSwitch[(t,2)] for t in self.time[0:]), "Mode switching MEOHSYN 2")
            self.m.addConstrs(
                (self.operationPoint_MEOHSYN[(t-1,0)] + gp.quicksum(self.operationPoint_MEOHSYN[(t,j)] for j in cf.synthesisgasInMethanolSynthesisValues[1:]) - 1 <= self.operationPointSwitch[(t,2)] for t in self.time[1:]), "Mode switching MEOHSYN 3")

            self.m.addConstrs(
                (self.operationPoint_DIS[(t-1,0)] >= self.operationPointSwitch[(t,3)] for t in self.time[1:]), "Mode switching DIS 1")
            self.m.addConstrs(
                (gp.quicksum(self.operationPoint_DIS[(t,j)] for j in cf.methanolWaterInDistillationValues[1:]) >= self.operationPointSwitch[(t,3)] for t in self.time[0:]), "Mode switching DIS 2")
            self.m.addConstrs(
                (self.operationPoint_DIS[(t-1,0)] + gp.quicksum(self.operationPoint_DIS[(t,j)] for j in cf.methanolWaterInDistillationValues[1:]) - 1 <= self.operationPointSwitch[(t,3)] for t in self.time[1:]), "Mode switching DIS 3")

        ## PV considered
        if self.param.param['controlParameters']['considerPV'] == False:
            self.m.addConstrs(
                self.usageOfPV[t] == 0 for t in self.time)
            self.m.addConstrs(
                self.powerInBatteryPV[t] == 0 for t in self.time)

        ## Battery considered
        if self.param.param['controlParameters']['considerBattery'] == False:
            self.m.addConstrs(
                self.powerInBatteryBought[t] == 0 for t in self.time)
            self.m.addConstrs(
                self.powerInBatteryPV[t] == 0 for t in self.time)
            self.m.addConstrs(
                self.powerOutBattery[t] == 0 for t in self.time)
            self.m.addConstrs(
                self.powerOutBatterySold[t] == 0 for t in self.time)
            
        ## Power Constraints

        if self.param.param['controlParameters']['uncertaintyPP'] == True:
            # power from battery and PV and grid to electrolyser and components must equal to needed power
            self.m.addConstrs(
                (self.powerOutBattery[t,r] + self.usageOfPV[t] + self.powerBought[t,r] - self.powerInBatteryBought[t,r] == (
                gp.quicksum(self.powerElectrolyser[(t,n)] * self.electrolyserMode[(t,n,3)] * timeStep for n in elec.enapterModules)
                + gp.quicksum(elec.powerElectrolyserMode[(n,m)] * self.electrolyserMode[(t,n,m)] * timeStep for n in elec.enapterModules for m in elec.modes[:-1])
                + gp.quicksum(cf.powerPlantComponentsUnit1[(j)] * self.operationPoint_ABSDES[(t,j)] * timeStep for j in cf.ABSDESValues)
                + gp.quicksum(cf.powerPlantComponentsUnit2[(j)] * self.operationPoint_MEOHSYN[(t,j)] * timeStep for j in cf.synthesisgasInMethanolSynthesisValues)
                + gp.quicksum(cf.powerPlantComponentsUnit3[(j)] * self.operationPoint_DIS[(t,j)] * timeStep for j in cf.methanolWaterInDistillationValues))
                for t in self.time[1:] for r in range(0,pp.numberUncertaintySamples)), "Battery output maximum")

            # Power to battery has always to be smaller than power bought
            self.m.addConstrs(
                (self.powerInBatteryBought[t,r] <= self.powerBought[t,r] for t in self.time[1:] for r in range(0,pp.numberUncertaintySamples)), "Power to battery has always to be smaller than power bought")

            # Power can not be sold and bought at the same time
            self.m.addConstrs(
                (self.powerBought[t,r] * self.powerOutBatterySold[t,r] == 0 for t in self.time[1:] for r in range(0,pp.numberUncertaintySamples)), "Power can not be sold and bought at the same time")
        
            # Battery can not be discharged and charged at the same time
            self.m.addConstrs(
                (self.powerInBatteryBought[t,r] * self.powerOutBattery[t,r] == 0 for t in self.time[1:] for r in range(0,pp.numberUncertaintySamples)), "Battery charge and discharge time 1")
            self.m.addConstrs(
                (self.powerInBatteryPV[t] * self.powerOutBattery[t,r] == 0 for t in self.time[1:] for r in range(0,pp.numberUncertaintySamples)), "Battery charge and discharge time 2")
            self.m.addConstrs(
                (self.powerInBatteryPV[t] * self.powerOutBatterySold[t,r] == 0 for t in self.time[1:] for r in range(0,pp.numberUncertaintySamples)), "Battery charge and discharge time 3")
            
            # Charge and discharge rate have to be smaller than maximum rate
            self.m.addConstrs(
                (self.powerInBatteryBought[t,r] + self.powerInBatteryPV[t] <= self.param.param['battery']['maxChargeRate'] for t in self.time[1:] for r in range(0,pp.numberUncertaintySamples)), "Battery charge rate")
            self.m.addConstrs(
                (self.powerOutBattery[t,r] + self.powerOutBatterySold[t,r] <= self.param.param['battery']['maxDischargeRate'] for t in self.time[1:] for r in range(0,pp.numberUncertaintySamples)), "Battery discharge rate")
            
             # Power cannot be sold
            if self.param.param['controlParameters']['powerSale'] == False:
                self.m.addConstrs(
                    (self.powerOutBatterySold[t,r] == 0 for t in self.time[1:] for r in range(0,pp.numberUncertaintySamples)), "No power can be sold")
            
        else:
            # power from battery and PV and grid to electrolyser and components must equal to needed power
            self.m.addConstrs(
                (self.powerOutBattery[t] + self.usageOfPV[t] + self.powerBought[t] - self.powerInBatteryBought[t] == (
                gp.quicksum(self.powerElectrolyser[(t,n)] * self.electrolyserMode[(t,n,3)] * timeStep for n in elec.enapterModules)
                + gp.quicksum(elec.powerElectrolyserMode[(n,m)] * self.electrolyserMode[(t,n,m)] * timeStep for n in elec.enapterModules for m in elec.modes[:-1])
                + gp.quicksum(cf.powerPlantComponentsUnit1[(j)] * self.operationPoint_ABSDES[(t,j)] * timeStep for j in cf.ABSDESValues)
                + gp.quicksum(cf.powerPlantComponentsUnit2[(j)] * self.operationPoint_MEOHSYN[(t,j)] * timeStep for j in cf.synthesisgasInMethanolSynthesisValues)
                + gp.quicksum(cf.powerPlantComponentsUnit3[(j)] * self.operationPoint_DIS[(t,j)] * timeStep for j in cf.methanolWaterInDistillationValues))
                for t in self.time[1:]), "Battery output maximum")

            # Power to battery has always to be smaller than power bought
            self.m.addConstrs(
                (self.powerInBatteryBought[t] <= self.powerBought[t] for t in self.time[1:]), "Power to battery has always to be smaller than power bought")

            # Power can not be sold and bought at the same time
            self.m.addConstrs(
                (self.powerBought[t] * self.powerOutBatterySold[t] == 0 for t in self.time[1:]), "Power can not be sold and bought at the same time")
            
            # Battery can not be discharged and charged at the same time
            self.m.addConstrs(
                (self.powerInBatteryBought[t] * self.powerOutBattery[t] == 0 for t in self.time[1:]), "Battery charge and discharge time 1")
            self.m.addConstrs(
                (self.powerInBatteryPV[t] * self.powerOutBattery[t] == 0 for t in self.time[1:]), "Battery charge and discharge time 2")
            self.m.addConstrs(
                (self.powerInBatteryPV[t] * self.powerOutBatterySold[t] == 0 for t in self.time[1:]), "Battery charge and discharge time 3")
            
            # Charge and discharge rate have to be smaller than maximum rate
            self.m.addConstrs(
                (self.powerInBatteryBought[t] + self.powerInBatteryPV[t] <= self.param.param['battery']['maxChargeRate'] for t in self.time[1:]), "Battery charge rate")
            self.m.addConstrs(
                (self.powerOutBattery[t] + self.powerOutBatterySold[t] <= self.param.param['battery']['maxDischargeRate'] for t in self.time[1:]), "Battery discharge rate")
            
             # Power cannot be sold
            if self.param.param['controlParameters']['powerSale'] == False:
                self.m.addConstrs(
                    (self.powerOutBatterySold[t] == 0 for t in self.time[1:]), "No power can be sold")
                

        # Power used from PV and stored in battery from PV must be equal or smaller than power available from PV
        if self.param.param['controlParameters']['uncertaintyPV'] == True:
            self.m.addConstrs(
                (self.usageOfPV[i] + self.powerInBatteryPV[i] <= pv.pvSamples[r,i] + 1000*(1-self.indicatorPV[r]) for i in self.time[1:] for r in range(0,pv.numberUncertaintySamples)), "PV upper bound available")
            self.m.addConstr(
                (gp.quicksum(self.indicatorPV[r] for r in range(0,pv.numberUncertaintySamples)) >= pv.alpha*pv.numberUncertaintySamples), 'Indicator PV')
        else:
            self.m.addConstrs(
                (self.usageOfPV[i] + self.powerInBatteryPV[i] <= pv.powerAvailable[i] for i in self.time[1:]), "PV upper bound available")



        ## Minimum operation point/operation mode constraint
        # Exactly one operation point for absorption, desorption and methanol synthesis has to be selected in every time step
        self.m.addConstrs(
            (self.operationPoint_ABSDES.sum(t,'*','*') == 1.0 for t in self.time), "Exactly one operation point for absorption, desorption and methanol synthesis per time step")
        # Exactly one operation point for methanol synthesis has to be selected every time step
        self.m.addConstrs(
            (self.operationPoint_MEOHSYN.sum(t,'*') == 1.0 for t in self.time), "Exactly one operation point for methanol synthesis per time step")
        # Exactly one operation point for distillation has to be selected in every time step
        self.m.addConstrs(
            (self.operationPoint_DIS.sum(t,'*') == 1.0 for t in self.time), "Exactly one operation point for distillation per time step")
        # Exactly one operation point for electrolyser has to be selected in every time step
        self.m.addConstrs(
            (gp.quicksum(self.electrolyserMode[(t,n,m)] for m in elec.modes) == 1 for t in self.time for n in elec.enapterModules), "one operation mode for electrolyser per time period")


        ## Initial time step constraints
        # No operation point for absorption, desorption and methanol synthesis in initial time step
        self.m.addConstr(
            (self.operationPoint_ABSDES[(0,0)] == 1), "No operation point for absorption, desorption and methanol synthesis in initial time step")
        # No operation point for methanol synthesis in initial time step
        self.m.addConstr(
            (self.operationPoint_MEOHSYN[(0,0)] == 1), "No operation point for methanol synthesis in initial time step")
        # No operation point for distillation in initial time step
        self.m.addConstr(
            (self.operationPoint_DIS[(0,0)] == 1), "No operation point for distillation in initial time step")
        # No power in electrolyser in initial time step
        self.m.addConstrs(
            (self.electrolyserMode[(0,n,2)] == 1 for n in elec.enapterModules), "Electrolyser modules are off at the beginning")
        # No input or output for battery in first time step
        self.m.addConstr(
            (self.powerInBatteryPV[0] == 0), "PV in battery initial time step")
        
        if self.param.param['controlParameters']['uncertaintyPP'] == True:
            self.m.addConstrs(
                (self.powerInBatteryBought[0,r] == 0 for r in range(0,pp.numberUncertaintySamples)), "Power bought battery initial time step")
            self.m.addConstrs(
                (self.powerOutBattery[0,r] == 0 for r in range(0,pp.numberUncertaintySamples)), "power out battery initial time step")
            self.m.addConstrs(
                (self.powerOutBatterySold[0,r] == 0 for r in range(0,pp.numberUncertaintySamples)), "power sold battery initial time step")
        else:
            self.m.addConstr(
                (self.powerInBatteryBought[0] == 0), "Power bought battery initial time step")
            self.m.addConstr(
                (self.powerOutBattery[0] == 0), "power out battery initial time step")
            self.m.addConstr(
                (self.powerOutBatterySold[0] == 0), "power sold battery initial time step")



        ## Electrolyser constraints
        self.m.addConstrs(
            (self.electrolyserMode[(t-1,n,0)] <= self.electrolyserMode[(t,n,3)] for t in self.time[1:] for n in elec.enapterModules), "Electrolyser after off comes off or ramp-up")
        self.m.addConstrs(
            (self.electrolyserMode[(t-1,n,1)] <= gp.quicksum(self.electrolyserMode[(t,n,m)] for m in [2,3]) for t in self.time[1:] for n in elec.enapterModules), "Electrolyser after off comes off or ramp-up")
        self.m.addConstrs(
            (self.electrolyserMode[(t-1,n,2)] <= gp.quicksum(self.electrolyserMode[(t,n,m)] for m in [0,2]) for t in self.time[1:] for n in elec.enapterModules), "Electrolyser after off comes off or ramp-up")
        self.m.addConstrs(
            (self.electrolyserMode[(t-1,n,3)] <= gp.quicksum(self.electrolyserMode[(t,n,m)] for m in [1,2,3]) for t in self.time[1:] for n in elec.enapterModules), "Electrolyser after off comes off or ramp-up")


        ## Hydrogen storage constraints
        self.m.addConstrs(
            ((self.param.param['storageH2']['InitialFilling'] 
                + gp.quicksum(self.powerElectrolyser[(l,n)] * self.electrolyserMode[(l,n,3)] * self.param.param['electrolyser']['constant'] * timeStep for l in self.time[0:t+1] for n in elec.enapterModules)
                - gp.quicksum(cf.massFlowHydrogenIn[(j)] * self.operationPoint_ABSDES[(l,j)] * timeStep for j in cf.ABSDESValues for l in self.time[0:t+1]) 
                - gp.quicksum(cf.massFlowAdditionalHydrogen[(j)] * self.operationPoint_ABSDES[(l,j)] * timeStep for j in cf.ABSDESValues for l in self.time[0:t+1])) 
                * self.param.param['R_H2'] * (self.param.param['Tamb'] + self.param.param['T0']) / (self.param.param['storageH2']['Volume'] * 100000) <= self.param.param['storageH2']['UpperBound'] for t in self.time), "Storage H2 upper bound")
        self.m.addConstrs(
            ((self.param.param['storageH2']['InitialFilling'] 
                + gp.quicksum(self.powerElectrolyser[(l,n)] * self.electrolyserMode[(l,n,3)] * self.param.param['electrolyser']['constant'] * timeStep for l in self.time[0:t+1] for n in elec.enapterModules)
                - gp.quicksum(cf.massFlowHydrogenIn[(j)] * self.operationPoint_ABSDES[(l,j)] * timeStep for j in cf.ABSDESValues for l in self.time[0:t+1]) 
                - gp.quicksum(cf.massFlowAdditionalHydrogen[(j)] * self.operationPoint_ABSDES[(l,j)] * timeStep for j in cf.ABSDESValues for l in self.time[0:t+1])) 
                * self.param.param['R_H2'] * (self.param.param['Tamb'] + self.param.param['T0']) / (self.param.param['storageH2']['Volume'] * 100000) >= self.param.param['storageH2']['LowerBound'] for t in self.time), "Storage H2 lower bound")
        self.m.addConstr(
            ((self.param.param['storageH2']['InitialFilling'] * self.param.param['R_H2'] * (self.param.param['Tamb'] + self.param.param['T0']) / (self.param.param['storageH2']['Volume'] * 100000)) -
                (self.param.param['storageH2']['InitialFilling'] + gp.quicksum(self.powerElectrolyser[(t,n)] * self.electrolyserMode[(t,n,3)] * self.param.param['electrolyser']['constant'] * timeStep for t in self.time for n in elec.enapterModules)
                - gp.quicksum(cf.massFlowHydrogenIn[(j)] * self.operationPoint_ABSDES[(t,j)] * timeStep for j in cf.ABSDESValues for t in self.time) 
                - gp.quicksum(cf.massFlowAdditionalHydrogen[(j)] * self.operationPoint_ABSDES[(t,j)] * timeStep for j in cf.ABSDESValues for t in self.time)) 
                * self.param.param['R_H2'] * (self.param.param['Tamb'] + self.param.param['T0']) / (self.param.param['storageH2']['Volume'] * 100000) <= self.param.param['constraints']['hydrogenStorageFillEqual']['UpperBound']), "Storage H2 equal filling upper bound")
        self.m.addConstr(
            ((self.param.param['storageH2']['InitialFilling'] * self.param.param['R_H2'] * (self.param.param['Tamb'] + self.param.param['T0']) / (self.param.param['storageH2']['Volume'] * 100000)) -
                (self.param.param['storageH2']['InitialFilling'] + gp.quicksum(self.powerElectrolyser[(t,n)] * self.electrolyserMode[(t,n,3)] * self.param.param['electrolyser']['constant'] * timeStep for t in self.time for n in elec.enapterModules)
                - gp.quicksum(cf.massFlowHydrogenIn[(j)] * self.operationPoint_ABSDES[(t,j)] * timeStep for j in cf.ABSDESValues for t in self.time) 
                - gp.quicksum(cf.massFlowAdditionalHydrogen[(j)] * self.operationPoint_ABSDES[(t,j)] * timeStep for j in cf.ABSDESValues for t in self.time)) 
                * self.param.param['R_H2'] * (self.param.param['Tamb'] + self.param.param['T0']) / (self.param.param['storageH2']['Volume'] * 100000) >= self.param.param['constraints']['hydrogenStorageFillEqual']['LowerBound']), "Storage H2 equal filling lower bound")


        ## Methanol water storage constraints
        self.m.addConstrs(
            ((self.param.param['storageMethanolWater']['InitialFilling'] 
                + gp.quicksum(cf.massFlowMethanolWaterStorageInSynthesis[(i)] / self.param.param['storageMethanolWater']['InitialDensity'] * self.operationPoint_MEOHSYN[(l,i)] * timeStep for i in cf.synthesisgasInMethanolSynthesisValues for l in self.time[0:t+1]) 
                - gp.quicksum(cf.massFlowMethanolWaterStorageOut[(i)] / self.param.param['storageMethanolWater']['InitialDensity'] * self.operationPoint_DIS[(l,i)] * timeStep for i in cf.methanolWaterInDistillationValues for l in self.time[0:t+1])) >= self.param.param['storageMethanolWater']['LowerBound'] for t in self.time), "Storage methanol water lower bound")
        self.m.addConstrs(
            ((self.param.param['storageMethanolWater']['InitialFilling'] 
                + gp.quicksum(cf.massFlowMethanolWaterStorageInSynthesis[(i)] / cf.densityMethanolWaterStorageInSynthesis[(i)] * self.operationPoint_MEOHSYN[(l,i)] * timeStep for i in cf.synthesisgasInMethanolSynthesisValues for l in self.time[0:t+1])  
                - gp.quicksum(cf.massFlowMethanolWaterStorageOut[(i)] / self.param.param['storageMethanolWater']['InitialDensity'] * self.operationPoint_DIS[(l,i)] * timeStep for i in cf.methanolWaterInDistillationValues for l in self.time[0:t+1])) <= self.param.param['storageMethanolWater']['UpperBound'] for t in self.time), "Storage methanol water upper bound")
        self.m.addConstr(
            (self.param.param['storageMethanolWater']['InitialFilling'] - 
            (self.param.param['storageMethanolWater']['InitialFilling'] 
                + gp.quicksum(cf.massFlowMethanolWaterStorageInSynthesis[(i)] / cf.densityMethanolWaterStorageInSynthesis[(i)] * self.operationPoint_MEOHSYN[(t,i)] * timeStep for i in cf.synthesisgasInMethanolSynthesisValues for t in self.time)  
                - gp.quicksum(cf.massFlowMethanolWaterStorageOut[(i)] / self.param.param['storageMethanolWater']['InitialDensity'] * self.operationPoint_DIS[(t,i)] * timeStep for i in cf.methanolWaterInDistillationValues for t in self.time)) <= self.param.param['constraints']['methanolWaterStorageFillEqual']['UpperBound']), "Storage methanol water equal filling upper bound")
        self.m.addConstr(
            (self.param.param['storageMethanolWater']['InitialFilling'] - 
            (self.param.param['storageMethanolWater']['InitialFilling'] 
                + gp.quicksum(cf.massFlowMethanolWaterStorageInSynthesis[(i)] / cf.densityMethanolWaterStorageInSynthesis[(i)] * self.operationPoint_MEOHSYN[(t,i)] * timeStep for i in cf.synthesisgasInMethanolSynthesisValues for t in self.time)  
                - gp.quicksum(cf.massFlowMethanolWaterStorageOut[(i)] / self.param.param['storageMethanolWater']['InitialDensity'] * self.operationPoint_DIS[(t,i)] * timeStep for i in cf.methanolWaterInDistillationValues for t in self.time))  >= self.param.param['constraints']['methanolWaterStorageFillEqual']['LowerBound']), "Storage methanol water equal filling lower bound")


        ## Battery constraints
        if self.param.param['controlParameters']['uncertaintyPP'] == True:
            self.m.addConstrs(
                (self.param.param['battery']['initialCharge'] 
                + gp.quicksum(self.powerInBatteryPV[l] for l in self.time[0:t+1]) 
                + gp.quicksum(self.powerInBatteryBought[l,r] for l in self.time[0:t+1])
                - gp.quicksum(self.powerOutBattery[l,r] for l in self.time[0:t+1])
                - gp.quicksum(self.powerOutBatterySold[l,r] for l in self.time[0:t+1])
                <= self.param.param['battery']['capacity'] for t in self.time for r in range(0,pp.numberUncertaintySamples)), "Battery upper bound")

            self.m.addConstrs(
                (self.param.param['battery']['initialCharge'] 
                + gp.quicksum(self.powerInBatteryPV[l] for l in self.time[0:t+1]) 
                + gp.quicksum(self.powerInBatteryBought[l,r] for l in self.time[0:t+1])
                - gp.quicksum(self.powerOutBattery[l,r] for l in self.time[0:t+1])
                - gp.quicksum(self.powerOutBatterySold[l,r] for l in self.time[0:t+1])
                >= self.param.param['battery']['minCharge'] for t in self.time for r in range(0,pp.numberUncertaintySamples)), "Battery lower bound")

            self.m.addConstrs(
                (self.param.param['battery']['initialCharge'] - (self.param.param['battery']['initialCharge'] 
                + gp.quicksum(self.powerInBatteryPV[t] for t in self.time) 
                + gp.quicksum(self.powerInBatteryBought[t,r] for t in self.time)
                - gp.quicksum(self.powerOutBattery[t,r] for t in self.time)
                - gp.quicksum(self.powerOutBatterySold[t,r] for t in self.time)) <= self.param.param['constraints']['batteryChargeEqual']['UpperBound'] for r in range(0,pp.numberUncertaintySamples)), "Battery equal charge upper bound")

            self.m.addConstrs(
                (self.param.param['battery']['initialCharge'] - (self.param.param['battery']['initialCharge'] 
                + gp.quicksum(self.powerInBatteryPV[t] for t in self.time) 
                + gp.quicksum(self.powerInBatteryBought[t,r] for t in self.time)
                - gp.quicksum(self.powerOutBattery[t,r] for t in self.time)
                - gp.quicksum(self.powerOutBatterySold[t,r] for t in self.time)) >= self.param.param['constraints']['batteryChargeEqual']['LowerBound'] for r in range(0,pp.numberUncertaintySamples)), "Battery equal charge lower bound")
            
        else:
            self.m.addConstrs(
                (self.param.param['battery']['initialCharge'] 
                + gp.quicksum(self.powerInBatteryPV[l] for l in self.time[0:t+1]) 
                + gp.quicksum(self.powerInBatteryBought[l] for l in self.time[0:t+1])
                - gp.quicksum(self.powerOutBattery[l] for l in self.time[0:t+1])
                - gp.quicksum(self.powerOutBatterySold[l] for l in self.time[0:t+1])
                <= self.param.param['battery']['capacity'] for t in self.time), "Battery upper bound")

            self.m.addConstrs(
                (self.param.param['battery']['initialCharge'] 
                + gp.quicksum(self.powerInBatteryPV[l] for l in self.time[0:t+1]) 
                + gp.quicksum(self.powerInBatteryBought[l] for l in self.time[0:t+1])
                - gp.quicksum(self.powerOutBattery[l] for l in self.time[0:t+1])
                - gp.quicksum(self.powerOutBatterySold[l] for l in self.time[0:t+1])
                >= self.param.param['battery']['capacity']*0.01 for t in self.time), "Battery lower bound")

            self.m.addConstr(
                (self.param.param['battery']['initialCharge'] - (self.param.param['battery']['initialCharge'] 
                + gp.quicksum(self.powerInBatteryPV[t] for t in self.time) 
                + gp.quicksum(self.powerInBatteryBought[t] for t in self.time)
                - gp.quicksum(self.powerOutBattery[t] for t in self.time)
                - gp.quicksum(self.powerOutBatterySold[t] for t in self.time)) <= self.param.param['constraints']['batteryChargeEqual']['UpperBound']), "Battery equal charge upper bound")

            self.m.addConstr(
                (self.param.param['battery']['initialCharge'] - (self.param.param['battery']['initialCharge'] 
                + gp.quicksum(self.powerInBatteryPV[t] for t in self.time) 
                + gp.quicksum(self.powerInBatteryBought[t] for t in self.time)
                - gp.quicksum(self.powerOutBattery[t] for t in self.time)
                - gp.quicksum(self.powerOutBatterySold[t] for t in self.time)) >= self.param.param['constraints']['batteryChargeEqual']['LowerBound']), "Battery equal charge lower bound")

        ## Synthesisgas storage
        self.m.addConstrs(
            ((self.param.param['storageSynthesisgas']['InitialFilling'] 
                + gp.quicksum(cf.massFlowSynthesisgasIn[(j)] * self.operationPoint_ABSDES[(l,j)] * timeStep for j in cf.ABSDESValues for l in self.time[0:t+1])
                - gp.quicksum(cf.massFlowSynthesisgasOut[(i)] * self.operationPoint_MEOHSYN[(l,i)] * timeStep for i in cf.synthesisgasInMethanolSynthesisValues for l in self.time[0:t+1]))
                * self.param.param['R_Synthesisgas'] * (self.param.param['Tamb'] + self.param.param['T0']) / (self.param.param['storageSynthesisgas']['Volume'] * 100000) >= self.param.param['storageSynthesisgas']['LowerBound'] for t in self.time), "Storage synthesis gas lower bound")
        self.m.addConstrs(
            ((self.param.param['storageSynthesisgas']['InitialFilling']  
                + gp.quicksum(cf.massFlowSynthesisgasIn[(j)] * self.operationPoint_ABSDES[(l,j)] * timeStep for j in cf.ABSDESValues for l in self.time[0:t+1])
                - gp.quicksum(cf.massFlowSynthesisgasOut[(i)] * self.operationPoint_MEOHSYN[(l,i)] * timeStep for i in cf.synthesisgasInMethanolSynthesisValues for l in self.time[0:t+1])) 
                * self.param.param['R_Synthesisgas'] * (self.param.param['Tamb'] + self.param.param['T0']) / (self.param.param['storageSynthesisgas']['Volume'] * 100000) <= self.param.param['storageSynthesisgas']['UpperBound'] for t in self.time), "Storage synthesis gas upper bound")
        self.m.addConstr(
            ((self.param.param['storageSynthesisgas']['InitialFilling']  * self.param.param['R_Synthesisgas'] * (self.param.param['Tamb'] + self.param.param['T0']) / (self.param.param['storageSynthesisgas']['Volume'] * 100000)) - 
                (self.param.param['storageSynthesisgas']['InitialFilling']  
                + gp.quicksum(cf.massFlowSynthesisgasIn[(j)] * self.operationPoint_ABSDES[(t,j)] * timeStep for j in cf.ABSDESValues for t in self.time)
                - gp.quicksum(cf.massFlowSynthesisgasOut[(i)] * self.operationPoint_MEOHSYN[(t,i)] * timeStep for i in cf.synthesisgasInMethanolSynthesisValues for t in self.time))
                * self.param.param['R_Synthesisgas'] * (self.param.param['Tamb'] + self.param.param['T0']) / (self.param.param['storageSynthesisgas']['Volume'] * 100000) <= self.param.param['constraints']['synthesisgasStorageFillEqual']['UpperBound']), "Storage synthesis gas equal filling upper bound")
        self.m.addConstr(
            ((self.param.param['storageSynthesisgas']['InitialFilling'] * self.param.param['R_Synthesisgas'] * (self.param.param['Tamb'] + self.param.param['T0']) / (self.param.param['storageSynthesisgas']['Volume'] * 100000)) - 
            (self.param.param['storageSynthesisgas']['InitialFilling'] 
                + gp.quicksum(cf.massFlowSynthesisgasIn[(j)] * self.operationPoint_ABSDES[(t,j)] * timeStep for j in cf.ABSDESValues for t in self.time)
                - gp.quicksum(cf.massFlowSynthesisgasOut[(i)] * self.operationPoint_MEOHSYN[(t,i)] * timeStep for i in cf.synthesisgasInMethanolSynthesisValues for t in self.time))
                * self.param.param['R_Synthesisgas'] * (self.param.param['Tamb'] + self.param.param['T0']) / (self.param.param['storageSynthesisgas']['Volume'] * 100000)  >= self.param.param['constraints']['synthesisgasStorageFillEqual']['LowerBound']), "Storage synthesis gas equal filling lower bound")

            

        ## Production constraints
        # Minimum amount of methane in outflowing biogas
        self.m.addConstrs(
            (gp.quicksum(cf.moleFractionMethaneBiogasOut[(j)] * self.operationPoint_ABSDES[(t,j)] for j in cf.ABSDESValues) >= self.param.param['constraints']['minMoleFractionCH4BiogasOut'] for t in self.time[1:]), "Mole fraction methane biogas out")
        # Hydrogen to carbon dioxide ratio upper bound
        self.m.addConstrs(
            (gp.quicksum(cf.moleFractionHydrogenSynthesisgas[(j)] / cf.moleFractionCarbondioxideSynthesisgas[(j)] * self.operationPoint_ABSDES[(t,j)] for j in cf.ABSDESValues) <= self.param.param['constraints']['maxRatioH2_CO2_Synthesisgas'] for t in self.time[1:]), "Hydrogen - carbon dixoide ratio upper bound")
        # Hydrogen to carbon dioxide ratio lower bound
        self.m.addConstrs(
            (gp.quicksum(cf.moleFractionHydrogenSynthesisgas[(j)] / cf.moleFractionCarbondioxideSynthesisgas[(j)] * self.operationPoint_ABSDES[(t,j)] for j in cf.ABSDESValues) >= self.param.param['constraints']['minRatioH2_CO2_Synthesisgas'] for t in self.time[1:]), "Hydrogen - carbon dixoide ratio lower bound")


        ## Rate of change constraints
        if self.param.param['controlParameters']['rateOfChangeConstranints'] == True:
            # Distillation (mass flow methanol water from storage)
            self.m.addConstrs(
                ((gp.quicksum(cf.massFlowMethanolWaterStorageOut[(j)] * self.operationPoint_DIS[(t-1,j)] * timeStep for j in cf.methanolWaterInDistillationValues)) - gp.quicksum((cf.massFlowMethanolWaterStorageOut[(j)] * self.operationPoint_DIS[(t,j)] * timeStep for j in cf.methanolWaterInDistillationValues)) >= self.param.param['constraints']['operationPointChange']['distillationUpwardBound'] * timeStep for t in self.time[1:]), "Operation point change distillation upward bound")
            self.m.addConstrs(
                ((gp.quicksum(cf.massFlowMethanolWaterStorageOut[(j)] * self.operationPoint_DIS[(t-1,j)] * timeStep for j in cf.methanolWaterInDistillationValues)) - gp.quicksum((cf.massFlowMethanolWaterStorageOut[(j)] * self.operationPoint_DIS[(t,j)] * timeStep for j in cf.methanolWaterInDistillationValues)) <= self.param.param['constraints']['operationPointChange']['distillationDownwardBound'] * timeStep for t in self.time[1:]), "Operation point change distillation downward bound")

            # Methanol synthesis (mass flow synthesis gas)
            self.m.addConstrs(
                ((gp.quicksum(cf.massFlowSynthesisgasOut[(j)] * self.operationPoint_MEOHSYN[(t-1,j)] * timeStep for j in cf.synthesisgasInMethanolSynthesisValues)) - gp.quicksum((cf.massFlowSynthesisgasOut[(j)] * self.operationPoint_MEOHSYN[(t,j)] * timeStep for j in cf.synthesisgasInMethanolSynthesisValues)) >= self.param.param['constraints']['operationPointChange']['MeOHSynthesisUpwardBound'] * timeStep for t in self.time[1:]), "Operation point change methanol synthesis upward bound")
            self.m.addConstrs(
                ((gp.quicksum(cf.massFlowSynthesisgasOut[(j)] * self.operationPoint_MEOHSYN[(t-1,j)] * timeStep for j in cf.synthesisgasInMethanolSynthesisValues)) - gp.quicksum((cf.massFlowSynthesisgasOut[(j)] * self.operationPoint_MEOHSYN[(t,j)] * timeStep for j in cf.synthesisgasInMethanolSynthesisValues)) <= self.param.param['constraints']['operationPointChange']['MeOHSynthesisDownwardBound'] * timeStep for t in self.time[1:]), "Operation point change methanol synthesis upper downward")


            # Absorption/Desorption (mass flow methanol water in cycle)
            self.m.addConstrs(
                ((gp.quicksum(cf.massFlowMethanolWaterInCycle[(j)] * self.operationPoint_ABSDES[(t-1,j)] * timeStep for j in cf.ABSDESValues)) - gp.quicksum((cf.massFlowMethanolWaterInCycle[(j)] * self.operationPoint_ABSDES[(t,j)] * timeStep for j in cf.ABSDESValues)) >= self.param.param['constraints']['operationPointChange']['MeOHWaterInCycleUpwardBound'] * timeStep for t in self.time[1:]), "Operation point change absorption/desorption upward bound")
            self.m.addConstrs(
                ((gp.quicksum(cf.massFlowMethanolWaterInCycle[(j)] * self.operationPoint_ABSDES[(t-1,j)] * timeStep for j in cf.ABSDESValues)) - gp.quicksum((cf.massFlowMethanolWaterInCycle[(j)] * self.operationPoint_ABSDES[(t,j)] * timeStep for j in cf.ABSDESValues)) <= self.param.param['constraints']['operationPointChange']['MeOHWaterInCycleDownwardBound'] * timeStep for t in self.time[1:]), "Operation point change absorption/desorption downward bound")
