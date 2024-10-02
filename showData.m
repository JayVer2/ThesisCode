clear
clc
close all
% Call the function to play the video and display ADC data with UI controls
play_video_and_adc('results/', 'results/adc_data.csv');

function play_video_and_adc(folderPath, adcDataFile)
    % Find the first .mp4 file in the given folder
    mp4Files = dir(fullfile(folderPath, '*.mp4'));
    if isempty(mp4Files)
        error('No .mp4 files found in the folder.');
    end

    % Use the first .mp4 file found
    videoFile = fullfile(folderPath, mp4Files(1).name);
    disp(['Playing video file: ', videoFile]);

    % Load the ADC data from the CSV file
    adcData = readmatrix(adcDataFile);
    timestamps = adcData(:, 1);  % First column: timestamps
    ch0 = adcData(:, 2);         % Second column: CH0 data
    ch1 = adcData(:, 3);         % Third column: CH1 data
    ch2 = adcData(:, 4);         % Fourth column: CH2 data
    Fx = ch0.*4; % X-axis
    Fy = ch1.*4; % Y-axis
    Fz = ch2.*4; % Z-axis

    % Set up the video player
    vidObj = VideoReader(videoFile);
    frameRate = vidObj.FrameRate;
    videoDuration = vidObj.Duration;  % Duration of the video in seconds

    % Set up the figure for video and ADC plot
    fig = figure('Name', 'Video and ADC Data', 'KeyPressFcn', @keyPressCallback);

    % Create a subplot for the video
    hVideo = subplot(1, 2, 1);
    vidFrame = readFrame(vidObj);  % Read the first frame
    hImage = imshow(vidFrame, 'Parent', hVideo);
    title(hVideo, 'Video Playback');

    % Create a subplot for the ADC data
    hADC = subplot(1, 2, 2);
    plot(timestamps, Fx, 'r', timestamps, Fy, 'g', timestamps, Fz, 'b');
    title(hADC, 'ADC Data');
    xlabel('Time (s)');
    ylabel('Force Readings');
    ylim([-20 20])
    legend('X-axis (CH0)', 'Y-axis (CH1)', 'Z-axis (CH2)');

    % Create a vertical line to indicate the current time in the ADC plot
    hold on;
    vLine = xline(0, '--k', 'LineWidth', 2);  % Initial position at t=0
    hold off;

    % Global variable to control playback state
    global isPlaying;
    isPlaying = true;

    % Create UI controls for Play, Pause, and Rewind
    uicontrol('Style', 'pushbutton', 'String', 'Play', ...
        'Position', [20 20 50 20], 'Callback', @playCallback);
    uicontrol('Style', 'pushbutton', 'String', 'Pause', ...
        'Position', [80 20 50 20], 'Callback', @pauseCallback);
    uicontrol('Style', 'pushbutton', 'String', 'Rewind', ...
        'Position', [140 20 50 20], 'Callback', @rewindCallback);

    % Set up a timer to match the video frame rate
    timerPeriod = max(1/frameRate, 0.001);  % Ensure minimum 1 ms period
    videoTimer = timer('ExecutionMode', 'fixedRate', 'Period', timerPeriod, ...
                       'TimerFcn', @(~,~) updateFrame());

    % Start the video playback and ADC synchronization
    start(videoTimer);

    % Nested function to update the video frame and the ADC line
    function updateFrame()
        if isPlaying && hasFrame(vidObj)
            % Update the video frame
            vidFrame = readFrame(vidObj);
            set(hImage, 'CData', vidFrame);

            % Update the vertical line on the ADC plot
            currentTime = vidObj.CurrentTime;  % Get the current time of the video
            set(vLine, 'Value', currentTime);  % Move the vertical line
            drawnow;
        elseif ~hasFrame(vidObj)
            % If the video has ended, loop back to the beginning
            vidObj.CurrentTime = 0;  % Reset the video to the start
            set(vLine, 'Value', 0);  % Reset the vertical line to the start
            playCallback();  % Start playing again
        end
    end

    % Play button callback
    function playCallback(~, ~)
        isPlaying = true;  % Resume playback
    end

    % Pause button callback
    function pauseCallback(~, ~)
        isPlaying = false;  % Pause playback
    end

    % Rewind button callback
    function rewindCallback(~, ~)
        % Move the video back by 1 second (adjustable)
        newTime = max(0, vidObj.CurrentTime - 1);  % Rewind by 1 second, no negative time
        vidObj.CurrentTime = newTime;
        % Update the vertical line in the ADC plot
        set(vLine, 'Value', newTime);
    end

    % Callback function for key presses (optional: handle play/pause with spacebar)
    function keyPressCallback(~, event)
        switch event.Key
            case 'space'
                if isPlaying
                    pauseCallback();
                else
                    playCallback();
                end
        end
    end
end
