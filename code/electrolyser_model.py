#!/usr/bin/env python3.10


##################################
########## Electrolyser ##########

class Electrolyser():
    def __init__(self, param):
        self.param = param
        self.enapterModules = list(range(0,self.param.param['electrolyser']['numberOfEnapterModules']))
        self.constant = self.param.param['electrolyser']['constant'] 
        self.powerLB = self.param.param['electrolyser']['powerLowerBound']
        self.powerUB = self.param.param['electrolyser']['powerUpperBound']
        self.modes = list(range(0,4))

        # Characteristic field for electrolyser
        self.powerElectrolyserMode = {}
        for i in self.enapterModules:
            self.powerElectrolyserMode[(i,0)] = (self.param.param['electrolyser']['powerLowerBound'] + (self.param.param['electrolyser']['powerUpperBound'] - self.param.param['electrolyser']['powerLowerBound']) / 2)
            self.powerElectrolyserMode[(i,1)] = self.param.param['electrolyser']['standbyPower']
            self.powerElectrolyserMode[(i,2)] = 0 


    def update(self, param):
        self.param = param
        self.enapterModules = list(range(0,self.param.param['electrolyser']['numberOfEnapterModules']))
        self.constant = self.param.param['electrolyser']['constant'] 
        self.powerLB = self.param.param['electrolyser']['powerLowerBound']
        self.powerUB = self.param.param['electrolyser']['powerUpperBound']

        # Characteristic field for electrolyser
        # 0 = Start-Up
        # 1 = Standby
        # 2 = Off
        # 3 = Running
        self.powerElectrolyserMode = {}
        for i in self.enapterModules:
            self.powerElectrolyserMode[(i,0)] = self.param.param['electrolyser']['powerLowerBound'] + (self.param.param['electrolyser']['powerUpperBound'] - self.param.param['electrolyser']['powerLowerBound']) / 2
            self.powerElectrolyserMode[(i,1)] = self.param.param['electrolyser']['standbyPower']
            self.powerElectrolyserMode[(i,2)] = 0   

        