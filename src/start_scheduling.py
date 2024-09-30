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

import numpy as np
import matplotlib.pyplot as plt
from copy import deepcopy
import os
import pickle
import matlab.engine

#####################################
########## Path management ##########
path = os.path.dirname(__file__)
path = os.path.abspath(os.path.join(path, os.pardir))

## Control parameters
optimizationHorizon = 5*24                  # Considered time period in hours
timeStep = 1                                # Time step of optimization in hours
timeLimit = 100                            # Time limit for the solver to terminate in seconds
optimalityGap = 0.01                        # Optimality gap for the solver to terminate 

numHoursToSimulate = 24                     # Number of hours to simulate before adaptation takes place

benchmark = False                          # If true benchmark scenario is calculated
sameOutputAsBenchmark = False               # If true the optimization has to has the exact same output as the benchmark scenario
testFeasibility = False                     # If true the optimization model will be tested for feasibility
rateOfChangeConstranints = False            # If true rate of change constraints will be considered
transitionConstraints = False                # If true transition constraints will be considered
powerSale = False                           # If true sale of power from battery will be considered
considerPV = False                          # If true pv data will be considered, otherwise it is set to zero
considerBattery = False                     # If true battery will be considered, otherwise it is set to zero
uncertaintyPV = False                       # If true uncertainty in pv-data will be considered as chance-constraints
uncertaintyPP = True                       # If true uncertainty in power price data will be considered with two stage stochastic optimization
checkPVUncertainty = False                  # If true uncertainty in pv-data will be used in simulations to validate normal scheduling which was optimized without considering pv uncertainty
checkPPUncertainty = False                  # If true uncertainty in popwer price data will be used in simulations to validate normal scheduling which was optimized without considering pp uncertainty 
strPathCharMapData = r'C:\PROJEKTE\PTX\Max\50_Daten\01_Stationäre_Kennfelder'
strPathCharMapDataCalc = r'C:\PROJEKTE\PTX\Max\50_Daten\01_Stationäre_Kennfelder\calc'
strPathCharMapDataDrift = r'C:\PROJEKTE\PTX\Max\50_Daten\01_Stationäre_Kennfelder\drift'
strPathPVData = r'C:\PROJEKTE\PTX\Max\50_Daten\05_PV'
strPathPPData = r'C:\PROJEKTE\PTX\Max\50_Daten\02_Energie' 
strPathInitialValues = r'C:\PROJEKTE\PTX\Max\21_Scheduling\gurobi\PtM' 
strPathAdaptationData = r'C:\PROJEKTE\PTX\Max\22_Adaptation'    

args = [optimizationHorizon, 
            timeStep, 
            timeLimit,
            optimalityGap,
            testFeasibility,
            numHoursToSimulate,  
            benchmark, 
            sameOutputAsBenchmark, 
            rateOfChangeConstranints, 
            transitionConstraints, 
            powerSale, 
            considerPV, 
            considerBattery, 
            uncertaintyPV, 
            uncertaintyPP,
            checkPVUncertainty,
            checkPPUncertainty,
            strPathCharMapData,
            strPathCharMapDataCalc,
            strPathPVData,
            strPathPPData,
            strPathInitialValues,
            strPathAdaptationData]


##################################
########## Optimization ##########

def funcInitialize(args):
    ## Load parameters
    param = Param(args)
    param.funcGet()

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

    ## Create models for optimization
    optModel = Optimization_Model(param)

    return param, cm, cmCalc, cmDrift, elec, pv, pp, optModel

def funcStartOptimization(argWorkflow, param, cm, cmCalc, cmDrift, elec, pv, pp, optModel):
    bUseCalcCharMap = argWorkflow[0]
    bUseDriftCharMap = argWorkflow[1]
    if len(argWorkflow) == 1:
        timeIteration = 25
    else:
        timeIteration = argWorkflow[2]

    ## Create characteristic fields
    cm.funcCreateCharacteristicMaps(strPathCharMapData)
    cmCalc.funcCreateCharacteristicMaps(strPathCharMapDataCalc)
    cmDrift.funcCreateCharacteristicMaps(strPathCharMapDataDrift)

    ## Parameter update
    elec.funcUpdate(param)
    pv.funcUpdate(param, timeIteration)
    pp.funcUpdate(param, timeIteration)
    param.funcUpdate(pv, pp, timeIteration)

    ########## Optimization ########

    ## Create models for optimization
    if bUseCalcCharMap == True:
        optModel.funcCreateOptimizationModel(cmCalc, elec, pv, pp)
        optModel.funcRunOptimization()

        ## Create results
        resultOpt = Result(param)
        resultOpt.funcGetResult(optModel, cmCalc, elec, pv, pp)
    elif bUseDriftCharMap == True:
        optModel.funcCreateOptimizationModel(cmDrift, elec, pv, pp)
        optModel.funcRunOptimization()

        ## Create results
        resultOpt = Result(param)
        resultOpt.funcGetResult(optModel, cmDrift, elec, pv, pp)
    else:
        optModel.funcCreateOptimizationModel(cm, elec, pv, pp)
        optModel.funcRunOptimization()

        ## Create results
        resultOpt = Result(param)
        resultOpt.funcGetResult(optModel, cm, elec, pv, pp)
    

    ########## Simulation ##########
    simulation = Simulation(param)
    
    # Mit gedriftetem Kennfeld -> Wahre Kosten bei Drift, diese Daten werden für die Adaption genutzt
    if bUseDriftCharMap == True:
        if param.param['controlParameters']['uncertaintyPP'] == False:

            simulation.funcStartSimulation(param, resultOpt, cmDrift, elec, pv, pp)
            resultOpt.funcSaveResult(optModel, "trueDriftCharMap")
    # Mit wahrem Kennfeld -> Wahre Kosten, diese Daten werden für die Adaption genutzt
    else:
        if param.param['controlParameters']['uncertaintyPP'] == False:

            simulation.funcStartSimulation(param, resultOpt, cm, elec, pv, pp)
            resultOpt.funcSaveResult(optModel, "trueCharMap")

    # Mit berechnetem Kennfeld -> Berechnete Kosten
    if bUseCalcCharMap == True:
        if param.param['controlParameters']['uncertaintyPP'] == False:
            simulation.funcStartSimulation(param, resultOpt, cmCalc, elec, pv, pp)

        resultOpt.funcSaveResult(optModel, "calcCharMap")

    
    resultOpt.funcPrintResult(optModel, cm, elec, pv, pp)

    #funcCheckUncertainty(param, resultOpt, cm, elec, pv, pp, simulation)

    return resultOpt, param, cm, cmCalc, cmDrift, elec, pv, pp, optModel

def funcCheckUncertainty(param, resultOpt, cm, elec, pv, pp, simulation):
    # Check scenarios with price uncertainty if pv uncertainty is not considered
    if param.param['controlParameters']['checkPPUncertainty'] == True:
        meanCosts = 0
        resultTemp = Result(param)
        for i in range(0, pp.iNumberUncertaintySamples):
            print(i)
            pp.arrPowerPriceHourly = pp.arrPowerPriceSamples[i]
            param.funcUpdate(pv,pp)
            resultOpt.dictResult["input"]["powerBought"] = resultOpt.dictResult["input"]["powerBoughtRaw"][i]
            resultOpt.dictResult["input"]["powerInBatteryBought"] = resultOpt.dictResult["input"]["powerInBatteryBoughtRaw"][i]
            resultOpt.dictResult["input"]["powerOutBattery"] = resultOpt.dictResult["input"]["powerOutBatteryRaw"][i]
            resultOpt.dictResult["input"]["powerOutBatterySold"] = resultOpt.dictResult["input"]["powerOutBatterySoldRaw"][i]
            resultTemp = deepcopy(resultOpt)
            simulation.funcStartSimulation(param, resultTemp, cm, elec, pv, pp)
            print("costs: " + str(resultTemp.result['costs']['all']))
            print(simulation.constrViolationOutput)
            meanCosts = meanCosts + resultTemp.dictResult['costs']['all']

        meanCosts = meanCosts / pv.iNumberUncertaintySamples
        print(meanCosts)

    # Check scenarios with pv uncertainty if price uncertainty is not considered
    elif param.param['controlParameters']['checkPVUncertainty'] == True:
        maxPowerBought = [0] * (param.param['controlParameters']['numberOfTimeSteps']+1)
        numberOfConstrViolations = 0
        meanCosts = 0
        resultTemp = Result(param)
        for i in range(0, pv.iNumberUncertaintySamples):
            pv.arrPowerAvailable = pv.arrPvSamples[i]
            param.funcUpdate(pv,pp)
            resultTemp = deepcopy(resultOpt)
            simulation.funcStartSimulation(param, resultTemp, cm, elec, pv, pp)
            if simulation.bConstrViolationInput == True:
                numberOfConstrViolations = numberOfConstrViolations + 1
            print(simulation.dictConstrViolationOutput)
            for t in range(0, param.param['controlParameters']['numberOfTimeSteps']+1):
                if resultTemp.dictResult['input']['powerBought'][t] >= maxPowerBought[t]:
                    maxPowerBought[t] = resultTemp.dictResult['input']['powerBought'][t]

            meanCosts = meanCosts + resultTemp.dictResult['costs']['all']
        
        maxPowerBoughtPrice = [i*j for i,j in zip(maxPowerBought, param.param['prices']['power'])]
        meanCosts = meanCosts / pv.iNumberUncertaintySamples
        print(np.sum(maxPowerBoughtPrice))
        print(meanCosts)
        print(numberOfConstrViolations)



def main(argWorkflow):
    param, cm, cmCalc, cmDrift, elec, pv, pp, optModel = funcInitialize(args)

    useAdaptation = False
    numberOfIterations = 101
    startDrift = 10
    endDrift = 15
    startCalculation = 5

    bUseCalcCharMap = False
    bUseDriftCharMap = False


    dataOpt, param, cm, cmCalc, cmDrift, elec, pv, pp, optModel = funcStartOptimization([bUseCalcCharMap,bUseDriftCharMap,0], param, cm, cmCalc, cmDrift, elec, pv, pp, optModel)

    if useAdaptation == True:
        path = r'C:\PROJEKTE\PTX\Max\22_Adaptation\src'
        pathParam = r'C:\PROJEKTE\PTX\Max\22_Adaptation\param.mat'
        eng = matlab.engine.start_matlab()
        eng.addpath(path)
        eng.createInstances(nargout=0)

        for i in range(1,numberOfIterations):

            eng.setup(i, startCalculation, startDrift, endDrift, pathParam, nargout=0)

            dataOpt, param, cm, cmCalc, elec, pv, pp, optModel = funcStartOptimization(argWorkflow, param, cm, cmCalc, elec, pv, pp, optModel)
    
            if i >= startCalculation:
                bUseCalcCharMap = True

            if i >= startDrift:
                bUseDriftCharMap = True
            
            dataOpt, param, cm, cmCalc, cmDrift, elec, pv, pp, optModel = funcStartOptimization([bUseCalcCharMap,bUseDriftCharMap,i], param, cm, cmCalc, cmDrift, elec, pv, pp, optModel)

    return dataOpt
    

    
if __name__ == "__main__":

    dataOpt = main([False, 0])
    
