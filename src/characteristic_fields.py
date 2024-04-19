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
        # Absorption/Desorption + Methanolsynthesis
        self.iIndexMassFlowHydrogenIn = self.param.param['charMap']['ABSDES']['index']['massFlowHydrogenIn']
        self.iIndexMassFlowBiogasIn = self.param.param['charMap']['ABSDES']['index']['massFlowBiogasIn']
        self.iIndexMassFlowBiogasOut = self.param.param['charMap']['ABSDES']['index']['massFlowBiogasOut']
        self.iIndexDensityBiogasOut = self.param.param['charMap']['ABSDES']['index']['densityBiogasOut']
        self.iIndexMoleFractionMethaneBiogasOut = self.param.param['charMap']['ABSDES']['index']['moleFractionMethaneBiogasOut']
        self.iIndexMassFlowSynthesisgasIn = self.param.param['charMap']['ABSDES']['index']['massFlowSynthesisgasIn']
        self.iIndexMoleFractionHydrogenSynthesisgas = self.param.param['charMap']['ABSDES']['index']['moleFractionH2Synthesisgas']
        self.iIndexMoleFractionCarbondioxideSynthesisgas = self.param.param['charMap']['ABSDES']['index']['moleFractionCO2Synthesisgas']
        self.iIndexMassFlowMethanolWaterStorageIn = self.param.param['charMap']['ABSDES']['index']['massFlowMethanolWaterStorageIn']
        self.iIndexDensityMethanolWaterStorageIn = self.param.param['charMap']['ABSDES']['index']['densityMethanolWaterStorageIn']
        self.iIndexMassFlowMethanolWaterInCycle = self.param.param['charMap']['ABSDES']['index']['massFlowMethanolWaterInCycle']
        self.iIndexMassFlowAdditionalHydrogen = self.param.param['charMap']['ABSDES']['index']['massFlowAdditionalHydrogen']
        self.iIndexPowerPlantComponentsUnit1 = self.param.param['charMap']['ABSDES']['index']['powerPlantComponentsUnit1']

        # Methanol Synthesis
        self.iIndexMassFlowSynthesisgasOut = self.param.param['charMap']['MEOHSYN']['index']['massFlowSynthesisgasOut']
        self.iIndexMassFlowMethanolWaterStorageInSynthesis = self.param.param['charMap']['MEOHSYN']['index']['massFlowMethanolWaterStorageIn']
        self.iIndexDensityMethanolWaterStorageInSynthesis = self.param.param['charMap']['MEOHSYN']['index']['densityMethanolWaterStorageIn']
        self.iIndexPowerPlantComponentsUnit2 =  self.param.param['charMap']['MEOHSYN']['index']['powerPlantComponentsUnit2']

        # Distillation
        self.iIndexMassFlowMethanolWaterStorageOut =  self.param.param['charMap']['MEOHSYN']['index']['massFlowMethanolWaterStorageOut']
        self.iIndexMassFlowMethanolOut =  self.param.param['charMap']['MEOHSYN']['index']['massFlowMethanolOut']
        self.iIndexPowerPlantComponentsUnit3 =  self.param.param['charMap']['MEOHSYN']['index']['powerPlantComponentsUnit3']
    

    def funcUpdate(self):
        self.funcSetCharMapsOutput()


    def funcCreateCharacteristicMaps(self, pathToCharMapData):
        ## Base data
        dataFrameCharMapAbsorptionDesorptionMethanolsynthesis = pd.read_excel(pathToCharMapData + "\AbsorptionDesorption_MethanolSynthese.xlsx")
        dataFrameCharMapMethanolsynthesis = pd.read_excel(pathToCharMapData + "\MethanolSynthese.xlsx")
        dataFrameCharMapDistillation = pd.read_excel(pathToCharMapData + "\Distillation.xlsx")
        arrCharMapAbsorptionDesorptionMethanolsynthesis = dataFrameCharMapAbsorptionDesorptionMethanolsynthesis.to_numpy()
        arrCharMapMethanolsynthesis = dataFrameCharMapMethanolsynthesis.to_numpy()
        arrCharMapDistillation = dataFrameCharMapDistillation.to_numpy()

        self.arrOperationPointsABSDES = []
        self.arrOperationPointsMEOHSYN = []
        self.arrOperationPointsDIS = []

        """
        #self.arrOperationPointsABSDES.append(0)
        for i in range(0,arrCharMapAbsorptionDesorptionMethanolsynthesis.shape[0]):
            if arrCharMapAbsorptionDesorptionMethanolsynthesis[i,self.iIndexMoleFractionMethaneBiogasOut] >= self.param.param['constraints']['minMoleFractionCH4BiogasOut']:
                if arrCharMapAbsorptionDesorptionMethanolsynthesis[i,self.iIndexMoleFractionHydrogenSynthesisgas] / arrCharMapAbsorptionDesorptionMethanolsynthesis[i,self.iIndexMoleFractionCarbondioxideSynthesisgas] >= self.param.param['constraints']['minRatioH2_CO2_Synthesisgas']:
                    if arrCharMapAbsorptionDesorptionMethanolsynthesis[i,self.iIndexMoleFractionHydrogenSynthesisgas] / arrCharMapAbsorptionDesorptionMethanolsynthesis[i,self.iIndexMoleFractionCarbondioxideSynthesisgas] <= self.param.param['constraints']['maxRatioH2_CO2_Synthesisgas']:
                        self.arrOperationPointsABSDES.append(i)
        """

        for i in range(0,arrCharMapAbsorptionDesorptionMethanolsynthesis.shape[0]):
            self.arrOperationPointsABSDES.append(i)

        for i in range(0,arrCharMapMethanolsynthesis.shape[0]):
            self.arrOperationPointsMEOHSYN.append(i)

        for i in range(0,arrCharMapDistillation.shape[0]):
            self.arrOperationPointsDIS.append(i)

        self.arrNumOfOperationPoints = [len(self.arrOperationPointsABSDES),len(self.arrOperationPointsDIS),len(self.arrOperationPointsDIS)]

        # Variable ranges for input variables and conversion values
        self.arrOperationPoints = []
        self.arrOperationPoints.append(self.arrOperationPointsABSDES)
        self.arrOperationPoints.append(self.arrOperationPointsMEOHSYN)
        self.arrOperationPoints.append(self.arrOperationPointsDIS)

        self.arrOperationPointsConversionToRealInputValues = []

        # Hydrogen in ABSDES
        self.arrOperationPointsConversionToRealInputValues.append([])
        for i in range(0,arrCharMapAbsorptionDesorptionMethanolsynthesis.shape[0]):
            self.arrOperationPointsConversionToRealInputValues[0].append(arrCharMapAbsorptionDesorptionMethanolsynthesis[i,self.iIndexMassFlowHydrogenIn])

        # Biogas in ABSDES
        self.arrOperationPointsConversionToRealInputValues.append([])
        for i in range(0,arrCharMapAbsorptionDesorptionMethanolsynthesis.shape[0]):
            self.arrOperationPointsConversionToRealInputValues[1].append(arrCharMapAbsorptionDesorptionMethanolsynthesis[i,self.iIndexMassFlowBiogasIn])

        # Synthesisgas in MEOHSYN
        self.arrOperationPointsConversionToRealInputValues.append([])
        for i in range(0,arrCharMapMethanolsynthesis.shape[0]):
            self.arrOperationPointsConversionToRealInputValues[2].append(arrCharMapMethanolsynthesis[i,self.iIndexMassFlowSynthesisgasOut])   

        # Methanol water in DIS
        self.arrOperationPointsConversionToRealInputValues.append([])
        for i in range(0,arrCharMapDistillation.shape[0]):
           self.arrOperationPointsConversionToRealInputValues[3].append(arrCharMapDistillation[i,self.iIndexMassFlowSynthesisgasOut])   


        self.arrCharMap = []
        ## Calculation of characteristic fields of ABSDES
        self.arrCharMap.append([])
        self.iLengthCharMapABSDES = arrCharMapAbsorptionDesorptionMethanolsynthesis.shape[1]
        self.iIndexOverallPowerPlantUnit1 = self.iLengthCharMapABSDES + 0
        self.iIndexVolumeFlowBiogasIn = self.iLengthCharMapABSDES + 1
        self.iIndexVolumeFlowBiogasOut = self.iLengthCharMapABSDES + 2

        for i in range(0,self.iLengthCharMapABSDES+3):
            self.arrCharMap[0].append({})


        for i in self.arrOperationPoints[0]:
            for k in range(0,self.iLengthCharMapABSDES):
                self.arrCharMap[0][k][(i)] = arrCharMapAbsorptionDesorptionMethanolsynthesis[i,k]

            fPowerPlantComponentsUnit1 = 0
            for j in range(0,len(self.iIndexPowerPlantComponentsUnit1)):
                fPowerPlantComponentsUnit1 = fPowerPlantComponentsUnit1 + np.abs(arrCharMapAbsorptionDesorptionMethanolsynthesis[i,self.iIndexPowerPlantComponentsUnit1[j]]) / 1000

    
            self.arrCharMap[0][self.iIndexOverallPowerPlantUnit1][(i)] = fPowerPlantComponentsUnit1     
            self.arrCharMap[0][self.iIndexVolumeFlowBiogasIn][(i)] = self.param.param['biogas']['pressureIn'] / self.param.param['p0'] * self.arrCharMap[0][self.iIndexMassFlowBiogasIn][(i)] / self.param.param['biogas']['densityIn'] * self.param.param['T0'] / self.param.param['biogas']['temperatureIn']
            self.arrCharMap[0][self.iIndexVolumeFlowBiogasOut][(i)] = self.param.param['biogas']['pressureOut'] / self.param.param['p0'] * self.arrCharMap[0][self.iIndexMassFlowBiogasOut][(i)] /  self.arrCharMap[0][self.iIndexDensityBiogasOut][(i)] * self.param.param['T0'] / self.param.param['biogas']['temperatureOut']
              

        ## Calculation of characteristic field of MEOHSYN
        self.arrCharMap.append([])
        self.iLengthCharMapMEOHSYN = arrCharMapMethanolsynthesis.shape[1]
        self.iIndexOverallPowerPlantUnit2 = self.iLengthCharMapMEOHSYN + 0
        for i in range(0,self.iLengthCharMapMEOHSYN+1):
            self.arrCharMap[1].append({})

        for i in self.arrOperationPoints[1]:
            for k in range(0,self.iLengthCharMapMEOHSYN):
                self.arrCharMap[1][k][(i)] = arrCharMapMethanolsynthesis[i,k]

            fPowerPlantComponentsUnit2 = 0
            for j in range(0,len(self.iIndexPowerPlantComponentsUnit2)):
                fPowerPlantComponentsUnit2 = fPowerPlantComponentsUnit2 + np.abs(arrCharMapMethanolsynthesis[i,self.iIndexPowerPlantComponentsUnit2[j]]) / 1000

            
            self.arrCharMap[1][self.iIndexOverallPowerPlantUnit2][(i)] = fPowerPlantComponentsUnit2

        ## Calculation of characteristic field of DIS
        self.arrCharMap.append([])
        self.iLengthCharMapDIS = arrCharMapDistillation.shape[1]
        self.iIndexOverallPowerPlantUnit3 = self.iLengthCharMapDIS + 0
        for i in range(0,self.iLengthCharMapDIS+1):
            self.arrCharMap[2].append({})

        for i in self.arrOperationPoints[2]: 
            for k in range(0,self.iLengthCharMapDIS):
                self.arrCharMap[2][k][(i)] = arrCharMapDistillation[i,k]

            fPowerPlantComponentsUnit3 = 0
            for j in range(0,len(self.iIndexPowerPlantComponentsUnit3)):
                fPowerPlantComponentsUnit3 = fPowerPlantComponentsUnit3 + np.abs(arrCharMapDistillation[i,self.iIndexPowerPlantComponentsUnit3[j]]) / 1000


            self.arrCharMap[2][self.iLengthCharMapDIS+0][(i)] = fPowerPlantComponentsUnit3
        
        ## Set variables

        self.funcSetCharMapsInputVariables()
        self.funcSetCharMapsInputVariablesConversion()
        self.funcSetCharMapsOutput()


    def funcSetCharMapsInputVariables(self):
        self.arrOperationPointsABSDES = self.arrOperationPoints[0]
        self.arrOperationPointsMEOHSYN = self.arrOperationPoints[1]
        self.arrOperationPointsDIS = self.arrOperationPoints[2]


    def funcSetCharMapsInputVariablesConversion(self):
        self.arrHydrogenInValuesConversion = self.arrOperationPointsConversionToRealInputValues[0]
        self.arrBiogasInValuesConversion = self.arrOperationPointsConversionToRealInputValues[1]
        self.arrSynthesisgasInMethanolSynthesisValuesConversion = self.arrOperationPointsConversionToRealInputValues[2]
        self.arrMethanolWaterInDistillationValuesConversion = self.arrOperationPointsConversionToRealInputValues[3]


    def funcSetCharMapsOutput(self):
        self.massFlowHydrogenIn = self.arrCharMap[0][self.iIndexMassFlowHydrogenIn]
        self.massFlowBiogasIn = self.arrCharMap[0][self.iIndexMassFlowBiogasIn]  
        self.massFlowBiogasOut = self.arrCharMap[0][self.iIndexMassFlowBiogasOut] 
        self.densityBiogasOut = self.arrCharMap[0][self.iIndexDensityBiogasOut]
        self.moleFractionMethaneBiogasOut = self.arrCharMap[0][self.iIndexMoleFractionMethaneBiogasOut]
        self.massFlowSynthesisgasIn = self.arrCharMap[0][self.iIndexMassFlowSynthesisgasIn]
        self.moleFractionHydrogenSynthesisgas = self.arrCharMap[0][self.iIndexMoleFractionHydrogenSynthesisgas]
        self.moleFractionCarbondioxideSynthesisgas = self.arrCharMap[0][self.iIndexMoleFractionCarbondioxideSynthesisgas]
        self.massFlowMethanolWaterStorageIn = self.arrCharMap[0][self.iIndexMassFlowMethanolWaterStorageIn]
        self.densityMethanolWaterStorageIn = self.arrCharMap[0][self.iIndexDensityMethanolWaterStorageIn]
        self.massFlowMethanolWaterInCycle = self.arrCharMap[0][self.iIndexMassFlowMethanolWaterInCycle]
        self.massFlowAdditionalHydrogen = self.arrCharMap[0][self.iIndexMassFlowAdditionalHydrogen]
        self.powerPlantComponentsUnit1 = self.arrCharMap[0][self.iIndexOverallPowerPlantUnit1]
        self.volumeBiogasIn = self.arrCharMap[0][self.iIndexVolumeFlowBiogasIn]
        self.volumeBiogasOut = self.arrCharMap[0][self.iIndexVolumeFlowBiogasOut]

        self.massFlowSynthesisgasOut = self.arrCharMap[1][self.iIndexMassFlowSynthesisgasOut]  
        self.massFlowMethanolWaterStorageInSynthesis = self.arrCharMap[1][self.iIndexMassFlowMethanolWaterStorageInSynthesis] 
        self.densityMethanolWaterStorageInSynthesis = self.arrCharMap[1][self.iIndexDensityMethanolWaterStorageInSynthesis]
        self.powerPlantComponentsUnit2 = self.arrCharMap[1][self.iIndexOverallPowerPlantUnit2]

        self.massFlowMethanolWaterStorageOut = self.arrCharMap[2][self.iIndexMassFlowMethanolWaterStorageOut]  
        self.massFlowMethanolOut = self.arrCharMap[2][self.iIndexMassFlowMethanolOut] 
        self.powerPlantComponentsUnit3 = self.arrCharMap[2][self.iIndexOverallPowerPlantUnit3]

