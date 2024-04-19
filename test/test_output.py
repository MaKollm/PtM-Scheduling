import sys, os
sys.path.append(os.path.join(os.path.dirname(sys.path[0]),'src'))

from start_scheduling import funcStartOptimization

def test_run_output():
    
    path = os.path.dirname(__file__)

    ###################################
    ########## TEST DATA SET ##########
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
    strPathCharMapData = path + r'\data_input'
    strPathPVData = path + r'\data_input'
    strPathPPData = path + r'\data_input'

    print(strPathPVData)

    args = [optimizationHorizon, 
                timeStep, 
                timeLimit,
                optimalityGap,
                testFeasibility,  
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
                strPathPVData,
                strPathPPData]
    
    funcStartOptimization(args)

    result = 1
    assert result == 1
