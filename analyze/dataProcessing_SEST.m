clear all

% Specify the folder containing the MATLAB files
folderPath = 'C:\PROJEKTE\PTX\Max\21_Scheduling\01_Scheduling_Results\01_data\results_v2_new\';
scenario = ["Case_1", "Case_5"];

for j = 1:numel(scenario)
    % List all files in the folder
    files = dir(fullfile(folderPath + scenario(j) + "\", 'data*')); % Change '*.m' to match your file extension
    
    % Iterate through each file
    for i = 1:length(files)
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

i = 1;

result = [mean(costElectricity(i,:));
            mean(costCarbonIntensity(i,:));
            mean(methanol(i,:));
            mean(runtime(i,:));
            mean(gap(i,:));
            sum(numInf(i,:))];

isInf = isinf(gap(i,:));
idx = [];
for j = 1:numel(isInf)
    if isInf(j) == false && gap(i,j) < 1000
        idx = [idx, j];
    end
end
%result2 = [mean(nonzeros(costElectricity(i,:)));
%            mean(nonzeros(costCarbonIntensity(i,:)));
%            mean(methanol(i,idx));
%            mean(runtime(i,idx));
%            mean(gap(i,idx));
%            sum(numInf)
%            sum(numZeros)];
            

%%

for i = 1:length(files)
    pvSize(i) = cellInput{1,i}.pvSize;
    batterySize(i) = cellInput{1,i}.batterySize;
end


%% Diagramme

fontSize = 10;
path = "C:\PROJEKTE\PTX\Max\21_Scheduling\01_Scheduling_Results\02_images\IEEE_SEST_2025";

num = 16;

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


% % Operation Mode + Point CO2CAP
% figure
% plot(cellInput{1,num}.massFlowHydrogenIn,'Color',"#0072BD",'LineWidth',2)
% grid on
% hold on
% ylabel("Mass flow hydrogen (kg/h)",'FontSize',fontSize,'Interpreter','LaTeX')
% yyaxis right
% plot(cellInput{1,num}.currentStateCO2CAP_SYN,'Color',"#A2142F",'LineWidth',2)
% ax = gca;
% ax.YAxis(2).Color = "#A2142F";
% 
% xlabel("Time (h)",'FontSize',fontSize,'Interpreter','LaTeX')
% ylabel("State of process",'FontSize',fontSize,'Interpreter','LaTeX')
% yticks([0 1 2 3 4])
% yticklabels({'Off','Startup','Standby','On','Shutdown'})
% %legend("variable","stationary",'FontSize',fontSize,'Interpreter','LaTeX')
% xlim([0 121])
% ylim([0 4])
% set(gca,'FontSize',fontSize,'TickLabelInterpreter','latex')
% exportgraphics(gcf,strcat(path + "\operation_point_state_CO2CAP.eps"),'ContentType','vector','Resolution',600)
% 
% 
% % Operation Mode + Point DIS
% figure
% plot(cellInput{1,num}.massFlowMethanolWaterStorage,'Color',"#0072BD",'LineWidth',2)
% grid on
% hold on
% ylabel("Mass flow hydrogen (kg/h)",'FontSize',fontSize,'Interpreter','LaTeX')
% yyaxis right
% plot(cellInput{1,num}.currentStateDIS,'Color',"#A2142F",'LineWidth',2)
% ax = gca;
% ax.YAxis(2).Color = "#A2142F";
% 
% xlabel("Time (h)",'FontSize',fontSize,'Interpreter','LaTeX')
% ylabel("State of process",'FontSize',fontSize,'Interpreter','LaTeX')
% yticks([0 1 2 3 4])
% yticklabels({'Off','Startup','Standby','On','Shutdown'})
% %legend("variable","stationary",'FontSize',fontSize,'Interpreter','LaTeX')
% xlim([0 121])
% ylim([0 4])
% set(gca,'FontSize',fontSize,'TickLabelInterpreter','latex')
% exportgraphics(gcf,strcat(path + "\operation_point_state_DIS.eps"),'ContentType','vector','Resolution',600)
% 
% 
% % Boxplot of prices / reduction
% figure
% boxplot(costElectricity','Labels',{'Flexible','Stationary'})
% xlabel("Case",'FontSize',fontSize,'Interpreter','LaTeX')
% ylabel("Electricity price (euro/kWh)",'FontSize',fontSize,'Interpreter','LaTeX')
% set(gca,'FontSize',fontSize,'TickLabelInterpreter','latex')
% exportgraphics(gcf,strcat(path + "\boxplot_prices.eps"),'ContentType','vector','Resolution',600)
% 
% 
% figure
% boxplot(costElectricity(1,:)' ./ costElectricity(2,:)','Labels',{'Flexible vs. Stationary'})
% xlabel("Case",'FontSize',fontSize,'Interpreter','LaTeX')
% ylabel("Cost reduction (%)",'FontSize',fontSize,'Interpreter','LaTeX')
% set(gca,'FontSize',fontSize,'TickLabelInterpreter','latex')
% exportgraphics(gcf,strcat(path + "\boxplot_cost_reduction.eps"),'ContentType','vector','Resolution',600)
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