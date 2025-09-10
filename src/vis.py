#!/usr/bin/env python3.10

import os
import pickle
import matplotlib.pyplot as plt
import imageio



def load_and_visu():
        pathInitialData = r'C:\PROJEKTE\PTX\Max\21_Scheduling\gurobi\PtM\input_data.pkl' 

        if os.path.isfile(pathInitialData) == True:
                with open(pathInitialData, 'rb') as f:
                        initialData = pickle.load(f)    

                visu(initialData)

def load_and_createGif():
        pathInitialData = r'C:\PROJEKTE\PTX\Max\21_Scheduling\gurobi\PtM' 
        filename = 'input_data_'
        matching_files = [f for f in os.listdir(pathInitialData) if filename in f]
        file_contents = []

        for file in matching_files:
                with open(os.path.join(pathInitialData, file), 'rb') as f:
                        file_contents.append(pickle.load(f))
 

        createGif(results=file_contents)
        pass


def visu(result):

        plt.figure(1)
        # State of CO2-Capture
        plt.subplot(2,3,1)
        plt.plot(result['input']['currentStateCO2CAP'])
        plt.title('State of the CO2-Capture')
        plt.xlabel('time in h')
        plt.ylabel('state')
        plt.grid(True)

        # State of Synthesis
        plt.subplot(2,3,2)
        plt.plot(result['input']['currentStateSYN'])
        plt.title('State of the Synthesis')
        plt.xlabel('time in h')
        plt.ylabel('state')
        plt.grid(True)

        # State of Distillation
        plt.subplot(2,3,3)
        plt.plot(result['input']['currentStateDIS'])
        plt.title('State of the Distillation')
        plt.xlabel('time in h')
        plt.ylabel('state')
        plt.grid(True)

        # Operating point of CO2-Capture
        plt.subplot(2,3,4)
        plt.plot(result['input']['operationPoint_CO2CAP_List'])
        plt.title('Operating point of the CO2-Capture')
        plt.xlabel('time in h')
        plt.ylabel('operating point')
        plt.grid(True)

        # Operating point of Synthesis
        plt.subplot(2,3,5)
        plt.plot(result['input']['operationPoint_SYN_List'])
        plt.title('Operating point of the Synthesis')
        plt.xlabel('time in h')
        plt.ylabel('operating point')
        plt.grid(True)

        # Operating point of Distillation
        plt.subplot(2,3,6)
        plt.plot(result['input']['operationPoint_DIS_List'])
        plt.title('Operating point of the Distillation')
        plt.xlabel('time in h')
        plt.ylabel('operating point')
        plt.grid(True)



        batteryLowerLimit = [result['param']['battery']['power'] / result['param']['battery']['power'] * 100 for _ in range(result['param']['controlParameters']['numberOfTimeSteps'])]
        batteryUpperLimit = [result['param']['battery']['minCharge'] / result['param']['battery']['power'] * 100 for _ in range(result['param']['controlParameters']['numberOfTimeSteps'])]
        batteryInitial = [result['param']['battery']['initialCharge'] / result['param']['battery']['power'] * 100 for _ in range(result['param']['controlParameters']['numberOfTimeSteps'])]
        H2StorageLowerLimit = [result['param']['storageH2']['LowerBound'] for _ in range(result['param']['controlParameters']['numberOfTimeSteps'])]
        H2StorageUpperLimit = [result['param']['storageH2']['UpperBound'] for _ in range(result['param']['controlParameters']['numberOfTimeSteps'])]
        #H2StorageInitial = [result['param']['storageH2']['InitialPressure'] for _ in range(result['param']['controlParameters']['numberOfTimeSteps'])]
        H2StorageInitial = [result['param']['constraints']['hydrogenStorageEqualValue'] for _ in range(result['param']['controlParameters']['numberOfTimeSteps'])]
        MethanolWaterStorageLowerLimit = [result['param']['storageMethanolWater']['LowerBound'] for _ in range(result['param']['controlParameters']['numberOfTimeSteps'])]
        MethanolWaterStorageUpperLimit = [result['param']['storageMethanolWater']['UpperBound'] for _ in range(result['param']['controlParameters']['numberOfTimeSteps'])]
        #MethanolWaterStorageInitial = [result['param']['storageMethanolWater']['InitialFilling'] for _ in range(result['param']['controlParameters']['numberOfTimeSteps'])]
        MethanolWaterStorageInitial = [result['param']['constraints']['methanolWaterStorageEqualValue'] for _ in range(result['param']['controlParameters']['numberOfTimeSteps'])]


        plt.figure(2)
        # Battery SOC
        plt.subplot(3,1,1)
        plt.plot(result['output_Scheduling']['batteryCharge'])
        plt.plot(batteryLowerLimit, 'r--')
        plt.plot(batteryUpperLimit, 'r--')
        plt.plot(batteryInitial, 'g:')
        plt.title('Battery charge')
        plt.xlabel('time in h')
        plt.ylabel('SOC in %')
        plt.grid(True)

        # Hydrogen storage
        plt.subplot(3,1,2)
        plt.plot(result['output_Scheduling']['storageH2Pressure'])
        plt.plot(H2StorageLowerLimit, 'r--')
        plt.plot(H2StorageUpperLimit, 'r--')
        plt.plot(H2StorageInitial, 'g:')
        plt.title('Hydrogen storage pressure')
        plt.xlabel('time in h')
        plt.ylabel('pressure in bar')
        plt.grid(True)

        # MeOH-Water storage
        plt.subplot(3,1,3)
        plt.plot(result['output_Scheduling']['storageMethanolWaterFilling'])
        plt.plot(MethanolWaterStorageLowerLimit, 'r--')
        plt.plot(MethanolWaterStorageUpperLimit, 'r--')
        plt.plot(MethanolWaterStorageInitial, 'g:')
        plt.title('Methanol-Water storage filling level')
        plt.xlabel('time in h')
        plt.ylabel('filling in cubic meter')
        plt.grid(True)


        plt.figure(3)
        # Power of electrolyser
        plt.subplot(4,1,1)
        plt.plot(result['input']['powerElectrolyser'])
        plt.title('Power electrolyser')
        plt.xlabel('time in h')
        plt.ylabel('power in kW')
        plt.grid(True)

        # Power of CO2-Capture
        plt.subplot(4,1,2)
        plt.plot(result['output_Scheduling']['powerPlantCO2CAP'])
        plt.title('Power CO2-Capture')
        plt.xlabel('time in h')
        plt.ylabel('power in kW')
        plt.grid(True)

        # Power of Synthesis
        plt.subplot(4,1,3)
        plt.plot(result['output_Scheduling']['powerPlantSYN'])
        plt.title('Power Synthesis')
        plt.xlabel('time in h')
        plt.ylabel('power in kW')
        plt.grid(True)

        # Power of CO2-Capture and Synthesis
        plt.subplot(4,1,4)
        plt.plot(result['output_Scheduling']['powerPlantDIS'])
        plt.title('Power Distillation')
        plt.xlabel('time in h')
        plt.ylabel('power in kW')
        plt.grid(True)



        plt.figure(4)
        # Power in battery from grid
        plt.subplot(2,2,1)
        plt.plot(result['input']['actualPowerInBatteryGrid'])
        plt.title('Power in battery from grid')
        plt.xlabel('time in h')
        plt.ylabel('power in kW')
        plt.grid(True)

        # Power in battery pv
        plt.subplot(2,2,2)
        plt.plot(result['input']['actualPowerInBatteryPV'])
        plt.title('Power in battery pv')
        plt.xlabel('time in h')
        plt.ylabel('power in kW')
        plt.grid(True)

        # Power out battery process
        plt.subplot(2,2,3)
        plt.plot(result['input']['actualPowerOutBattery'])
        plt.title('Power out battery for process')
        plt.xlabel('time in h')
        plt.ylabel('power in kW')
        plt.grid(True)

        # Power out battery sold
        plt.subplot(2,2,4)
        plt.plot(result['input']['actualPowerOutBatterySold'])
        plt.title('Power out battery sold')
        plt.xlabel('time in h')
        plt.ylabel('power in kW')
        plt.grid(True)



        plt.figure(5)
        # PV
        plt.plot(result['input']['usageOfPV'])
        plt.plot(result['param']['pv']['powerAvailable'])
        plt.title('PV')
        plt.xlabel('time in h')
        plt.ylabel('power in kW')
        plt.grid(True)

        plt.figure(6)
        # PV
        plt.plot(result['input']['usageOfWind'])
        plt.plot(result['param']['wt']['powerAvailable'])
        plt.title('Wind')
        plt.xlabel('time in h')
        plt.ylabel('power in kW')
        plt.grid(True)



        # Power
        fig, ax1 = plt.subplots()
        ax2 = ax1.twinx()
        ax1.plot(result['input']['powerGrid'], 'b-')
        ax2.plot(result['param']['prices']['power'], 'g-')
        ax1.set_xlabel('time in h')
        ax1.set_ylabel('electricity from grid in kWh')
        ax2.set_ylabel('electricity price in euro/kWh')
        ax1.grid(True)
        

        plt.figure(8)
        # Dynamic variables CO2 Capture
        plt.subplot(2,1,1)
        plt.plot(result['output_Scheduling']['massFlowBiogasOut'])
        plt.plot(result['output_Scheduling']['massFlowSynthesisgasOut'])
        plt.title('Mass flows CO2-Capture')
        plt.xlabel('time in h')
        plt.ylabel('mass flow in kg/h')
        plt.legend(["biogas out", "synthesis gas out"])
        plt.grid(True)

        plt.subplot(2,1,2)
        plt.plot(result['output_Scheduling']['moleFractionCO2BiogasOut'])
        plt.plot(result['output_Scheduling']['moleFractionH2SynthesisgasIn'])
        plt.plot(result['output_Scheduling']['moleFractionCO2SynthesisgasIn'])
        plt.title('Mole fractions CO2-Capture')
        plt.xlabel('time in h')
        plt.ylabel('fraction [-]')
        plt.legend(["mole fraction CO2 biogas out", "mole fraction H2 synthesis gas", "mole fraction CO2 synthesis gas"])
        plt.grid(True)


        plt.show()


        


def createGif(results):

        H2Pressure_Scheduling = []
        H2Pressure_Sim = []
        volFlowMethanolOut_Scheduling = []
        volFlowMethanolOut_Sim = []
        volFlowMethanolWater_Scheduling = []
        volFlowMethanolWater_Sim = []

        for result in results:
                H2Pressure_Scheduling.append([result['param']['storageH2']['InitialPressure']] + result['output_Scheduling']['storageH2Pressure'])
                H2Pressure_Sim.append([result['param']['storageH2']['InitialPressure']] + result['output_Sim']['storageH2Pressure'])

                volFlowMethanolOut_Scheduling.append(result['output_Scheduling']['volFlowMethanolOut'])
                volFlowMethanolOut_Sim.append(result['output_Sim']['volFlowMethanolOut'])

                volFlowMethanolWater_Scheduling.append(result['output_Scheduling']['volFlowMethanolWaterStorageIn'])
                volFlowMethanolWater_Sim.append(result['output_Sim']['volFlowMethanolWaterStorageIn'])
      


        #if not os.path.exists(r'C:\PROJEKTE\PTX\Max\21_Scheduling\01_Scheduling_Results\01_data\results_v3\frames'):
        #        os.makedirs(r'C:\PROJEKTE\PTX\Max\21_Scheduling\01_Scheduling_Results\01_data\results_v3\frames')
        frames = []

        for idx, result in enumerate(results):
                ########## H2 pressure ##########
                x_full = list(range(0,result['param']['controlParameters']['numTimeStepsToSimulate']*idx + result['param']['controlParameters']['numberOfTimeSteps'] + 1))
                fig, ax = plt.subplots()
                ax.plot(x_full,[result['param']['storageH2']['LowerBound'] for _ in range(len(x_full))], 'r--')
                ax.plot(x_full,[result['param']['storageH2']['UpperBound'] for _ in range(len(x_full))], 'r--')
                ax.plot(x_full,[result['param']['constraints']['hydrogenStorageEqualValue'] for _ in range(len(x_full))], 'g:')   
                x_sched = list(range(result['param']['controlParameters']['numTimeStepsToSimulate']*idx,result['param']['controlParameters']['numTimeStepsToSimulate']*idx + result['param']['controlParameters']['numberOfTimeSteps'] + 1))
                plt.plot(x_sched,H2Pressure_Scheduling[idx], label='Prediction H2 pressure')
                       
                for i in range(0,idx):
                        x_sim = list(range(result['param']['controlParameters']['numTimeStepsToSimulate']*i,result['param']['controlParameters']['numTimeStepsToSimulate']*(i+1) + 1))
                        x_sched = list(range(result['param']['controlParameters']['numTimeStepsToSimulate']*i,result['param']['controlParameters']['numTimeStepsToSimulate']*i + result['param']['controlParameters']['numberOfTimeSteps'] + 1))

                        if i == 0:
                                ax.plot(x_sim,H2Pressure_Sim[i], 'k-', label='Measured H2 pressure')
                                ax.plot(x_sched,H2Pressure_Scheduling[i], 'b--', alpha=0.5, label='Old prediction H2 pressure')
                        else:
                                ax.plot(x_sim,H2Pressure_Sim[i], 'k-', label='_nolegend_')
                                ax.plot(x_sched,H2Pressure_Scheduling[i], 'b--', alpha=0.5, label='_nolegend_')
                
                plt.axvline(result['param']['controlParameters']['numTimeStepsToSimulate']*idx, color='k', linestyle='--')

                plt.legend(loc='lower left')
                plt.savefig(f"frame_{(idx*2)}.png")
                plt.show()

                x_full = list(range(0,result['param']['controlParameters']['numTimeStepsToSimulate']*idx + result['param']['controlParameters']['numberOfTimeSteps']))
                fig, ax = plt.subplots()
                ax.plot(x_full,[result['param']['storageH2']['LowerBound'] for _ in range(len(x_full))], 'r--')
                ax.plot(x_full,[result['param']['storageH2']['UpperBound'] for _ in range(len(x_full))], 'r--')
                ax.plot(x_full,[result['param']['constraints']['hydrogenStorageEqualValue'] for _ in range(len(x_full))], 'g:')          
                for i in range(0,idx+1):
                        x_sim = list(range(result['param']['controlParameters']['numTimeStepsToSimulate']*i,result['param']['controlParameters']['numTimeStepsToSimulate']*(i+1) + 1))
                        if i == 0:
                                ax.plot(x_sim,H2Pressure_Sim[i], 'k-', label='Measured H2 pressure')
                        else:
                                ax.plot(x_sim,H2Pressure_Sim[i], 'k-', label='_nolegend_')

                x_sched = list(range(result['param']['controlParameters']['numTimeStepsToSimulate']*idx,result['param']['controlParameters']['numTimeStepsToSimulate']*idx + result['param']['controlParameters']['numberOfTimeSteps'] + 1))
                ax.plot(x_sched,H2Pressure_Scheduling[idx], 'b--', alpha=0.5, label='Old prediction H2 pressure')
                plt.axvline(result['param']['controlParameters']['numTimeStepsToSimulate']*(idx+1), color='k', linestyle='--')
                plt.legend(loc='lower left')
                plt.savefig(f"frame_{(idx*2)+1}.png")
                plt.show()


                ########## Methanol water produced ##########
                x_full = list(range(0,result['param']['controlParameters']['numTimeStepsToSimulate']*idx + result['param']['controlParameters']['numberOfTimeSteps'] + 1))
                fig, ax = plt.subplots()         

                x_sched = list(range(result['param']['controlParameters']['numTimeStepsToSimulate']*idx,result['param']['controlParameters']['numTimeStepsToSimulate']*idx + result['param']['controlParameters']['numberOfTimeSteps'] + 1))
                x_sched_double = [x_sched[0]] + [x for x in x_sched[1:-1] for _ in (0, 1)] + [x_sched[-1]]
                volFlowMethanolWater_Scheduling_double = [x for x in volFlowMethanolWater_Scheduling[idx] for _ in (0, 1)]
                plt.plot(x_sched_double,volFlowMethanolWater_Scheduling_double, label='Prediction methanol output')

                for i in range(0,idx):
                        x_sim = list(range(result['param']['controlParameters']['numTimeStepsToSimulate']*i,result['param']['controlParameters']['numTimeStepsToSimulate']*(i+1) + 1))
                        x_sim_double = [x_sim[0]] + [x for x in x_sim[1:-1] for _ in (0, 1)] + [x_sim[-1]]
                        x_sched = list(range(result['param']['controlParameters']['numTimeStepsToSimulate']*i,result['param']['controlParameters']['numTimeStepsToSimulate']*i + result['param']['controlParameters']['numberOfTimeSteps'] + 1))
                        x_sched_double = [x_sched[0]] + [x for x in x_sched[1:-1] for _ in (0, 1)] + [x_sched[-1]]
                        volFlowMethanolWater_Sim_double = [x for x in volFlowMethanolWater_Sim[i] for _ in (0, 1)]
                        volFlowMethanolWater_Scheduling_double = [x for x in volFlowMethanolWater_Scheduling[i] for _ in (0, 1)]

                        if i == 0:
                                ax.plot(x_sim_double,volFlowMethanolWater_Sim_double, 'k-', label='Measured methanol output')
                                ax.plot(x_sched_double,volFlowMethanolWater_Scheduling_double, 'b--', alpha=0.5, label='Old prediction methanol output')
                        else:
                                ax.plot(x_sim_double,volFlowMethanolWater_Sim_double, 'k-', label='_nolegend_')
                                ax.plot(x_sched_double,volFlowMethanolWater_Scheduling_double, 'b--', alpha=0.5, label='_nolegend_')
                                
                
                plt.axvline(result['param']['controlParameters']['numTimeStepsToSimulate']*idx, color='k', linestyle='--')

                plt.legend()
                plt.savefig(f"frame2_{(idx*2)}.png")
                plt.show()


                x_full = list(range(0,result['param']['controlParameters']['numTimeStepsToSimulate']*idx + result['param']['controlParameters']['numberOfTimeSteps'] + 1))
                fig, ax = plt.subplots()        
                for i in range(0,idx+1):
                        x_sim = list(range(result['param']['controlParameters']['numTimeStepsToSimulate']*i,result['param']['controlParameters']['numTimeStepsToSimulate']*(i+1) + 1))
                        x_sim_double = [x_sim[0]] + [x for x in x_sim[1:-1] for _ in (0, 1)] + [x_sim[-1]]
                        volFlowMethanolWater_Sim_double = [x for x in volFlowMethanolWater_Sim[i] for _ in (0, 1)]
                        if i == 0:
                                ax.plot(x_sim_double,volFlowMethanolWater_Sim_double, 'k-', label='Measured methanol output')
                        else:
                                ax.plot(x_sim_double,volFlowMethanolWater_Sim_double, 'k-', label='_nolegend_')

                x_sched = list(range(result['param']['controlParameters']['numTimeStepsToSimulate']*idx,result['param']['controlParameters']['numTimeStepsToSimulate']*idx + result['param']['controlParameters']['numberOfTimeSteps'] + 1))
                x_sched_double = [x_sched[0]] + [x for x in x_sched[1:-1] for _ in (0, 1)] + [x_sched[-1]]
                volFlowMethanolWater_Scheduling_double = [x for x in volFlowMethanolWater_Scheduling[idx] for _ in (0, 1)]
                ax.plot(x_sched_double,volFlowMethanolWater_Scheduling_double, 'b--', alpha=0.5, label='Old prediction methanol output')
                plt.axvline(result['param']['controlParameters']['numTimeStepsToSimulate']*(idx+1), color='k', linestyle='--')
                plt.legend()
                plt.savefig(f"frame2_{(idx*2)+1}.png")
                plt.show()

                """
                ########## Methanol produced ##########
                x_full = list(range(0,result['param']['controlParameters']['numTimeStepsToSimulate']*idx + result['param']['controlParameters']['numberOfTimeSteps'] + 1))
                fig, ax = plt.subplots()         
                for i in range(0,idx):
                        x_sim = list(range(result['param']['controlParameters']['numTimeStepsToSimulate']*i,result['param']['controlParameters']['numTimeStepsToSimulate']*(i+1) + 1))
                        x_sim_double = [x_sim[0]] + [x for x in x_sim[1:-1] for _ in (0, 1)] + [x_sim[-1]]
                        x_sched = list(range(result['param']['controlParameters']['numTimeStepsToSimulate']*i,result['param']['controlParameters']['numTimeStepsToSimulate']*i + result['param']['controlParameters']['numberOfTimeSteps'] + 1))
                        x_sched_double = [x_sched[0]] + [x for x in x_sched[1:-1] for _ in (0, 1)] + [x_sched[-1]]
                        volFlowMethanolOut_Sim_double = [x for x in volFlowMethanolOut_Sim[i] for _ in (0, 1)]
                        volFlowMethanolOut_Scheduling_double = [x for x in volFlowMethanolOut_Scheduling[i] for _ in (0, 1)]

                        ax.plot(x_sim_double,volFlowMethanolOut_Sim_double, 'k-', label='Measured methanol output')
                        ax.plot(x_sched_double,volFlowMethanolOut_Scheduling_double, 'b--', alpha=0.5, label='Old prediction methanol output')
                
                x_sched = list(range(result['param']['controlParameters']['numTimeStepsToSimulate']*idx,result['param']['controlParameters']['numTimeStepsToSimulate']*idx + result['param']['controlParameters']['numberOfTimeSteps'] + 1))
                x_sched_double = [x_sched[0]] + [x for x in x_sched[1:-1] for _ in (0, 1)] + [x_sched[-1]]
                volFlowMethanolOut_Scheduling_double = [x for x in volFlowMethanolOut_Scheduling[idx] for _ in (0, 1)]
                
                plt.plot(x_sched_double,volFlowMethanolOut_Scheduling_double, label='Prediction methanol output')
                plt.axvline(result['param']['controlParameters']['numTimeStepsToSimulate']*idx, color='k', linestyle='--')
                plt.legend()
                plt.show()
                #plt.savefig(f'plot_{idx}_added.png')


                fig, ax = plt.subplots()        
                for i in range(0,idx+1):
                        x_sim = list(range(result['param']['controlParameters']['numTimeStepsToSimulate']*i,result['param']['controlParameters']['numTimeStepsToSimulate']*(i+1) + 1))
                        x_sim_double = [x_sim[0]] + [x for x in x_sim[1:-1] for _ in (0, 1)] + [x_sim[-1]]
                        volFlowMethanolOut_Sim_double = [x for x in volFlowMethanolOut_Sim[i] for _ in (0, 1)]
                        ax.plot(x_sim_double,volFlowMethanolOut_Sim_double, 'k-', label='Measured methanol output')

                x_sched = list(range(result['param']['controlParameters']['numTimeStepsToSimulate']*idx,result['param']['controlParameters']['numTimeStepsToSimulate']*idx + result['param']['controlParameters']['numberOfTimeSteps'] + 1))
                x_sched_double = [x_sched[0]] + [x for x in x_sched[1:-1] for _ in (0, 1)] + [x_sched[-1]]
                volFlowMethanolOut_Scheduling_double = [x for x in volFlowMethanolOut_Scheduling[idx] for _ in (0, 1)]
                ax.plot(x_sched_double,volFlowMethanolOut_Scheduling_double, 'b--', alpha=0.5, label='Old prediction methanol output')
                plt.axvline(result['param']['controlParameters']['numTimeStepsToSimulate']*(idx+1), color='k', linestyle='--')

                plt.legend()
                plt.show()
                """

        # GIF erstellen
        images = [imageio.imread(f"frame_{i}.png") for i in range(len(results)*2)]
        imageio.mimsave('h2_pressure.gif', images, duration=2)

        # GIF erstellen
        images = [imageio.imread(f"frame2_{i}.png") for i in range(len(results)*2)]
        imageio.mimsave('methanol_water.gif', images, duration=2)


#load_and_visu()
#load_and_createGif()