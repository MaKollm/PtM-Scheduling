#!/usr/bin/env python3.10

from characteristic_fields import *
from params import *
from optimization_model import *
from electrolyser_model import *
from pv_model import *
from calculate_results import *

import gurobipy as gp
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from gurobipy import GRB
from gurobipy import *
from scipy.io import savemat



##################################
########## Optimization ##########

def start_optimization():
    optimizationHorizon = 48
    benchmark = False
    timeLimit = 10000

    testFeasibility = False

    rateOfChangeConstranints = False
    transitionConstraints = False
    powerSale = False
    uncertainty = True
    sameOutputAsBenchmark = False

    ## Load parameters
    param = get_params(optimizationHorizon,benchmark,timeLimit,testFeasibility,rateOfChangeConstranints,transitionConstraints,powerSale,uncertainty,sameOutputAsBenchmark)

    ## Create characteristic fields
    cf = CharField(param)
    cf.create_characteristic_fields()

    ## Create electrolyser
    elec = Electrolyser(param)

    ## Create PV
    pv = PV(param)
    pv.create_PV()
    pv.model_uncertainty()

    ## Create optimization model
    OptModel = Optimization_Model(param,cf,elec,pv)

    OptModel.create_optimization_model()
    OptModel.run_optimization()

    ## Results
    result = Results(param,OptModel,cf,elec,pv)
    result.input()
    result.output()
    


def test():
    optimizationHorizon = 48
    benchmark = False
    timeLimit = 1000

    testFeasibility = False

    rateOfChangeConstranints = False
    transitionConstraints = False
    powerSale = False
    uncertainty = False
    sameOutputAsBenchmark = False

    ## Load parameters
    param = get_params(optimizationHorizon,benchmark,timeLimit,testFeasibility,rateOfChangeConstranints,transitionConstraints,powerSale,uncertainty,sameOutputAsBenchmark)

    pv = PV(param)
    pv.create_PV()
    pv.model_uncertainty()
    pv.get_real_data()


def main():
    start_optimization()
    #test()

    
if __name__ == "__main__":
    main()   