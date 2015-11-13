// CONNECTION 
//LINKBOT_FUNCTION(connect, "Connect to the Linkbot." )
//LINKBOT_FUNCTION(disconnect, "Disconnect from the Linkbot." )

// MOVEMENT
LINKBOT_FUNCTION(drive, 
"Move the motors by a relative position using the PID controller." )
LINKBOT_FUNCTION(driveTo,
"Move the motors to an absolute position using the PID controller.")
LINKBOT_FUNCTION(move,
"Move the motors by a relative position at a constant velocity. \n\n"
"The velocity may be set by the \"setJointSpeeds()\" function.")
LINKBOT_FUNCTION(moveContinuous, "stub")
LINKBOT_FUNCTION(moveTo, "stub")
LINKBOT_FUNCTION(motorPower, "stub")
LINKBOT_FUNCTION(stop, "stub")
LINKBOT_FUNCTION(moveSmooth, "Move motor(s) with smooth accel/decel at the \n"
"beginning and end of the motion.")
LINKBOT_FUNCTION(moveAccel, "Accelerate the joints at a specified rate.")

// GETTERS
LINKBOT_FUNCTION(getAccelerometer, "stub")
//LINKBOT_FUNCTION(getAdcRaw, "stub")
//LINKBOT_FUNCTION(getAdcRaw2, "stub")
LINKBOT_FUNCTION(getBatteryVoltage, "stub")
LINKBOT_FUNCTION(getFormFactor, "stub")
LINKBOT_FUNCTION(getJointAngles, "stub")
LINKBOT_FUNCTION(getJointSpeeds, "stub")
LINKBOT_FUNCTION(getJointStates, "stub")
LINKBOT_FUNCTION(getLedColor, "stub")
LINKBOT_FUNCTION(getVersions, "stub")
LINKBOT_FUNCTION(getJointSafetyAngles, "stub")
LINKBOT_FUNCTION(getJointSafetyThresholds, "stub")

// SETTERS
LINKBOT_FUNCTION(resetEncoderRevs, "stub")
LINKBOT_FUNCTION(setLedColor, "stub")
LINKBOT_FUNCTION(setJointSpeeds, "stub")
LINKBOT_FUNCTION(setBuzzerFrequency, "stub")
LINKBOT_FUNCTION(setJointSafetyThresholds, "stub")
LINKBOT_FUNCTION(setJointSafetyAngles, "stub")
LINKBOT_FUNCTION(setJointAccelI, "stub")
LINKBOT_FUNCTION(setJointAccelF, "stub")

// CALLBACKS
LINKBOT_FUNCTION(setAccelerometerEventCallback, "stub")
LINKBOT_FUNCTION(setButtonEventCallback, "stub")
LINKBOT_FUNCTION(setEncoderEventCallback, "stub")
LINKBOT_FUNCTION(setJointEventCallback, "stub")

// MISC
LINKBOT_FUNCTION(writeEeprom, "stub")
LINKBOT_FUNCTION(readEeprom, "stub")
LINKBOT_FUNCTION(writeTwi, "stub")
LINKBOT_FUNCTION(readTwi, "stub")
LINKBOT_FUNCTION(writeReadTwi, "stub")
