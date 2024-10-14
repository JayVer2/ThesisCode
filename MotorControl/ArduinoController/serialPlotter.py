import serial
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Configure the serial port
ser = serial.Serial('COM8', 9600)  # Change 'COM3' to your Arduino port
ser.flush()

# Create a figure for plotting
fig, ax = plt.subplots()
xdata, ydata, setpoint_data = [], [], []

def animate(i):
    if ser.in_waiting > 0:
        line = ser.readline().decode('utf-8').rstrip()
        try:
            velocity, setpoint = map(float, line.split(","))
            xdata.append(i)
            ydata.append(velocity)
            setpoint_data.append(setpoint)
            ax.clear()
            ax.plot(xdata, ydata, label="Velocity (mm/s)")
            ax.plot(xdata, setpoint_data, label="Setpoint (mm/s)")
            ax.legend()
        except ValueError:
            pass

ani = animation.FuncAnimation(fig, animate, interval=100)
plt.xlabel('Time')
plt.ylabel('Velocity (mm/s)')
plt.show()
