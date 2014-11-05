#!/usr/bin/env python

from linkbot import _linkbot as _L
import time
import threading
import functools

class Linkbot:
    '''
    The Linkbot class.

    Create a new Linkbot object by specifying the robot's Serial ID in the
    constructor. For instance::
        
        import linkbot
        myLinkbot = linkbot.Linkbot('ABCD')
        myLinkbot.connect()

    The previous snippet of code creates a new variable called "myLinkbot" which
    is connected to a physical robot with the serial ID "ABCD".
    '''
    class FormFactor:
        I = 0
        L = 1
        T = 2

    class JointStates:
        STOP = 0
        HOLD = 1
        MOVING = 2
        FAIL = 3

        def __init__(self):
            self._lock = threading.Condition()
            self._state = [self.STOP]*3

        def lock(self):
            self._lock.acquire()

        def unlock(self):
            self._lock.release()

        def state(self, index):
            return self._state[index]

        def set_state(self, index, state):
            self._state[index] = state
            self._lock.notify_all()

        def wait(self, timeout=None):
            self._lock.wait(timeout)

    def __init__(self, serialId):
        _L.linkbotPythonInit()
        self.__impl = _L.linkbotNew(serialId)
        self._jointStates = Linkbot.JointStates()
        self.__accelCb = None
        self.__encoderCb = None
        self.__jointCb = None
        self.__buttonCb = None
        time.sleep(2)

# Connection

    def connect(self):
        '''
        Connect to the robot.
        '''
        # Enable joint event callbacks
        _L.linkbotConnect(self.__impl)
        self._formFactor = self.getFormFactor()
        if self._formFactor == Linkbot.FormFactor.I:
            self._motorMask = 0x05
        elif self._formFactor == Linkbot.FormFactor.L:
            self._motorMask = 0x03
        elif self._formFactor == Linkbot.FormFactor.T:
            self._motorMask = 0x07
        else:
            self._motorMask = 0x01
        self.enableJointEvents()

    def disconnect(self):
        '''
        Disconnect from the robot.
        '''
        _L.linkbotDisconnect(self.__impl)

# Getters

    def getAccelerometerData(self):
        '''
        Get the current accelerometer readings. 

        Example::

            x, y, z = robot.getAccelerometerData()

        @rtype: (number, number, number)
        @return: A list of acceleration values in the x, y, and z directions. 
                 Accelerometer values are in units of "G's", where 1 G
                 is standard earth gravitational acceleration (9.8m/s/s) 
        '''
        values = _L.linkbotGetAccelerometer(self.__impl)
        assert(values[0] == 0)
        return tuple(values[2:])

    def getFormFactor(self):
        '''
        Get the robot's form factor. 

        @rtype: linkbot.Linkbot.FormFactor()
        @return: A number indicating the form factor. An enumeration class 
                 called Linkbot.FormFactor is available. The return value is one
                 of:
                    - 0 -> Linkbot-I
                    - 1 -> Linkbot-L
                    - 2 -> Linkbot-T
        '''
        values = _L.linkbotGetFormFactor(self.__impl)
        assert(values[0] == 0)
        return values[1]

    def getJointAngles(self):
        '''
        Get the current joint angles of the robot.

        @rtype: (number, number, number)
        @return: Returned values are in degrees. The three values indicate the
                 joint angles for joints 1, 2, and 3 respectively. Values
                 for joints which are not movable (i.e. joint 2 on a Linkbot-I)
                 are always zero.
        '''
        values = _L.linkbotGetJointAngles(self.__impl)
        assert(values[0] == 0)
        return tuple(values[2:])

    def getJointStates(self):
        '''
        Get the movement state for each of the joints.

        @rtype: (Linkbot.JointStates, Linkbot.JointStates, Linkbot.JointStates)
        '''
        values = _L.linkbotGetJointStates(self.__impl)
        assert(values[0] == 0)
        return tuple(values[2:])

    def getLedColor(self):
        '''
        Get the current color of the Linkbot's multi-color LED.

        @rtype: (number, number, number)
        @return: Each value in the returned tuple is the intensity of the red,
                 green, and blue channels, respectively. Each value is a number
                 between 0 - 255.
        '''
        values = _L.linkbotGetLedColor(self.__impl)
        assert(values[0] == 0)
        return tuple(values[1:])

# Setters
    def setBuzzerFrequency(self, freq):
        '''
        Set the Linkbot's buzzer frequency. Setting the frequency to zero turns
        off the buzzer.

        @param freq: The frequency to set the buzzer, in Hertz.
        '''
        rc = _L.linkbotSetBuzzerFrequencyOn(self.__impl, freq)
        assert(rc == 0)

    def setJointSpeed(self, jointNo, speed):
        '''
        Set the speed for a single joint on the robot.

        @param jointNo: The joint to set the speed. Should be 1, 2, or 3.
        @param speed: The requested speed of the joint, in degrees/second.
        '''
        self.setJointSpeeds(speed, speed, speed, 1<<(jointNo-1))

    def setJointSpeeds(self, s1, s2, s3, mask=0x07):
        '''
        Set the speed of each joint on the robot. 

        @param s1, s2, s3: The requested speed of each joint, in degrees/second.
            The values should be in the range (-200, 200). Negative speeds
            indicate that the joint will move in the negative direction when
            using the "moveContinuous()" function, but all other movement
            functions will use the absolute value of the speed.
        '''
        rc = _L.linkbotSetJointSpeeds(self.__impl, mask, s1, s2, s3)
        assert(rc == 0)

# Movement
    def drive(self, j1, j2, j3, mask=0x07):
        self.driveNB(j1, j2, j3, mask)
        self.moveWait(mask)

    def driveNB(self, j1, j2, j3, mask=0x07):
        rc = _L.linkbotDrive(self.__impl, mask, j1, j2, j3)
        assert(rc == 0)

    def driveJoint(self, jointNo, angle):
        self.driveJointNB(jointNo, angle)
        self.moveWait(1<<(jointNo-1))

    def driveJointNB(self, jointNo, angle):
        self.driveNB(angle, angle, angle, 1<<(jointNo-1))

    def driveJointTo(self, jointNo, angle):
        self.driveJointToNB(jointNo, angle)
        self.moveWait(1<<(jointNo))

    def driveJointToNB(self, jointNo, angle):
        self.driveToNB(angle, angle, angle, 1<<(jointNo-1))

    def driveTo(self, j1, j2, j3, mask=0x07):
        self.driveToNB(j1, j2, j3, mask)
        self.moveWait(mask)
        
    def driveToNB(self, j1, j2, j3, mask=0x07):
        rc = _L.linkbotDriveTo(self.__impl, mask, j1, j2, j3)
        assert(rc == 0)
    
    def move(self, j1, j2, j3, mask=0x07):
        '''
        Move the joints on a robot and wait until all movements are finished.

        robot.move(90, 0, -90) # Drives Linkbot-I forward by turning wheels
                               # 90 degrees
        '''
        self.moveNB(j1, j2, j3, mask)
        self.moveWait(mask)

    def moveNB(self, j1, j2, j3, mask=0x07):
        '''
        Move the joints on a robot and wait until all movements are finished.

        This function returns as soon as the joints begin moving.

        # The following code makes a Linkbot-I change its LED color to red and
        # then blue while it is rolling forward.
        robot.moveNB(90, 0, -90)
        robot.setLedColor(255, 0, 0)
        time.sleep(0.5)
        robot.setLEDColor(0, 0, 255)

        '''
        rc = _L.linkbotMove(self.__impl, mask, j1, j2, j3)
        assert(rc == 0)

    def moveContinuous(self, dir1, dir2, dir3, mask=0x07):
        '''
        This function makes the joints on a robot begin moving continuously,
        "forever". 

        @param dir1, dir2, dir3: These parameters should be members of the
            Linkbot.JointStates class. They should be one of:
                - Linkbot.JointStates.STOP : Stop and relax the joint wherever
                  it is.
                - Linkbot.JointStates.HOLD : Stop and make the joint stay at its
                  current position.
                - Linkbot.JointStates.MOVING : Begin moving the joint at
                  whatever speed the joint was last set to with the
                  setJointSpeeds() function.
        '''
        rc = _L.linkbotMoveContinuous(mask, dir1, dir2, dir3)
        assert(rc == 0)

    def moveJoint(self, jointNo, angle):
        '''
        Move a single joint and wait for the motion to finish.

        # The following code moves joint 1 90 degrees, and then moves joint 3 90
        # degrees after joint 1 has stopped moving.
        robot.moveJoint(1, 90)
        robot.moveJoint(3, 90)
        '''
        assert (jointNo >= 1 and jointNo <= 3)
        self.moveJointNB(jointNo, angle)
        self.moveWait(1<<(jointNo-1))

    def moveJointNB(self, jointNo, angle):
        '''
        Move a single joint. Returns after the joint begins moving.

        # The following code moves joint 1 90 degrees and moves joint 3 90
        # degrees simultaneously.
        robot.moveJointNB(1, 90)
        robot.moveJointNB(3, 90)
        '''
        assert (jointNo >= 1 and jointNo <= 3)
        mask = 1<<(jointNo-1)
        _L.linkbotMove(self.__impl, mask, angle, angle, angle)

    def moveJointWait(self, jointNo):
        '''
        Wait for a single joint to stop moving.
        '''
        assert(jointNo >= 1 and jointNo <=3)
        self.moveWait(1<<(jointNo-1))

    def moveWait(self, mask = 0x07):
        '''
        Wait for one or more joints to finish moving.

        If called with no arguments, wait for all joints to finish moving. The
        'mask' parameter is a bitmask and can be used to specify which joint(s)
        to wait for. i.e. 

        robot.moveWait(0x01) # Only wait for joint 1
        robot.moveWait(0x03) # 0x03 is 0b011 in binary, so wait for joints 1 and
                             # 2 to finish moving.
        '''
        mask = mask & self._motorMask
        self._jointStates.lock()
        states = _L.linkbotGetJointStates(self.__impl)[2:]
        for s,i in zip(states, range(len(states))):
            self._jointStates.set_state(i, s)

        for i in range(3):
            if (1<<i) & mask:
                while self._jointStates.state(i) == Linkbot.JointStates.MOVING:
                    self._jointStates.wait()
        self._jointStates.unlock()

    # CALLBACKS

    def disableAccelerometerEvents(self):
        rc = _L.linkbotUnsetPythonAccelerometerEventCallback(self.__impl)
        assert(rc == 0)

    def disableButtonEvents(self):
        rc = _L.linkbotUnsetPythonButtonEventCallback(self.__impl)
        assert(rc == 0)

    def disableEncoderEvents(self):
        rc = _L.linkbotUnsetPythonEncoderEventCallback(self.__impl)
        assert(rc == 0)

    def disableJointEvents(self):
        rc = _L.linkbotUnsetPythonJointEventCallback(self.__impl)
        assert(rc == 0)

    def enableAccelerometerEvents(self, cb=None):
        _L.linkbotSetPythonAccelerometerEventCallback(self.__impl,
            self.accelerometerEventCB)
        self.__accelCb = cb

    def enableEncoderEvents(self, granularity=20.0, cb=None):
        _L.linkbotSetPythonEncoderEventCallback(self.__impl, 
                                                granularity, 
                                                self.encoderEventCB)
        self.__encoderCb = cb

    def enableButtonEvents(self, cb=None):
        _L.linkbotSetPythonButtonEventCallback(self.__impl, self.buttonEventCB)
        self.__buttonCb = cb

    def enableJointEvents(self, cb=None):
        _L.linkbotSetPythonJointEventCallback(self.__impl, self.jointEventCB)
        self.__jointCb = cb

    def buttonEventCB(self, buttonNo, state, timestamp):
        if self.__buttonCb is not None:
            self.__buttonCb(buttonNo, state, timestamp)

    def encoderEventCB(self, jointNo, angle, timestamp):
        if self.__encoderCb is not None:
            self.__encoderCb(jointNo, angle, timestamp)

    def accelerometerEventCB(self, x, y, z, timestamp):
        if self.__accelCb is not None:
            self.__accelCb(x, y, z, timestamp)

    def jointEventCB(self, jointNo, state, timestamp):
        self._jointStates.lock()
        self._jointStates.set_state(jointNo, state)
        self._jointStates.unlock()
        if self.__jointCb is not None:
            self.__jointCb(jointNo, state, timestamp)

    def testCB(self):
        print('Test CB called.')
