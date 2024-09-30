#!/usr/bin/env python3.10


##################################
########## Electrolyser ##########

class Electrolyser():
    def __init__(self, param):
        self.param = param
        self.arrEnapterModules = list(range(0,self.param.param['electrolyser']['numberOfEnapterModules']))
        self.fCalculationConstant = self.param.param['electrolyser']['constant'] 
        self.fPowerLB = self.param.param['electrolyser']['powerLowerBound']
        self.fPowerUB = self.param.param['electrolyser']['powerUpperBound']
        self.arrModes = list(range(0,4))

        # Characteristic field for electrolyser
        self.dictPowerElectrolyserMode = {}
        for i in self.arrEnapterModules:
            self.dictPowerElectrolyserMode[(i,0)] = (self.param.param['electrolyser']['powerLowerBound'] + (self.param.param['electrolyser']['powerUpperBound'] - self.param.param['electrolyser']['powerLowerBound']) / 2)
            self.dictPowerElectrolyserMode[(i,1)] = self.param.param['electrolyser']['standbyPower']
            self.dictPowerElectrolyserMode[(i,2)] = 0 


    def funcUpdate(self, param):
        self.param = param
        self.arrEnapterModules = list(range(0,self.param.param['electrolyser']['numberOfEnapterModules']))
        self.fConstant = self.param.param['electrolyser']['constant'] 
        self.fPowerLB = self.param.param['electrolyser']['powerLowerBound']
        self.fPowerUB = self.param.param['electrolyser']['powerUpperBound']

        # Characteristic field for electrolyser
        # 0 = Start-Up
        # 1 = Standby
        # 2 = Off
        # 3 = Running
        self.dictPowerElectrolyserMode = {}
        for i in self.arrEnapterModules:
            self.dictPowerElectrolyserMode[(i,0)] = self.param.param['electrolyser']['powerLowerBound'] + (self.param.param['electrolyser']['powerUpperBound'] - self.param.param['electrolyser']['powerLowerBound']) / 2
            self.dictPowerElectrolyserMode[(i,1)] = self.param.param['electrolyser']['standbyPower']
            self.dictPowerElectrolyserMode[(i,2)] = 0   

        