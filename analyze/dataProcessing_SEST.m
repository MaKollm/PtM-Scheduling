clear all

% Specify the folder containing the MATLAB files
folderPath = 'C:\PROJEKTE\PTX\Max\21_Scheduling\01_Scheduling_Results\01_data\results_v2_new\';
scenario = ["Case_1","Case_5"];
scenario = ["Case_63"];

for j = 1:numel(scenario)
    % List all files in the folder
    files = dir(fullfile(folderPath + scenario(j) + "\", 'data*')); % Change '*.m' to match your file extension
    
    % Iterate through each file
    for i = 1:length(files)
        if i ~= 33
            % Get the file name
            filename = files(i).name;
        
            % Load the MATLAB file (optional)
            load(fullfile(folderPath + scenario(j) + "\", filename));
    
            cellInput{j,i} = input;
            cellOutput{j,i} = output;
            cellCosts{j,i} = costs;
            cellParam{j,i} = param;
        
            if param.optimization.status ~= 3
                costElectricity(j,i) = costs.powerBought;
                costCarbonIntensity(j,i) = costs.carbonIntensity / 1000;
                methanol(j,i) = sum(output.massFlowMethanolOut);
                pvSize(j,i) = input.pvSize;
                batterySize(j,i) = input.batterySize;
                numInf(j,i) = 0;
            else
                numInf(j,i) = 1;
            end
    
            gap(j,i) = param.optimization.gap;
            runtime(j,i) = param.optimization.runtime;
            status(j,i) = param.optimization.status;
            
            if gap(j,i) > 1000 && param.optimization.status ~= 3
                numZeros(j,i) = 1;
            else
                numZeros(j,i) = 0;
            end
        end
    end
end

i = 1;

result = [mean(costElectricity(i,:));
            mean(costCarbonIntensity(i,:));
            mean(methanol(i,:));
            mean(runtime(i,:));
            mean(gap(i,:));
            sum(numInf)];

isInf = isinf(gap(i,:));
idx = [];
for j = 1:numel(isInf)
    if isInf(j) == false && gap(i,j) < 1000 %&& methanol(i,j) > 108
        idx = [idx, j];
    end
end
result2 = [mean(nonzeros(costElectricity(i,:)));
            mean(nonzeros(costCarbonIntensity(i,:)));
            mean(methanol(i,idx));
            mean(runtime(i,idx));
            mean(gap(i,idx));
            sum(numInf)
            sum(numZeros)];
            
annualMethanol = sum(methanol(i,:))

%%

for i = 1:length(files)
    pvSize(i) = cellInput{1,i}.pvSize;
    batterySize(i) = cellInput{1,i}.batterySize;
end

%% Load characteristic maps

cm_CO2CAP_SYN = readtable("C:\PROJEKTE\PTX\Max\50_Daten\01_Stationäre_Kennfelder\maps_Aspen_v2\PtMCharMap_CO2_Capture_Synthesis.xlsx");
cm_DIS = readtable("C:\PROJEKTE\PTX\Max\50_Daten\01_Stationäre_Kennfelder\maps_Aspen_v2\PtMCharMap_Distillation.xlsx");

cm_power_CO2CAP_SYN = cm_CO2CAP_SYN.POWER_ALL(2:end);
cm_power_DIS = cm_DIS.DUTY_ALL(2:end);

mass_flow_synthesis = cm_CO2CAP_SYN.MIXED_ResolvedMassFlow_ResolvedMassFlow_2(2:end);
%mass_flow_methanol_water_in_storage = cm_CO2CAP_SYN.
mass_flow_distillation = cm_DIS.MassComponentFlows_MEOH_MassComponentFlows_MEOH_1(2:end);


%% Diagramme new

fontSize = 12;
path = "C:\PROJEKTE\PTX\Max\21_Scheduling\01_Scheduling_Results\02_images\IEEE_SEST_2025";

num = 16; % 37


for k = 1:numel(scenario)
    for i = 1:size(cellInput{k,num}.operationPoint_CO2CAP_SYN,1)
        for j = 1:size(cellInput{k,num}.operationPoint_CO2CAP_SYN,2)
            if int16(cellInput{k,num}.operationPoint_CO2CAP_SYN(i,j)) == 1
                op_CO2CAP_SYN(i,k) = j;
                power_CO2CAP_SYN(i,k) = cm_power_CO2CAP_SYN(j);
                mass_flow_CO2CAP_SYN(i,k) = mass_flow_synthesis(j);
            end
        end
    
        for j = 1:size(cellInput{k,num}.operationPoint_DIS,2)
            if int16(cellInput{k,num}.operationPoint_DIS(i,j)) == 1
                op_DIS(i,k) = j;
                power_DIS(i,k) = cm_power_DIS(j);
                mass_flow_DIS(i,k) = mass_flow_distillation(j);
            end
        end
    end

    %cap_CO2CAP_SYN(:,k) = mass_flow_CO2CAP_SYN(:,k) ./ max(mass_flow_CO2CAP_SYN(:,k)) * 100;
    %cap_DIS(:,k) = mass_flow_DIS(:,k) ./ max(mass_flow_DIS(:,k)) * 100;
    cap_CO2CAP_SYN(:,k) = mass_flow_CO2CAP_SYN(:,k) ./ max(mass_flow_synthesis) * 100;
    cap_DIS(:,k) = mass_flow_DIS(:,k) ./ max(mass_flow_distillation) * 100;
    cap_ELEC(:,k) = cellInput{k,num}.powerElectrolyser ./ 19.2 * 100;
end

x = [0:120];
cellParam{1,num}.prices.power(1) = cellParam{1,num}.prices.power(2);
cellParam{2,num}.prices.power(1) = cellParam{2,num}.prices.power(2);

cellParam{1,num}.carbonIntensity.carbonIntensity(1) = cellParam{1,num}.carbonIntensity.carbonIntensity(2);
cellParam{2,num}.carbonIntensity.carbonIntensity(1) = cellParam{2,num}.carbonIntensity.carbonIntensity(2);


% Operation Mode + Point CO2CAP
figure
%plot(cellInput{1,num}.massFlowHydrogenIn,'Color',"#0072BD",'LineWidth',2)
plot(x,op_CO2CAP_SYN(:,1),'Color',"#0072BD",'LineWidth',2,'LineStyle','--')
grid on
hold on
plot(x,op_CO2CAP_SYN(:,2),'Color',"#0072BD",'LineWidth',2,'LineStyle','-')
%ylabel("Mass flow hydrogen (kg/h)",'FontSize',fontSize,'Interpreter','LaTeX')
ylabel("Operating point of CO$_2$-Capture and Synthesis",'FontSize',fontSize,'Interpreter','LaTeX');
yyaxis right
plot(x,cellInput{1,num}.currentStateCO2CAP_SYN,'Color',"#A2142F",'LineWidth',2,'LineStyle','--')
plot(x,cellInput{2,num}.currentStateCO2CAP_SYN,'Color',"#A2142F",'LineWidth',2,'LineStyle','-')
ax = gca;
ax.YAxis(2).Color = "#A2142F";%"#000000";%"#A2142F";

xlabel("Time (h)",'FontSize',fontSize,'Interpreter','LaTeX')
ylabel("State of CO$_2$-Capture and Synthesis",'FontSize',fontSize,'Interpreter','LaTeX')
yticks([0 1 2 3 4])
yticklabels({'Off','Startup','Standby','On','Shutdown'})
legend("operating point - stationary","operating point - flexible", "state - stationary", "state - flexible","Location","best",'FontSize',fontSize,'Interpreter','LaTeX')
xlim([x(1) x(end)])
ylim([0 4])
set(gca,'FontSize',fontSize,'TickLabelInterpreter','latex')
savefig(gcf,strcat(path + "\operation_point_state_CO2CAP.fig"));
exportgraphics(gcf,strcat(path + "\operation_point_state_CO2CAP.eps"),'ContentType','vector','Resolution',600)


% Operation Mode + Point DIS
figure
%plot(cellInput{1,num}.massFlowHydrogenIn,'Color',"#0072BD",'LineWidth',2)
plot(x,op_DIS(:,1),'Color',"#0072BD",'LineWidth',2,'LineStyle','--')
grid on
hold on
plot(x,op_DIS(:,2),'Color',"#0072BD",'LineWidth',2,'LineStyle','-')
%ylabel("Mass flow hydrogen (kg/h)",'FontSize',fontSize,'Interpreter','LaTeX')
ylabel("Operating point of Distillation",'FontSize',fontSize,'Interpreter','LaTeX');
yyaxis right
plot(x,cellInput{1,num}.currentStateDIS,'Color',"#A2142F",'LineWidth',2,'LineStyle','--')
plot(x,cellInput{2,num}.currentStateDIS,'Color',"#A2142F",'LineWidth',2,'LineStyle','-')
ax = gca;
ax.YAxis(2).Color = "#A2142F";%"#000000";%"#A2142F";

xlabel("Time (h)",'FontSize',fontSize,'Interpreter','LaTeX')
ylabel("State of Distillation",'FontSize',fontSize,'Interpreter','LaTeX')
yticks([0 1 2 3 4])
yticklabels({'Off','Startup','Standby','On','Shutdown'})
legend("operating point - stationary","operating point - flexible", "state - stationary", "state - flexible","Location","best",'FontSize',fontSize,'Interpreter','LaTeX')
xlim([x(1) x(end)])
ylim([0 4])
set(gca,'FontSize',fontSize,'TickLabelInterpreter','latex')
savefig(gcf,strcat(path + "\operation_point_state_DIS.fig"));
exportgraphics(gcf,strcat(path + "\operation_point_state_DIS.eps"),'ContentType','vector','Resolution',600)


% Electricity + Price
figure
plot(x,cellInput{1,num}.powerBought,'Color',"#0072BD",'LineWidth',2)
grid on
hold on
plot(x,cellInput{2,num}.powerBought,'Color',"#A2142F",'LineWidth',2)
yline(cellParam{1,num}.peakLoadCapping.maximumLoad,"LineStyle","--",'LineWidth',2)
text(2,30,"maximum allowed load","Interpreter","latex")
ylabel("Power consumption (kWh)",'FontSize',fontSize,'Interpreter','LaTeX')
ylim([0 cellParam{1,num}.peakLoadCapping.maximumLoad/0.8])
yyaxis right
plot(x,cellParam{1,num}.prices.power,'Color',"#EDB120",'LineWidth',2)
ax = gca;
ax.YAxis(2).Color = "#EDB120";

xlabel("Time (h)",'FontSize',fontSize,'Interpreter','LaTeX')
ylabel("Electricity price (euro/kWh)",'FontSize',fontSize,'Interpreter','LaTeX')
legend("stationary","flexible",'Location','southeast','FontSize',fontSize,'Interpreter','LaTeX')
xlim([x(1) x(end)])
set(gca,'FontSize',fontSize,'TickLabelInterpreter','latex')
savefig(gcf,strcat(path + "\electricity_consumption_price_stationary_variable.fig"));
exportgraphics(gcf,strcat(path + "\electricity_consumption_price_stationary_variable.eps"),'ContentType','vector','Resolution',600)


% Electricity + Carbon intensity
figure
plot(x,cellInput{1,num}.powerBought,'Color',"#0072BD",'LineWidth',2)
grid on
hold on
plot(x,cellInput{2,num}.powerBought,'Color',"#A2142F",'LineWidth',2)
ylabel("Power consumption (kWh)",'FontSize',fontSize,'Interpreter','LaTeX')
yyaxis right
ylim([0 inf])
plot(x,cellParam{1,num}.carbonIntensity.carbonIntensity,'Color',"#EDB120",'LineWidth',2)
ax = gca;
ax.YAxis(2).Color = "#EDB120";

xlabel("Time (h)",'FontSize',fontSize,'Interpreter','LaTeX')
ylabel("Carbon intensity (g/kWh)",'FontSize',fontSize,'Interpreter','LaTeX')
legend("stationary","flexible",'Location','best','FontSize',fontSize,'Interpreter','LaTeX')
xlim([x(1) x(end)])
set(gca,'FontSize',fontSize,'TickLabelInterpreter','latex')
savefig(gcf,strcat(path + "\electricity_consumption_carbon_intensity_stationary_variable.fig"));
exportgraphics(gcf,strcat(path + "\electricity_consumption_carbon_intensity_stationary_variable.eps"),'ContentType','vector','Resolution',600)



% Electricity + Price als Bar plot aufgeteilt in CO2-CAP, DIS and ELEC
power = [power_CO2CAP_SYN(:,2),power_DIS(:,2),cellInput{2,num}.powerElectrolyser'];

figure
bar(x,power,"stacked");
grid on
hold on
ylabel("Power consumption (kWh)",'FontSize',fontSize,'Interpreter','LaTeX')
yyaxis right
plot(x,cellParam{2,num}.prices.power,'Color',"#EDB120",'LineWidth',2)
ax = gca;
ax.YAxis(2).Color = "#EDB120";

xlabel("Time (h)",'FontSize',fontSize,'Interpreter','LaTeX')
ylabel("Electricity price (euro/kWh)",'FontSize',fontSize,'Interpreter','LaTeX')
legend("CO$_2$-Capture and Synthesis","Distillation","Elektrolyser",'Location','best','FontSize',fontSize,'Interpreter','LaTeX')
xlim([x(1) x(end)])
set(gca,'FontSize',fontSize,'TickLabelInterpreter','latex')
savefig(gcf,strcat(path + "\electricity_consumption_price_bar_plot.fig"));
exportgraphics(gcf,strcat(path + "\electricity_consumption_price_bar_plot.eps"),'ContentType','vector','Resolution',600)


% Capacity of CO2-CAP + DIS + ELEC
figure
plot(x,cap_CO2CAP_SYN(:,1),'Color',"#0072BD",'LineWidth',2,'LineStyle',"-");
grid on
hold on
plot(x,cap_CO2CAP_SYN(:,2),'Color',"#A2142F",'LineWidth',2,'LineStyle',"-");
plot(x,cap_DIS(:,1),'Color',"#0072BD",'LineWidth',2,'LineStyle',"--");
plot(x,cap_DIS(:,2),'Color',"#A2142F",'LineWidth',2,'LineStyle',"--");
plot(x,cap_ELEC(:,1),'Color',"#0072BD",'LineWidth',2,'LineStyle',"-.");
plot(x,cap_ELEC(:,2),'Color',"#A2142F",'LineWidth',2,'LineStyle',"-.");

ylabel("Capacity (%)",'FontSize',fontSize,'Interpreter','LaTeX')
xlabel("Time (h)",'FontSize',fontSize,'Interpreter','LaTeX')
legend("CO$_2$-Capture and Synthesis - stationary", "CO$_2$-Capture and Synthesis - flexible", "Distillation - stationary", "Distillation - flexible","Electrolyser - stationary", "Electrolyser - flexible",'Location','best','FontSize',fontSize,'Interpreter','LaTeX')
xlim([x(1) x(end)])
set(gca,'FontSize',fontSize,'TickLabelInterpreter','latex')
savefig(gcf,strcat(path + "\capacity_plot.fig"));
exportgraphics(gcf,strcat(path + "\capacity_plot.eps"),'ContentType','vector','Resolution',600)





figure
subplot(3,1,1)
plot(x,cap_CO2CAP_SYN(:,1),'Color',"#0072BD",'LineWidth',2,'LineStyle',"-");
grid on
hold on
plot(x,cap_CO2CAP_SYN(:,2),'Color',"#A2142F",'LineWidth',2,'LineStyle',"-");
ylabel("Capacity (%)",'FontSize',fontSize,'Interpreter','LaTeX')
xlabel("Time (h)",'FontSize',fontSize,'Interpreter','LaTeX')
legend("stationary","flexible",'Location','best','FontSize',fontSize,'Interpreter','LaTeX')
xlim([x(1) x(end)])
title("CO$_2$-Capture and Synthesis","FontSize",fontSize,"Interpreter","latex")
set(gca,'FontSize',fontSize,'TickLabelInterpreter','latex')

subplot(3,1,2)
plot(x,cap_DIS(:,1),'Color',"#0072BD",'LineWidth',2,'LineStyle',"-");
grid on
hold on
plot(x,cap_DIS(:,2),'Color',"#A2142F",'LineWidth',2,'LineStyle',"-");
ylabel("Capacity (%)",'FontSize',fontSize,'Interpreter','LaTeX')
xlabel("Time (h)",'FontSize',fontSize,'Interpreter','LaTeX')
legend("stationary","flexible",'Location','best','FontSize',fontSize,'Interpreter','LaTeX')
xlim([x(1) x(end)])
title("Distillation","FontSize",fontSize,"Interpreter","latex")
set(gca,'FontSize',fontSize,'TickLabelInterpreter','latex')

subplot(3,1,3)
plot(x,cap_ELEC(:,1),'Color',"#0072BD",'LineWidth',2,'LineStyle',"-");
grid on
hold on
plot(x,cap_ELEC(:,2),'Color',"#A2142F",'LineWidth',2,'LineStyle',"-");
ylabel("Capacity (%)",'FontSize',fontSize,'Interpreter','LaTeX')
xlabel("Time (h)",'FontSize',fontSize,'Interpreter','LaTeX')
legend("stationary","flexible",'Location','best','FontSize',fontSize,'Interpreter','LaTeX')
xlim([x(1) x(end)])
title("Electrolyser","FontSize",fontSize,"Interpreter","latex")
set(gca,'FontSize',fontSize,'TickLabelInterpreter','latex')

savefig(gcf,strcat(path + "\capacity_subplot.fig"));
exportgraphics(gcf,strcat(path + "\capacity_subplot.eps"),'ContentType','vector','Resolution',600)

% Storage H2 + Methanol Water
figure
subplot(2,1,1)
plot(x,(cellOutput{1,num}.storageH2Pressure - double(cellParam{1,num}.storageH2.LowerBound)) ./ (double(cellParam{1,num}.storageH2.UpperBound) - double(cellParam{1,num}.storageH2.LowerBound)) .* 100,'Color',"#0072BD",'LineWidth',2,'LineStyle',"-");
grid on
hold on
plot(x,(cellOutput{2,num}.storageH2Pressure  -double(cellParam{2,num}.storageH2.LowerBound)) ./ (double(cellParam{2,num}.storageH2.UpperBound) - double(cellParam{2,num}.storageH2.LowerBound)) .* 100,'Color',"#A2142F",'LineWidth',2,'LineStyle',"-");
ylabel("SOC (%)",'FontSize',fontSize,'Interpreter','LaTeX')
xlabel("Time (h)",'FontSize',fontSize,'Interpreter','LaTeX')
legend("stationary","flexible","Elektrolyser",'Location','northeast','FontSize',fontSize,'Interpreter','LaTeX')
xlim([x(1) x(end)])
ylim([0 100]);
title("Hydrogen storage tank","Interpreter","latex")
set(gca,'FontSize',fontSize,'TickLabelInterpreter','latex')

subplot(2,1,2)
plot(x,cellOutput{1,num}.storageMethanolWaterFilling ./ double(cellParam{1,num}.storageMethanolWater.UpperBound) .* 100,'Color',"#0072BD",'LineWidth',2,'LineStyle',"-");
grid on
hold on
plot(x,cellOutput{2,num}.storageMethanolWaterFilling ./ double(cellParam{2,num}.storageMethanolWater.UpperBound) .* 100,'Color',"#A2142F",'LineWidth',2,'LineStyle',"-");
ylabel("SOC (%)",'FontSize',fontSize,'Interpreter','LaTeX')
xlabel("Time (h)",'FontSize',fontSize,'Interpreter','LaTeX')
legend("stationary","flexible","Elektrolyser",'Location','northeast','FontSize',fontSize,'Interpreter','LaTeX')
xlim([x(1) x(end)])
ylim([0 100]);
title("Methanol-water storage tank","Interpreter","latex")
set(gca,'FontSize',fontSize,'TickLabelInterpreter','latex')


savefig(gcf,strcat(path + "\storage_subplot.fig"));
exportgraphics(gcf,strcat(path + "\storage_subplot.eps"),'ContentType','vector','Resolution',600)


% SOC Battery
figure
plot(cellOutput{1,num}.batteryCharge,'Color',"#0072BD",'LineWidth',2)
grid on
hold on
plot(cellOutput{2,num}.batteryCharge,'Color',"#A2142F",'LineWidth',2)
ylabel("SOC (%)",'FontSize',fontSize,'Interpreter','LaTeX')
yyaxis right
plot(cellParam{1,num}.prices.power,'Color',"#EDB120",'LineWidth',2)
ax = gca;
ax.YAxis(2).Color = "#EDB120";

xlabel("Time (h)",'FontSize',fontSize,'Interpreter','LaTeX')
ylabel("Electricity price (euro/kWh)",'FontSize',fontSize,'Interpreter','LaTeX')
legend("stationary","flexible",'Location','best','FontSize',fontSize,'Interpreter','LaTeX')
xlim([x(1) x(end)])
set(gca,'FontSize',fontSize,'TickLabelInterpreter','latex')
savefig(gcf,strcat(path + "\electricity_price_SOC.fig"));
exportgraphics(gcf,strcat(path + "\electricity_price_pv.eps"),'ContentType','vector','Resolution',600)


% Power from grid + power from pv + electricity price bar plot
pv = [cellInput{2,num}.powerBought', cellInput{2,num}.usageOfPV'];

figure
bar(x,pv,"stacked");
grid on
hold on
ylabel("Power (kW)",'FontSize',fontSize,'Interpreter','LaTeX')
yyaxis right
plot(x,cellParam{1,num}.prices.power,'Color',"#EDB120",'LineWidth',2)
ax = gca;
ax.YAxis(2).Color = "#EDB120";

xlabel("Time (h)",'FontSize',fontSize,'Interpreter','LaTeX')
ylabel("Electricity price (euro/kWh)",'FontSize',fontSize,'Interpreter','LaTeX')
legend("power from grid","power from pv",'Location','best','FontSize',fontSize,'Interpreter','LaTeX')
xlim([x(1) x(end)])
set(gca,'FontSize',fontSize,'TickLabelInterpreter','latex')
savefig(gcf,strcat(path + "\electricity_price_pv.fig"));
exportgraphics(gcf,strcat(path + "\electricity_price_pv.eps"),'ContentType','vector','Resolution',600)


% Battery charging + discharging + electricity price bar plot
battery = [cellInput{2,num}.actualPowerInBatteryBought' + cellInput{2,num}.actualPowerInBatteryPV', cellInput{2,num}.actualPowerOutBattery'];

figure
bar(x,battery,"stacked");
grid on
hold on
ylabel("power (kW)",'FontSize',fontSize,'Interpreter','LaTeX')
yyaxis right
plot(x,cellParam{1,num}.prices.power,'Color',"#EDB120",'LineWidth',2)
ax = gca;
ax.YAxis(2).Color = "#EDB120";

xlabel("Time (h)",'FontSize',fontSize,'Interpreter','LaTeX')
ylabel("Electricity price (euro/kWh)",'FontSize',fontSize,'Interpreter','LaTeX')
legend("charging","discharging",'Location','best','FontSize',fontSize,'Interpreter','LaTeX')
xlim([x(1) x(end)])
set(gca,'FontSize',fontSize,'TickLabelInterpreter','latex')
savefig(gcf,strcat(path + "\electricity_price_battery.fig"));
exportgraphics(gcf,strcat(path + "\electricity_price_battery.eps"),'ContentType','vector','Resolution',600)

% Battery charging + discharging + electricity price bar plot + SOC??

%% Diagramme 

% figure('Position',[10 10 560 250])
% plot(1:120,power,'LineWidth',2)
% grid on
% ylabel("Electricity price (euro/kWh)",'FontSize',fontSize,'Interpreter','LaTeX')
% xlabel("Time (h)",'FontSize',fontSize,'Interpreter','LaTeX')
% set(gca,'FontSize',fontSize,'TickLabelInterpreter','latex')
% exportgraphics(gcf,strcat(path + "\power_price_small.eps"),'ContentType','vector','Resolution',600)
% 
% figure('Position',[10 10 560 250])
% plot(1:120,pv,'LineWidth',2)
% grid on
% ylabel("Power (kW)",'FontSize',fontSize,'Interpreter','LaTeX')
% xlabel("Time (h)",'FontSize',fontSize,'Interpreter','LaTeX')
% set(gca,'FontSize',fontSize,'TickLabelInterpreter','latex')
% exportgraphics(gcf,strcat(path + "\pv_small.eps"),'ContentType','vector','Resolution',600)


% % PV and power price
% figure
% subplot(2,1,1)
% plot(1:120,power,'LineWidth',2)
% grid on
% ylabel("power price in euro/kWh",'FontSize',fontSize,'Interpreter','LaTeX')
% xlabel("time in h",'FontSize',fontSize,'Interpreter','LaTeX')
% set(gca,'FontSize',fontSize,'TickLabelInterpreter','latex')
% 
% subplot(2,1,2)
% plot(1:120,pv(2:end),'LineWidth',2)
% grid on
% xlabel("time in h",'FontSize',fontSize,'Interpreter','LaTeX')
% ylabel("power in kWh",'FontSize',fontSize,'Interpreter','LaTeX')
% xlim([0 121])
% set(gca,'FontSize',fontSize,'TickLabelInterpreter','latex')



% Electricity + Price
figure
plot(cellInput{1,num}.powerBought,'Color',"#0072BD",'LineWidth',2)
grid on
hold on
plot(cellInput{2,num}.powerBought,'Color',"#A2142F",'LineWidth',2)
ylabel("Power consumption (kWh)",'FontSize',fontSize,'Interpreter','LaTeX')
yyaxis right
plot(cellParam{1,num}.prices.power,'Color',"#EDB120",'LineWidth',2)
ax = gca;
ax.YAxis(2).Color = "#EDB120";

xlabel("Time (h)",'FontSize',fontSize,'Interpreter','LaTeX')
ylabel("Electricity price (euro/kWh)",'FontSize',fontSize,'Interpreter','LaTeX')
legend("variable","stationary",'Location','best','FontSize',fontSize,'Interpreter','LaTeX')
xlim([0 121])
set(gca,'FontSize',fontSize,'TickLabelInterpreter','latex')
exportgraphics(gcf,strcat(path + "\electricity_consumption_price_stationary_variable.eps"),'ContentType','vector','Resolution',600)


% Operation Mode + Point CO2CAP
figure
plot(cellInput{1,num}.massFlowHydrogenIn,'Color',"#0072BD",'LineWidth',2)
grid on
hold on
ylabel("Mass flow hydrogen (kg/h)",'FontSize',fontSize,'Interpreter','LaTeX')
yyaxis right
plot(cellInput{1,num}.currentStateCO2CAP_SYN,'Color',"#A2142F",'LineWidth',2)
ax = gca;
ax.YAxis(2).Color = "#A2142F";

xlabel("Time (h)",'FontSize',fontSize,'Interpreter','LaTeX')
ylabel("State of process",'FontSize',fontSize,'Interpreter','LaTeX')
yticks([0 1 2 3 4])
yticklabels({'Off','Startup','Standby','On','Shutdown'})
%legend("variable","stationary",'FontSize',fontSize,'Interpreter','LaTeX')
xlim([0 121])
ylim([0 4])
set(gca,'FontSize',fontSize,'TickLabelInterpreter','latex')
exportgraphics(gcf,strcat(path + "\operation_point_state_CO2CAP.eps"),'ContentType','vector','Resolution',600)


% Operation Mode + Point DIS
figure
plot(cellInput{1,num}.massFlowMethanolWaterStorage,'Color',"#0072BD",'LineWidth',2)
grid on
hold on
ylabel("Mass flow hydrogen (kg/h)",'FontSize',fontSize,'Interpreter','LaTeX')
yyaxis right
plot(cellInput{1,num}.currentStateDIS,'Color',"#A2142F",'LineWidth',2)
ax = gca;
ax.YAxis(2).Color = "#A2142F";

xlabel("Time (h)",'FontSize',fontSize,'Interpreter','LaTeX')
ylabel("State of process",'FontSize',fontSize,'Interpreter','LaTeX')
yticks([0 1 2 3 4])
yticklabels({'Off','Startup','Standby','On','Shutdown'})
%legend("variable","stationary",'FontSize',fontSize,'Interpreter','LaTeX')
xlim([0 121])
ylim([0 4])
set(gca,'FontSize',fontSize,'TickLabelInterpreter','latex')
exportgraphics(gcf,strcat(path + "\operation_point_state_DIS.eps"),'ContentType','vector','Resolution',600)


% Boxplot of prices / reduction
figure
boxplot(costElectricity','Labels',{'Flexible','Stationary'})
xlabel("Case",'FontSize',fontSize,'Interpreter','LaTeX')
ylabel("Electricity price (euro/kWh)",'FontSize',fontSize,'Interpreter','LaTeX')
set(gca,'FontSize',fontSize,'TickLabelInterpreter','latex')
exportgraphics(gcf,strcat(path + "\boxplot_prices.eps"),'ContentType','vector','Resolution',600)


figure
boxplot(costElectricity(1,:)' ./ costElectricity(2,:)','Labels',{'Flexible vs. Stationary'})
xlabel("Case",'FontSize',fontSize,'Interpreter','LaTeX')
ylabel("Cost reduction (%)",'FontSize',fontSize,'Interpreter','LaTeX')
set(gca,'FontSize',fontSize,'TickLabelInterpreter','latex')
exportgraphics(gcf,strcat(path + "\boxplot_cost_reduction.eps"),'ContentType','vector','Resolution',600)
% % PV
% for i = 1:121
%     bary(i,:) = [input.powerBought(i), input.usageOfPV(i)];
% end
% figure
% bar(1:121,bary, 'stacked')
% grid on
% hold on
% 
% ylabel("Power (kW)",'FontSize',fontSize,'Interpreter','LaTeX')
% xlabel("Time (h)",'FontSize',fontSize,'Interpreter','LaTeX')
% xlim([0 121])
% yyaxis right
% plot(param.prices.power,'Color',"#EDB120",'LineWidth',2)
% ax = gca;
% ax.YAxis(2).Color = "#EDB120";
% 
% xlabel("Time (h)",'FontSize',fontSize,'Interpreter','LaTeX')
% ylabel("Electricity price (euro/kWh)",'FontSize',fontSize,'Interpreter','LaTeX')
% legend("power from grid","power from pv",'FontSize',fontSize,'Interpreter','LaTeX')
% xlim([0 121])
% set(gca,'FontSize',fontSize,'TickLabelInterpreter','latex')
% exportgraphics(gcf,strcat(path + "\pv_variable.eps"),'ContentType','vector','Resolution',600)



% Battery with price
% figure
% bar(1:121,input.powerInBatteryBought)%,'FaceColor',"#0072BD",'EdgeColor',"#0072BD",'LineWidth',2)
% grid on
% hold on
% bar(1:121,input.powerOutBattery)%,'FaceColor',"#A2142F",'EdgeColor',"#A2142F",'LineWidth',2)
% ylabel("Power (kW)",'FontSize',fontSize,'Interpreter','LaTeX')
% ylim([0 10])
% yyaxis right
% plot(param.prices.power,'Color',"#EDB120",'LineWidth',2)
% ax = gca;
% ax.YAxis(2).Color = "#EDB120";
% 
% xlabel("Time (h)",'FontSize',fontSize,'Interpreter','LaTeX')
% ylabel("Electricity price (euro/kWh)",'FontSize',fontSize,'Interpreter','LaTeX')
% legend("charging","discharging",'FontSize',fontSize,'Interpreter','LaTeX')
% xlim([0 121])
% set(gca,'FontSize',fontSize,'TickLabelInterpreter','latex')
% exportgraphics(gcf,strcat(path + "\battery_charging_discharging_variable.eps"),'ContentType','vector','Resolution',600)

% 
% % Battery with SOC
% figure
% b1 = bar(1:121,input.powerInBatteryBought,'FaceColor',"#0072BD",'EdgeColor',"#0072BD",'LineWidth',2);
% b1.FaceAlpha = 0.5;
% b1.LineWidth = 0.0000001;
% grid on
% hold on
% b2 = bar(1:121,input.powerOutBattery,'FaceColor',"#A2142F",'EdgeColor',"#A2142F",'LineWidth',2);
% b2.FaceAlpha = 0.5;
% b2.LineWidth = 0.01;
% ylabel("power in kW",'FontSize',fontSize,'Interpreter','LaTeX')
% ylim([0 10])
% yyaxis right
% plot(output.batteryCharge / double(param.battery.capacity),'Color','#EDB120','LineWidth',2)
% ax = gca;
% ax.YAxis(2).Color = "#EDB120";
% 
% xlabel("time in h",'FontSize',fontSize,'Interpreter','LaTeX')
% ylabel("SOC of the battery",'FontSize',fontSize,'Interpreter','LaTeX')
% legend("charging","discharging",'FontSize',fontSize,'Interpreter','LaTeX')
% xlim([0 121])
% set(gca,'FontSize',fontSize,'TickLabelInterpreter','latex')
% 
% % Battery with SOC - 2 plots
% figure
% subplot(2,1,1)
% b1 = bar(1:121,input.powerInBatteryBought,'FaceColor',"#0072BD",'EdgeColor',"#0072BD",'LineWidth',2);
% b1.FaceAlpha = 0.5;
% b1.LineWidth = 0.0000001;
% grid on
% hold on
% b2 = bar(1:121,input.powerOutBattery,'FaceColor',"#A2142F",'EdgeColor',"#A2142F",'LineWidth',2);
% b2.FaceAlpha = 0.5;
% b2.LineWidth = 0.01;
% ylabel("power in kW",'FontSize',fontSize,'Interpreter','LaTeX')
% ylim([0 10])
% legend("charging","discharging",'FontSize',fontSize,'Interpreter','LaTeX')
% 
% subplot(2,1,2)
% plot(output.batteryCharge / double(param.battery.capacity),'Color','k','LineWidth',2)
% %ax = gca;
% %ax.YAxis(2).Color = "#EDB120";
% xlabel("time in h",'FontSize',fontSize,'Interpreter','LaTeX')
% ylabel("SOC of the battery",'FontSize',fontSize,'Interpreter','LaTeX')
% xlim([0 121])
% set(gca,'FontSize',fontSize,'TickLabelInterpreter','latex')


% % Ramping
% figure
% subplot(2,1,1)
% plot(1:121, input.methanolWaterInDistillation,'Color',"#0072BD",'LineWidth',2);
% grid on
% xlabel("time in h",'FontSize',fontSize,'Interpreter','LaTeX')
% ylabel("mass flow in kg/h",'FontSize',fontSize,'Interpreter','LaTeX')
% xlim([1 121])

% 
% subplot(2,1,2)
% plot(input.synthesisgasInMethanolSynthesis,'Color',"#0072BD",'LineWidth',2);
% grid on
% xlabel("time in h",'FontSize',fontSize,'Interpreter','LaTeX')
% ylabel("mass flow in kg/h",'FontSize',fontSize,'Interpreter','LaTeX')
% xlim([0 121])
% set(gca,'FontSize',fontSize,'TickLabelInterpreter','latex')