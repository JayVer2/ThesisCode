
import usb.core
import usb.util
from PIL import Image
import numpy as np


from time import sleep
from mcculw import ul
from mcculw.enums import DigitalIODirection
from mcculw.device_info import DaqDeviceInfo

try:
    from console_examples_util import config_first_detected_device
except ImportError:
    from .console_examples_util import config_first_detected_device




def send_pulse(val):
    # By default, the example detects and displays all available devices and
    # selects the first device listed. Use the dev_id_list variable to filter
    # detected devices by device ID (see UL documentation for device IDs).
    # If use_device_detection is set to False, the board_num variable needs to
    # match the desired board number configured with Instacal.
    use_device_detection = True
    dev_id_list = []
    board_num = 0

    try:
        if use_device_detection:
            config_first_detected_device(board_num, dev_id_list)

        daq_dev_info = DaqDeviceInfo(board_num)
        if not daq_dev_info.supports_digital_io:
            raise Exception('Error: The DAQ device does not support '
                            'digital I/O')

        # print('\nActive DAQ device: ', daq_dev_info.product_name, ' (',
        #       daq_dev_info.unique_id, ')\n', sep='')

        dio_info = daq_dev_info.get_dio_info()

        # Find the first port that supports input, defaulting to None
        # if one is not found.
        port = next((port for port in dio_info.port_info if port.supports_output),
                    None)
        if not port:
            raise Exception('Error: The DAQ device does not support '
                            'digital output')

        # If the port is configurable, configure it for output.
        if port.is_port_configurable:
            ul.d_config_port(board_num, port.type, DigitalIODirection.OUT)

        port_value = val

        print('Setting', port.type.name, 'to', port_value)

        # Output the value to the port
        ul.d_out(board_num, port.type, port_value)

        # sleep(5)
        # ul.d_out(board_num, port.type, port_value)
        # sleep(5)
        # bit_num = 0
        # bit_value = 0
        # print('Setting', port.type.name, 'bit', bit_num, 'to', bit_value)

        # Output the value to the bit
        # ul.d_bit_out(board_num, port.type, bit_num, bit_value)
        
    except Exception as e:
        print('\n', e)
    finally:
        if use_device_detection:
            ul.release_daq_device(board_num)




# Find the camera
dev = usb.core.find(idVendor=0x0547, idProduct=0x1002)

# Ensure the device is found
if dev is None:
    raise ValueError('Camera not found')
else:
    print("Camera found")

# Set the windowing registers for a 200x200 window in the center
# Row Start: (1536 - 200) / 2 = 668 -> 0x029C
# Column Start: (2048 - 200) / 2 = 924 -> 0x039C
# Window Height: 200 -> 0x00C7 (register value = height - 1)
# Window Width: 200 -> 0x00C7 (register value = width - 1)

# # Write to Row Start Register (0x01)
# dev.ctrl_transfer(0x40, 0x01, 0x0001, 0x0000, b'\x02\x9C')

# # Write to Column Start Register (0x02)
# dev.ctrl_transfer(0x40, 0x01, 0x0002, 0x0000, b'\x03\x9C')

# # Write to Window Height Register (0x03)
# dev.ctrl_transfer(0x40, 0x01, 0x0003, 0x0000, b'\x00\xC7')

# # Write to Window Width Register (0x04)
# dev.ctrl_transfer(0x40, 0x01, 0x0004, 0x0000, b'\x00\xC7')


# Assuming Endpoint 2 (0x82) is the IN endpoint for image data
endpoint = 0x82
buffer_size = 2048 * 1536 * 3  # 200x200 pixels, 3 bytes per pixel for RGB

#Send trigger pulse
send_pulse(0xFF)
# Read the image data
raw_image_data = dev.read(endpoint, buffer_size, timeout=5000)
print(raw_image_data)
send_pulse(0x00)
# Convert raw image data to a numpy array and reshape it into an image
image_array = np.frombuffer(raw_image_data, dtype=np.uint8).reshape((2048, 1536, 3))

# Convert to a PIL Image
image = Image.fromarray(image_array, 'RGB')

# Save or display the image
image.show()  # To display
# image.save('captured_image.png')  # To save the image

print("Image captured and displayed.")








