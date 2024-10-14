import pyADC
import androidCam
import time



def main():

    results_path="C:/Users/jgver/Documents/University/Thesis/ThesisCode/results"

    # First, initialize the ADC (this part prepares the device and minimizes latency)
    adc_settings = pyADC.initialize_ADC(duration=1)

    cam = androidCam.Android_Recorder()
    cam.init()
    time.sleep(2) #Wait for camera to start and autofocus
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