
from __future__ import absolute_import, division, print_function
from builtins import *  # @UnusedWildImport

from ctypes import cast, POINTER, c_double, c_ushort, c_ulong
import time
import csv

from mcculw import ul
from mcculw.enums import ScanOptions
from mcculw.device_info import DaqDeviceInfo

try:
    from console_examples_util import config_first_detected_device
except ImportError:
    from .console_examples_util import config_first_detected_device

# Initialization function to set up ADC and prepare for scanning
def initialize_ADC(duration):
    use_device_detection = True
    dev_id_list = []
    board_num = 0
    rate = 20000  # 20,000 samples per second
    points_per_channel = round(rate * duration)

    # Initialize variables that will be used across functions
    adc_settings = {
        'board_num': board_num,
        'rate': rate,
        'points_per_channel': points_per_channel,
        'memhandle': None,
        'total_count': None,
        'ctypes_array': None,
        'ai_range': None,
        'scan_options': ScanOptions.FOREGROUND
    }

    try:
        if use_device_detection:
            config_first_detected_device(board_num, dev_id_list)

        daq_dev_info = DaqDeviceInfo(board_num)
        if not daq_dev_info.supports_analog_input:
            raise Exception('Error: The DAQ device does not support analog input')

        print('\nActive DAQ device: ', daq_dev_info.product_name, ' (', daq_dev_info.unique_id, ')\n', sep='')

        ai_info = daq_dev_info.get_ai_info()
        low_chan = 0
        high_chan = min(3, ai_info.num_chans - 1)
        num_chans = high_chan - low_chan + 1
        total_count = points_per_channel * num_chans
        ai_range = ai_info.supported_ranges[0]

        # Set up the scan options
        if ScanOptions.SCALEDATA in ai_info.supported_scan_options:
            adc_settings['scan_options'] |= ScanOptions.SCALEDATA
            memhandle = ul.scaled_win_buf_alloc(total_count)
            ctypes_array = cast(memhandle, POINTER(c_double))
        elif ai_info.resolution <= 16:
            memhandle = ul.win_buf_alloc(total_count)
            ctypes_array = cast(memhandle, POINTER(c_ushort))
        else:
            memhandle = ul.win_buf_alloc_32(total_count)
            ctypes_array = cast(memhandle, POINTER(c_ulong))

        if not memhandle:
            raise Exception('Error: Failed to allocate memory')

        # Store initialized values in the dictionary
        adc_settings['memhandle'] = memhandle
        adc_settings['ctypes_array'] = ctypes_array
        adc_settings['total_count'] = total_count
        adc_settings['ai_range'] = ai_range
        adc_settings['num_chans'] = num_chans
        adc_settings['low_chan'] = low_chan
        adc_settings['high_chan'] = high_chan

        print('ADC initialized and ready for scan.')

        return adc_settings

    except Exception as e:
        print('\n', e)
        return None


# Function to start the scan with minimal latency
def start_scan(adc_settings, csv_path):
    try:
        # Start the scan
        ul.a_in_scan(
            adc_settings['board_num'], 
            adc_settings['low_chan'], 
            adc_settings['high_chan'], 
            adc_settings['total_count'], 
            adc_settings['rate'], 
            adc_settings['ai_range'], 
            adc_settings['memhandle'], 
            adc_settings['scan_options']
        )

        print('Scan started successfully.')

        # Open a CSV file to save timestamps and the first three channels
        with open(csv_path, mode='w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            # Write the header
            csv_writer.writerow(['Timestamp (s)', 'CH0', 'CH1', 'CH2'])

            current_time = 0
            data_index = 0
            rate = adc_settings['rate']
            num_chans = adc_settings['num_chans']
            ctypes_array = adc_settings['ctypes_array']

            # Store the data with timestamps
            for index in range(adc_settings['points_per_channel']):
                current_time += (1 / rate)  # Calculate timestamp
                row_data = [current_time]  # Store the timestamp

                # Add only the first three channels (ignore the fourth)
                for ch_num in range(3):  # CH0, CH1, CH2
                    eng_value = ctypes_array[data_index]
                    data_index += 1
                    row_data.append(eng_value)

                # Skip the fourth channel (CH3)
                data_index += 1  # Skip CH3

                # Write the timestamp and the first three channels to the CSV
                csv_writer.writerow(row_data)

        print(f"Data successfully saved to {csv_path}")

    except Exception as e:
        print('\n', e)
    finally:
        if adc_settings['memhandle']:
            ul.win_buf_free(adc_settings['memhandle'])


