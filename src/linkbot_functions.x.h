// CONNECTION 
LINKBOT_FUNCTION(connect, "Connect to the Linkbot." )
LINKBOT_FUNCTION(disconnect, "Disconnect from the Linkbot." )

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

// GETTERS
LINKBOT_FUNCTION(getAccelerometer, "stub")
LINKBOT_FUNCTION(getFormFactor, "stub")
LINKBOT_FUNCTION(getJointAngles, "stub")
LINKBOT_FUNCTION(getJointSpeeds, "stub")
LINKBOT_FUNCTION(getJointStates, "stub")
LINKBOT_FUNCTION(getLedColor, "stub")
LINKBOT_FUNCTION(getVersions, "stub")

// SETTERS
LINKBOT_FUNCTION(setLedColor, "stub")
LINKBOT_FUNCTION(setEncoderEventThreshold, "stub")
LINKBOT_FUNCTION(setJointSpeeds, "stub")
LINKBOT_FUNCTION(setJointStates, "stub")
LINKBOT_FUNCTION(setBuzzerFrequencyOn, "stub")

// CALLBACKS
LINKBOT_FUNCTION(setAccelerometerEventCallback, "stub")
LINKBOT_FUNCTION(setButtonEventCallback, "stub")
LINKBOT_FUNCTION(setEncoderEventCallback, "stub")
LINKBOT_FUNCTION(setJointEventCallback, "stub")