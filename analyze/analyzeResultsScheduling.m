clear all

% Specify the folder containing the MATLAB files
folderPath = 'C:\PROJEKTE\PTX\Max\21_Scheduling\gurobi\PtM\';
folderPath = 'C:\PROJEKTE\PTX\Max\21_Scheduling\01_Scheduling_Results\01_data\Case_study_34\';

% List all files in the folder
files = dir(fullfile(folderPath, 'data_opt*')); % Change '*.m' to match your file extension

% Iterate through each file
for i = 1:length(files)
    % Get the file name
    filename = files(i).name;

    % Load the MATLAB file (optional)
    load(fullfile(folderPath, filename));

    var{i} = output.massFlowMethanolOut;
    var{i} = input.powerElectrolyser;
    % var{i} = input.hydrogenInput;
    % var{i} = output.powerPlantABSDES_MEOHSYN;
    % var{i} = output.massFlowMeOHWaterInCycle;
end






%% Diagramme

numHoursToSimulate = 24;
numOptimizationHorizon = 24*5;

figure


counter = 1;
sumMethanolProduced = 0;
legendTxt = [];
for i = 1:12%size(var,2)

    sumMethanolProduced = sumMethanolProduced + sum(var{i}(2:numHoursToSimulate+1));
    p(i) = plot([1 + numHoursToSimulate*(i-1):1 + numHoursToSimulate*(i-1) + numOptimizationHorizon - 1],var{i}(2:end),'LineWidth',2,'Color',[0 0.4470 0.7410],'LineStyle','-');
    ylabel("methanol in kg/h")
    %ylabel("power electrolyser in kWh")
    xlabel("time in h")
    xlim([0 numHoursToSimulate*i+numOptimizationHorizon])
    title("Iteration: " + i);
    hold on
    grid on

    if i == 1
        legendTxt = ["current schedule"];
        legend([p(i)]);
    else
        legendTxt = ["old schedule", "realised schedule", "current time", "current schedule"];
        legend(legendTxt);
    end

    drawnow
    frame = getframe(gcf);
    im{counter} = frame2im(frame);
    counter = counter + 1;

    delete(p(i));
    if i > 1
        %delete(o(i-1))
        o(i-1).HandleVisibility = 'off';
        r(i-1).HandleVisibility = 'off';
        delete(vline(i-1))
    end

    o(i) = plot([1 + numHoursToSimulate*(i-1):1 + numHoursToSimulate*(i-1) + numOptimizationHorizon - 1],var{i}(2:end),'LineWidth',2,'Color',[0.4660 0.6740 0.1880],'LineStyle','--');
    r(i) = plot([1 + numHoursToSimulate*(i-1):1 + numHoursToSimulate*(i-1) + numHoursToSimulate - 1],var{i}(2:numHoursToSimulate+1),'LineWidth',2,'Color',[0.6350 0.0780 0.1840],'LineStyle','-');
    

    vline(i) = xline(numHoursToSimulate*i,'k--');

    legendTxt = ["old schedule", "realised schedule", "current time"];
    legend(legendTxt);

    
    drawnow
    frame = getframe(gcf);
    im{counter} = frame2im(frame);
    counter = counter + 1;

    delete(p(i));

end

filename = "schedulingHorizon.gif"; % Specify the output file name
for i = 1:numel(im)
    [A,map] = rgb2ind(im{i},256);
    if i == 1
        imwrite(A,map,filename,"gif","LoopCount",Inf,"DelayTime",1);
    else
        imwrite(A,map,filename,"gif","WriteMode","append","DelayTime",1);
    end
end
