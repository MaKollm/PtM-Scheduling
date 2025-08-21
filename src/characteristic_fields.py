#!/usr/bin/env python3.10

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.ticker import LinearLocator


#########################################################
########## Definition of characteristic fields ##########

class CharMap():

    def __init__(self, param):
        self.param = param
  
        ## Characteristic field indices
        # CO2-Capture
        self.iIndexMassFlowHydrogenInCO2CAP = self.param.param['charMap']['CO2CAP']['index']['massFlowHydrogenIn']
        self.iIndexMassFlowBiogasIn = self.param.param['charMap']['CO2CAP']['index']['massFlowBiogasIn']
        self.iIndexMassFlowBiogasOut = self.param.param['charMap']['CO2CAP']['index']['massFlowBiogasOut']
        self.iIndexMoleFractionMethaneBiogasOut = self.param.param['charMap']['CO2CAP']['index']['moleFractionMethaneBiogasOut']
        self.iIndexMoleFractionCO2BiogasOut = self.param.param['charMap']['CO2CAP']['index']['moleFractionCO2BiogasOut']
        self.iIndexMassFlowSynthesisgasIn = self.param.param['charMap']['CO2CAP']['index']['massFlowSynthesisgasIn']
        self.iIndexMoleFractionH2SynthesisgasIn = self.param.param['charMap']['CO2CAP']['index']['moleFractionH2Synthesisgas']
        self.iIndexMoleFractionCO2SynthesisgasIn = self.param.param['charMap']['CO2CAP']['index']['moleFractionCO2Synthesisgas']
        self.iIndexPowerPlantComponentsUnit1 = self.param.param['charMap']['CO2CAP']['index']['powerPlantComponentsUnit1']

        # Synthesis
        self.iIndexMassFlowSynthesisgasIn = self.param.param['charMap']['SYN']['index']['massFlowSynthesisgasIn']
        self.iIndexMassFlowHydrogenInSYN = self.param.param['charMap']['SYN']['index']['massFlowHydrogenIn']
        self.iIndexMassFlowMethanolWaterStorageIn = self.param.param['charMap']['SYN']['index']['massFlowMethanolWaterStorageIn']
        self.iIndexVolFlowMethanolWaterStorageIn = self.param.param['charMap']['SYN']['index']['volFlowMethanolWaterStorageIn']
        self.iIndexDensityMethanolWaterStorageIn = self.param.param['charMap']['SYN']['index']['densityMethanolWaterStorageIn']
        self.iIndexMassFlowSynthesisPurge = self.param.param['charMap']['SYN']['index']['massFlowSynthesisPurge']
        self.iIndexMoleFractionCO2SynthesisPurge = self.param.param['charMap']['SYN']['index']['moleFractionCO2SynthesisPurge']
        self.iIndexPowerPlantComponentsUnit2 = self.param.param['charMap']['SYN']['index']['powerPlantComponentsUnit2']


        # Distillation
        self.iIndexMassFlowMethanolWaterStorageOut =  self.param.param['charMap']['DIS']['index']['massFlowMethanolWaterStorageOut']
        self.iIndexMassFlowMethanolOut =  self.param.param['charMap']['DIS']['index']['massFlowMethanolOut']
        self.iIndexVolFlowMethanolOut =  self.param.param['charMap']['DIS']['index']['volFlowMethanolOut']
        self.iIndexMoleFractionMethanolOut = self.param.param['charMap']['DIS']['index']['moleFractionMethanolOut']
        self.iIndexPowerPlantComponentsUnit3 =  self.param.param['charMap']['DIS']['index']['powerPlantComponentsUnit3']
    

    def funcUpdate(self):
        self.funcSetCharMapsOutput()


    def funcCreateCharacteristicMaps(self, pathToCharMapData):
        ## Base data
        dataFrameCharMapCO2Capture = pd.read_excel(pathToCharMapData + "\PtMCharMap_CO2_Capture.xlsx")
        dataFrameCharMapCO2Capture = dataFrameCharMapCO2Capture.iloc[2:]
        arrCharMapDefaultCO2Capture = dataFrameCharMapCO2Capture.to_numpy()
        dataFrameCharMapSynthesis = pd.read_excel(pathToCharMapData + "\PtMCharMap_Synthesis.xlsx")
        dataFrameCharMapSynthesis = dataFrameCharMapSynthesis.iloc[2:]
        arrCharMapDefaultSynthesis = dataFrameCharMapSynthesis.to_numpy()
        dataFrameCharMapDistillation = pd.read_excel(pathToCharMapData + "\PtMCharMap_Distillation.xlsx")
        dataFrameCharMapDistillation = dataFrameCharMapDistillation.iloc[2:]
        arrCharMapDefaultDistillation = dataFrameCharMapDistillation.to_numpy()
        
        self.arrOperationPointsCO2CAP = []
        self.arrOperationPointsSYN = []
        self.arrOperationPointsDIS = []
        self.arrOperationPointsELEC = []


        for i in range(0,arrCharMapDefaultCO2Capture.shape[0]):
            self.arrOperationPointsCO2CAP.append(i)

        for i in range(0,arrCharMapDefaultSynthesis.shape[0]):
            self.arrOperationPointsSYN.append(i)

        for i in range(0,arrCharMapDefaultDistillation.shape[0]):
            self.arrOperationPointsDIS.append(i)

        for i in range(0,self.param.param['electrolyser']['numberOperationPoints']):
            self.arrOperationPointsELEC.append(i)
        


        self.arrNumOfOperationPoints = [len(self.arrOperationPointsCO2CAP),len(self.arrOperationPointsSYN),len(self.arrOperationPointsDIS), len(self.arrOperationPointsELEC)]

        # Variable ranges for input variables and conversion values
        self.arrOperationPoints = []
        self.arrOperationPoints.append(self.arrOperationPointsCO2CAP)
        self.arrOperationPoints.append(self.arrOperationPointsSYN)
        self.arrOperationPoints.append(self.arrOperationPointsDIS)
        self.arrOperationPoints.append(self.arrOperationPointsELEC)

        self.arrOperationPointsConversionToRealInputValues = []

        # Biogas and Hydrogen in CO2CAP
        self.arrOperationPointsConversionToRealInputValues.append([])
        self.arrOperationPointsConversionToRealInputValues.append([])
        for i in range(0,arrCharMapDefaultCO2Capture.shape[0]):
            self.arrOperationPointsConversionToRealInputValues[0].append(arrCharMapDefaultCO2Capture[i,self.iIndexMassFlowBiogasIn])
            self.arrOperationPointsConversionToRealInputValues[1].append(arrCharMapDefaultCO2Capture[i,self.iIndexMassFlowHydrogenInCO2CAP])

        # Synthesisgas in SYN
        self.arrOperationPointsConversionToRealInputValues.append([])
        for i in range(0,arrCharMapDefaultSynthesis.shape[0]):
           self.arrOperationPointsConversionToRealInputValues[2].append(arrCharMapDefaultSynthesis[i,self.iIndexMassFlowSynthesisgasIn])  

        # Methanol water in DIS
        self.arrOperationPointsConversionToRealInputValues.append([])
        for i in range(0,arrCharMapDefaultDistillation.shape[0]):
           self.arrOperationPointsConversionToRealInputValues[3].append(arrCharMapDefaultDistillation[i,self.iIndexMassFlowMethanolWaterStorageOut])   

        # Power in Electrolyser
        self.arrOperationPointsConversionToRealInputValues.append([])
        for i in range(0,self.param.param['electrolyser']['numberOperationPoints']):
            self.arrOperationPointsConversionToRealInputValues[4].append(self.param.param['electrolyser']['conversionValues'][i])


        self.arrCharMap = []
        ## Calculation of characteristic fields of CO2CAP
        self.arrCharMap.append([])
        self.iLengthCharMapCO2CAP_SYN = arrCharMapDefaultCO2Capture.shape[1]

        for i in range(0,self.iLengthCharMapCO2CAP_SYN):
            self.arrCharMap[0].append({})

        for i in self.arrOperationPoints[0]:
            for k in range(0,self.iLengthCharMapCO2CAP_SYN):
                self.arrCharMap[0][k][(i)] = arrCharMapDefaultCO2Capture[i,k]

        ## Calculation of characteristic field of SYN
        self.arrCharMap.append([])
        self.iLengthCharMapSYN = arrCharMapDefaultSynthesis.shape[1]
        
        for i in range(0,self.iLengthCharMapSYN):
            self.arrCharMap[1].append({})

        for i in self.arrOperationPoints[1]: 
            for k in range(0,self.iLengthCharMapSYN):
                self.arrCharMap[1][k][(i)] = arrCharMapDefaultSynthesis[i,k]

        ## Calculation of characteristic field of DIS
        self.arrCharMap.append([])
        self.iLengthCharMapDIS = arrCharMapDefaultDistillation.shape[1]
        
        for i in range(0,self.iLengthCharMapDIS):
            self.arrCharMap[2].append({})

        for i in self.arrOperationPoints[2]: 
            for k in range(0,self.iLengthCharMapDIS):
                self.arrCharMap[2][k][(i)] = arrCharMapDefaultDistillation[i,k]

        # Electrolyser
        self.arrCharMap.append([])
        self.iLengthCharMapELEC = 1
        
        for i in range(0,self.iLengthCharMapELEC):
            self.arrCharMap[3].append({})

        for i in self.arrOperationPoints[3]: 
            for k in range(0,self.iLengthCharMapELEC):
                self.arrCharMap[3][k][(i)] = self.arrOperationPointsConversionToRealInputValues[4][i]
        
        ## Set variables

        self.funcSetCharMapsInputVariables()
        self.funcSetCharMapsInputVariablesConversion()
        self.funcSetCharMapsOutput()


    def funcSetCharMapsInputVariables(self):
        self.arrOperationPointsCO2CAP = self.arrOperationPoints[0]
        self.arrOperationPointsSYN = self.arrOperationPoints[1]
        self.arrOperationPointsDIS = self.arrOperationPoints[2]
        self.arrOperationPointsELEC = self.arrOperationPoints[3]


    def funcSetCharMapsInputVariablesConversion(self):
        self.arrBiogasInValuesConversion = self.arrOperationPointsConversionToRealInputValues[0]
        self.arrHydrogenInValuesConversion = self.arrOperationPointsConversionToRealInputValues[1]
        self.arrSynthesisgasInValuesConversion = self.arrOperationPointsConversionToRealInputValues[2]
        self.arrMethanolWaterInDistillationValuesConversion = self.arrOperationPointsConversionToRealInputValues[3]
        self.arrPowerElectrolyser = self.arrOperationPointsConversionToRealInputValues[4]


    def funcSetCharMapsOutput(self):
        self.massFlowHydrogenInCO2CAP = self.arrCharMap[0][self.iIndexMassFlowHydrogenInCO2CAP]
        self.massFlowBiogasIn = self.arrCharMap[0][self.iIndexMassFlowBiogasIn]  
        self.massFlowBiogasOut = self.arrCharMap[0][self.iIndexMassFlowBiogasOut] 
        self.moleFractionMethaneBiogasOut = self.arrCharMap[0][self.iIndexMoleFractionMethaneBiogasOut]
        self.moleFractionCO2BiogasOut = self.arrCharMap[0][self.iIndexMoleFractionCO2BiogasOut]
        self.massFlowSynthesisgasInCO2CAP = self.arrCharMap[0][self.iIndexMassFlowSynthesisgasIn]
        self.moleFractionH2SynthesisgasIn = self.arrCharMap[0][self.iIndexMoleFractionH2SynthesisgasIn]
        self.moleFractionCO2SynthesisgasIn = self.arrCharMap[0][self.iIndexMoleFractionCO2SynthesisgasIn]
        self.powerPlantComponentsUnit1 = self.arrCharMap[0][self.iIndexPowerPlantComponentsUnit1]

        self.massFlowHydrogenInSYN = self.arrCharMap[1][self.iIndexMassFlowHydrogenInSYN]
        self.massFlowSynthesisgasInSYN = self.arrCharMap[1][self.iIndexMassFlowSynthesisgasIn]
        self.massFlowMethanolWaterStorageIn = self.arrCharMap[1][self.iIndexMassFlowMethanolWaterStorageIn]
        self.volFlowMethanolWaterStorageIn = self.arrCharMap[1][self.iIndexVolFlowMethanolWaterStorageIn]

        self.densityMethanolWaterStorageIn = self.arrCharMap[1][self.iIndexDensityMethanolWaterStorageIn]
        self.massFlowSynthesisPurge = self.arrCharMap[1][self.iIndexMassFlowSynthesisPurge]
        self.moleFractionCO2SynthesisPurge = self.arrCharMap[1][self.iIndexMoleFractionCO2SynthesisPurge]
        self.powerPlantComponentsUnit2 = self.arrCharMap[1][self.iIndexPowerPlantComponentsUnit2]

        self.massFlowMethanolWaterStorageOut = self.arrCharMap[2][self.iIndexMassFlowMethanolWaterStorageOut]  
        self.massFlowMethanolOut = self.arrCharMap[2][self.iIndexMassFlowMethanolOut] 
        self.volFlowMethanolOut = self.arrCharMap[2][self.iIndexVolFlowMethanolOut] 
        self.moleFractionMethanolOut = self.arrCharMap[2][self.iIndexMoleFractionMethanolOut]
        self.powerPlantComponentsUnit3 = self.arrCharMap[2][self.iIndexPowerPlantComponentsUnit3]

        self.powerElectrolyser = self.arrCharMap[3][0]


