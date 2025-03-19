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
        # CO2-Capture + Synthesis
        self.iIndexMassFlowHydrogenIn = self.param.param['charMap']['CO2CAP_SYN']['index']['massFlowHydrogenIn']
        self.iIndexMassFlowBiogasIn = self.param.param['charMap']['CO2CAP_SYN']['index']['massFlowBiogasIn']
        self.iIndexMassFlowBiogasOut = self.param.param['charMap']['CO2CAP_SYN']['index']['massFlowBiogasOut']
        self.iIndexMoleFractionMethaneBiogasOut = self.param.param['charMap']['CO2CAP_SYN']['index']['moleFractionMethaneBiogasOut']
        self.iIndexMoleFractionCO2BiogasOut = self.param.param['charMap']['CO2CAP_SYN']['index']['moleFractionCO2BiogasOut']
        self.iIndexMassFlowSynthesisgasIn = self.param.param['charMap']['CO2CAP_SYN']['index']['massFlowSynthesisgasIn']
        self.iIndexMoleFractionH2SynthesisgasIn = self.param.param['charMap']['CO2CAP_SYN']['index']['moleFractionH2Synthesisgas']
        self.iIndexMoleFractionCO2SynthesisgasIn = self.param.param['charMap']['CO2CAP_SYN']['index']['moleFractionCO2Synthesisgas']
        self.iIndexMassFlowMethanolWaterStorageIn = self.param.param['charMap']['CO2CAP_SYN']['index']['massFlowMethanolWaterStorageIn']
        self.iIndexDensityMethanolWaterStorageIn = self.param.param['charMap']['CO2CAP_SYN']['index']['densityMethanolWaterStorageIn']
        self.iIndexMassFlowSynthesisPurge = self.param.param['charMap']['CO2CAP_SYN']['index']['massFlowSynthesisPurge']
        self.iIndexMoleFractionCO2SynthesisPurge = self.param.param['charMap']['CO2CAP_SYN']['index']['moleFractionCO2SynthesisPurge']
        self.iIndexPowerPlantComponentsUnit1 = self.param.param['charMap']['CO2CAP_SYN']['index']['powerPlantComponentsUnit1']

        # Distillation
        self.iIndexMassFlowMethanolWaterStorageOut =  self.param.param['charMap']['DIS']['index']['massFlowMethanolWaterStorageOut']
        self.iIndexMassFlowMethanolOut =  self.param.param['charMap']['DIS']['index']['massFlowMethanolOut']
        self.iIndexMoleFractionMethanolOut = self.param.param['charMap']['DIS']['index']['moleFractionMethanolOut']
        self.iIndexPowerPlantComponentsUnit2 =  self.param.param['charMap']['DIS']['index']['powerPlantComponentsUnit2']
    

    def funcUpdate(self):
        self.funcSetCharMapsOutput()


    def funcCreateCharacteristicMaps(self, pathToCharMapData):
        ## Base data
        dataFrameCharMapCO2CaptureSynthesis = pd.read_excel(pathToCharMapData + "\PtMCharMap_CO2_Capture_Synthesis.xlsx")
        dataFrameCharMapCO2CaptureSynthesis = dataFrameCharMapCO2CaptureSynthesis.iloc[2:]
        arrCharMapDefaultCO2CaptureSynthesis = dataFrameCharMapCO2CaptureSynthesis.to_numpy()
        dataFrameCharMapDistillation = pd.read_excel(pathToCharMapData + "\PtMCharMap_Distillation.xlsx")
        dataFrameCharMapDistillation = dataFrameCharMapDistillation.iloc[2:]
        arrCharMapDefaultDistillation = dataFrameCharMapDistillation.to_numpy()
        
        self.arrOperationPointsCO2CAP_SYN = []
        self.arrOperationPointsDIS = []
        self.arrOperationPointsELEC = []


        for i in range(0,arrCharMapDefaultCO2CaptureSynthesis.shape[0]):
            self.arrOperationPointsCO2CAP_SYN.append(i)

        for i in range(0,arrCharMapDefaultDistillation.shape[0]):
            self.arrOperationPointsDIS.append(i)

        for i in range(0,self.param.param['electrolyser']['numberOperationPoints']):
            self.arrOperationPointsELEC.append(i)
        


        self.arrNumOfOperationPoints = [len(self.arrOperationPointsCO2CAP_SYN),len(self.arrOperationPointsDIS), len(self.arrOperationPointsELEC)]

        # Variable ranges for input variables and conversion values
        self.arrOperationPoints = []
        self.arrOperationPoints.append(self.arrOperationPointsCO2CAP_SYN)
        self.arrOperationPoints.append(self.arrOperationPointsDIS)
        self.arrOperationPoints.append(self.arrOperationPointsELEC)

        self.arrOperationPointsConversionToRealInputValues = []

        # Biogas in CO2CAP_SYN
        self.arrOperationPointsConversionToRealInputValues.append([])
        self.arrOperationPointsConversionToRealInputValues.append([])
        for i in range(0,arrCharMapDefaultCO2CaptureSynthesis.shape[0]):
            self.arrOperationPointsConversionToRealInputValues[0].append(arrCharMapDefaultCO2CaptureSynthesis[i,self.iIndexMassFlowBiogasIn])
            self.arrOperationPointsConversionToRealInputValues[1].append(arrCharMapDefaultCO2CaptureSynthesis[i,self.iIndexMassFlowHydrogenIn])

        # Methanol water in DIS
        self.arrOperationPointsConversionToRealInputValues.append([])
        for i in range(0,arrCharMapDefaultDistillation.shape[0]):
           self.arrOperationPointsConversionToRealInputValues[2].append(arrCharMapDefaultDistillation[i,self.iIndexMassFlowMethanolWaterStorageOut])   

        # Power in Electrolyser
        self.arrOperationPointsConversionToRealInputValues.append([])
        for i in range(0,self.param.param['electrolyser']['numberOperationPoints']):
            self.arrOperationPointsConversionToRealInputValues[3].append(self.param.param['electrolyser']['conversionValues'][i])


        self.arrCharMap = []
        ## Calculation of characteristic fields of CO2CAP_SYN
        self.arrCharMap.append([])
        self.iLengthCharMapCO2CAP_SYN = arrCharMapDefaultCO2CaptureSynthesis.shape[1]

        for i in range(0,self.iLengthCharMapCO2CAP_SYN):
            self.arrCharMap[0].append({})



        for i in self.arrOperationPoints[0]:
            for k in range(0,self.iLengthCharMapCO2CAP_SYN):
                self.arrCharMap[0][k][(i)] = arrCharMapDefaultCO2CaptureSynthesis[i,k]

        ## Calculation of characteristic field of DIS
        self.arrCharMap.append([])
        self.iLengthCharMapDIS = arrCharMapDefaultDistillation.shape[1]
        
        for i in range(0,self.iLengthCharMapDIS):
            self.arrCharMap[1].append({})

        for i in self.arrOperationPoints[1]: 
            for k in range(0,self.iLengthCharMapDIS):
                self.arrCharMap[1][k][(i)] = arrCharMapDefaultDistillation[i,k]

        # Electrolyser
        self.arrCharMap.append([])
        self.iLengthCharMapELEC = 1
        
        for i in range(0,self.iLengthCharMapELEC):
            self.arrCharMap[2].append({})

        for i in self.arrOperationPoints[2]: 
            for k in range(0,self.iLengthCharMapELEC):
                self.arrCharMap[2][k][(i)] = self.arrOperationPointsConversionToRealInputValues[3][i]
        
        ## Set variables

        self.funcSetCharMapsInputVariables()
        self.funcSetCharMapsInputVariablesConversion()
        self.funcSetCharMapsOutput()


    def funcSetCharMapsInputVariables(self):
        self.arrOperationPointsCO2CAP_SYN = self.arrOperationPoints[0]
        self.arrOperationPointsDIS = self.arrOperationPoints[1]
        self.arrOperationPointsELEC = self.arrOperationPoints[2]


    def funcSetCharMapsInputVariablesConversion(self):
        self.arrBiogasInValuesConversion = self.arrOperationPointsConversionToRealInputValues[0]
        self.arrHydrogenInValuesConversion = self.arrOperationPointsConversionToRealInputValues[1]
        self.arrMethanolWaterInDistillationValuesConversion = self.arrOperationPointsConversionToRealInputValues[2]
        self.arrPowerElectrolyser = self.arrOperationPointsConversionToRealInputValues[3]


    def funcSetCharMapsOutput(self):
        self.massFlowHydrogenIn = self.arrCharMap[0][self.iIndexMassFlowHydrogenIn]
        self.massFlowBiogasIn = self.arrCharMap[0][self.iIndexMassFlowBiogasIn]  
        self.massFlowBiogasOut = self.arrCharMap[0][self.iIndexMassFlowBiogasOut] 
        self.moleFractionMethaneBiogasOut = self.arrCharMap[0][self.iIndexMoleFractionMethaneBiogasOut]
        self.moleFractionCO2BiogasOut = self.arrCharMap[0][self.iIndexMoleFractionCO2BiogasOut]
        self.massFlowSynthesisgasIn = self.arrCharMap[0][self.iIndexMassFlowSynthesisgasIn]
        self.moleFractionH2SynthesisgasIn = self.arrCharMap[0][self.iIndexMoleFractionH2SynthesisgasIn]
        self.moleFractionCO2SynthesisgasIn = self.arrCharMap[0][self.iIndexMoleFractionCO2SynthesisgasIn]
        self.massFlowMethanolWaterStorageIn = self.arrCharMap[0][self.iIndexMassFlowMethanolWaterStorageIn]
        self.densityMethanolWaterStorageIn = self.arrCharMap[0][self.iIndexDensityMethanolWaterStorageIn]
        self.massFlowSynthesisPurge = self.arrCharMap[0][self.iIndexMassFlowSynthesisPurge]
        self.moleFractionCO2SynthesisPurge = self.arrCharMap[0][self.iIndexMoleFractionCO2SynthesisPurge]
        self.powerPlantComponentsUnit1 = self.arrCharMap[0][self.iIndexPowerPlantComponentsUnit1]

        self.massFlowMethanolWaterStorageOut = self.arrCharMap[1][self.iIndexMassFlowMethanolWaterStorageOut]  
        self.massFlowMethanolOut = self.arrCharMap[1][self.iIndexMassFlowMethanolOut] 
        self.moleFractionMethanolOut = self.arrCharMap[1][self.iIndexMoleFractionMethanolOut]
        self.powerPlantComponentsUnit2 = self.arrCharMap[1][self.iIndexPowerPlantComponentsUnit2]

        self.powerElectrolyser = self.arrCharMap[2][0]


