#!/usr/bin/env python3.10


##################################
########## Electrolyser ##########

class Electrolyser():
    def __init__(self, param):
        self.enapterModules = list(range(0,param['electrolyser']['numberOfEnapterModules']))
        self.constant = param['electrolyser']['constant'] 
        self.powerLB = param['electrolyser']['powerLowerBound']
        self.powerUB = param['electrolyser']['powerUpperBound']
        self.modes = list(range(0,4))

        # Characteristic field for electrolyser
        self.powerElectrolyserMode = {}
        for i in self.enapterModules:
            self.powerElectrolyserMode[(i,0)] = param['electrolyser']['powerLowerBound'] + (param['electrolyser']['powerUpperBound'] - param['electrolyser']['powerLowerBound']) / 2
            self.powerElectrolyserMode[(i,1)] = param['electrolyser']['standbyPower']
            self.powerElectrolyserMode[(i,2)] = 0    