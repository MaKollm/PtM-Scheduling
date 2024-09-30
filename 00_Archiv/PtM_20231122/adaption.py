#!/usr/bin/env python3.10

from characteristic_fields import *
from params import *
from optimization_model import *
from electrolyser_model import *
from pv_model import *
from result import *
from simulation import *

import numpy as np


##############################
########## Adaption ##########

class Adaption():

    def __init__(self, param):
        self.param = param
        self.cfSim = CharField(param)
        self.cfSim.create_characteristic_fields()
        self.resultAdaption = Result(param)
        self.simulationAdaption = Simulation(param)

        self.iteration = 0
        self.adaptionInterval = 0
        self.optimizationInterval = 0
        self.adaptIndex = 0

        self.covFactorStart = 1

        # Drift variables
        np.random.seed(2)
        self.driftSign = []
        for i in range(0,len(self.cfSim.charField)):
            self.driftSign.append([])
            for j in range(0,len(self.cfSim.charField[i])):
                self.driftSign[i].append(2*np.random.randint(0,2,size=(len(self.cfSim.charField[i][j])))-1)


    def update(self, param):
        self.param = param


    def start(self, iteration, adaptionInterval, optimizationInterval, adaptIndex, cfOpt, elec, pv, pp, resultOpt):
        self.iteration = iteration
        self.adaptionInterval = adaptionInterval
        self.optimizationInterval = optimizationInterval
        self.adaptIndex = adaptIndex

        self.covFactor = self.covFactorStart + self.iteration*1

        self.simulate_cfSim_drift()
        self.simulate(resultOpt, elec, pv, pp)
        cfOpt = self.adapt_cf(resultOpt, cfOpt)

        return cfOpt, self.simulationAdaption, self.cfSim


    def simulate_cfSim_drift(self):

        self.cov = []
        for i in range(0,len(self.cfSim.charField)):
            self.cov.append([])
            for j in range(0,len(self.cfSim.charField[i])):
                self.cov[i].append(np.zeros((len(self.cfSim.charField[i][j]),len(self.cfSim.charField[i][j]))))


        self.mean = []
        for i in range(0,len(self.cfSim.charField)):
            self.mean.append([])
            for j in range(0,len(self.cfSim.charField[i])):
                self.mean[i].append(np.zeros(len(self.cfSim.charField[i][j])))
                if j >= 4:
                    for k in range(1,len(self.cfSim.charField[i][j])):
                        if i == 0:
                            self.mean[i][j][k] = self.cfSim.charField[i][j][(self.cfSim.opList_ABSDES[k])]
                            self.cov[i][j][k,k] = np.abs(self.mean[i][j][k] / self.covFactor)

                            self.cfSim.charField[i][j][(self.cfSim.opList_ABSDES[k])] = self.cfSim.charField[i][j][(self.cfSim.opList_ABSDES[k])] + np.abs(np.abs(self.cfSim.charField[i][j][(self.cfSim.opList_ABSDES[k])]) - np.abs(np.random.normal(self.mean[i][j][k], self.cov[i][j][k,k], 1)))[0] * self.driftSign[i][j][k]
                        else:
                            self.mean[i][j][k] = self.cfSim.charField[i][j][(k)]
                            self.cov[i][j][k,k] = np.abs(self.mean[i][j][k] / self.covFactor)
                            self.cfSim.charField[i][j][(k)] = self.cfSim.charField[i][j][(k)] + np.abs(np.abs(self.cfSim.charField[i][j][(k)]) - np.abs(np.random.normal(self.mean[i][j][k], self.cov[i][j][k,k], 1)))[0] * self.driftSign[i][j][k]
                            
    def simulate_sensor_values(self, optResult, elec, pv):
        # Simple method: just take value from characteristic field with drift
        

        # Complicated method: characteristic field with drift is ground truth, 
        # so simulate sensors a get values from normal distribution around ground truth in a specific time interval and take the mean value

        return self.cfSim.charField
    
    def simulate(self, optResult, elec, pv, pp):

        self.resultAdaption.result['input'] = optResult.result['input']
        self.simulationAdaption.start_simulation(self.param, self.resultAdaption, self.cfSim, elec, pv, pp)


    def adapt_cf(self, resultOpt, cfOpt):
        index = (self.adaptIndex % self.optimizationInterval) + 1
        # ABSDES
        for i in cfOpt.ABSDESValues:
            if resultOpt.result['input']['operationPoint_ABSDES'][index,i] == 1:
                for j in range(4,len(cfOpt.charField[0])): 
                    print(self.cfSim.charField[0][j][(i)])
                    cfOpt.charField[0][j][(i)] = self.cfSim.charField[0][j][(i)] - (cfOpt.charField[0][j][(i)] - self.cfSim.charField[0][j][(i)])*0.1

        for i in cfOpt.synthesisgasInMethanolSynthesisValues:
            if resultOpt.result['input']['operationPoint_MEOHSYN'][index,i] == 1:
                for j in range(3,len(cfOpt.charField[1])):
                    cfOpt.charField[1][j][(i)] = cfOpt.charField[1][j][(i)] - (cfOpt.charField[1][j][(i)] - self.cfSim.charField[1][j][(i)])*0.1

        for i in cfOpt.methanolWaterInDistillationValues:
            if resultOpt.result['input']['operationPoint_DIS'][index,i] == 1:
                for j in range(3,len(cfOpt.charField[2])):
                    cfOpt.charField[2][j][(i)] = self.cfSim.charField[2][j][(i)] - (cfOpt.charField[2][j][(i)] - self.cfSim.charField[2][j][(i)])*0.1

        return cfOpt 


    def visualize_cf(self):
        pass
