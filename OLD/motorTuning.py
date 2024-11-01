import serial
import time
import matplotlib.pyplot as plt

# Set up the Arduino connection
arduino_port = 'COM8'
baud_rate = 9600  # Must match the Arduino Serial baud rate

# Initialize serial communication with the Arduino
try:
    ser = serial.Serial(arduino_port, baud_rate, timeout=1)
    time.sleep(2)  # Wait for Arduino to initialize
    print(f"Connected to Arduino on port {arduino_port}")
except serial.SerialException:
    print(f"Could not open port {arduino_port}")
    exit()

# Function to send the desired velocity to the Arduino
def send_velocity(velocity):
    ser.write(f"{velocity}\n".encode())  # Send as bytes with a newline character
    print(f"Velocity {velocity} mm/s sent to Arduino.")

# Set the desired velocity
desired_velocity = 40.0  # Change this value as needed
send_velocity(desired_velocity)

# Initialize lists to store the data for plotting
time_data = []
velocity_data = []
voltage_data = []
duty_cycle_data = []
error_data = []
loop_duration_data = []  # To store loop durations

start_time = time.time()

# Loop to read data from Arduino and store it
try:
    while True:
        # Read data from Arduino
        line = ser.readline().decode('utf-8').strip()
        if line:
            try:
                # Parse the line as comma-separated values (velocity, voltage, duty cycle, error, loop duration)
                current_time = time.time() - start_time
                velocity, voltage = map(float, line.split(','))

                # Update data lists
                time_data.append(current_time)
                velocity_data.append(velocity)
                voltage_data.append(voltage)

            except ValueError:
                print(f"Error parsing data: {line}")
except KeyboardInterrupt:
    print("Plotting stopped by user.")
finally:
    # Close the serial connection in the "finally" block to ensure it's always closed
    ser.close()
    print("Serial connection closed.")

# Plot the data after collection
plt.figure(figsize=(8, 14))

# Velocity vs Time
plt.subplot(2, 1, 1)
plt.plot(time_data, velocity_data, 'r-')
plt.title('Velocity vs Time')
plt.xlabel('Time (s)')
plt.ylabel('Velocity (mm/s)')

# Voltage vs Time
plt.subplot(2, 1, 2)
plt.plot(time_data, voltage_data, 'b-')
plt.title('Analog Voltage vs Time')
plt.xlabel('Time (s)')
plt.ylabel('Voltage (V)')

print(voltage_data)
print(velocity_data)

# Show the plot
plt.tight_layout()
plt.show()
