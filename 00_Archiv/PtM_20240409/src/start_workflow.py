#!/usr/bin/env python3.10

import start_scheduling
import matlab.engine


for i in range(0,5):
    start_scheduling.main([False,i])


    

"""
# Start Matlab and create empty dataSets for characteristic fields
path = r'C:\PROJEKTE\PTX\Max\22_Adaptation\src'
eng = matlab.engine.start_matlab()
eng.addpath(path)
eng.createEmptyDataSet(nargout=0)


bUseCalcCharMap = False

start_scheduling.main([bUseCalcCharMap,0])

for i in range(1,6):    

    eng.setup(i,nargout=0)

    bUseCalcCharMap = True
    start_scheduling.main([bUseCalcCharMap,i])
"""