#!/usr/bin/env python3.10

from characteristic_fields import *

import gurobipy as gp
from gurobipy import GRB
from gurobipy import *

class Optimization_Model():

    def __init__(self, param, cf, elec, pv):
        self.param = param  
        self.cf = cf
        self.elec = elec
        self.pv = pv



    def create_optimization_model(self):
        self.time = list(range(0,self.param['controlParameters']['optimizationHorizon']+1))

        self.m = gp.Model('ptm')

        self.create_variables()
        self.create_constraints()
        self.create_cost_function()

        self.m.update()



    def run_optimization(self):
        #self.m.Params.TimeLimit = self.param['controlParameters']['timeLimit']
        self.m.Params.MIPGap = 0.01
        if self.param['controlParameters']['testFeasibility'] == True:
            self.m.computeIIS()
            self.m.write("model.ilp")
        
        self.m.optimize()



    ########## Variables ##########
    def create_variables(self):
        cf = self.cf
        pv = self.pv
        param = self.param

        self.operationPoint_ABSDES = self.m.addVars(self.time,cf.hydrogenInValues,cf.biogasInValues, vtype=GRB.BINARY)
        self.operationPoint_MEOHSYN = self.m.addVars(self.time,cf.synthesisgasInMethanolSynthesisValues, vtype=GRB.BINARY)
        self.operationPoint_DIS = self.m.addVars(self.time,cf.methanolWaterInDistillationValues, vtype=GRB.BINARY)
        self.operationPointSwitch = self.m.addVars(self.time,[1,2,3],vtype=GRB.BINARY)

        self.powerElectrolyser = self.m.addVars(self.time,param['electrolyser']['numberOfEnapterModules'],lb=param['electrolyser']['powerLowerBound'], ub=param['electrolyser']['powerUpperBound'],vtype=GRB.CONTINUOUS)
        self.electrolyserMode = self.m.addVars(self.time,param['electrolyser']['numberOfEnapterModules'],4, vtype=GRB.BINARY)
        self.usageOfPV = self.m.addVars(self.time,lb=0.0,ub=1000,vtype=GRB.CONTINUOUS)
        self.powerInBatteryPV = self.m.addVars(self.time,lb=0,ub=param['battery']['maxChargeRate'], vtype=GRB.CONTINUOUS)
        self.powerInBatteryBought = self.m.addVars(self.time,lb=0,ub=param['battery']['maxChargeRate'], vtype=GRB.CONTINUOUS)
        self.powerOutBattery = self.m.addVars(self.time,lb=0,ub=param['battery']['maxDischargeRate'], vtype=GRB.CONTINUOUS)
        self.powerOutBatterySold = self.m.addVars(self.time,lb=0,ub=param['battery']['maxDischargeRate'], vtype=GRB.CONTINUOUS)
        self.powerBought = self.m.addVars(self.time,lb=0.0,ub=100,vtype=GRB.CONTINUOUS)

        if param['controlParameters']['uncertainty'] == True:
            self.indicatorPV = self.m.addVars(range(0,pv.uncertaintySamples),vtype=GRB.BINARY)




    ########## Cost function ##########
    def create_cost_function(self):
        cf = self.cf
        param = self.param
        time = self.time


        self.m.setObjective(1000 - gp.quicksum(cf.massFlowMethanolOut[(j)] * self.operationPoint_DIS[(i,j)] * param['prices']['methanol']  for i in time for j in cf.methanolWaterInDistillationValues)
                - gp.quicksum(cf.volumeBiogasOut[(j,k)] * self.operationPoint_ABSDES[(i,j,k)] * param['methane']['brennwert'] * param['prices']['methane'] for i in time for j in cf.hydrogenInValues for k in cf.biogasInValues)
                + gp.quicksum(cf.volumeBiogasIn[(j,k)] * self.operationPoint_ABSDES[(i,j,k)] * param['biogas']['brennwert'] * param['prices']['biogas'] for i in time for j in cf.hydrogenInValues for k in cf.biogasInValues)
                + gp.quicksum(param['prices']['power'][i] * self.powerBought[i] for i in time)
                - gp.quicksum(param['prices']['powerSold'] * self.powerOutBatterySold[i] for i in time),GRB.MINIMIZE)



    ########## Constraints ##########
    def create_constraints(self):
        cf = self.cf
        elec = self.elec
        pv = self.pv
        param = self.param
        time = self.time

        if param['controlParameters']['benchmark'] == False:
            if param['controlParameters']['sameOutputAsBenchmark'] == False:
                self.m.addConstr(
                    (gp.quicksum(cf.massFlowMethanolOut[(j)] * self.operationPoint_DIS[(t,j)] for j in cf.methanolWaterInDistillationValues for t in time) >= param['methanol']['minimumAmountOpt']), "Minimum amount methanol produced")    
            else:
                self.m.addConstr(
                    (gp.quicksum(cf.massFlowMethanolOut[(j)] * self.operationPoint_DIS[(t,j)] for j in cf.methanolWaterInDistillationValues for t in time) <= param['methanol']['sameAmountBenchmark']*1.01), "Amount methanol produced is same as benchmark upper bound") 
                self.m.addConstr(
                    (gp.quicksum(cf.massFlowMethanolOut[(j)] * self.operationPoint_DIS[(t,j)] for j in cf.methanolWaterInDistillationValues for t in time) >= param['methanol']['sameAmountBenchmark']), "Amount methanol produced is same as benchmark lower bound")    
                self.m.addConstr(
                    (gp.quicksum(cf.volumeBiogasOut[(j,k)] * self.operationPoint_ABSDES[(t,j,k)] for j in cf.hydrogenInValues for k in cf.biogasInValues for t in time) <= param['methane']['sameAmountVolumeBenchmark']*1.01), "Amount methane (volume) produced is same as benchmark upper bound")    
                self.m.addConstr(
                    (gp.quicksum(cf.volumeBiogasOut[(j,k)] * self.operationPoint_ABSDES[(t,j,k)] for j in cf.hydrogenInValues for k in cf.biogasInValues for t in time) >= param['methane']['sameAmountVolumeBenchmark']), "Amount methane (volume) produced is same as benchmark lower bound") 

        if param['controlParameters']['benchmark'] == True:
            # Minimum amount of methanol which has to be produced
            self.m.addConstr(
                (gp.quicksum(cf.massFlowMethanolOut[(j)] * self.operationPoint_DIS[(t,j)] for j in cf.methanolWaterInDistillationValues for t in time) >= param['methanol']['minimumAmountBenchmark']), "Minimum amount methanol produced benchmark")
            # The same operation point for absorption and desorption for every time step
            self.m.addConstrs(
                (self.operationPoint_ABSDES[(t-1,j,k)] == self.operationPoint_ABSDES[(t,j,k)] for t in time[2:] for j in cf.hydrogenInValues for k in cf.biogasInValues), "Benchmark operation point absorption, desorption and methanolsynthesis")
            # The same operation point for distillation for every time step
            self.m.addConstrs(
                (self.operationPoint_DIS[(t-1,j)] == self.operationPoint_DIS[(t,j)] for t in time[2:] for j in cf.methanolWaterInDistillationValues), "Benchmark operation point distillation")
            # The same operation point for methanol synthesis for every time step
            self.m.addConstrs(
                (self.operationPoint_MEOHSYN[(t-1,j)] == self.operationPoint_MEOHSYN[(t,j)] for t in time[2:] for j in cf.synthesisgasInMethanolSynthesisValues), "Benchmark operation point methanol synthesis")
            # The same power in electrolyser for every time step
            #self.m.addConstrs(
            #    (self.powerElectrolyser[(t-1,n)] == self.powerElectrolyser[(t,n)] for t in time[2:] for n in elec.enapterModules), "Benchmark power electrolyser")

            
        if param['controlParameters']['benchmark'] == False:

            if param['controlParameters']['transitionConstraints'] == True:

                ## Minimum stay time per mode constraints
                self.m.addConstrs(
                    (gp.quicksum(self.operationPoint_ABSDES[(i,j,k)] for i in time[t:t+param['constraints']['transitionTimes']['minimumStayTimeABSDES']] for j in cf.hydrogenInValues[1:] for k in cf.biogasInValues[1:]) >= self.operationPointSwitch[(t,1)]*param['constraints']['transitionTimes']['minimumStayTimeABSDES'] for t in time[1:]), "Mode switching minimum stay constraint ABSDES")
                self.m.addConstrs(
                    (gp.quicksum(self.operationPoint_MEOHSYN[(i,j)] for i in time[t:t+param['constraints']['transitionTimes']['minimumStayTimeMEOHSYN']] for j in cf.synthesisgasInMethanolSynthesisValues[1:]) >= self.operationPointSwitch[(t,2)]*param['constraints']['transitionTimes']['minimumStayTimeMEOHSYN'] for t in time[1:]), "Mode switching minimum stay constraint MEOHSYN")
                self.m.addConstrs(
                    (gp.quicksum(self.operationPoint_DIS[(i,j)] for i in time[t:t+param['constraints']['transitionTimes']['minimumStayTimeDIS']] for j in cf.methanolWaterInDistillationValues[1:]) >= self.operationPointSwitch[(t,3)]*param['constraints']['transitionTimes']['minimumStayTimeDIS'] for t in time[1:]), "Mode switching minimum stay constraint DIS")
                
                
                ## Maximum stay time per mode constraints
                self.m.addConstrs(
                    ((1 - gp.quicksum(self.operationPoint_ABSDES[(t+param['constraints']['transitionTimes']['maximumStayTimeABSDES'],j,k)] for j in cf.hydrogenInValues[1:] for k in cf.biogasInValues[1:])) >= self.operationPointSwitch[(t,1)] - gp.quicksum(self.operationPoint_ABSDES[(t+i,0,0)] for i in range(param['constraints']['transitionTimes']['minimumStayTimeABSDES'],param['constraints']['transitionTimes']['maximumStayTimeABSDES'])) for t in time[1:-(param['constraints']['transitionTimes']['maximumStayTimeABSDES'])]), "Mode switching maximum stay constraint mode ABSDES")
                self.m.addConstrs(
                    ((1 - gp.quicksum(self.operationPoint_MEOHSYN[(t+param['constraints']['transitionTimes']['maximumStayTimeMEOHSYN'],j)] for j in cf.synthesisgasInMethanolSynthesisValues[1:])) >= self.operationPointSwitch[(t,2)] - gp.quicksum(self.operationPoint_MEOHSYN[(t+i,0)] for i in range(param['constraints']['transitionTimes']['minimumStayTimeMEOHSYN'],param['constraints']['transitionTimes']['maximumStayTimeMEOHSYN'])) for t in time[1:-(param['constraints']['transitionTimes']['maximumStayTimeMEOHSYN'])]), "Mode switching maximum stay constraint mode MEOHSYN")
                self.m.addConstrs(
                    ((1 - gp.quicksum(self.operationPoint_DIS[(t+param['constraints']['transitionTimes']['maximumStayTimeDIS'],j)] for j in cf.methanolWaterInDistillationValues[1:])) >= self.operationPointSwitch[(t,3)] - gp.quicksum(self.operationPoint_DIS[(t+i,0)] for i in range(param['constraints']['transitionTimes']['minimumStayTimeDIS'],param['constraints']['transitionTimes']['maximumStayTimeDIS'])) for t in time[1:-(param['constraints']['transitionTimes']['maximumStayTimeDIS'])]), "Mode switching maximum stay constraint mode DIS")

            ## Mode switching constraints
            self.m.addConstrs(
                (self.operationPoint_ABSDES[(i-1,0,0)] >= self.operationPointSwitch[(i,1)] for i in time[1:]), "Mode switching ABSDES 1")
            self.m.addConstrs(
                (gp.quicksum(self.operationPoint_ABSDES[(i,j,k)] for j in cf.hydrogenInValues[1:] for k in cf.biogasInValues[1:]) >= self.operationPointSwitch[(i,1)] for i in time[0:]), "Mode switching ABSDES 2")
            self.m.addConstrs(
                (self.operationPoint_ABSDES[(i-1,0,0)] + gp.quicksum(self.operationPoint_ABSDES[(i,j,k)] for j in cf.hydrogenInValues[1:] for k in cf.biogasInValues[1:]) - 1 <= self.operationPointSwitch[(i,1)] for i in time[1:]), "Mode switching ABSDES 3")

            self.m.addConstrs(
                (self.operationPoint_MEOHSYN[(i-1,0)] >= self.operationPointSwitch[(i,2)] for i in time[1:]), "Mode switching MEOHSYN 1")
            self.m.addConstrs(
                (gp.quicksum(self.operationPoint_MEOHSYN[(i,j)] for j in cf.synthesisgasInMethanolSynthesisValues[1:]) >= self.operationPointSwitch[(i,2)] for i in time[0:]), "Mode switching MEOHSYN 2")
            self.m.addConstrs(
                (self.operationPoint_MEOHSYN[(i-1,0)] + gp.quicksum(self.operationPoint_MEOHSYN[(i,j)] for j in cf.synthesisgasInMethanolSynthesisValues[1:]) - 1 <= self.operationPointSwitch[(i,2)] for i in time[1:]), "Mode switching MEOHSYN 3")

            self.m.addConstrs(
                (self.operationPoint_DIS[(i-1,0)] >= self.operationPointSwitch[(i,3)] for i in time[1:]), "Mode switching DIS 1")
            self.m.addConstrs(
                (gp.quicksum(self.operationPoint_DIS[(i,j)] for j in cf.methanolWaterInDistillationValues[1:]) >= self.operationPointSwitch[(i,3)] for i in time[0:]), "Mode switching DIS 2")
            self.m.addConstrs(
                (self.operationPoint_DIS[(i-1,0)] + gp.quicksum(self.operationPoint_DIS[(i,j)] for j in cf.methanolWaterInDistillationValues[1:]) - 1 <= self.operationPointSwitch[(i,3)] for i in time[1:]), "Mode switching DIS 3")

        ## Power Constraints
        # power from battery and PV and grid to electrolyser and components must equal to needed power
        self.m.addConstrs(
            (self.powerOutBattery[i] + self.usageOfPV[i] + self.powerBought[i] - self.powerInBatteryBought[i] == (
            gp.quicksum(self.powerElectrolyser[(i,n)] * self.electrolyserMode[(i,n,3)] for n in elec.enapterModules)
            + gp.quicksum(elec.powerElectrolyserMode[(n,m)] * self.electrolyserMode[(i,n,m)] for n in elec.enapterModules for m in elec.modes[:-1])
            + gp.quicksum(cf.powerPlantComponentsUnit1[(j,k)] * self.operationPoint_ABSDES[(i,j,k)] for j in cf.hydrogenInValues for k in cf.biogasInValues)
            + gp.quicksum(cf.powerPlantComponentsUnit2[(j)] * self.operationPoint_MEOHSYN[(i,j)] for j in cf.synthesisgasInMethanolSynthesisValues)
            + gp.quicksum(cf.powerPlantComponentsUnit3[(j)] * self.operationPoint_DIS[(i,j)] for j in cf.methanolWaterInDistillationValues))
            for i in time[1:]), "Battery output maximum")

        # Power to battery has always to be smaller than power bought
        self.m.addConstrs(
            (self.powerInBatteryBought[i] <= self.powerBought[i] for i in time[1:]), "Power to battery has always to be smaller than power bought")

        # Power can not be sold and bought at the same time
        self.m.addConstrs(
            (self.powerInBatteryBought[t] * self.powerOutBatterySold[t] == 0 for t in time[1:]), "Power can not be sold and bought at the same time 1")
        self.m.addConstrs(
            (self.powerBought[i] * self.powerOutBatterySold[i] == 0 for i in time[1:]), "Power can not be sold and bought at the same time 2")

        # Battery can not be discharged and charged at the same time
        self.m.addConstrs(
            (self.powerInBatteryBought[i] * self.powerOutBattery[i] == 0 for i in time[1:]), "Battery charge and discharge time 1")
        self.m.addConstrs(
            (self.powerInBatteryPV[i] * self.powerOutBattery[i] == 0 for i in time[1:]), "Battery charge and discharge time 2")
        self.m.addConstrs(
            (self.powerInBatteryPV[i] * self.powerOutBatterySold[i] == 0 for i in time[1:]), "Battery charge and discharge time 3")
        
        # Charge and discharge rate have to be smaller than maximum rate
        self.m.addConstrs(
            (self.powerInBatteryBought[i] + self.powerInBatteryPV[i] <= param['battery']['maxChargeRate'] for i in time[1:]), "Battery charge rate")
        self.m.addConstrs(
            (self.powerOutBattery[i] + self.powerOutBatterySold[i] <= param['battery']['maxDischargeRate'] for i in time[1:]), "Battery discharge rate")

        # Power used from PV and stored in PV from battery must be smaller than power available from PV
        if param['controlParameters']['uncertainty'] == True:
            self.m.addConstrs(
                (self.usageOfPV[i] + self.powerInBatteryPV[i] <= pv.pvSamples[r,i] + 1000*(1-self.indicatorPV[r]) for i in time[1:] for r in range(0,pv.uncertaintySamples)), "PV upper bound available")
            self.m.addConstr(
                (gp.quicksum(self.indicatorPV[r] for r in range(0,pv.uncertaintySamples)) >= pv.alpha*pv.uncertaintySamples), 'Indicator PV')
        else:
            self.m.addConstrs(
                (self.usageOfPV[i] + self.powerInBatteryPV[i] <= pv.powerAvailable[i] for i in time[1:]), "PV upper bound available")

        # Power cannot be sold
        if param['controlParameters']['powerSale'] == False:
            self.m.addConstrs(
                (self.powerOutBatterySold[i] == 0 for i in time[1:]), "No power can be sold")



        ## Minimum operation point/operation mode constraint
        # Exactly one operation point for absorption, desorption and methanol synthesis has to be selected in every time step
        self.m.addConstrs(
            (self.operationPoint_ABSDES.sum(i,'*','*') == 1.0 for i in time), "Exactly one operation point for absorption, desorption and methanol synthesis per time step")
        # Exactly one operation point for methanol synthesis has to be selected every time step
        self.m.addConstrs(
            (self.operationPoint_MEOHSYN.sum(i,'*') == 1.0 for i in time), "Exactly one operation point for methanol synthesis per time step")
        # Exactly one operation point for distillation has to be selected in every time step
        self.m.addConstrs(
            (self.operationPoint_DIS.sum(i,'*') == 1.0 for i in time), "Exactly one operation point for distillation per time step")
        self.m.addConstrs(
            (gp.quicksum(self.electrolyserMode[(i,n,m)] for m in elec.modes) == 1 for i in time for n in elec.enapterModules), "one operation mode for electrolyser per time period")


        ## Initial time step constraints
        # No operation point for absorption, desorption and methanol synthesis in initial time step
        self.m.addConstr(
            (self.operationPoint_ABSDES[(0,0,0)] == 1), "No operation point for absorption, desorption and methanol synthesis in initial time step")
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
        self.m.addConstr(
            (self.powerInBatteryBought[0] == 0), "Power bought battery initial time step")
        self.m.addConstr(
            (self.powerOutBattery[0] == 0), "power out battery initial time step")
        self.m.addConstr(
            (self.powerOutBatterySold[0] == 0), "power sold battery initial time step")

        ## Operation points constraints
        # Sets all combinations of input variables for absorption, desorption and methanol synthesis to 0, where exactly one input variable is 0 because they are not defined 
        self.m.addConstrs(
            (gp.quicksum(self.operationPoint_ABSDES[(i,j,0)] for j in cf.hydrogenInValues[1:]) == 0 for i in time[1:]), 'Set not defined operation points of absorption, desorption and methanol synthesis to 0 (1)')
        self.m.addConstrs(
            (gp.quicksum(self.operationPoint_ABSDES[(i,0,j)] for j in cf.biogasInValues[1:]) == 0 for i in time[1:]), 'Set not defined operation points of absorption, desorption and methanol synthesis to 0 (2)')
        # Electrolyser constraints
        self.m.addConstrs(
            (self.electrolyserMode[(i-1,n,0)] <= self.electrolyserMode[(i,n,3)] for i in time[1:] for n in elec.enapterModules), "Electrolyser after off comes off or ramp-up")
        self.m.addConstrs(
            (self.electrolyserMode[(i-1,n,1)] <= gp.quicksum(self.electrolyserMode[(i,n,m)] for m in [2,3]) for i in time[1:] for n in elec.enapterModules), "Electrolyser after off comes off or ramp-up")
        self.m.addConstrs(
            (self.electrolyserMode[(i-1,n,2)] <= gp.quicksum(self.electrolyserMode[(i,n,m)] for m in [0,2]) for i in time[1:] for n in elec.enapterModules), "Electrolyser after off comes off or ramp-up")
        self.m.addConstrs(
            (self.electrolyserMode[(i-1,n,3)] <= gp.quicksum(self.electrolyserMode[(i,n,m)] for m in [1,2,3]) for i in time[1:] for n in elec.enapterModules), "Electrolyser after off comes off or ramp-up")


        ## Hydrogen storage constraints
        self.m.addConstrs(
            ((param['storageH2']['InitialFilling'] 
                + gp.quicksum(self.powerElectrolyser[(l,n)] * self.electrolyserMode[(l,n,3)] * (param['electrolyser']['constant']) for l in time[0:i+1] for n in elec.enapterModules)
                - gp.quicksum(cf.massFlowHydrogenIn[(j,k)] * self.operationPoint_ABSDES[(l,j,k)] for j in cf.hydrogenInValues for k in cf.biogasInValues for l in time[0:i+1]) 
                - gp.quicksum(cf.massFlowAdditionalHydrogen[(j,k)] * self.operationPoint_ABSDES[(l,j,k)] for j in cf.hydrogenInValues for k in cf.biogasInValues for l in time[0:i+1])) 
                * param['R_H2'] * (param['Tamb'] + param['T0']) / (param['storageH2']['Volume'] * 100000) <= param['storageH2']['UpperBound'] for i in time), "Storage H2 upper bound")
        self.m.addConstrs(
            ((param['storageH2']['InitialFilling'] 
                + gp.quicksum(self.powerElectrolyser[(l,n)] * self.electrolyserMode[(l,n,3)] * (param['electrolyser']['constant']) for l in time[0:i+1] for n in elec.enapterModules)
                - gp.quicksum(cf.massFlowHydrogenIn[(j,k)] * self.operationPoint_ABSDES[(l,j,k)] for j in cf.hydrogenInValues for k in cf.biogasInValues for l in time[0:i+1]) 
                - gp.quicksum(cf.massFlowAdditionalHydrogen[(j,k)] * self.operationPoint_ABSDES[(l,j,k)] for j in cf.hydrogenInValues for k in cf.biogasInValues for l in time[0:i+1])) 
                * param['R_H2'] * (param['Tamb'] + param['T0']) / (param['storageH2']['Volume'] * 100000) >= param['storageH2']['LowerBound'] for i in time), "Storage H2 lower bound")
        self.m.addConstr(
            ((param['storageH2']['InitialFilling'] * param['R_H2'] * (param['Tamb'] + param['T0']) / (param['storageH2']['Volume'] * 100000)) -
                (param['storageH2']['InitialFilling'] + gp.quicksum(self.powerElectrolyser[(l,n)] * self.electrolyserMode[(l,n,3)] * (param['electrolyser']['constant']) for l in time for n in elec.enapterModules)
                - gp.quicksum(cf.massFlowHydrogenIn[(j,k)] * self.operationPoint_ABSDES[(l,j,k)] for j in cf.hydrogenInValues for k in cf.biogasInValues for l in time) 
                - gp.quicksum(cf.massFlowAdditionalHydrogen[(j,k)] * self.operationPoint_ABSDES[(l,j,k)] for j in cf.hydrogenInValues for k in cf.biogasInValues for l in time)) 
                * param['R_H2'] * (param['Tamb'] + param['T0']) / (param['storageH2']['Volume'] * 100000) <= param['constraints']['hydrogenStorageFillEqual']['UpperBound']), "Storage H2 equal filling upper bound")
        self.m.addConstr(
            ((param['storageH2']['InitialFilling'] * param['R_H2'] * (param['Tamb'] + param['T0']) / (param['storageH2']['Volume'] * 100000)) -
                (param['storageH2']['InitialFilling'] + gp.quicksum(self.powerElectrolyser[(l,n)] * self.electrolyserMode[(l,n,3)] * (param['electrolyser']['constant']) for l in time for n in elec.enapterModules)
                - gp.quicksum(cf.massFlowHydrogenIn[(j,k)] * self.operationPoint_ABSDES[(l,j,k)] for j in cf.hydrogenInValues for k in cf.biogasInValues for l in time) 
                - gp.quicksum(cf.massFlowAdditionalHydrogen[(j,k)] * self.operationPoint_ABSDES[(l,j,k)] for j in cf.hydrogenInValues for k in cf.biogasInValues for l in time)) 
                * param['R_H2'] * (param['Tamb'] + param['T0']) / (param['storageH2']['Volume'] * 100000) >= param['constraints']['hydrogenStorageFillEqual']['LowerBound']), "Storage H2 equal filling lower bound")


        ## Methanol water storage constraints
        self.m.addConstrs(
            ((param['storageMethanolWater']['InitialFilling'] 
                + gp.quicksum(cf.massFlowMethanolWaterStorageInSynthesis[(i)] / param['storageMethanolWater']['InitialDensity'] * self.operationPoint_MEOHSYN[(l,i)] for i in cf.synthesisgasInMethanolSynthesisValues for l in time[0:h+1]) 
                - gp.quicksum(cf.massFlowMethanolWaterStorageOut[(i)] / param['storageMethanolWater']['InitialDensity']  * self.operationPoint_DIS[(l,i)] for i in cf.methanolWaterInDistillationValues for l in time[0:h+1])) >= param['storageMethanolWater']['LowerBound'] for h in time), "Storage methanol water lower bound")
        self.m.addConstrs(
            ((param['storageMethanolWater']['InitialFilling'] 
                + gp.quicksum(cf.massFlowMethanolWaterStorageInSynthesis[(i)] / cf.densityMethanolWaterStorageInSynthesis[(i)] * self.operationPoint_MEOHSYN[(l,i)] for i in cf.synthesisgasInMethanolSynthesisValues for l in time[0:h+1])  
                - gp.quicksum(cf.massFlowMethanolWaterStorageOut[(i)] / param['storageMethanolWater']['InitialDensity']  * self.operationPoint_DIS[(l,i)] for i in cf.methanolWaterInDistillationValues for l in time[0:h+1])) <= param['storageMethanolWater']['UpperBound'] for h in time), "Storage methanol water upper bound")
        self.m.addConstr(
            (param['storageMethanolWater']['InitialFilling'] - 
            (param['storageMethanolWater']['InitialFilling'] 
                + gp.quicksum(cf.massFlowMethanolWaterStorageInSynthesis[(i)] / cf.densityMethanolWaterStorageInSynthesis[(i)] * self.operationPoint_MEOHSYN[(l,i)] for i in cf.synthesisgasInMethanolSynthesisValues for l in time)  
                - gp.quicksum(cf.massFlowMethanolWaterStorageOut[(i)] / param['storageMethanolWater']['InitialDensity']  * self.operationPoint_DIS[(l,i)] for i in cf.methanolWaterInDistillationValues for l in time)) <= param['constraints']['methanolWaterStorageFillEqual']['UpperBound']), "Storage methanol water equal filling upper bound")
        self.m.addConstr(
            (param['storageMethanolWater']['InitialFilling'] - 
            (param['storageMethanolWater']['InitialFilling'] 
                + gp.quicksum(cf.massFlowMethanolWaterStorageInSynthesis[(i)] / cf.densityMethanolWaterStorageInSynthesis[(i)] * self.operationPoint_MEOHSYN[(l,i)] for i in cf.synthesisgasInMethanolSynthesisValues for l in time)  
                - gp.quicksum(cf.massFlowMethanolWaterStorageOut[(i)] / param['storageMethanolWater']['InitialDensity']  * self.operationPoint_DIS[(l,i)] for i in cf.methanolWaterInDistillationValues for l in time))  >= param['constraints']['methanolWaterStorageFillEqual']['LowerBound']), "Storage methanol water equal filling lower bound")


        ## Battery constraints
        self.m.addConstrs(
            (param['battery']['initialCharge'] 
            + gp.quicksum(self.powerInBatteryPV[l] for l in time[0:i+1]) 
            + gp.quicksum(self.powerInBatteryBought[l] for l in time[0:i+1])
            - gp.quicksum(self.powerOutBattery[l] for l in time[0:i+1])
            - gp.quicksum(self.powerOutBatterySold[l] for l in time[0:i+1])
            <= param['battery']['capacity'] for i in time), "Battery upper bound")

        self.m.addConstrs(
            (param['battery']['initialCharge'] 
            + gp.quicksum(self.powerInBatteryPV[l] for l in time[0:i+1]) 
            + gp.quicksum(self.powerInBatteryBought[l] for l in time[0:i+1])
            - gp.quicksum(self.powerOutBattery[l] for l in time[0:i+1])
            - gp.quicksum(self.powerOutBatterySold[l] for l in time[0:i+1])
            >= param['battery']['capacity']*0.01 for i in time), "Battery lower bound")

        self.m.addConstr(
            (param['battery']['initialCharge'] - (param['battery']['initialCharge'] 
            + gp.quicksum(self.powerInBatteryPV[l] for l in time) 
            + gp.quicksum(self.powerInBatteryBought[l] for l in time)
            - gp.quicksum(self.powerOutBattery[l] for l in time)
            - gp.quicksum(self.powerOutBatterySold[l] for l in time)) <= param['constraints']['batteryChargeEqual']['UpperBound']), "Battery equal charge upper bound")

        self.m.addConstr(
            (param['battery']['initialCharge'] - (param['battery']['initialCharge'] 
            + gp.quicksum(self.powerInBatteryPV[l] for l in time) 
            + gp.quicksum(self.powerInBatteryBought[l] for l in time)
            - gp.quicksum(self.powerOutBattery[l] for l in time)
            - gp.quicksum(self.powerOutBatterySold[l] for l in time)) >= param['constraints']['batteryChargeEqual']['LowerBound']), "Battery equal charge lower bound")

        ## Synthesisgas storage
        self.m.addConstrs(
            ((param['storageSynthesisgas']['InitialFilling'] 
                + gp.quicksum(cf.massFlowSynthesisgasIn[(j,k)] * self.operationPoint_ABSDES[(l,j,k)] for j in cf.hydrogenInValues for k in cf.biogasInValues for l in time[0:h+1])
                - gp.quicksum(cf.massFlowSynthesisgasOut[(i)] * self.operationPoint_MEOHSYN[(l,i)] for i in cf.synthesisgasInMethanolSynthesisValues for l in time[0:h+1]))
                * param['R_Synthesisgas'] * (param['Tamb'] + param['T0']) / (param['storageSynthesisgas']['Volume'] * 100000) >= param['storageSynthesisgas']['LowerBound'] for h in time), "Storage synthesis gas lower bound")
        self.m.addConstrs(
            ((param['storageSynthesisgas']['InitialFilling']  
                + gp.quicksum(cf.massFlowSynthesisgasIn[(j,k)] * self.operationPoint_ABSDES[(l,j,k)] for j in cf.hydrogenInValues for k in cf.biogasInValues for l in time[0:h+1])
                - gp.quicksum(cf.massFlowSynthesisgasOut[(i)] * self.operationPoint_MEOHSYN[(l,i)] for i in cf.synthesisgasInMethanolSynthesisValues for l in time[0:h+1])) 
                * param['R_Synthesisgas'] * (param['Tamb'] + param['T0']) / (param['storageSynthesisgas']['Volume'] * 100000) <= param['storageSynthesisgas']['UpperBound'] for h in time), "Storage synthesis gas upper bound")
        self.m.addConstr(
            ((param['storageSynthesisgas']['InitialFilling']  * param['R_Synthesisgas'] * (param['Tamb'] + param['T0']) / (param['storageSynthesisgas']['Volume'] * 100000)) - 
                (param['storageSynthesisgas']['InitialFilling']  
                + gp.quicksum(cf.massFlowSynthesisgasIn[(j,k)] * self.operationPoint_ABSDES[(l,j,k)] for j in cf.hydrogenInValues for k in cf.biogasInValues for l in time)
                - gp.quicksum(cf.massFlowSynthesisgasOut[(i)] * self.operationPoint_MEOHSYN[(l,i)] for i in cf.synthesisgasInMethanolSynthesisValues for l in time))
                * param['R_Synthesisgas'] * (param['Tamb'] + param['T0']) / (param['storageSynthesisgas']['Volume'] * 100000) <= param['constraints']['synthesisgasStorageFillEqual']['UpperBound']), "Storage synthesis gas equal filling upper bound")
        self.m.addConstr(
            ((param['storageSynthesisgas']['InitialFilling'] * param['R_Synthesisgas'] * (param['Tamb'] + param['T0']) / (param['storageSynthesisgas']['Volume'] * 100000)) - 
            (param['storageSynthesisgas']['InitialFilling'] 
                + gp.quicksum(cf.massFlowSynthesisgasIn[(j,k)] * self.operationPoint_ABSDES[(l,j,k)] for j in cf.hydrogenInValues for k in cf.biogasInValues for l in time)
                - gp.quicksum(cf.massFlowSynthesisgasOut[(i)] * self.operationPoint_MEOHSYN[(l,i)] for i in cf.synthesisgasInMethanolSynthesisValues for l in time))
                * param['R_Synthesisgas'] * (param['Tamb'] + param['T0']) / (param['storageSynthesisgas']['Volume'] * 100000)  >= param['constraints']['synthesisgasStorageFillEqual']['LowerBound']), "Storage synthesis gas equal filling lower bound")

            

        ## Production constraints
        # Minimum amount of methane in outflowing biogas
        self.m.addConstrs(
            (gp.quicksum(cf.moleFractionMethaneBiogasOut[(j,k)] * self.operationPoint_ABSDES[(l,j,k)] for j in cf.hydrogenInValues for k in cf.biogasInValues) >= param['constraints']['minMoleFractionCH4BiogasOut'] for l in time[1:]), "Mole fraction methane biogas out")
        # Hydrogen to carbon dioxide ratio upper bound
        self.m.addConstrs(
            (gp.quicksum(cf.moleFractionHydrogenSynthesisgas[(j,k)] / cf.moleFractionCarbondioxideSynthesisgas[(j,k)] * self.operationPoint_ABSDES[(l,j,k)] for j in cf.hydrogenInValues for k in cf.biogasInValues) <= param['constraints']['maxRatioH2_CO2_Synthesisgas'] for l in time[1:]), "Hydrogen - carbon dixoide ratio upper bound")
        # Hydrogen to carbon dioxide ratio lower bound
        self.m.addConstrs(
            (gp.quicksum(cf.moleFractionHydrogenSynthesisgas[(j,k)] / cf.moleFractionCarbondioxideSynthesisgas[(j,k)] * self.operationPoint_ABSDES[(l,j,k)] for j in cf.hydrogenInValues for k in cf.biogasInValues) >= param['constraints']['minRatioH2_CO2_Synthesisgas'] for l in time[1:]), "Hydrogen - carbon dixoide ratio lower bound")


        ## Rate of change constraints
        if param['controlParameters']['rateOfChangeConstranints'] == True:
            # Distillation (mass flow methanol water from storage)
            self.m.addConstrs(
                ((gp.quicksum(cf.massFlowMethanolWaterStorageOut[(j)] * self.operationPoint_DIS[(l-1,j)] for j in cf.methanolWaterInDistillationValues)) - gp.quicksum((cf.massFlowMethanolWaterStorageOut[(j)] * self.operationPoint_DIS[(l,j)] for j in cf.methanolWaterInDistillationValues)) >= param['constraints']['operationPointChange']['distillationUpwardBound'] for l in time[2:]), "Operation point change distillation upward bound")
            self.m.addConstrs(
                ((gp.quicksum(cf.massFlowMethanolWaterStorageOut[(j)] * self.operationPoint_DIS[(l-1,j)] for j in cf.methanolWaterInDistillationValues)) - gp.quicksum((cf.massFlowMethanolWaterStorageOut[(j)] * self.operationPoint_DIS[(l,j)] for j in cf.methanolWaterInDistillationValues)) <= param['constraints']['operationPointChange']['distillationDownwardBound'] for l in time[2:]), "Operation point change distillation downward bound")

            # Methanol synthesis (mass flow synthesis gas)
            self.m.addConstrs(
                ((gp.quicksum(cf.massFlowSynthesisgasOut[(j)] * self.operationPoint_MEOHSYN[(l-1,j)] for j in cf.synthesisgasInMethanolSynthesisValues)) - gp.quicksum((cf.massFlowSynthesisgasOut[(j)] * self.operationPoint_MEOHSYN[(l,j)] for j in cf.synthesisgasInMethanolSynthesisValues)) >= param['constraints']['operationPointChange']['MeOHSynthesisUpwardBound'] for l in time[2:]), "Operation point change methanol synthesis upward bound")
            self.m.addConstrs(
                ((gp.quicksum(cf.massFlowSynthesisgasOut[(j)] * self.operationPoint_MEOHSYN[(l-1,j)] for j in cf.synthesisgasInMethanolSynthesisValues)) - gp.quicksum((cf.massFlowSynthesisgasOut[(j)] * self.operationPoint_MEOHSYN[(l,j)] for j in cf.synthesisgasInMethanolSynthesisValues)) <= param['constraints']['operationPointChange']['MeOHSynthesisDownwardBound'] for l in time[2:]), "Operation point change methanol synthesis upper downward")


            # Absorption/Desorption (mass flow methanol water in cycle)
            self.m.addConstrs(
                ((gp.quicksum(cf.massFlowMethanolWaterInCycle[(j,k)] * self.operationPoint_ABSDES[(l-1,j,k)] for j in cf.hydrogenInValues for k in cf.biogasInValues)) - gp.quicksum((cf.massFlowMethanolWaterInCycle[(j,k)] * self.operationPoint_ABSDES[(l,j,k)] for j in cf.hydrogenInValues for k in cf.biogasInValues)) >= param['constraints']['operationPointChange']['MeOHWaterInCycleUpwardBound'] for l in time[3:]), "Operation point change absorption/desorption upward bound")
            self.m.addConstrs(
                ((gp.quicksum(cf.massFlowMethanolWaterInCycle[(j,k)] * self.operationPoint_ABSDES[(l-1,j,k)] for j in cf.hydrogenInValues for k in cf.biogasInValues)) - gp.quicksum((cf.massFlowMethanolWaterInCycle[(j,k)] * self.operationPoint_ABSDES[(l,j,k)] for j in cf.hydrogenInValues for k in cf.biogasInValues)) <= param['constraints']['operationPointChange']['MeOHWaterInCycleDownwardBound'] for l in time[3:]), "Operation point change absorption/desorption downward bound")
