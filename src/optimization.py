#!/usr/bin/env python3.10

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
import imageio
from copy import deepcopy
from matplotlib.animation import FuncAnimation


##################################
########## Optimization ##########

def start_optimization():
    ## Control parameters
    optimizationHorizon = 5*24                  # Considered time period in hours
    timeStep = 1                                # Time step of optimization in hours
    timeLimit = 1000                            # Time limit for the solver to terminate in seconds
    optimalityGap = 0.01                        # Optimality gap for the solver to terminate 
    benchmark = True                            # If true benchmark scenario is calculated
    sameOutputAsBenchmark = True                # If true the optimization has to has the exact same output as the benchmark scenario
    testFeasibility = False                     # If true the optimization model will be tested for feasibility
    rateOfChangeConstranints = False            # If true rate of change constraints will be considered
    transitionConstraints = False               # If true transition constraints will be considered
    powerSale = False                           # If true sale of power from battery will be considered
    considerPV = False                          # If true pv data will be considered, otherwise it is set to zero
    considerBattery = False                     # If true battery will be considered, otherwise it is set to zero
    uncertaintyPV = False                       # If true uncertainty in pv-data will be considered as chance-constraints
    uncertaintyPP = False                       # If true uncertainty in power price data will be considered with two stage stochastic optimization
    checkPVUncertainty = False                  # If true uncertainty in pv-data will be used in simulations to validate normal scheduling which was optimized without considering pv uncertainty
    checkPPUncertainty = False                  # If true uncertainty in popwer price data will be used in simulations to validate normal scheduling which was optimized without considering pp uncertainty        


    ## Load parameters
    param = Param(optimizationHorizon,timeStep,timeLimit,optimalityGap,testFeasibility,benchmark,sameOutputAsBenchmark,rateOfChangeConstranints,transitionConstraints,powerSale,uncertaintyPV,uncertaintyPP,checkPVUncertainty,checkPPUncertainty,considerPV,considerBattery)
    param.get()

    ## Create characteristic fields
    cm = CharMap(param)
    cm.funcCreateCharacteristicMaps()

    ## Create electrolyser
    elec = Electrolyser(param)

    ## Create PV
    pv = PV(param)

    ## Create electricity price
    pp = PowerPrice(param)


    ## Create models for optimization
    param.update(pv, pp)
    optModel = Optimization_Model(param)
    optModel.funcCreateOptimizationModel(cm, elec, pv, pp)
    optModel.funcRunOptimization()

    ## Create results
    resultOpt = Result(param)
    resultOpt.funcGetResult(optModel, cm, elec, pv, pp)

    simulation = Simulation(param)
    
    if param.param['controlParameters']['uncertaintyPP'] == False:
        simulation.funcStartSimulation(param, resultOpt, cm, elec, pv, pp)

    resultOpt.funcPrintResult(optModel, cm, elec, pv, pp)
    resultOpt.funcSaveResult(optModel, cm, elec, pv, pp)
    



    # Check scenarios with price uncertainty if pv uncertainty is not considered
    if param.param['controlParameters']['checkPPUncertainty'] == True:
        meanCosts = 0
        resultTemp = Result(param)
        for i in range(0, pp.numberUncertaintySamples):
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

        meanCosts = meanCosts / pv.numberUncertaintySamples
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
            if simulation.constrViolationInputBool == True:
                numberOfConstrViolations = numberOfConstrViolations + 1
            print(simulation.constrViolationOutput)
            for t in range(0, param.param['controlParameters']['numberOfTimeSteps']+1):
                if resultTemp.dictResult['input']['powerBought'][t] >= maxPowerBought[t]:
                    maxPowerBought[t] = resultTemp.dictResult['input']['powerBought'][t]

            meanCosts = meanCosts + resultTemp.dictResult['costs']['all']
        
        maxPowerBoughtPrice = [i*j for i,j in zip(maxPowerBought, param.param['prices']['power'])]
        meanCosts = meanCosts / pv.iNumberUncertaintySamples
        print(np.sum(maxPowerBoughtPrice))
        print(meanCosts)
        print(numberOfConstrViolations)  


def test():
    ## Control parameters
    optimizationHorizon = 5*24                  # Considered time period in hours
    timeStep = 1                                # Time step of optimization in hours
    timeLimit = 100                            # Time limit for the solver to terminate in seconds
    optimalityGap = 0.01                        # Optimality gap for the solver to terminate 
    benchmark = True                            # If true benchmark scenario is calculated
    sameOutputAsBenchmark = True                # If true the optimization has to has the exact same output as the benchmark scenario
    testFeasibility = False                     # If true the optimization model will be tested for feasibility
    rateOfChangeConstranints = False            # If true rate of change constraints will be considered
    transitionConstraints = False               # If true transition constraints will be considered
    powerSale = False                           # If true sale of power from battery will be considered
    considerPV = False                          # If true pv data will be considered, otherwise it is set to zero
    considerBattery = False                     # If true battery will be considered, otherwise it is set to zero
    uncertaintyPV = False                       # If true uncertainty in pv-data will be considered as chance-constraints
    uncertaintyPP = False                       # If true uncertainty in power price data will be considered with two stage stochastic optimization
    checkPVUncertainty = False                  # If true uncertainty in pv-data will be used in simulations to validate normal scheduling which was optimized without considering pv uncertainty
    checkPPUncertainty = False                  # If true uncertainty in popwer price data will be used in simulations to validate normal scheduling which was optimized without considering pp uncertainty          


    ## Load parameters
    param = Param(optimizationHorizon,timeStep,timeLimit,optimalityGap,testFeasibility,benchmark,sameOutputAsBenchmark,rateOfChangeConstranints,transitionConstraints,powerSale,uncertaintyPV,uncertaintyPP,checkPVUncertainty,checkPPUncertainty,considerPV,considerBattery)
    
    param.funcGet()

    ## Create characteristic fields
    cm = CharMap(param)
    cm.funcCreateCharacteristicMaps()

    ## Create electrolyser
    elec = Electrolyser(param)

    ## Create PV
    pv = PV(param)

    ## Create electricity price
    pp = PowerPrice(param)

    ## Create models for optimization
    optModel = Optimization_Model(param)

    for iteration in range(0,1):
        print("Iteration:")
        print(iteration)

        elec.funcUpdate(param)
        pv.funcUpdate(param, iteration)
        pp.funcUpdate(param, iteration)
        param.funcUpdate(pv, pp)

        ## Create models for optimization
        optModel.funcCreateOptimizationModel(cm, elec, pv, pp)
        optModel.funcRunOptimization()

        ## Create results
        resultOpt = Result(param)
        resultOpt.funcGetResult(optModel, cm, elec, pv, pp)

        simulation = Simulation(param)
        
        if param.param['controlParameters']['uncertaintyPP'] == False:
            simulation.funcStartSimulation(param, resultOpt, cm, elec, pv, pp)

        resultOpt.funcPrintResult(optModel, cm, elec, pv, pp)
        resultOpt.funcSaveResult(optModel, cm, elec, pv, pp, iteration)



def main():
    #start_optimization()
    test()

    
if __name__ == "__main__":
    main()   