#!/usr/bin/env python3.10
# %%

from characteristic_fields import *
from params import *
from optimization_model import *
from electrolyser_model import *
from pv_model import *
from result import *
from electricity_price import *
from simulation import *
from checkSimResults import *
from carbon_intensity import *

import numpy as np
import matplotlib.pyplot as plt
import os
import matlab.engine
import time

#####################################
########## Path management ##########
path = os.path.dirname(__file__)
path = os.path.abspath(os.path.join(path, os.pardir))

## Control parameters
optimizationHorizon = 5*24                 # Considered time period in hours
timeStep = 1                                # Time step of optimization in hours
timeLimit = 1000                           # Time limit for the solver to terminate in seconds
optimalityGap = 0.01                        # Optimality gap for the solver to terminate 

numHoursToSimulate = 24                     # Number of hours to simulate before adaptation takes place

objectiveFunction = 1                       # 1: Power costs, 2: Carbon intensity, 3: Amount methanol

benchmark = True                           # If true benchmark scenario is calculated
sameOutputAsBenchmark = False               # If true the optimization has to has the exact same output as the benchmark scenario
testFeasibility = False                     # If true the optimization model will be tested for feasibility
rateOfChangeConstranints = False            # If true rate of change constraints will be considered
transitionConstraints = False                # If true transition constraints will be considered
powerSale = False                           # If true sale of power from battery will be considered
powerPurchase = True                        # If true purchase of power from the grid will be considered
considerPV = False                          # If true pv data will be considered, otherwise it is set to zero
considerBattery = False                     # If true battery will be considered, otherwise it is set to zero
peakLoadCapping = False                     # If true, the power input is limited up to a fixed value

strPathCharMapData = r'C:\PROJEKTE\PTX\Max\50_Daten\01_Stationäre_Kennfelder\maps_Aspen_v3'
strPathCharMapDataCalc = r'C:\PROJEKTE\PTX\Max\50_Daten\01_Stationäre_Kennfelder\maps_Aspen_v3\calc'
strPathCharMapDataDrift = r'C:\PROJEKTE\PTX\Max\50_Daten\01_Stationäre_Kennfelder\maps_Aspen_v3\drift'
strPathPVData = r'C:\PROJEKTE\PTX\Max\50_Daten\05_PV'
strPathPPData = r'C:\PROJEKTE\PTX\Max\50_Daten\02_Energie' 
strPathInitialValues = r'C:\PROJEKTE\PTX\Max\21_Scheduling\gurobi\PtM_v3' 
strPathAdaptationData = r'C:\PROJEKTE\PTX\Max\22_Adaptation'    

args = [optimizationHorizon, 
            timeStep, 
            timeLimit,
            optimalityGap,
            testFeasibility,
            numHoursToSimulate,  
            objectiveFunction,
            benchmark, 
            sameOutputAsBenchmark, 
            rateOfChangeConstranints, 
            transitionConstraints, 
            powerSale, 
            powerPurchase,
            considerPV, 
            considerBattery, 
            peakLoadCapping,
            strPathCharMapData,
            strPathCharMapDataCalc,
            strPathPVData,
            strPathPPData,
            strPathInitialValues,
            strPathAdaptationData]


##################################
########## Optimization ##########

def funcInitialize(args, j):
    ## Load parameters
    param = Param(args)
    param.funcGet(j)

    ## Create characteristic fields
    cm = CharMap(param)
    cmCalc = CharMap(param)
    cmDrift = CharMap(param)

    ## Create electrolyser
    elec = Electrolyser(param)

    ## Create PV
    pv = PV(param)

    ## Create electricity price
    pp = PowerPrice(param)

    ## Create carbon intensity price
    ci = CarbonIntensity(param)

    ## Create models for optimization
    optModel = Optimization_Model(param)

    ## Create checks
    checkResults = CheckSimulationResults(param)

    
    return param, cm, cmCalc, cmDrift, elec, pv, pp, ci, optModel, checkResults

def funcStartOptimization(argWorkflow, param, cm, cmCalc, cmDrift, elec, pv, pp, ci, optModel, checkResults):
    bUseCalcCharMap = argWorkflow[0]
    bUseDriftCharMap = argWorkflow[1]
    if len(argWorkflow) == 1:
        timeIteration = 25
    else:
        timeIteration = argWorkflow[2]

    ## Create characteristic fields
    cm.funcCreateCharacteristicMaps(strPathCharMapData)
    #cmCalc.funcCreateCharacteristicMaps(strPathCharMapDataCalc)
    #cmDrift.funcCreateCharacteristicMaps(strPathCharMapDataDrift)

    ## Parameter update
    elec.funcUpdate(param)
    pv.funcUpdate(param, timeIteration)
    pp.funcUpdate(param, timeIteration)
    ci.funcUpdate(param, timeIteration)
    param.funcUpdate(pv, pp, ci, timeIteration)

    ########## Optimization ########

    ## Create models for optimization
    if bUseCalcCharMap == True:
        optModel.funcCreateOptimizationModel(cmCalc, elec, pv, pp, ci)
        optModel.funcRunOptimization()

        ## Create results
        resultOpt = Result(param)
        resultOpt.funcGetResult(optModel, cmCalc, elec, pv, pp, ci)
    elif bUseDriftCharMap == True:
        optModel.funcCreateOptimizationModel(cmDrift, elec, pv, pp, ci)
        optModel.funcRunOptimization()

        ## Create results
        resultOpt = Result(param)
        resultOpt.funcGetResult(optModel, cmDrift, elec, pv, pp, ci)
    else:
        optModel.funcCreateOptimizationModel(cm, elec, pv, pp, ci)
        optModel.funcRunOptimization()

        ## Create results
        resultOpt = Result(param)
        resultOpt.funcGetResult(optModel, cm, elec, pv, pp, ci)
    

    ########## Simulation ##########
    simulation = Simulation(param)
    
    if optModel.m.status != GRB.INFEASIBLE and optModel.m.SolCount > 0:
        # Mit gedriftetem Kennfeld -> Wahre Kosten bei Drift, diese Daten werden für die Adaption genutzt
        if bUseDriftCharMap == True:
            simulation.funcStartSimulation(param, resultOpt, cmDrift, elec, pv, pp, ci)
            resultOpt.funcSaveResult(optModel, "trueDriftCharMap")

        # Mit wahrem Kennfeld -> Wahre Kosten, diese Daten werden für die Adaption genutzt
        else:
            simulation.funcStartSimulation(param, resultOpt, cm, elec, pv, pp, ci)
            resultOpt.funcSaveResult(optModel, "trueCharMap")

        # Mit berechnetem Kennfeld -> Berechnete Kosten
        if bUseCalcCharMap == True:
            simulation.funcStartSimulation(param, resultOpt, cmCalc, elec, pv, pp, ci)
            resultOpt.funcSaveResult(optModel, "calcCharMap")
    
        resultOpt.funcPrintResult(optModel, cm, elec, pv, pp, ci)
        resultOpt.funcVisualizationResult(optModel, cm, elec, pv, pp, ci)
    
    else:
        resultOpt.funcSaveResult(optModel, "trueCharMap")


    #checkResults.funcStartCheck(param, resultOpt, cm, elec, pv, pp, ci, simulation)

    return resultOpt, param, cm, cmCalc, cmDrift, elec, pv, pp, ci, optModel, checkResults


def main(argWorkflow):
    for j in range(0, 1):
        param, cm, cmCalc, cmDrift, elec, pv, pp, ci, optModel, checkResults = funcInitialize(args, j)

        useAdaptation = False
        scheduleMoreTimes = True

        numberOfIterations = 1


        bUseCalcCharMap = False
        bUseDriftCharMap = False
        

        if scheduleMoreTimes == True:
            for i in range(0, numberOfIterations):           
                dataOpt, param, cm, cmCalc, cmDrift, elec, pv, pp, ci, optModel, checkResults = funcStartOptimization([bUseCalcCharMap,bUseDriftCharMap,i], param, cm, cmCalc, cmDrift, elec, pv, pp, ci, optModel, checkResults)        
            #     dataOpt, param, cm, cmCalc, cmDrift, elec, pv, pp, ci, optModel, checkResults = funcStartOptimization([bUseCalcCharMap,bUseDriftCharMap,j], param, cm, cmCalc, cmDrift, elec, pv, pp, ci, optModel, checkResults)
        else:
            dataOpt, param, cm, cmCalc, cmDrift, elec, pv, pp, ci, optModel, checkResults = funcStartOptimization([bUseCalcCharMap,bUseDriftCharMap,0], param, cm, cmCalc, cmDrift, elec, pv, pp, ci, optModel, checkResults)
            

        startDrift = 10
        endDrift = 15
        startCalculation = 5

        if useAdaptation == True:
            path = r'C:\PROJEKTE\PTX\Max\22_Adaptation\src'
            pathParam = r'C:\PROJEKTE\PTX\Max\22_Adaptation\param.mat'
            eng = matlab.engine.start_matlab()
            eng.addpath(path)
            eng.createInstances(nargout=0)

            for i in range(1,numberOfIterations):

                eng.setup(i, startCalculation, startDrift, endDrift, pathParam, nargout=0)

                dataOpt, param, cm, cmCalc, elec, pv, pp, ci, optModel, checkResults = funcStartOptimization(argWorkflow, param, cm, cmCalc, elec, pv, pp, ci, optModel, checkResults)
        
                if i >= startCalculation:
                    bUseCalcCharMap = True

                if i >= startDrift:
                    bUseDriftCharMap = True
                
                dataOpt, param, cm, cmCalc, cmDrift, elec, pv, pp, ci, optModel, checkResults = funcStartOptimization([bUseCalcCharMap,bUseDriftCharMap,i], param, cm, cmCalc, cmDrift, elec, pv, pp, ci, optModel, checkResults)


    return dataOpt
    

    
if __name__ == "__main__":

    dataOpt = main([False, 0])
    

# %%
