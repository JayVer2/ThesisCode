from __future__ import absolute_import, division, print_function
from builtins import *  # @UnusedWildImport

from ctypes import cast, POINTER, c_double, c_ushort, c_ulong
import time

from mcculw import ul
from mcculw.enums import ScanOptions
from mcculw.device_info import DaqDeviceInfo

try:
    from console_examples_util import config_first_detected_device
except ImportError:
    from .console_examples_util import config_first_detected_device


def ADC_Scan():
    use_device_detection = True
    dev_id_list = []
    board_num = 0
    rate = 20000  # 20,000 samples per second
    duration = 5  # Capture data for 2 seconds (change as needed)
    points_per_channel = round(rate * duration)
    memhandle = None

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

        scan_options = ScanOptions.FOREGROUND

        if ScanOptions.SCALEDATA in ai_info.supported_scan_options:
            scan_options |= ScanOptions.SCALEDATA
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

        # Start the scan
        ul.a_in_scan(board_num, low_chan, high_chan, total_count, rate, ai_range, memhandle, scan_options)

        print('Scan completed successfully. Data with timestamps:')

        # Store the data with timestamps
        data_with_timestamps = []
        # start_time = time.time()
        current_time = 0

        # Print the data with timestamps
        data_index = 0
        for index in range(points_per_channel):
            current_time = current_time + (1/rate)  # Calculate timestamp
            row_data = [current_time]  # Store the timestamp first
            for _ in range(num_chans):
                if ScanOptions.SCALEDATA in scan_options:
                    eng_value = ctypes_array[data_index]
                else:
                    eng_value = ul.to_eng_units(board_num, ai_range, ctypes_array[data_index])
                data_index += 1
                row_data.append(eng_value)
            data_with_timestamps.append(row_data)

        # Display the results (timestamp, channel data)
        print(f"{'Timestamp (s)':>15} {'CH0':>10} {'CH1':>10} {'CH2':>10} {'CH3':>10}")
        for row in data_with_timestamps:
            print(f"{row[0]:>15.5f} {row[1]:>10.3f} {row[2]:>10.3f} {row[3]:>10.3f} {row[4]:>10.3f}")

    except Exception as e:
        print('\n', e)
    finally:
        if memhandle:
            ul.win_buf_free(memhandle)
        if use_device_detection:
            ul.release_daq_device(board_num)


if __name__ == '__main__':
    ADC_Scan()
