#include "RoboClaw.h"
#include <SoftwareSerial.h>

// SoftwareSerial for Arduino Uno (pins 10 and 11)
SoftwareSerial roboSerial(10, 11); // RX, TX
RoboClaw roboclaw(&roboSerial, 10000); // Adjust timeout as needed

volatile unsigned long pulseCount = 0;

unsigned long lastTime = 0;
unsigned long lastPulseCount = 0;
unsigned long startTime = 0;
float velocity = 0.0;

float Kp = 0.5;         // Proportional gain
float Ki = 0.05;        // Integral gain
float Kd = 0.01;        // Derivative gain

float integral = 0.0;
float lastError = 0.0;

bool directionForward = true;

const float encoderResolution = 0.00125; // Encoder resolution in mm (1.25 µm)

void setup() {
  // Initialize serial communication for debugging
  Serial.begin(9600);

  // Initialize SoftwareSerial for RoboClaw
  roboSerial.begin(38400); // Default baud rate for RoboClaw

  // Set up the encoder pin as an input
  pinMode(2, INPUT_PULLUP);

  // Attach an interrupt to the encoder pin
  attachInterrupt(digitalPinToInterrupt(2), encoderISR, RISING);

  // Record the start time
  startTime = millis();
}

void loop() {
  unsigned long currentTime = millis();

  // Update every 100 ms
  if (currentTime - lastTime >= 100) {
    noInterrupts(); // Disable interrupts to read pulseCount safely
    unsigned long currentPulseCount = pulseCount;
    interrupts();   // Re-enable interrupts

    // Calculate pulses counted in the interval
    unsigned long pulses = currentPulseCount - lastPulseCount;
    lastPulseCount = currentPulseCount;

    // Calculate velocity in mm per second
    velocity = (pulses * encoderResolution * 1000.0) / (currentTime - lastTime);

    // Check if 10 seconds have passed and reverse the direction
    if (currentTime - startTime >= 10000) {
      directionForward = !directionForward;
      startTime = currentTime; // Reset the timer for the next direction change
      integral = 0; // Reset integral term when changing direction
    }

    // Set target velocity based on the current direction
    float setpoint = directionForward ? 20.0 : -20.0; // 10 mm/s speed (negative for reverse)

    // PID Control
    float error = setpoint - velocity;
    integral += error * (currentTime - lastTime) / 1000.0;
    float derivative = (error - lastError) / ((currentTime - lastTime) / 1000.0);
    float output = Kp * error + Ki * integral + Kd * derivative;
    lastError = error;

    // Convert PID output to duty cycle (-100 to 100)
    int dutyCycle = constrain((int)output, -100, 100);

    // Control the motor
    setMotorDuty(dutyCycle);

    // For debugging
    Serial.print(velocity);
    Serial.print(",");
    Serial.println(setpoint);


    lastTime = currentTime;
  }
}

void encoderISR() {
  pulseCount++;
}

void setMotorDuty(int dutyCycle) {
  // Map dutyCycle from -100 to 100 to -32767 to 32767
  int16_t duty = map(dutyCycle, -100, 100, -32767, 32767);

  // Ensure duty is within bounds
  duty = constrain(duty, -32767, 32767);

  // Send command to RoboClaw (address 0x80 by default)
  uint8_t address = 0x80;
  roboclaw.DutyM1(address, duty);
}
