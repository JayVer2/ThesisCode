// Includes required to use RoboClaw library
#include <SoftwareSerial.h>
#include "RoboClaw.h"

// SoftwareSerial pins for RoboClaw communication (pins 10 and 11)
SoftwareSerial serial(10, 11);
RoboClaw roboclaw(&serial, 10000); // Timeout of 10 seconds

#define address 0x80 // Default address for RoboClaw

void setup() {
  // Initialize serial communication with the PC
  Serial.begin(9600); // Must match the baud rate in the Python script

  // Initialize serial communication with the RoboClaw
  roboclaw.begin(38400); // Default baud rate for RoboClaw

  // Print a message to indicate readiness
  Serial.println("Arduino is ready to receive the duty cycle value.");
}

void loop() {
  // Check if data is available from the PC
  roboclaw.DutyM1(address, 0);

  if (Serial.available() > 0) {
    // Read the incoming string until a newline character
    String inputString = Serial.readStringUntil('\n');

    // Remove any leading/trailing whitespace
    inputString.trim();

    // Convert the string to an integer
    int duty = inputString.toInt();

    delay(2500); //Add small delay to give camera and force sensors time to start up
    // Validate the duty cycle value (-32767 to 32767)
    if (duty < -32767) duty = -32767;
    if (duty > 32767) duty = 32767;

    // Send the duty cycle command to the RoboClaw
    roboclaw.DutyM1(address, duty);

    // Optional: Send a confirmation back to the PC
    Serial.print("Duty cycle set to: ");
    Serial.println(duty);

    delay(7000); //Wait 5 seconds for needle to pierce tissue
    //Retract needle
    duty = -12000;
    // Send the duty cycle command to the RoboClaw
    roboclaw.DutyM1(address, duty);
    delay(5000); //Wait for it to retract
  }

  // Optional: Add a small delay to prevent overwhelming the loop
  delay(100);
}



