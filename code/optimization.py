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
    cf = CharField(param)
    cf.create_characteristic_fields()

    ## Create electrolyser
    elec = Electrolyser(param)

    ## Create PV
    pv = PV(param)

    ## Create electricity price
    pp = PowerPrice(param)


    ## Create models for optimization
    param.update(pv, pp)
    optModel = Optimization_Model(param)
    optModel.create_optimization_model(cf, elec, pv, pp)
    optModel.run_optimization()

    ## Create results
    resultOpt = Result(param)
    resultOpt.get_results(optModel, cf, elec, pv, pp)

    simulation = Simulation(param)
    
    if param.param['controlParameters']['uncertaintyPP'] == False:
        simulation.start_simulation(param, resultOpt, cf, elec, pv, pp)

    resultOpt.print(optModel, cf, elec, pv, pp)
    resultOpt.save_data(optModel, cf, elec, pv, pp)
    



    # Check scenarios with price uncertainty if pv uncertainty is not considered
    if param.param['controlParameters']['checkPPUncertainty'] == True:
        meanCosts = 0
        resultTemp = Result(param)
        for i in range(0, pp.numberUncertaintySamples):
            print(i)
            pp.powerPriceHourly = pp.powerPriceSamples[i]
            param.update(pv,pp)
            resultOpt.result["input"]["powerBought"] = resultOpt.result["input"]["powerBoughtRaw"][i]
            resultOpt.result["input"]["powerInBatteryBought"] = resultOpt.result["input"]["powerInBatteryBoughtRaw"][i]
            resultOpt.result["input"]["powerOutBattery"] = resultOpt.result["input"]["powerOutBatteryRaw"][i]
            resultOpt.result["input"]["powerOutBatterySold"] = resultOpt.result["input"]["powerOutBatterySoldRaw"][i]
            resultTemp = deepcopy(resultOpt)
            simulation.start_simulation(param, resultTemp, cf, elec, pv, pp)
            print("costs: " + str(resultTemp.result['costs']['all']))
            print(simulation.constrViolationOutput)
            meanCosts = meanCosts + resultTemp.result['costs']['all']

        meanCosts = meanCosts / pv.numberUncertaintySamples
        print(meanCosts)

    # Check scenarios with pv uncertainty if price uncertainty is not considered
    elif param.param['controlParameters']['checkPVUncertainty'] == True:
        maxPowerBought = [0] * (param.param['controlParameters']['numberOfTimeSteps']+1)
        numberOfConstrViolations = 0
        meanCosts = 0
        resultTemp = Result(param)
        for i in range(0, pv.numberUncertaintySamples):
            pv.powerAvailable = pv.pvSamples[i]
            param.update(pv,pp)
            resultTemp = deepcopy(resultOpt)
            simulation.start_simulation(param, resultTemp, cf, elec, pv, pp)
            if simulation.constrViolationInputBool == True:
                numberOfConstrViolations = numberOfConstrViolations + 1
            print(simulation.constrViolationOutput)
            for t in range(0, param.param['controlParameters']['numberOfTimeSteps']+1):
                if resultTemp.result['input']['powerBought'][t] >= maxPowerBought[t]:
                    maxPowerBought[t] = resultTemp.result['input']['powerBought'][t]

            meanCosts = meanCosts + resultTemp.result['costs']['all']
        
        maxPowerBoughtPrice = [i*j for i,j in zip(maxPowerBought, param.param['prices']['power'])]
        meanCosts = meanCosts / pv.numberUncertaintySamples
        print(np.sum(maxPowerBoughtPrice))
        print(meanCosts)
        print(numberOfConstrViolations)  


def test():
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
    cf = CharField(param)
    cf.create_characteristic_fields()

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

        elec.update(param)
        pv.update(param, iteration)
        pp.update(param, iteration)
        param.update(pv, pp)

        ## Create models for optimization
        optModel.create_optimization_model(cf, elec, pv, pp)
        optModel.run_optimization()

        ## Create results
        resultOpt = Result(param)
        resultOpt.get_results(optModel, cf, elec, pv, pp)

        simulation = Simulation(param)
        
        if param.param['controlParameters']['uncertaintyPP'] == False:
            simulation.start_simulation(param, resultOpt, cf, elec, pv, pp)

        resultOpt.print(optModel, cf, elec, pv, pp)
        resultOpt.save_data(optModel, cf, elec, pv, pp, iteration)



def main():
    #start_optimization()
    test()

    
if __name__ == "__main__":
    main()   