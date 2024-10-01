

d = daq("mcc");

addinput(d,"Board0","Ai0","Voltage");

addinput(d,"Board0","Ai1","Voltage");

addinput(d,"Board0","Ai2","Voltage");

d.Rate = 20000;

ADC_out = read(d,seconds(0.5));
x = mean(ADC_out.Board0_Ai0); %X-axis
y = mean(ADC_out.Board0_Ai1); %Y-axis
z = mean(ADC_out.Board0_Ai2); %Z-axis


plot(ADC_out.Time, ADC_out.Variables)
xlabel("Time (s)")
ylabel("Amplitude")
% ylim([-5.5 5])
legend(ADC_out.Properties.VariableNames, "Interpreter", "none")

clear d


%% Process all data
Fx = (ADC_out.Board0_Ai0).*4; %X-axis
Fy = (ADC_out.Board0_Ai1).*4; %Y-axis
Fz = (ADC_out.Board0_Ai2).*4; %Z-axis


