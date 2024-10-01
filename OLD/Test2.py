import serial

# Open serial connection (adjust the COM port and baud rate)
ser = serial.Serial('COM5', 9600)  # Replace 'COM3' with the appropriate port

# Send the serial command to trigger snapshot
ser.write(b'f')  # Example command to trigger a frame capture

# Optionally read the response
response = ser.read(100)  # Read up to 10 bytes
print(response)

# Close the serial connection
ser.close()
