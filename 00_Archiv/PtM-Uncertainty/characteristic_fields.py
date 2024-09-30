#!/usr/bin/env python3.10

import pandas as pd
import numpy as np


#########################################################
########## Definition of characteristic fields ##########

class CharField():

    def __init__(self, param):
        self.param = param
  
        ## Characteristic field indices
        # Absorption/Desorption + Methanolsynthesis
        self.indexMassFlowHydrogenIn = param['charField']['ABSDES']['index']['massFlowHydrogenIn']
        self.indexMassFlowBiogasIn = param['charField']['ABSDES']['index']['massFlowBiogasIn']
        self.indexMassFlowBiogasOut = param['charField']['ABSDES']['index']['massFlowBiogasOut']
        self.indexDensityBiogasOut = param['charField']['ABSDES']['index']['densityBiogasOut']
        self.indexMoleFractionMethaneBiogasOut = param['charField']['ABSDES']['index']['moleFractionMethaneBiogasOut']
        self.indexMassFlowSynthesisgasIn = param['charField']['ABSDES']['index']['massFlowSynthesisgasIn']
        self.indexMoleFractionHydrogenSynthesisgas = param['charField']['ABSDES']['index']['moleFractionH2Synthesisgas']
        self.indexMoleFractionCarbondioxideSynthesisgas = param['charField']['ABSDES']['index']['moleFractionCO2Synthesisgas']
        self.indexMassFlowMethanolWaterStorageIn = param['charField']['ABSDES']['index']['massFlowMethanolWaterStorageIn']
        self.indexDensityMethanolWaterStorageIn = param['charField']['ABSDES']['index']['densityMethanolWaterStorageIn']
        self.indexMassFlowMethanolWaterInCycle = param['charField']['ABSDES']['index']['massFlowMethanolWaterInCycle']
        self.indexMassFlowAdditionalHydrogen = param['charField']['ABSDES']['index']['massFlowAdditionalHydrogen']
        self.indexPowerPlantComponentsUnit1 = param['charField']['ABSDES']['index']['powerPlantComponentsUnit1']

        # Methanol Synthesis
        self.indexMassFlowSynthesisgasOut = param['charField']['MEOHSYN']['index']['massFlowSynthesisgasOut']
        self.indexMassFlowMethanolWaterStorageInSynthesis = param['charField']['MEOHSYN']['index']['massFlowMethanolWaterStorageIn']
        self.indexDensityMethanolWaterStorageInSynthesis = param['charField']['MEOHSYN']['index']['densityMethanolWaterStorageIn']
        self.indexPowerPlantComponentsUnit2 =  param['charField']['MEOHSYN']['index']['powerPlantComponentsUnit2']

        # Distillation
        self.indexMassFlowMethanolWaterStorageOut =  param['charField']['MEOHSYN']['index']['massFlowMethanolWaterStorageOut']
        self.indexMassFlowMethanolOut =  param['charField']['MEOHSYN']['index']['massFlowMethanolOut']
        self.indexPowerPlantComponentsUnit3 =  param['charField']['MEOHSYN']['index']['powerPlantComponentsUnit3']


    def create_characteristic_fields(self):

        ## Base data
        charField_Absorption_Desorption_Methanolsynthesis_DataFrame = pd.read_excel(r'C:\Users\ne9836\Promotion_IAI\50_Daten\01_Stationäre_Kennfelder\AbsorptionDesorption_MethanolSynthese.xlsx')
        charField_Methanolsynthesis_DataFrame = pd.read_excel(r'C:\Users\ne9836\Promotion_IAI\50_Daten\01_Stationäre_Kennfelder\MethanolSynthese.xlsx')
        charField_Distillation_DataFrame = pd.read_excel(r'C:\Users\ne9836\Promotion_IAI\50_Daten\01_Stationäre_Kennfelder\Distillation.xlsx')
        charField_Absorption_Desorption_Methanolsynthesis = charField_Absorption_Desorption_Methanolsynthesis_DataFrame.to_numpy()
        charField_Methanolsynthesis = charField_Methanolsynthesis_DataFrame.to_numpy()
        charField_Distillation = charField_Distillation_DataFrame.to_numpy()


        # Variable ranges for input variables and conversion values
        self.variablesList = []
        self.variablesList.append(list(range(0,101+1)))
        self.variablesList.append(list(range(0,9+1)))
        self.variablesList.append(list(range(0,100+1)))
        self.variablesList.append(list(range(0,101)))

        self.variablesListConversion = []

        # Hydrogen in ABSDES
        self.variablesListConversion.append([])
        self.variablesListConversion[0].append(0)
        for i in self.variablesList[0][1:]:
            self.variablesListConversion[0].append(0.1+(i-1)*0.004)

        # Biogas in ABSDES
        self.variablesListConversion.append([])
        self.variablesListConversion[1].append(0)
        for i in self.variablesList[1][1:]:
            self.variablesListConversion[1].append(4+(i-1)*0.25)

        # Synthesisgas in MEOHSYN
        self.variablesListConversion.append([])
        self.variablesListConversion[2].append(0)
        for i in self.variablesList[2][1:]:
            self.variablesListConversion[2].append(0.04+(i-1)*0.04)    

        # Methanol water in DIS
        self.variablesListConversion.append([])
        self.variablesListConversion[3].append(0)
        for i in self.variablesList[3][1:]:
           self.variablesListConversion[3].append(0.1+(i-1)*0.1)

        ## Calculation of characteristic fields of ABSDES
        self.charField_ABSDES = []
        self.lengthCharField_ABSDES = charField_Absorption_Desorption_Methanolsynthesis.shape[1]
        for i in range(0,self.lengthCharField_ABSDES+3):
            self.charField_ABSDES.append({})

        counter = 0
        for i in self.variablesList[0]: 
            for j in self.variablesList[1]:
                if (i != 0 and j != 0):
                    for k in range(0,self.lengthCharField_ABSDES):
                        self.charField_ABSDES[k][(i,j)] = charField_Absorption_Desorption_Methanolsynthesis[counter,k]
            
                    self.charField_ABSDES[self.lengthCharField_ABSDES+0][(i,j)] = (abs(charField_Absorption_Desorption_Methanolsynthesis[counter,self.indexPowerPlantComponentsUnit1[0]]) \
                                                        + abs(charField_Absorption_Desorption_Methanolsynthesis[counter,self.indexPowerPlantComponentsUnit1[1]]) \
                                                        + abs(charField_Absorption_Desorption_Methanolsynthesis[counter,self.indexPowerPlantComponentsUnit1[2]]) \
                                                        + abs(charField_Absorption_Desorption_Methanolsynthesis[counter,self.indexPowerPlantComponentsUnit1[3]])) / 1000 
                    
                    self.charField_ABSDES[self.lengthCharField_ABSDES+1][(i,j)] = self.param['biogas']['pressureIn'] / self.param['p0'] * self.variablesListConversion[1][j] / self.param['biogas']['densityIn'] * self.param['T0'] / self.param['biogas']['temperatureIn']
                    self.charField_ABSDES[self.lengthCharField_ABSDES+2][(i,j)] = self.param['biogas']['pressureOut'] / self.param['p0'] * self.charField_ABSDES[self.indexMassFlowBiogasOut][(i,j)] /  self.charField_ABSDES[self.indexDensityBiogasOut][(i,j)] * self.param['T0'] / self.param['biogas']['temperatureOut']

                
                else:
                    self.charField_ABSDES[self.indexMassFlowHydrogenIn][(i,j)] = 0
                    self.charField_ABSDES[self.indexMassFlowBiogasOut][(i,j)] = 0
                    self.charField_ABSDES[self.indexDensityBiogasOut][(i,j)] = self.param['biogas']['densityIn']
                    self.charField_ABSDES[self.indexMoleFractionMethaneBiogasOut][(i,j)] =  self.param['biogas']['minimumMoleFractionMethane']
                    self.charField_ABSDES[self.indexMassFlowSynthesisgasIn][(i,j)] = 0
                    self.charField_ABSDES[self.indexMoleFractionHydrogenSynthesisgas][(i,j)] = 0.75
                    self.charField_ABSDES[self.indexMoleFractionCarbondioxideSynthesisgas][(i,j)] = 0.25
                    self.charField_ABSDES[self.indexMassFlowMethanolWaterStorageIn][(i,j)] = 0
                    self.charField_ABSDES[self.indexDensityMethanolWaterStorageIn][(i,j)] = self.param['storageMethanolWater']['InitialDensity'] = 804.5443
                    self.charField_ABSDES[self.indexMassFlowMethanolWaterInCycle][(i,j)] = 250
                    self.charField_ABSDES[self.indexMassFlowAdditionalHydrogen][(i,j)] = 0
                    self.charField_ABSDES[self.lengthCharField_ABSDES+0][(i,j)] = 0
                    self.charField_ABSDES[self.lengthCharField_ABSDES+1][(i,j)] = 0
                    self.charField_ABSDES[self.lengthCharField_ABSDES+2][(i,j)] = 0
                if i != 0 and j != 0:
                    counter = counter + 1
                
        ## Calculation of characteristic field of MEOHSYN
        self.charField_MEOHSYN = []
        self.lengthCharField_MEOHSYN = charField_Methanolsynthesis.shape[1]
        for i in range(0,self.lengthCharField_MEOHSYN+1):
            self.charField_MEOHSYN.append({})

        for i in self.variablesList[2]:
                if (i != 0):
                    for k in range(0,self.lengthCharField_MEOHSYN):
                        self.charField_MEOHSYN[k][(i)] = charField_Methanolsynthesis[i-1,k]

                    self.charField_MEOHSYN[self.lengthCharField_MEOHSYN+0][(i)] = (abs(charField_Methanolsynthesis[i-1,self.indexPowerPlantComponentsUnit2[0]]) \
                                                        + abs(charField_Methanolsynthesis[i-1,self.indexPowerPlantComponentsUnit2[1]]) \
                                                        + abs(charField_Methanolsynthesis[i-1,self.indexPowerPlantComponentsUnit2[2]]) \
                                                        + abs(charField_Methanolsynthesis[i-1,self.indexPowerPlantComponentsUnit2[3]])) / 1000
                    

                else:
                    self.charField_MEOHSYN[self.indexMassFlowSynthesisgasOut][(i)] = 0
                    self.charField_MEOHSYN[self.indexMassFlowMethanolWaterStorageInSynthesis][(i)] = 0
                    self.charField_MEOHSYN[self.indexDensityMethanolWaterStorageInSynthesis][(i)] = self.param['storageMethanolWater']['InitialDensity']
                    self.charField_MEOHSYN[self.lengthCharField_MEOHSYN+0][(i)] = 0

        ## Calculation of characteristic field of DIS
        self.charField_DIS = []
        self.lengthCharField_DIS = charField_Distillation.shape[1]
        for i in range(0,self.lengthCharField_DIS+1):
            self.charField_DIS.append({})

        for i in self.variablesList[3]: 
                if (i != 0):
                    for k in range(0,self.lengthCharField_DIS):
                        self.charField_DIS[k][(i)] = charField_Distillation[i,k]

                    self.charField_DIS[self.lengthCharField_DIS+0][(i)] = (abs(charField_Distillation[i,self.indexPowerPlantComponentsUnit3[0]]) \
                                                + abs(charField_Distillation[i,self.indexPowerPlantComponentsUnit3[1]]) \
                                                + abs(charField_Distillation[i,self.indexPowerPlantComponentsUnit3[2]]) \
                                                + abs(charField_Distillation[i,self.indexPowerPlantComponentsUnit3[3]])) / 1000
                
                else:
                    self.charField_DIS[self.indexMassFlowMethanolOut][(i)] = 0
                    self.charField_DIS[self.indexMassFlowMethanolWaterStorageOut][(i)] = 0
                    self.charField_DIS[self.lengthCharField_DIS][(i)] = 0

        ## Set variables

        self.set_charField_input_variables()
        self.set_charField_input_variables_conversion()
        self.set_charField_output_ABSDES()
        self.set_charField_output_MEOHSYN()
        self.set_charField_output_DIS()


    def set_charField_input_variables(self):
        self.hydrogenInValues = self.variablesList[0]
        self.biogasInValues = self.variablesList[1]
        self.synthesisgasInMethanolSynthesisValues = self.variablesList[2]
        self.methanolWaterInDistillationValues = self.variablesList[3]


    def set_charField_input_variables_conversion(self):
        self.hydrogenInValuesConversion = self.variablesListConversion[0]
        self.biogasInValuesConversion = self.variablesListConversion[1]
        self.synthesisgasInMethanolSynthesisValuesConversion = self.variablesListConversion[2]
        self.methanolWaterInDistillationValuesConversion = self.variablesListConversion[3]

    def set_charField_output_ABSDES(self):
        self.massFlowHydrogenIn = self.charField_ABSDES[self.indexMassFlowHydrogenIn]  
        self.massFlowBiogasOut = self.charField_ABSDES[self.indexMassFlowBiogasOut] 
        self.densityBiogasOut = self.charField_ABSDES[self.indexDensityBiogasOut]
        self.moleFractionMethaneBiogasOut = self.charField_ABSDES[self.indexMoleFractionMethaneBiogasOut]
        self.massFlowSynthesisgasIn = self.charField_ABSDES[self.indexMassFlowSynthesisgasIn]
        self.moleFractionHydrogenSynthesisgas = self.charField_ABSDES[self.indexMoleFractionHydrogenSynthesisgas]
        self.moleFractionCarbondioxideSynthesisgas = self.charField_ABSDES[self.indexMoleFractionCarbondioxideSynthesisgas]
        self.massFlowMethanolWaterStorageIn = self.charField_ABSDES[self.indexMassFlowMethanolWaterStorageIn]
        self.densityMethanolWaterStorageIn = self.charField_ABSDES[self.indexDensityMethanolWaterStorageIn]
        self.massFlowMethanolWaterInCycle = self.charField_ABSDES[self.indexMassFlowMethanolWaterInCycle]
        self.massFlowAdditionalHydrogen = self.charField_ABSDES[self.indexMassFlowAdditionalHydrogen]

        self.powerPlantComponentsUnit1 = self.charField_ABSDES[self.lengthCharField_ABSDES+0]
        self.volumeBiogasIn = self.charField_ABSDES[self.lengthCharField_ABSDES+1]
        self.volumeBiogasOut = self.charField_ABSDES[self.lengthCharField_ABSDES+2]

    def set_charField_output_MEOHSYN(self):
        self.massFlowSynthesisgasOut = self.charField_MEOHSYN[self.indexMassFlowSynthesisgasOut]  
        self.massFlowMethanolWaterStorageInSynthesis = self.charField_MEOHSYN[self.indexMassFlowMethanolWaterStorageInSynthesis] 
        self.densityMethanolWaterStorageInSynthesis = self.charField_MEOHSYN[self.indexDensityMethanolWaterStorageInSynthesis]
        self.powerPlantComponentsUnit2 = self.charField_MEOHSYN[self.lengthCharField_MEOHSYN+0]

    def set_charField_output_DIS(self):
        self.massFlowMethanolWaterStorageOut = self.charField_DIS[self.indexMassFlowMethanolWaterStorageOut]  
        self.massFlowMethanolOut = self.charField_DIS[self.indexMassFlowMethanolOut] 
        self.powerPlantComponentsUnit3 = self.charField_DIS[self.lengthCharField_DIS+0]

