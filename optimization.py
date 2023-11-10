#!/usr/bin/env python3.10

from characteristic_fields import *
from params import *
from optimization_model import *
from electrolyser_model import *
from pv_model import *
from result import *
from adaption import *
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
    optimizationHorizon = 5*24                # Considered time period in hours
    timeStep = 1                          # Time step of optimization in hours
    timeLimit = 1000                         # Time limit for the solver to terminate in seconds
    optimalityGap = 0.01                    # Optimality gap for the solver to terminate 
    benchmark = True                    # If true benchmark scenario is calculated
    sameOutputAsBenchmark = True          # If true the optimization has to has the exact same output as the benchmark scenario
    testFeasibility = False                # If true the optimization model will be tested for feasibility
    rateOfChangeConstranints = False        # If true rate of change constraints will be considered
    transitionConstraints = False          # If true transition constraints will be considered
    powerSale = False                       # If true sale of power from battery will be considered
    considerPV = False                       # If true pv data will be considered, otherwise it is set to zero
    considerBattery = False                 # If true battery will be considered, otherwise it is set to zero
    uncertaintyPV = False                 # If true uncertainty in pv-data will be considered as chance-constraints
    uncertaintyPP = False                   # If true uncertainty in power price data will be considered with two stage stochastic optimization
    checkPVUncertainty = False               # If true uncertainty in pv-data will be used in simulations to validate normal scheduling which was optimized without considering pv uncertainty
    checkPPUncertainty = False              # If true uncertainty in popwer price data will be used in simulations to validate normal scheduling which was optimized without considering pp uncertainty        


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
        print(np.sum(maxPowerBoughtPrice))
        meanCosts = meanCosts / pv.numberUncertaintySamples
        print(meanCosts)
        print(numberOfConstrViolations)  


def test():
    ## Control parameters
    optimizationHorizon = 5*24                # Considered time period in hours
    timeStep = 1                          # Time step of optimization in hours
    timeLimit = 1000                         # Time limit for the solver to terminate in seconds
    optimalityGap = 0.01                    # Optimality gap for the solver to terminate 
    benchmark = False                    # If true benchmark scenario is calculated
    sameOutputAsBenchmark = True          # If true the optimization has to has the exact same output as the benchmark scenario
    testFeasibility = False                # If true the optimization model will be tested for feasibility
    rateOfChangeConstranints = False        # If true rate of change constraints will be considered
    transitionConstraints = False          # If true transition constraints will be considered
    powerSale = False                       # If true sale of power from battery will be considered
    considerPV = True                       # If true pv data will be considered, otherwise it is set to zero
    considerBattery = False                 # If true battery will be considered, otherwise it is set to zero
    uncertaintyPV = False                 # If true uncertainty in pv-data will be considered as chance-constraints
    uncertaintyPP = False                   # If true uncertainty in power price data will be considered with two stage stochastic optimization
    checkPVUncertainty = False               # If true uncertainty in pv-data will be used in simulations to validate normal scheduling which was optimized without considering pv uncertainty
    checkPPUncertainty = False              # If true uncertainty in popwer price data will be used in simulations to validate normal scheduling which was optimized without considering pp uncertainty        


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

    for iteration in range(0,51):
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
                
    

def adaption():
    ## Control parameters
    optimizationHorizon = 3*24                # Considered time period in hours
    timeStep = 1                            # Time step of optimization in hours
    timeLimit = 100                         # Time limit for the solver to terminate in seconds
    optimalityGap = 0.01                    # Optimality gap for the solver to terminate 
    benchmark = False                     # If true benchmark scenario is calculated
    sameOutputAsBenchmark = False           # If true the optimization has to has the exact same output as the benchmark scenario
    testFeasibility = False                 # If true the optimization model will be tested for feasibility
    rateOfChangeConstranints = False        # If true rate of change constraints will be considered
    transitionConstraints = False          # If true transition constraints will be considered
    powerSale = False                       # If true sale of power from battery will be considered
    uncertaintyPV = False                 # If true uncertainty in pv-data will be considered as chance-constraints
    uncertaintyPP = False                   # If true uncertainty in power price data will be considered with two stage stochastic optimization
    checkPVUncertainty = False               # If true uncertainty in pv-data will be used in simulations to validate normal scheduling which was optimized without considering pv uncertainty
    checkPPUncertainty = True              # If true uncertainty in popwer price data will be used in simulations to validate normal scheduling which was optimized without considering pp uncertainty        

    ## Adaption parameters
    adaptionInterval = 1                    # Interval of adaption in time steps
    optimizationInterval = 1                # Interval of optimization in time steps
    numberOfIterations = 10                 # Number of time steps/iterations considered for optimization and adaption

    ## Load parameters
    param = Param(optimizationHorizon,timeStep,timeLimit,optimalityGap,testFeasibility,benchmark,sameOutputAsBenchmark,rateOfChangeConstranints,transitionConstraints,powerSale,uncertaintyPV,uncertaintyPP,checkPVUncertainty,checkPPUncertainty)
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

    ## Create models for optimization, adaption and results
    optModel = Optimization_Model(param)
    adaption = Adaption(param)
    resultOpt = Result(param)
    simulation = Simulation(param)

    ## Create empty lists to store data
    cfList = []
    cfSimList = []
    resultOptList = []
    resultSimList = []
    paramList = []

    for iteration in range(0,numberOfIterations):
        print("Iteration:")
        print(iteration)

        elec.update(param)
        pv.update(param, iteration)
        pp.update(param, iteration)
        param.update(pv, pp)
        
        if iteration >= 0 and iteration % optimizationInterval == 0:

            ## Create optimization model
            optModel.update(param)
            optModel.create_optimization_model(cf, elec, pv, pp)
            optModel.run_optimization()

            ## Results
            resultOpt.update(param)
            resultOpt.get_results(optModel, cf, elec, pv, pp)
            simulation.start_simulation(param, resultOpt, cf, elec, pv, pp)

            resultOpt.print(optModel, cf, elec, pv, pp)
            resultOpt.save_data(optModel, cf, elec, pv, pp)


        if iteration > 0 and iteration % adaptionInterval == 0:
            ## Adaption
            for i in range(iteration-adaptionInterval,iteration):
                cfTemp = deepcopy(cfList[i])
                adaption.update(paramList[i])
                cf, resultSim, cfSim = adaption.start(iteration, adaptionInterval, optimizationInterval, i, cfTemp, elec, pv, pp, resultOptList[i])
                cf.update()

                resultSimList.append(Result(paramList[i]))
                resultSimList[i] = deepcopy(resultSim)
                cfSimList.append(CharField(paramList[i]))
                cfSimListTemp = deepcopy(cfSim)
                cfSimList.append(cfSimListTemp)


        resultOptList.append(Result(param))
        resultOptList[iteration] = deepcopy(resultOpt)
        print(resultOptList)

        paramList.append(Param())
        paramList[iteration] = deepcopy(param)

        cfList.append(CharField(param))
        cfList[iteration] = deepcopy(cf)

    #kwargs_write = {'fps':1.0, 'quantizer':'nq'}
    #imageio.mimsave('./powers.gif', [plot_for_offset(i, cfList, 100) for i in range(0,len(cfList))], fps=1)

    kwargs_write = {'fps':1.0, 'quantizer':'nq'}
    imageio.mimsave('./3D.gif', [plot_for_3D(i, cfList, 100) for i in range(0,len(cfList))], fps=1)

    print(cfList[0].variablesList[0])

def plot_for_3D(i, cfList, y_max):

    charField_Absorption_Desorption_Methanolsynthesis_DataFrame = pd.read_excel(r'C:\Users\ne9836\Promotion_IAI\50_Daten\01_Stationäre_Kennfelder\AbsorptionDesorption_MethanolSynthese.xlsx')
    charField_Absorption_Desorption_Methanolsynthesis = charField_Absorption_Desorption_Methanolsynthesis_DataFrame.to_numpy()
    for j in cfList[0].variablesList[0]:
        charField_Absorption_Desorption_Methanolsynthesis[j,cfList[0].indexMassFlowBiogasOut] = cfList[i].charField[0][cfList[0].indexMassFlowBiogasOut][(j)]

    # Data for plotting
    X = np.arange(4, 6+0.25, 0.25)
    Y = np.arange(0.1, 0.5+0.004, 0.004)
    Z = np.ndarray(shape=(len(Y),len(X)))
    #Z = np.ndarray(shape=(4,6))
    counter = 0
    for i in range(0,Z.shape[0]):
        for j in range(0,Z.shape[1]):
            Z[i,j] = charField_Absorption_Desorption_Methanolsynthesis[counter,cfList[0].indexMassFlowBiogasOut] 
            counter = counter + 1
    X, Y = np.meshgrid(X,Y)

    fig, ax = plt.subplots(subplot_kw={"projection": "3d"})
    # Plot the surface.
    surf = ax.plot_surface(X, Y, Z, cmap=cm.coolwarm,
                       linewidth=0, antialiased=False)
        

    # IMPORTANT ANIMATION CODE HERE
    # Used to keep the limits constant
    #ax.set_ylim(np.min(y), np.max(y))#y_max)

    # Used to return the plot as an image rray
    fig.canvas.draw()       # draw the canvas, cache the renderer
    image = np.frombuffer(fig.canvas.tostring_rgb(), dtype='uint8')
    image  = image.reshape(fig.canvas.get_width_height()[::-1] + (3,))

    return image

def plot_for_offset(i, cfList, y_max):
    # Data for plotting
    x = cfList[0].methanolWaterInDistillationValuesConversion
    y = []
    for key in cfList[i].powerPlantComponentsUnit2:
        y.append(cfList[i].powerPlantComponentsUnit2[key])

    fig, ax = plt.subplots(figsize=(10,5))
    ax.plot(x,y)
    ax.grid()
    ax.set_xlabel("x")
    ax.set_ylabel("y")

    # IMPORTANT ANIMATION CODE HERE
    # Used to keep the limits constant
    ax.set_ylim(np.min(y), np.max(y))#y_max)

    # Used to return the plot as an image rray
    fig.canvas.draw()       # draw the canvas, cache the renderer
    image = np.frombuffer(fig.canvas.tostring_rgb(), dtype='uint8')
    image  = image.reshape(fig.canvas.get_width_height()[::-1] + (3,))

    return image



def main():
    #start_optimization()
    #adaption()
    test()

    
if __name__ == "__main__":
    main()   