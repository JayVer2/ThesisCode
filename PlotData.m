clear 
close all
clc

adcDataFile = 'results/humanSkin/90deg-22G1-50/adc_data.csv';

% Load the ADC data from the CSV file
adcData = readmatrix(adcDataFile);
t = adcData(:, 1);  % First column: timestamps
ch0 = adcData(:, 2);         % Second column: CH0 data
ch1 = adcData(:, 3);         % Third column: CH1 data
ch2 = adcData(:, 4);         % Fourth column: CH2 data

% Define x-limits for the time range
x_limits = [0.95, 1.14];

% Find the indices that correspond to the x-limits
idx = t >= x_limits(1) & t <= x_limits(2);

% Apply x-limits to the time and channel data
t = t(idx);
ch0 = ch0(idx);
ch1 = ch1(idx);
ch2 = ch2(idx);

% Number of initial data points to average for zeroing
numPointsToZero = 5;

% Calculate the mean of the first few data points for each axis
ch0_offset = mean(ch0(1:numPointsToZero));
ch1_offset = mean(ch1(1:numPointsToZero));
ch2_offset = mean(ch2(1:numPointsToZero));

% Subtract the calculated offsets from each channel to zero the data
ch0 = ch0 - ch0_offset;
ch1 = ch1 - ch1_offset;
ch2 = ch2 - ch2_offset;

Fx = ch0.*4; % X-axis
Fy = ch1.*4; % Y-axis
Fz = ch2.*4; % Z-axis

figure(1);
hold on
subplot(1,3,1);
plot(t, Fx,'r', t, Fy,'g', t, Fz, 'b');
xlim([0.95 1.14])
ylim([-0.1 0.45])
xlabel('Time (s)');
ylabel('Force (N)');
title("100mm/s Data");
legend('Fx','Fy','Fz');
FormatNice


%% 200mms

adcDataFile = 'results/TestRound1/30deg-20G1-200mms/adc_data.csv';

% Load the ADC data from the CSV file
adcData = readmatrix(adcDataFile);
t = adcData(:, 1);  % First column: timestamps
ch0 = adcData(:, 2);         % Second column: CH0 data
ch1 = adcData(:, 3);         % Third column: CH1 data
ch2 = adcData(:, 4);         % Fourth column: CH2 data

% Define x-limits for the time range
x_limits = [0.95, 1.06];

% Find the indices that correspond to the x-limits
idx = t >= x_limits(1) & t <= x_limits(2);

% Apply x-limits to the time and channel data
t = t(idx);
ch0 = ch0(idx);
ch1 = ch1(idx);
ch2 = ch2(idx);

% Number of initial data points to average for zeroing
numPointsToZero = 5;

% Calculate the mean of the first few data points for each axis
ch0_offset = mean(ch0(1:numPointsToZero));
ch1_offset = mean(ch1(1:numPointsToZero));
ch2_offset = mean(ch2(1:numPointsToZero));

% Subtract the calculated offsets from each channel to zero the data
ch0 = ch0 - ch0_offset;
ch1 = ch1 - ch1_offset;
ch2 = ch2 - ch2_offset;

Fx = ch0.*4; % X-axis
Fy = ch1.*4; % Y-axis
Fz = ch2.*4; % Z-axis

figure(1);
hold on
subplot(1,3,2);
plot(t, Fx,'r', t, Fy,'g', t, Fz, 'b');
xlim([0.95 1.06])
ylim([-0.1 0.45])
xlabel('Time (s)');
ylabel('Force (N)');
title("200mm/s Data");
FormatNice


%% 300mms

adcDataFile = 'results/TestRound1/30deg-20G1-300mms/adc_data.csv';

% Load the ADC data from the CSV file
adcData = readmatrix(adcDataFile);
t = adcData(:, 1);  % First column: timestamps
ch0 = adcData(:, 2);         % Second column: CH0 data
ch1 = adcData(:, 3);         % Third column: CH1 data
ch2 = adcData(:, 4);         % Fourth column: CH2 data

% Define x-limits for the time range
x_limits = [0.95, 1.05];

% Find the indices that correspond to the x-limits
idx = t >= x_limits(1) & t <= x_limits(2);

% Apply x-limits to the time and channel data
t = t(idx);
ch0 = ch0(idx);
ch1 = ch1(idx);
ch2 = ch2(idx);

% Number of initial data points to average for zeroing
numPointsToZero = 5;

% Calculate the mean of the first few data points for each axis
ch0_offset = mean(ch0(1:numPointsToZero));
ch1_offset = mean(ch1(1:numPointsToZero));
ch2_offset = mean(ch2(1:numPointsToZero));

% Subtract the calculated offsets from each channel to zero the data
ch0 = ch0 - ch0_offset;
ch1 = ch1 - ch1_offset;
ch2 = ch2 - ch2_offset;

Fx = ch0.*4; % X-axis
Fy = ch1.*4; % Y-axis
Fz = ch2.*4; % Z-axis

figure(1);
hold on
subplot(1,3,3);
plot(t, Fx,'r', t, Fy,'g', t, Fz, 'b');
xlim([0.95 1.05])
ylim([-0.1 0.45])
xlabel('Time (s)');
ylabel('Force (N)');
title("300mm/s Data");
FormatNice;