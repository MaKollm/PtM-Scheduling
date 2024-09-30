% clear all
% 
% % Specify the folder containing the MATLAB files
% folderPath = 'C:\PROJEKTE\PTX\Max\21_Scheduling\01_Scheduling_Results\01_data\optimization_50_weeks_battery_oversizing_20240224\';
% 
% 
% % List all files in the folder
% files = dir(fullfile(folderPath, 'data*')); % Change '*.m' to match your file extension
% 
% % Iterate through each file
% for i = 1:length(files)
%     % Get the file name
%     filename = files(i).name;
% 
%     % Load the MATLAB file (optional)
%     load(fullfile(folderPath, filename));
% 
%     cost(i) = costs.powerBought;
%     gap(i) = param.optimization.gap;
%     runtime(i) = param.optimization.runtime;
%     methanol(i) = sum(output.massFlowMethanolOut);
%     methane(i) = sum(output.volumeBiogasOut);
%     biogas(i) = sum(output.volumeBiogasIn);
% end
% 
% mean(cost)
% mean(methanol)
% mean(methane)
% mean(biogas)
% mean(runtime)
% mean(gap)




%% Diagramme

fontSize = 10;
path = "C:\PROJEKTE\PTX\Max\21_Scheduling\01_Scheduling_Results\02_images\IEEE_SEST_2024";

% figure('Position',[10 10 560 250])
% plot(1:120,power,'LineWidth',2)
% grid on
% ylabel("Electricity price (euro/kWh)",'FontSize',fontSize,'Interpreter','LaTeX')
% xlabel("Time (h)",'FontSize',fontSize,'Interpreter','LaTeX')
% set(gca,'FontSize',fontSize,'TickLabelInterpreter','latex')
% exportgraphics(gcf,strcat(path + "\power_price_small.eps"),'ContentType','vector','Resolution',600)

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



% % Electricity + Price
% figure
% plot(input.powerBought,'Color',"#0072BD",'LineWidth',2)
% grid on
% hold on
% plot(inputB.powerBought,'Color',"#A2142F",'LineWidth',2)
% ylabel("Power consumption (kWh)",'FontSize',fontSize,'Interpreter','LaTeX')
% yyaxis right
% plot(param.prices.power,'Color',"#EDB120",'LineWidth',2)
% ax = gca;
% ax.YAxis(2).Color = "#EDB120";
% 
% xlabel("Time (h)",'FontSize',fontSize,'Interpreter','LaTeX')
% ylabel("Electricity price (euro/kWh)",'FontSize',fontSize,'Interpreter','LaTeX')
% legend("variable","stationary",'FontSize',fontSize,'Interpreter','LaTeX')
% xlim([0 121])
% set(gca,'FontSize',fontSize,'TickLabelInterpreter','latex')
% exportgraphics(gcf,strcat(path + "\electricity_consumption_price_stationary_variable.eps"),'ContentType','vector','Resolution',600)

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
figure
bar(1:121,input.powerInBatteryBought)%,'FaceColor',"#0072BD",'EdgeColor',"#0072BD",'LineWidth',2)
grid on
hold on
bar(1:121,input.powerOutBattery)%,'FaceColor',"#A2142F",'EdgeColor',"#A2142F",'LineWidth',2)
ylabel("Power (kW)",'FontSize',fontSize,'Interpreter','LaTeX')
ylim([0 10])
yyaxis right
plot(param.prices.power,'Color',"#EDB120",'LineWidth',2)
ax = gca;
ax.YAxis(2).Color = "#EDB120";

xlabel("Time (h)",'FontSize',fontSize,'Interpreter','LaTeX')
ylabel("Electricity price (euro/kWh)",'FontSize',fontSize,'Interpreter','LaTeX')
legend("charging","discharging",'FontSize',fontSize,'Interpreter','LaTeX')
xlim([0 121])
set(gca,'FontSize',fontSize,'TickLabelInterpreter','latex')
exportgraphics(gcf,strcat(path + "\battery_charging_discharging_variable.eps"),'ContentType','vector','Resolution',600)

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