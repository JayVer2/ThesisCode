import pyADC
import androidCam
import time
from arduinoComs import setDuty
import os


def main():

    results_path="C:/Users/jgver/Documents/University/Thesis/ThesisCode/results/humanSkinTest2/90deg-24G1-25"
    if not os.path.exists(results_path):
        os.makedirs(results_path)

    time.sleep(5)
    # desired_vel = 20
    # slope = 75.1
    
    # intercept = 4296.74
    # duty = slope * desired_vel + intercept

    # 20% duty approx 10-30mm/s
    # 50% duty approx 150mm/s
    # 100% duty approx 300-400mm/s
    duty = 0.25 * 32767

    if duty > 32767:
        duty = 32767
    # duty = 32767
    # duty = 6000
    #At 32767, took 0.067s
    #At 6000, took 1.12s

    duration = (0.0002)*(32767-duty)+2.0

    print(duty, duration)

    # First, initialize the ADC (this part prepares the device and minimizes latency)
    adc_settings = pyADC.initialize_ADC(duration)

    cam = androidCam.Android_Recorder()
    cam.init()
    time.sleep(2) #Wait for camera to start and autofocus

    #Start motor and scanners
    setDuty(duty)
    cam.Start()
    # Once initialized, we can trigger the scan as needed
    if adc_settings:
        csv_output_path = results_path+'/adc_data.csv'
        pyADC.start_scan(adc_settings, csv_output_path)

    cam.Stop()
    cam.Save(results_path)
    pass




if __name__ == '__main__':
    main()