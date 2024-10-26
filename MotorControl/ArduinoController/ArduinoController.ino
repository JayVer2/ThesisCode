// Include required libraries
#include <SoftwareSerial.h>
#include "RoboClaw.h"

// SoftwareSerial pins for RoboClaw communication (pins 10 and 11)
SoftwareSerial serial(10, 11);
RoboClaw roboclaw(&serial, 10000); // Timeout of 10 seconds

#define address 0x80 // Default address for RoboClaw

// PID constants (adjust these values based on tuning)
double Kp = 0.0;   // Reduce proportional gain
double Ki = 0.005;      // Keep integral gain at 0 for now
double Kd = 0.1;     // Increase derivative gain for more damping

// PID variables
double error = 0;
double previous_error = 0;
double integral = 0;
double derivative;
double output;

// Timing variables
unsigned long currentTime = 0;
unsigned long previousTime = 0;
double deltaTime = 0.0;

// Voltage and position variables
double V_initial = 0.0;
double V_current = 0.0;
double deltaV = 0.0;
double deltaX = 0;
double deltaX_previous = 0;
double deltaV_per_mm = 5.24 / 25.4;  // Voltage change per mm

// Velocity variables
double actual_velocity = 0.0;

// Travel distance limit (in mm)
double travelLimit = 25.4;

// Control loop duration (adjust as needed)
unsigned long controlLoopDuration = 3000;  // in milliseconds

// Define the maximum number of iterations for storing data
#define MAX_ITERATIONS 150

// Arrays to store data during the control loop
float velocity_data[MAX_ITERATIONS];
float voltage_data[MAX_ITERATIONS];

// Counter for storing loop iterations
int iteration = 0;

void setup() {
  // Initialize serial communication with the PC
  Serial.begin(9600);

  // Initialize serial communication with the RoboClaw
  roboclaw.begin(38400);

  // Initialize analog input pin for LVDT (assuming A0)
  pinMode(A0, INPUT);

  // Print a message to indicate readiness
  Serial.println("Arduino is ready to receive the desired velocity value.");
}

double calculateInitialDutyCycle(double desired_velocity) {
  // Coefficients from the provided equation
  double slope = 75.1;
  double intercept = 4296.74;

  // Calculate and return the initial duty cycle based on the desired velocity
  return (slope * desired_velocity + intercept);
  // return 0;
}

void loop() {
  // Check if data is available from the PC
  if (Serial.available() > 0) {
    // Read the incoming string until a newline character
    String inputString = Serial.readStringUntil('\n');

    // Remove any leading/trailing whitespace
    inputString.trim();

    // Convert the string to a double (desired velocity in mm/s)
    double desired_velocity = inputString.toDouble();

    // Wait briefly if necessary (adjust delay as needed)
    delay(100);

    // Calculate the initial duty cycle based on the desired velocity
    int initial_duty = calculateInitialDutyCycle(desired_velocity);
    int previous_duty = initial_duty;
    Serial.print("Desired vel: ");
    Serial.println(desired_velocity);
    Serial.println(initial_duty);

    // Send the initial duty cycle to the RoboClaw before PID refinement
    roboclaw.DutyM1(address, initial_duty);

    // Initialize variables before starting the control loop
    previousTime = millis() - 10;  // Ensure deltaTime is at least 10 ms
    previous_error = 0;
    integral = 0;
    deltaX_previous = 0;

    // Record the start time of the control loop
    unsigned long controlLoopStartTime = millis();

    // Read initial voltage
    int analogValue = analogRead(A0);
    V_initial = analogValue * (5.0 / 1023.0);

    // Reset iteration counter
    iteration = 0;

    // Start the control loop
    bool reachedLimit = false;
    while (!reachedLimit && (millis() - controlLoopStartTime) < controlLoopDuration && iteration < MAX_ITERATIONS) {

      // Read current time and calculate deltaTime
      currentTime = millis();
      deltaTime = (currentTime - previousTime) / 1000.0;  // Convert to seconds

      // Prevent division by zero
      if (deltaTime <= 0) {
        deltaTime = 0.001;  // Minimum deltaTime of 1 ms
      }

      // Read current voltage from LVDT
      analogValue = analogRead(A0);
      V_current = analogValue * (5.0 / 1023.0);

      // Calculate change in voltage
      deltaV = V_initial - V_current;  // Reverse the sign to treat decreasing voltage as forward movement

      // Convert deltaV to deltaX (position change in mm)
      deltaX = deltaV * (25.4 / 5.24);  // Based on your linear relationship

      // Calculate actual velocity (mm/s)
      actual_velocity = (deltaX - deltaX_previous) / deltaTime;

      // Calculate PID error terms
      error = desired_velocity - actual_velocity;
      integral += error * deltaTime;
      derivative = (error - previous_error) / deltaTime;

      // Compute PID output
      output = Kp * error + Ki * integral + Kd * derivative;

      // Modify the current duty cycle by adding the PID output
      int duty = previous_duty + (int)output;

      // Limit duty cycle to max values to prevent saturation
      if (duty > 32767) duty = 32767;
      if (duty < -32767) duty = -32767;

      // Send the new duty cycle command to the RoboClaw
      roboclaw.DutyM1(address, duty);

      // Store the current duty cycle for the next loop
      previous_duty = duty;

      // Update previous variables for next iteration
      previousTime = currentTime;
      previous_error = error;
      deltaX_previous = deltaX;

      // Check if the motor has traveled the full 25.4mm distance
      if (deltaX >= travelLimit || (deltaX >= (travelLimit / 2) && abs(actual_velocity) < 0.01)) {
        // break;
        // Exit the loop after starting reverse motion
        reachedLimit = true;
      }

      // Save data to arrays
      velocity_data[iteration] = actual_velocity;
      voltage_data[iteration] = V_current;

      iteration++;  // Move to the next iteration
    }

    // Set duty cycle to zero and stop the motor
    roboclaw.DutyM1(address, 0);
    Serial.println("Reached limit, stopping motor.");

    // Wait for 2 seconds
    delay(1000);

    // Apply a duty of -15000 to move in the other direction
    int reverseDuty = -15000;
    roboclaw.DutyM1(address, reverseDuty);
    Serial.println("Reversing motor with duty cycle -15000.");

    delay(2500);

    // After control loop ends, stop the motor
    roboclaw.DutyM1(address, 0);

    // Print all data after the control loop ends
    for (int i = 0; i < iteration; i++) {
      Serial.print(velocity_data[i]);
      Serial.print(",");
      Serial.println(voltage_data[i]);
    }

    // Reset all variables to initial state after the loop ends
    error = 0;
    previous_error = 0;
    integral = 0;
    derivative = 0;
    output = 0;
    deltaTime = 0.0;
    deltaX = 0;
    deltaX_previous = 0;
    actual_velocity = 0.0;
    V_initial = analogRead(A0) * (5.0 / 1023.0);  // Reset initial voltage

    // Print a message indicating readiness for new input
    Serial.println("Arduino is ready to receive the next desired velocity value.");
  }

  // Small delay to prevent overwhelming the loop
  delay(10);
}

