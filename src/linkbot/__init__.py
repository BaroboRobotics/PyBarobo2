#!/usr/bin/env python3

from linkbot import _linkbot 

import time
import threading
import multiprocessing
import functools

class Linkbot (_linkbot.Linkbot):
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
            self._lock = multiprocessing.Condition()
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

    def __init__(self, serialId = 'LOCL'):
        _linkbot.Linkbot.__init__(self, serialId)
        self.__serialId = serialId
        self._jointStates = Linkbot.JointStates()
        self.__accelCb = None
        self.__encoderCb = None
        self.__jointCb = None
        self.__buttonCb = None

# Connection

    def connect(self, serialId = None):
        '''
        Connect to the robot.
        '''
        _linkbot.Linkbot.connect(self)
        self._formFactor = self.getFormFactor()
        if self._formFactor == Linkbot.FormFactor.I:
            self._motorMask = 0x05
        elif self._formFactor == Linkbot.FormFactor.L:
            self._motorMask = 0x03
        elif self._formFactor == Linkbot.FormFactor.T:
            self._motorMask = 0x07
        else:
            self._motorMask = 0x01
        # Enable joint event callbacks
        self.enableJointEvents()


# Getters

    def getJointAngle(self, jointNo):
        '''
        Get the current angle for a particular joint
        '''
        assert(jointNo >= 1 and jointNo <= 3)
        return self.getJointAngles()[jointNo-1]

    def getJointAngles(self):
        '''
        Get the current joint angles of the robot.

        Example::
            j1, j2, j3 = robot.getJointAngles()

        @rtype: (number, number, number)
        @return: Returned values are in degrees. The three values indicate the
                 joint angles for joints 1, 2, and 3 respectively. Values
                 for joints which are not movable (i.e. joint 2 on a Linkbot-I)
                 are always zero.
        '''
        values = _linkbot.Linkbot.linkbotGetJointAngles(self)
        return tuple(values[1:])

    def getJointSpeed(self, jointNo):
        return self.getJointSpeeds()[jointNo-1]
   
# Setters
    def setBuzzerFrequency(self, freq):
        '''
        Set the Linkbot's buzzer frequency. Setting the frequency to zero turns
        off the buzzer.

        @param freq: The frequency to set the buzzer, in Hertz.
        '''
        _linkbot.Linkbot.setBuzzerFrequencyOn(self, float(freq))

    def setJointSpeed(self, jointNo, speed):
        '''
        Set the speed for a single joint on the robot.

        @param jointNo: The joint to set the speed. Should be 1, 2, or 3.
        @param speed: The requested speed of the joint, in degrees/second.
        '''
        self.setJointSpeeds(speed, speed, speed, mask=(1<<(jointNo-1)) )

    def setJointSpeeds(self, s1, s2, s3, mask=0x07):
        _linkbot.Linkbot.setJointSpeeds(self, mask, s1, s2, s3)
    
# Movement
    def drive(self, j1, j2, j3, mask=0x07):
        self.driveNB(j1, j2, j3, mask)
        self.moveWait(mask)

    def driveNB(self, j1, j2, j3, mask=0x07):
        _linkbot.Linkbot.drive(self, mask, j1, j2, j3)

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
        _linkbot.Linkbot.driveTo(self, mask, j1, j2, j3)
    
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
        _linkbot.Linkbot.move(self, mask, j1, j2, j3)

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
        _linkbot.Linkbot.moveContinuous(self, mask, dir1, dir2, dir3)

    def moveJoint(self, jointNo, angle):
        '''
        Move a single joint and wait for the motion to finish.

        Example::

            # The following code moves joint 1 90 degrees, and then moves joint
            # 3 90 degrees after joint 1 has stopped moving.
            robot.moveJoint(1, 90)
            robot.moveJoint(3, 90)
        '''
        assert (jointNo >= 1 and jointNo <= 3)
        self.moveJointNB(jointNo, angle)
        self.moveWait(1<<(jointNo-1))

    def moveJointNB(self, jointNo, angle):
        '''
        Move a single joint. Returns after the joint begins moving.

        Example::

            # The following code moves joint 1 90 degrees and moves joint 3 90
            # degrees simultaneously.
            robot.moveJointNB(1, 90)
            robot.moveJointNB(3, 90)
        '''
        assert (jointNo >= 1 and jointNo <= 3)
        mask = 1<<(jointNo-1)
        self.moveNB(angle, angle, angle, mask)

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
        to wait for. i.e. ::

            robot.moveWait(0x01) # Only wait for joint 1
            robot.moveWait(0x03) # 0x03 is 0b011 in binary, so wait for joints 1
                                 # and 2 to finish moving.
        '''
        mask = mask & self._motorMask
        self._jointStates.lock()
        states = _linkbot.Linkbot.getJointStates(self)[1:]
        for s,i in zip(states, range(len(states))):
            self._jointStates.set_state(i, s)

        for i in range(3):
            if (1<<i) & mask:
                while self._jointStates.state(i) == Linkbot.JointStates.MOVING:
                    self._jointStates.wait()
        self._jointStates.unlock()

    def stopJoint(self, jointNo):
        '''
        Stop a single joint on the robot, immediately making the joint coast.
        '''
        self.stop(1<<(jointNo-1))

    def stop(self, mask=0x07):
        _linkbot.Linkbot.stop(self, mask)

    # CALLBACKS

    def disableAccelerometerEvents(self):
        '''
        Make the robot stop reporting accelerometer change events.
        '''
        self.setAccelerometerEventCallback(None)

    def disableButtonEvents(self):
        '''
        Make the robot stop reporting button change events.
        '''
        self.setButtonEventCallback(None)

    def disableEncoderEvents(self):
        '''
        Make the robot stop reporting encoder change events.
        '''
        self.setEncoderEventCallback(None, 20)

    def disableJointEvents(self):
        '''
        Make the robot stop reporting joint status change events.
        '''
        # Here, we don't actually want to disable the C++ level callbacks
        # because that will break moveWait(), which requires the C++ level
        # callbacks to be running. Instead, we just set our user level callback
        # object to None.
        self.__jointCb = None

    def enableAccelerometerEvents(self, cb=None):
        '''
        Make the robot begin reporting accelerometer change events. To handle
        these events, a callback function may be specified by the "cb"
        parameter, or the member function "accelerometerEventCB()" may be
        overridden.

        @param cb: (optional) A callback function that will be called when
        accelerometer events are received. The callback function prototype
        should be cb(x, y, z, timestamp)
        '''
        self.__accelCb = cb
        self.setAccelerometerEventCallback(self.accelerometerEventCB)

    def enableEncoderEvents(self, granularity=20.0, cb=None):
        '''
        Make the robot begin reporting joint encoder events. To handle these
        events, a callback function may be specified by the "cb" parameter, or
        the member function "encoderEventCB()" may be overridden.

        @param granularity: (optional) The granularity of the reported encoder
        events, in degrees. For example, setting the granularity to "10.0" means
        the robot will report an encoder event for every 10 degrees that a joint
        is rotated.
        @param cb: (optional) The callback function to handle the event. The
        function prototype should be cb(jointNo, angle, timestamp)
        '''
        self.__encoderCb = cb
        self.setEncoderEventCallback(self.encoderEventCB, granularity)

    def enableButtonEvents(self, cb=None):
        '''
        Make the robot begin reporting button events. To handle the events, a
        callback function may be specified by the "cb" parameter, or the member
        function "buttonEventCB()" may be overridden.

        @param cb: (optional) A callback function with the prototype
        cb(ButtonNo, buttonState, timestamp)
        '''
        self.__buttonCb = cb
        self.setButtonEventCallback(self.buttonEventCB)

    def enableJointEvents(self, cb=None):
        self.__jointCb = cb
        self.setJointEventCallback(self.jointEventCB)

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

    def _setSerialId(self, serialId):
        rc = _L.linkbotWriteEeprom(self.__impl, 0x412, serialId, 4)
        assert(rc == 0)
