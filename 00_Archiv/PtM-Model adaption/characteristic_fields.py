#!/usr/bin/env python3.10

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.ticker import LinearLocator


#########################################################
########## Definition of characteristic fields ##########

class CharField():

    def __init__(self, param):
        self.param = param
  
        ## Characteristic field indices
        # Absorption/Desorption + Methanolsynthesis
        self.indexMassFlowHydrogenIn = self.param.param['charField']['ABSDES']['index']['massFlowHydrogenIn']
        self.indexMassFlowBiogasIn = self.param.param['charField']['ABSDES']['index']['massFlowBiogasIn']
        self.indexMassFlowBiogasOut = self.param.param['charField']['ABSDES']['index']['massFlowBiogasOut']
        self.indexDensityBiogasOut = self.param.param['charField']['ABSDES']['index']['densityBiogasOut']
        self.indexMoleFractionMethaneBiogasOut = self.param.param['charField']['ABSDES']['index']['moleFractionMethaneBiogasOut']
        self.indexMassFlowSynthesisgasIn = self.param.param['charField']['ABSDES']['index']['massFlowSynthesisgasIn']
        self.indexMoleFractionHydrogenSynthesisgas = self.param.param['charField']['ABSDES']['index']['moleFractionH2Synthesisgas']
        self.indexMoleFractionCarbondioxideSynthesisgas = self.param.param['charField']['ABSDES']['index']['moleFractionCO2Synthesisgas']
        self.indexMassFlowMethanolWaterStorageIn = self.param.param['charField']['ABSDES']['index']['massFlowMethanolWaterStorageIn']
        self.indexDensityMethanolWaterStorageIn = self.param.param['charField']['ABSDES']['index']['densityMethanolWaterStorageIn']
        self.indexMassFlowMethanolWaterInCycle = self.param.param['charField']['ABSDES']['index']['massFlowMethanolWaterInCycle']
        self.indexMassFlowAdditionalHydrogen = self.param.param['charField']['ABSDES']['index']['massFlowAdditionalHydrogen']
        self.indexPowerPlantComponentsUnit1 = self.param.param['charField']['ABSDES']['index']['powerPlantComponentsUnit1']

        # Methanol Synthesis
        self.indexMassFlowSynthesisgasOut = self.param.param['charField']['MEOHSYN']['index']['massFlowSynthesisgasOut']
        self.indexMassFlowMethanolWaterStorageInSynthesis = self.param.param['charField']['MEOHSYN']['index']['massFlowMethanolWaterStorageIn']
        self.indexDensityMethanolWaterStorageInSynthesis = self.param.param['charField']['MEOHSYN']['index']['densityMethanolWaterStorageIn']
        self.indexPowerPlantComponentsUnit2 =  self.param.param['charField']['MEOHSYN']['index']['powerPlantComponentsUnit2']

        # Distillation
        self.indexMassFlowMethanolWaterStorageOut =  self.param.param['charField']['MEOHSYN']['index']['massFlowMethanolWaterStorageOut']
        self.indexMassFlowMethanolOut =  self.param.param['charField']['MEOHSYN']['index']['massFlowMethanolOut']
        self.indexPowerPlantComponentsUnit3 =  self.param.param['charField']['MEOHSYN']['index']['powerPlantComponentsUnit3']

    

    def update(self):
        self.set_charField_output_ABSDES()
        self.set_charField_output_MEOHSYN()
        self.set_charField_output_DIS()



    def create_characteristic_fields(self):
        ## Base data
        charField_Absorption_Desorption_Methanolsynthesis_DataFrame = pd.read_excel(r'C:\Users\ne9836\Promotion_IAI\50_Daten\01_Stationäre_Kennfelder\AbsorptionDesorption_MethanolSynthese.xlsx')
        charField_Methanolsynthesis_DataFrame = pd.read_excel(r'C:\Users\ne9836\Promotion_IAI\50_Daten\01_Stationäre_Kennfelder\MethanolSynthese.xlsx')
        charField_Distillation_DataFrame = pd.read_excel(r'C:\Users\ne9836\Promotion_IAI\50_Daten\01_Stationäre_Kennfelder\Distillation.xlsx')
        charField_Absorption_Desorption_Methanolsynthesis = charField_Absorption_Desorption_Methanolsynthesis_DataFrame.to_numpy()
        charField_Methanolsynthesis = charField_Methanolsynthesis_DataFrame.to_numpy()
        charField_Distillation = charField_Distillation_DataFrame.to_numpy()

    
        self.opList_ABSDES = [0]
        for i in range(0,charField_Absorption_Desorption_Methanolsynthesis.shape[0]):
            if charField_Absorption_Desorption_Methanolsynthesis[i,self.indexMoleFractionMethaneBiogasOut] >= self.param.param['constraints']['minMoleFractionCH4BiogasOut']:
                if charField_Absorption_Desorption_Methanolsynthesis[i,self.indexMoleFractionHydrogenSynthesisgas] / charField_Absorption_Desorption_Methanolsynthesis[i,self.indexMoleFractionCarbondioxideSynthesisgas] >= self.param.param['constraints']['minRatioH2_CO2_Synthesisgas']:
                    if charField_Absorption_Desorption_Methanolsynthesis[i,self.indexMoleFractionHydrogenSynthesisgas] / charField_Absorption_Desorption_Methanolsynthesis[i,self.indexMoleFractionCarbondioxideSynthesisgas] <= self.param.param['constraints']['maxRatioH2_CO2_Synthesisgas']:
                        self.opList_ABSDES.append(i+1)

        X = np.arange(4, 6+0.25, 0.25)
        Y = np.arange(0.1, 0.5+0.004, 0.004)
        Z = np.ndarray(shape=(len(Y),len(X)))
        #Z = np.ndarray(shape=(4,6))
        counter = 0
        for i in range(0,Z.shape[0]):
            for j in range(0,Z.shape[1]):
               Z[i,j] = charField_Absorption_Desorption_Methanolsynthesis[counter,self.indexMassFlowBiogasOut] 
               counter = counter + 1
        X, Y = np.meshgrid(X,Y)

        """
        fig, ax = plt.subplots(subplot_kw={"projection": "3d"})
        # Plot the surface.
        surf = ax.plot_surface(X, Y, Z, cmap=cm.coolwarm,
                       linewidth=0, antialiased=False)
        
        plt.show()
        """



        # Variable ranges for input variables and conversion values
        self.variablesList = []
        self.variablesList.append(self.opList_ABSDES)
        self.variablesList.append(list(range(0,100+1)))
        self.variablesList.append(list(range(0,101)))

        self.variablesListConversion = []

        # Hydrogen in ABSDES
        self.variablesListConversion.append([])
        self.variablesListConversion[0].append(0)
        for i in range(0,charField_Absorption_Desorption_Methanolsynthesis.shape[0]):
            self.variablesListConversion[0].append(charField_Absorption_Desorption_Methanolsynthesis[i,self.indexMassFlowHydrogenIn])

        # Biogas in ABSDES
        self.variablesListConversion.append([])
        self.variablesListConversion[1].append(0)
        for i in range(0,charField_Absorption_Desorption_Methanolsynthesis.shape[0]):
            self.variablesListConversion[1].append(charField_Absorption_Desorption_Methanolsynthesis[i,self.indexMassFlowBiogasIn])

        # Synthesisgas in MEOHSYN
        self.variablesListConversion.append([])
        self.variablesListConversion[2].append(0)
        for i in range(0,charField_Methanolsynthesis.shape[0]):
            self.variablesListConversion[2].append(charField_Methanolsynthesis[i,self.indexMassFlowSynthesisgasOut])   

        # Methanol water in DIS
        self.variablesListConversion.append([])
        self.variablesListConversion[3].append(0)
        for i in range(1,charField_Distillation.shape[0]):
           self.variablesListConversion[3].append(charField_Distillation[i,self.indexMassFlowSynthesisgasOut])   


        self.charField = []
        ## Calculation of characteristic fields of ABSDES
        self.charField.append([])
        self.lengthCharField_ABSDES = charField_Absorption_Desorption_Methanolsynthesis.shape[1]
        for i in range(0,self.lengthCharField_ABSDES+3):
            self.charField[0].append({})


        for i in self.variablesList[0]:
            if (i != 0):
                for k in range(0,self.lengthCharField_ABSDES):
                    self.charField[0][k][(i)] = charField_Absorption_Desorption_Methanolsynthesis[i-1,k]

        
                self.charField[0][self.lengthCharField_ABSDES+0][(i)] = (abs(charField_Absorption_Desorption_Methanolsynthesis[i-1,self.indexPowerPlantComponentsUnit1[0]]) \
                                                    + abs(charField_Absorption_Desorption_Methanolsynthesis[i-1,self.indexPowerPlantComponentsUnit1[1]]) \
                                                    + abs(charField_Absorption_Desorption_Methanolsynthesis[i-1,self.indexPowerPlantComponentsUnit1[2]]) \
                                                    + abs(charField_Absorption_Desorption_Methanolsynthesis[i-1,self.indexPowerPlantComponentsUnit1[3]])) / 1000 
                
                self.charField[0][self.lengthCharField_ABSDES+1][(i)] = self.param.param['biogas']['pressureIn'] / self.param.param['p0'] * self.charField[0][self.indexMassFlowBiogasIn][(i)] / self.param.param['biogas']['densityIn'] * self.param.param['T0'] / self.param.param['biogas']['temperatureIn']
                self.charField[0][self.lengthCharField_ABSDES+2][(i)] = self.param.param['biogas']['pressureOut'] / self.param.param['p0'] * self.charField[0][self.indexMassFlowBiogasOut][(i)] /  self.charField[0][self.indexDensityBiogasOut][(i)] * self.param.param['T0'] / self.param.param['biogas']['temperatureOut']

              
            else:
                for k in range(0,self.lengthCharField_ABSDES):
                    self.charField[0][k][(i)] = charField_Absorption_Desorption_Methanolsynthesis[i-1,k]

                self.charField[0][self.indexMassFlowHydrogenIn][(i)] = 0
                self.charField[0][self.indexMassFlowBiogasOut][(i)] = 0
                self.charField[0][self.indexDensityBiogasOut][(i)] = self.param.param['biogas']['densityIn']
                self.charField[0][self.indexMoleFractionMethaneBiogasOut][(i)] =  self.param.param['biogas']['minimumMoleFractionMethane']
                self.charField[0][self.indexMassFlowSynthesisgasIn][(i)] = 0
                self.charField[0][self.indexMoleFractionHydrogenSynthesisgas][(i)] = 0.75
                self.charField[0][self.indexMoleFractionCarbondioxideSynthesisgas][(i)] = 0.25
                self.charField[0][self.indexMassFlowMethanolWaterStorageIn][(i)] = 0
                self.charField[0][self.indexDensityMethanolWaterStorageIn][(i)] = self.param.param['storageMethanolWater']['InitialDensity'] = 804.5443
                self.charField[0][self.indexMassFlowMethanolWaterInCycle][(i)] = 250
                self.charField[0][self.indexMassFlowAdditionalHydrogen][(i)] = 0
                self.charField[0][self.lengthCharField_ABSDES+0][(i)] = 0
                self.charField[0][self.lengthCharField_ABSDES+1][(i)] = 0
                self.charField[0][self.lengthCharField_ABSDES+2][(i)] = 0
            
                
        ## Calculation of characteristic field of MEOHSYN
        self.charField.append([])
        self.lengthCharField_MEOHSYN = charField_Methanolsynthesis.shape[1]
        for i in range(0,self.lengthCharField_MEOHSYN+1):
            self.charField[1].append({})

        for i in self.variablesList[1]:
                if (i != 0):
                    for k in range(0,self.lengthCharField_MEOHSYN):
                        self.charField[1][k][(i)] = charField_Methanolsynthesis[i-1,k]

                    self.charField[1][self.lengthCharField_MEOHSYN+0][(i)] = (abs(charField_Methanolsynthesis[i-1,self.indexPowerPlantComponentsUnit2[0]]) \
                                                        + abs(charField_Methanolsynthesis[i-1,self.indexPowerPlantComponentsUnit2[1]]) \
                                                        + abs(charField_Methanolsynthesis[i-1,self.indexPowerPlantComponentsUnit2[2]]) \
                                                        + abs(charField_Methanolsynthesis[i-1,self.indexPowerPlantComponentsUnit2[3]])) / 1000
                    

                else:
                    for k in range(0,self.lengthCharField_MEOHSYN):
                        self.charField[1][k][(i)] = charField_Methanolsynthesis[i-1,k]

                    self.charField[1][self.indexMassFlowSynthesisgasOut][(i)] = 0
                    self.charField[1][self.indexMassFlowMethanolWaterStorageInSynthesis][(i)] = 0
                    self.charField[1][self.indexDensityMethanolWaterStorageInSynthesis][(i)] = self.param.param['storageMethanolWater']['InitialDensity']
                    self.charField[1][self.lengthCharField_MEOHSYN+0][(i)] = 0

        ## Calculation of characteristic field of DIS
        self.charField.append([])
        self.lengthCharField_DIS = charField_Distillation.shape[1]
        for i in range(0,self.lengthCharField_DIS+1):
            self.charField[2].append({})

        for i in self.variablesList[2]: 
                if (i != 0):
                    for k in range(0,self.lengthCharField_DIS):
                        self.charField[2][k][(i)] = charField_Distillation[i,k]

                    self.charField[2][self.lengthCharField_DIS+0][(i)] = (abs(charField_Distillation[i,self.indexPowerPlantComponentsUnit3[0]]) \
                                                + abs(charField_Distillation[i,self.indexPowerPlantComponentsUnit3[1]]) \
                                                + abs(charField_Distillation[i,self.indexPowerPlantComponentsUnit3[2]]) \
                                                + abs(charField_Distillation[i,self.indexPowerPlantComponentsUnit3[3]])) / 1000
                
                else:
                    for k in range(0,self.lengthCharField_DIS):
                        self.charField[2][k][(i)] = charField_Distillation[i,k]

                    self.charField[2][self.indexMassFlowMethanolOut][(i)] = 0
                    self.charField[2][self.indexMassFlowMethanolWaterStorageOut][(i)] = 0
                    self.charField[2][self.lengthCharField_DIS][(i)] = 0
        
        ## Set variables

        self.set_charField_input_variables()
        self.set_charField_input_variables_conversion()
        self.set_charField_output_ABSDES()
        self.set_charField_output_MEOHSYN()
        self.set_charField_output_DIS()


    def set_charField_input_variables(self):
        self.ABSDESValues = self.variablesList[0]
        self.synthesisgasInMethanolSynthesisValues = self.variablesList[1]
        self.methanolWaterInDistillationValues = self.variablesList[2]


    def set_charField_input_variables_conversion(self):
        self.hydrogenInValuesConversion = self.variablesListConversion[0]
        self.biogasInValuesConversion = self.variablesListConversion[1]
        self.synthesisgasInMethanolSynthesisValuesConversion = self.variablesListConversion[2]
        self.methanolWaterInDistillationValuesConversion = self.variablesListConversion[3]

    def set_charField_output_ABSDES(self):
        self.massFlowHydrogenIn = self.charField[0][self.indexMassFlowHydrogenIn]
        self.massFlowBiogasIn = self.charField[0][self.indexMassFlowBiogasIn]  
        self.massFlowBiogasOut = self.charField[0][self.indexMassFlowBiogasOut] 
        self.densityBiogasOut = self.charField[0][self.indexDensityBiogasOut]
        self.moleFractionMethaneBiogasOut = self.charField[0][self.indexMoleFractionMethaneBiogasOut]
        self.massFlowSynthesisgasIn = self.charField[0][self.indexMassFlowSynthesisgasIn]
        self.moleFractionHydrogenSynthesisgas = self.charField[0][self.indexMoleFractionHydrogenSynthesisgas]
        self.moleFractionCarbondioxideSynthesisgas = self.charField[0][self.indexMoleFractionCarbondioxideSynthesisgas]
        self.massFlowMethanolWaterStorageIn = self.charField[0][self.indexMassFlowMethanolWaterStorageIn]
        self.densityMethanolWaterStorageIn = self.charField[0][self.indexDensityMethanolWaterStorageIn]
        self.massFlowMethanolWaterInCycle = self.charField[0][self.indexMassFlowMethanolWaterInCycle]
        self.massFlowAdditionalHydrogen = self.charField[0][self.indexMassFlowAdditionalHydrogen]

        self.powerPlantComponentsUnit1 = self.charField[0][self.lengthCharField_ABSDES+0]
        self.volumeBiogasIn = self.charField[0][self.lengthCharField_ABSDES+1]
        self.volumeBiogasOut = self.charField[0][self.lengthCharField_ABSDES+2]

    def set_charField_output_MEOHSYN(self):
        self.massFlowSynthesisgasOut = self.charField[1][self.indexMassFlowSynthesisgasOut]  
        self.massFlowMethanolWaterStorageInSynthesis = self.charField[1][self.indexMassFlowMethanolWaterStorageInSynthesis] 
        self.densityMethanolWaterStorageInSynthesis = self.charField[1][self.indexDensityMethanolWaterStorageInSynthesis]
        self.powerPlantComponentsUnit2 = self.charField[1][self.lengthCharField_MEOHSYN+0]

    def set_charField_output_DIS(self):
        self.massFlowMethanolWaterStorageOut = self.charField[2][self.indexMassFlowMethanolWaterStorageOut]  
        self.massFlowMethanolOut = self.charField[2][self.indexMassFlowMethanolOut] 
        self.powerPlantComponentsUnit3 = self.charField[2][self.lengthCharField_DIS+0]

