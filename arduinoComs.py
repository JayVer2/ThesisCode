import serial
import time


def setDuty(duty):
    arduino_port = 'COM8'
    baud_rate = 9600  

    # Initialize serial communication with the Arduino
    try:
        ser = serial.Serial(arduino_port, baud_rate, timeout=1)
        time.sleep(2)  # Wait for Arduino to initialize
        print(f"Connected to Arduino on port {arduino_port}")
    except serial.SerialException:
        print(f"Could not open port {arduino_port}")
        exit()

    response = ser.readline().decode('utf-8').strip()
    if response:
        print(f"Arduino says: {response}")

    # Send the duty cycle value to the Arduino
    ser.write(f"{duty}\n".encode())  # Send as bytes with a newline character
    print(f"Duty cycle {duty} sent to Arduino.")

    # Optional: Read the confirmation from the Arduino
    response = ser.readline().decode('utf-8').strip()
    if response:
        print(f"Arduino says: {response}")

    # Close the serial connection
    ser.close()
    print("Serial connection closed.")
