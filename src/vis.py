#!/usr/bin/env python3.10

import os
import pickle
import matplotlib.pyplot as plt


def load_and_visu():
        pathInitialData = r'C:\PROJEKTE\PTX\Max\21_Scheduling\gurobi\PtM_v2\input_data.pkl' 

        if os.path.isfile(pathInitialData) == True:
                with open(pathInitialData, 'rb') as f:
                        initialData = pickle.load(f)    

                visu(initialData)


def visu(result):

        plt.figure(1)
        # State of CO2-Capture
        plt.subplot(2,3,1)
        plt.plot(result['input']['currentStateCO2CAP'])
        plt.title('State of the CO2-Capture')
        plt.xlabel('time in h')
        plt.ylabel('state')

        # State of Synthesis
        plt.subplot(2,3,2)
        plt.plot(result['input']['currentStateSYN'])
        plt.title('State of the Synthesis')
        plt.xlabel('time in h')
        plt.ylabel('state')

        # State of Distillation
        plt.subplot(2,3,3)
        plt.plot(result['input']['currentStateDIS'])
        plt.title('State of the Distillation')
        plt.xlabel('time in h')
        plt.ylabel('state')

        # Operating point of CO2-Capture
        plt.subplot(2,3,4)
        plt.plot(result['input']['massFlowBiogasIn'])
        plt.title('Operating point of the CO2-Capture')
        plt.xlabel('time in h')
        plt.ylabel('operating point')

        # Operating point of Synthesis
        plt.subplot(2,3,5)
        plt.plot(result['input']['massFlowSynthesisgasIn'])
        plt.title('Operating point of the Synthesis')
        plt.xlabel('time in h')
        plt.ylabel('operating point')

        # Operating point of Distillation
        plt.subplot(2,3,6)
        plt.plot(result['input']['massFlowMethanolWaterStorage'])
        plt.title('Operating point of the Distillation')
        plt.xlabel('time in h')
        plt.ylabel('operating point')



        batteryLowerLimit = [result['param']['battery']['power'] / result['param']['battery']['power'] * 100 for _ in range(result['param']['controlParameters']['numberOfTimeSteps'])]
        batteryUpperLimit = [result['param']['battery']['minCharge'] / result['param']['battery']['power'] * 100 for _ in range(result['param']['controlParameters']['numberOfTimeSteps'])]
        batteryInitial = [result['param']['battery']['initialCharge'] / result['param']['battery']['power'] * 100 for _ in range(result['param']['controlParameters']['numberOfTimeSteps'])]
        H2StorageLowerLimit = [result['param']['storageH2']['LowerBound'] for _ in range(result['param']['controlParameters']['numberOfTimeSteps'])]
        H2StorageUpperLimit = [result['param']['storageH2']['UpperBound'] for _ in range(result['param']['controlParameters']['numberOfTimeSteps'])]
        H2StorageInitial = [result['param']['storageH2']['InitialPressure'] for _ in range(result['param']['controlParameters']['numberOfTimeSteps'])]
        MethanolWaterStorageLowerLimit = [result['param']['storageMethanolWater']['LowerBound'] for _ in range(result['param']['controlParameters']['numberOfTimeSteps'])]
        MethanolWaterStorageUpperLimit = [result['param']['storageMethanolWater']['UpperBound'] for _ in range(result['param']['controlParameters']['numberOfTimeSteps'])]
        MethanolWaterStorageInitial = [result['param']['storageMethanolWater']['InitialFilling'] for _ in range(result['param']['controlParameters']['numberOfTimeSteps'])]





        plt.figure(2)
        # Battery SOC
        plt.subplot(3,1,1)
        plt.plot(result['output']['batteryCharge'])
        plt.plot(batteryLowerLimit, 'r--')
        plt.plot(batteryUpperLimit, 'r--')
        plt.plot(batteryInitial, 'g:')
        plt.title('Battery charge')
        plt.xlabel('time in h')
        plt.ylabel('SOC in %')

        # Hydrogen storage
        plt.subplot(3,1,2)
        plt.plot(result['output']['storageH2Pressure'])
        plt.plot(H2StorageLowerLimit, 'r--')
        plt.plot(H2StorageUpperLimit, 'r--')
        plt.plot(H2StorageInitial, 'g:')
        plt.title('Hydrogen storage pressure')
        plt.xlabel('time in h')
        plt.ylabel('pressure in bar')

        # MeOH-Water storage
        plt.subplot(3,1,3)
        plt.plot(result['output']['storageMethanolWaterFilling'])
        plt.plot(MethanolWaterStorageLowerLimit, 'r--')
        plt.plot(MethanolWaterStorageUpperLimit, 'r--')
        plt.plot(MethanolWaterStorageInitial, 'g:')
        plt.title('Methanol-Water storage filling level')
        plt.xlabel('time in h')
        plt.ylabel('filling in cubic meter')


        plt.figure(3)
        # Power of electrolyser
        plt.subplot(4,1,1)
        plt.plot(result['input']['powerElectrolyser'])
        plt.title('Power electrolyser')
        plt.xlabel('time in h')
        plt.ylabel('power in kW')

        # Power of CO2-Capture
        plt.subplot(4,1,2)
        plt.plot(result['output']['powerPlantCO2CAP'])
        plt.title('Power CO2-Capture')
        plt.xlabel('time in h')
        plt.ylabel('power in kW')

        # Power of Synthesis
        plt.subplot(4,1,3)
        plt.plot(result['output']['powerPlantSYN'])
        plt.title('Power Synthesis')
        plt.xlabel('time in h')
        plt.ylabel('power in kW')

        # Power of CO2-Capture and Synthesis
        plt.subplot(4,1,4)
        plt.plot(result['output']['powerPlantDIS'])
        plt.title('Power Distillation')
        plt.xlabel('time in h')
        plt.ylabel('power in kW')



        plt.figure(4)
        # Power in battery bought
        plt.subplot(2,2,1)
        plt.plot(result['input']['actualPowerInBatteryBought'])
        plt.title('Power in battery bought')
        plt.xlabel('time in h')
        plt.ylabel('power in kW')

        # Power in battery pv
        plt.subplot(2,2,2)
        plt.plot(result['input']['actualPowerInBatteryPV'])
        plt.title('Power in battery pv')
        plt.xlabel('time in h')
        plt.ylabel('power in kW')

        # Power out battery process
        plt.subplot(2,2,3)
        plt.plot(result['input']['actualPowerOutBattery'])
        plt.title('Power out battery for process')
        plt.xlabel('time in h')
        plt.ylabel('power in kW')

        # Power out battery sold
        plt.subplot(2,2,4)
        plt.plot(result['input']['actualPowerOutBatterySold'])
        plt.title('Power out battery sold')
        plt.xlabel('time in h')
        plt.ylabel('power in kW')



        plt.figure(5)
        # PV
        plt.plot(result['input']['usageOfPV'])
        plt.plot(result['param']['pv']['powerAvailable'])
        plt.title('PV')
        plt.xlabel('time in h')
        plt.ylabel('power in kW')



        # Power
        fig, ax1 = plt.subplots()
        ax2 = ax1.twinx()
        ax1.plot(result['input']['powerBought'], 'b-')
        ax2.plot(result['param']['prices']['power'], 'g-')
        ax1.set_xlabel('time in h')
        ax1.set_ylabel('electricity bought in kWh')
        ax2.set_ylabel('electricity price in euro/kWh')




        plt.show()



#load_and_visu()