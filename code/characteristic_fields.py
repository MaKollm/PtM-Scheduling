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

    

    def update(self):
        self.set_charMap_output_ABSDES()
        self.set_charMap_output_MEOHSYN()
        self.set_charMap_output_DIS()



    def create_characteristic_fields(self):
        ## Base data
        dataFrameCharMapAbsorptionDesorptionMethanolsynthesis = pd.read_excel(r'C:\PROJEKTE\PTX\Max\50_Daten\01_Stationäre_Kennfelder\AbsorptionDesorption_MethanolSynthese.xlsx')
        dataFrameCharMapMethanolsynthesis = pd.read_excel(r'C:\PROJEKTE\PTX\Max\50_Daten\01_Stationäre_Kennfelder\MethanolSynthese.xlsx')
        dataFrameCharMapDistillation = pd.read_excel(r'C:\PROJEKTE\PTX\Max\50_Daten\01_Stationäre_Kennfelder\Distillation.xlsx')
        arrCharMapAbsorptionDesorptionMethanolsynthesis = dataFrameCharMapAbsorptionDesorptionMethanolsynthesis.to_numpy()
        arrCharMapMethanolsynthesis = dataFrameCharMapMethanolsynthesis.to_numpy()
        arrCharMapDistillation = dataFrameCharMapDistillation.to_numpy()

        self.arrOperationPointsABSDES = []
        self.arrOperationPointsMEOHSYN = []
        self.arrOperationPointsDIS = []

        for i in range(0,arrCharMapAbsorptionDesorptionMethanolsynthesis.shape[0]):
            if arrCharMapAbsorptionDesorptionMethanolsynthesis[i,self.iIndexMoleFractionMethaneBiogasOut] >= self.param.param['constraints']['minMoleFractionCH4BiogasOut']:
                if arrCharMapAbsorptionDesorptionMethanolsynthesis[i,self.iIndexMoleFractionHydrogenSynthesisgas] / arrCharMapAbsorptionDesorptionMethanolsynthesis[i,self.iIndexMoleFractionCarbondioxideSynthesisgas] >= self.param.param['constraints']['minRatioH2_CO2_Synthesisgas']:
                    if arrCharMapAbsorptionDesorptionMethanolsynthesis[i,self.iIndexMoleFractionHydrogenSynthesisgas] / arrCharMapAbsorptionDesorptionMethanolsynthesis[i,self.iIndexMoleFractionCarbondioxideSynthesisgas] <= self.param.param['constraints']['maxRatioH2_CO2_Synthesisgas']:
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
        self.arrOperationPointsConversionToRealInputValues[0].append(0)
        for i in range(0,arrCharMapAbsorptionDesorptionMethanolsynthesis.shape[0]):
            self.arrOperationPointsConversionToRealInputValues[0].append(arrCharMapAbsorptionDesorptionMethanolsynthesis[i,self.iIndexMassFlowHydrogenIn])

        # Biogas in ABSDES
        self.arrOperationPointsConversionToRealInputValues.append([])
        self.arrOperationPointsConversionToRealInputValues[1].append(0)
        for i in range(0,arrCharMapAbsorptionDesorptionMethanolsynthesis.shape[0]):
            self.arrOperationPointsConversionToRealInputValues[1].append(arrCharMapAbsorptionDesorptionMethanolsynthesis[i,self.iIndexMassFlowBiogasIn])

        # Synthesisgas in MEOHSYN
        self.arrOperationPointsConversionToRealInputValues.append([])
        self.arrOperationPointsConversionToRealInputValues[2].append(0)
        for i in range(0,arrCharMapMethanolsynthesis.shape[0]):
            self.arrOperationPointsConversionToRealInputValues[2].append(arrCharMapMethanolsynthesis[i,self.iIndexMassFlowSynthesisgasOut])   

        # Methanol water in DIS
        self.arrOperationPointsConversionToRealInputValues.append([])
        self.arrOperationPointsConversionToRealInputValues[3].append(0)
        for i in range(1,arrCharMapDistillation.shape[0]):
           self.arrOperationPointsConversionToRealInputValues[3].append(arrCharMapDistillation[i,self.iIndexMassFlowSynthesisgasOut])   


        self.arrCharMap = []
        ## Calculation of characteristic fields of ABSDES
        self.arrCharMap.append([])
        self.iLengthCharMapABSDES = arrCharMapAbsorptionDesorptionMethanolsynthesis.shape[1]
        for i in range(0,self.self.iLengthCharMapABSDES+3):
            self.arrCharMap[0].append({})


        for i in self.arrOperationPoints[0]:
            for k in range(0,self.lengthCharField_ABSDES):
                self.arrCharMap[0][k][(i)] = arrCharMapAbsorptionDesorptionMethanolsynthesis[i,k]

            fPowerConsumptionComponentsUnit1 = 0
            for j in range(0,len(self.iIndexPowerPlantComponentsUnit1)):
                fPowerConsumptionComponentsUnit1 = fPowerConsumptionComponentsUnit1 + np.abs(arrCharMapAbsorptionDesorptionMethanolsynthesis[i,self.iIndexPowerPlantComponentsUnit1[j]]) / 1000

    
            self.arrCharMap[0][self.lengthCharField_ABSDES+0][(i)] = fPowerConsumptionComponentsUnit1
            
            self.arrCharMap[0][self.lengthCharField_ABSDES+1][(i)] = self.param.param['biogas']['pressureIn'] / self.param.param['p0'] * self.charField[0][self.iIndexMassFlowBiogasIn][(i)] / self.param.param['biogas']['densityIn'] * self.param.param['T0'] / self.param.param['biogas']['temperatureIn']
            self.arrCharMap[0][self.lengthCharField_ABSDES+2][(i)] = self.param.param['biogas']['pressureOut'] / self.param.param['p0'] * self.charField[0][self.iIndexMassFlowBiogasOut][(i)] /  self.charField[0][self.iIndexDensityBiogasOut][(i)] * self.param.param['T0'] / self.param.param['biogas']['temperatureOut']
            
                
        ## Calculation of characteristic field of MEOHSYN
        self.charField.append([])
        self.lengthCharField_MEOHSYN = charField_Methanolsynthesis.shape[1]
        for i in range(0,self.lengthCharField_MEOHSYN+1):
            self.charField[1].append({})

        for i in self.arrOperationPoints[1]:
                if (i != 0):
                    for k in range(0,self.lengthCharField_MEOHSYN):
                        self.charField[1][k][(i)] = charField_Methanolsynthesis[i-1,k]

                    self.charField[1][self.lengthCharField_MEOHSYN+0][(i)] = (abs(charField_Methanolsynthesis[i-1,self.iIndexPowerPlantComponentsUnit2[0]]) \
                                                        + abs(charField_Methanolsynthesis[i-1,self.iIndexPowerPlantComponentsUnit2[1]]) \
                                                        + abs(charField_Methanolsynthesis[i-1,self.iIndexPowerPlantComponentsUnit2[2]]) \
                                                        + abs(charField_Methanolsynthesis[i-1,self.iIndexPowerPlantComponentsUnit2[3]])) / 1000
                    

                else:
                    for k in range(0,self.lengthCharField_MEOHSYN):
                        self.charField[1][k][(i)] = charField_Methanolsynthesis[i-1,k]

                    self.charField[1][self.iIndexMassFlowSynthesisgasOut][(i)] = 0
                    self.charField[1][self.iIndexMassFlowMethanolWaterStorageInSynthesis][(i)] = 0
                    self.charField[1][self.iIndexDensityMethanolWaterStorageInSynthesis][(i)] = self.param.param['storageMethanolWater']['InitialDensity']
                    self.charField[1][self.lengthCharField_MEOHSYN+0][(i)] = 0

        ## Calculation of characteristic field of DIS
        self.charField.append([])
        self.lengthCharField_DIS = charField_Distillation.shape[1]
        for i in range(0,self.lengthCharField_DIS+1):
            self.charField[2].append({})

        for i in self.arrOperationPoints[2]: 
                if (i != 0):
                    for k in range(0,self.lengthCharField_DIS):
                        self.charField[2][k][(i)] = charField_Distillation[i,k]

                    self.charField[2][self.lengthCharField_DIS+0][(i)] = (abs(charField_Distillation[i,self.iIndexPowerPlantComponentsUnit3[0]]) \
                                                + abs(charField_Distillation[i,self.iIndexPowerPlantComponentsUnit3[1]]) \
                                                + abs(charField_Distillation[i,self.iIndexPowerPlantComponentsUnit3[2]]) \
                                                + abs(charField_Distillation[i,self.iIndexPowerPlantComponentsUnit3[3]])) / 1000
                
                else:
                    for k in range(0,self.lengthCharField_DIS):
                        self.charField[2][k][(i)] = charField_Distillation[i,k]

                    self.charField[2][self.iIndexMassFlowMethanolOut][(i)] = 0
                    self.charField[2][self.iIndexMassFlowMethanolWaterStorageOut][(i)] = 0
                    self.charField[2][self.lengthCharField_DIS][(i)] = 0
        
        ## Set variables

        self.set_charField_input_variables()
        self.set_charField_input_variables_conversion()
        self.set_charField_output_ABSDES()
        self.set_charField_output_MEOHSYN()
        self.set_charField_output_DIS()


    def set_charField_input_variables(self):
        self.ABSDESValues = self.arrOperationPoints[0]
        self.synthesisgasInMethanolSynthesisValues = self.arrOperationPoints[1]
        self.methanolWaterInDistillationValues = self.arrOperationPoints[2]


    def set_charField_input_variables_conversion(self):
        self.hydrogenInValuesConversion = self.arrOperationPointsConversionToRealInputValues[0]
        self.biogasInValuesConversion = self.arrOperationPointsConversionToRealInputValues[1]
        self.synthesisgasInMethanolSynthesisValuesConversion = self.arrOperationPointsConversionToRealInputValues[2]
        self.methanolWaterInDistillationValuesConversion = self.arrOperationPointsConversionToRealInputValues[3]

    def set_charField_output_ABSDES(self):
        self.massFlowHydrogenIn = self.charField[0][self.iIndexMassFlowHydrogenIn]
        self.massFlowBiogasIn = self.charField[0][self.iIndexMassFlowBiogasIn]  
        self.massFlowBiogasOut = self.charField[0][self.iIndexMassFlowBiogasOut] 
        self.densityBiogasOut = self.charField[0][self.iIndexDensityBiogasOut]
        self.moleFractionMethaneBiogasOut = self.charField[0][self.iIndexMoleFractionMethaneBiogasOut]
        self.massFlowSynthesisgasIn = self.charField[0][self.iIndexMassFlowSynthesisgasIn]
        self.moleFractionHydrogenSynthesisgas = self.charField[0][self.iIndexMoleFractionHydrogenSynthesisgas]
        self.moleFractionCarbondioxideSynthesisgas = self.charField[0][self.iIndexMoleFractionCarbondioxideSynthesisgas]
        self.massFlowMethanolWaterStorageIn = self.charField[0][self.iIndexMassFlowMethanolWaterStorageIn]
        self.densityMethanolWaterStorageIn = self.charField[0][self.iIndexDensityMethanolWaterStorageIn]
        self.massFlowMethanolWaterInCycle = self.charField[0][self.iIndexMassFlowMethanolWaterInCycle]
        self.massFlowAdditionalHydrogen = self.charField[0][self.iIndexMassFlowAdditionalHydrogen]

        self.powerPlantComponentsUnit1 = self.charField[0][self.lengthCharField_ABSDES+0]
        self.volumeBiogasIn = self.charField[0][self.lengthCharField_ABSDES+1]
        self.volumeBiogasOut = self.charField[0][self.lengthCharField_ABSDES+2]

    def set_charField_output_MEOHSYN(self):
        self.massFlowSynthesisgasOut = self.charField[1][self.iIndexMassFlowSynthesisgasOut]  
        self.massFlowMethanolWaterStorageInSynthesis = self.charField[1][self.iIndexMassFlowMethanolWaterStorageInSynthesis] 
        self.densityMethanolWaterStorageInSynthesis = self.charField[1][self.iIndexDensityMethanolWaterStorageInSynthesis]
        self.powerPlantComponentsUnit2 = self.charField[1][self.lengthCharField_MEOHSYN+0]

    def set_charField_output_DIS(self):
        self.massFlowMethanolWaterStorageOut = self.charField[2][self.iIndexMassFlowMethanolWaterStorageOut]  
        self.massFlowMethanolOut = self.charField[2][self.iIndexMassFlowMethanolOut] 
        self.powerPlantComponentsUnit3 = self.charField[2][self.lengthCharField_DIS+0]

