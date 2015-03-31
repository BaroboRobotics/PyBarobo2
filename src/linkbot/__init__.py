#!/usr/bin/env python3

"""
.. module::linkbot
    :synopsis: A module for controlling Barobo Linkbots.

.. moduleauthor:: David Ko <david@barobo.com>
"""

from linkbot import _linkbot 

import time
import threading
import multiprocessing
import functools
import atexit

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
        """Create a new Linkbot object

        :param serialId: A robot's Serial ID.  If ommitted, will
              attempt to connect to a Linkbot connected locally via USB. The
              serial ID may be specified here, in the connect() function, or not
              at all.
        :type serialId: str
        """
        serialId = serialId.upper()
        _linkbot.Linkbot.__init__(self, serialId)
        self.__serialId = serialId
        self._jointStates = Linkbot.JointStates()
        self.__accelCb = None
        self.__encoderCb = None
        self.__jointCb = None
        self.__buttonCb = None
        atexit.register(self._releaseCallbacks)

        self._formFactor = self.getFormFactor()
        if self._formFactor == Linkbot.FormFactor.I:
            self._motorMask = 0x05
        elif self._formFactor == Linkbot.FormFactor.L:
            self._motorMask = 0x03
        elif self._formFactor == Linkbot.FormFactor.T:
            self._motorMask = 0x07
        else:
            self._motorMask = 0x01


# Connection

    def connect(self, serialId = None):
        """ Connect to the robot. (DEPRECATED)

        This function is no longer required to form a connection with a Linkbot.
        All connection now happens in __init__(). Calling this function does
        nothing, but it is kept here for backwards-compatability purposes.
        
        :type serialId: str
        :param serialId: (optional): The serial ID may be specified here or in
              the Linkbot constructor. If specified in both locations, the one
              specified here will override the one specified in the constructor.
        """ 
        pass

# Getters
    def getAccelerometer(self):
        '''Get the current accelerometer values for 3 primary axes

        :rtype: (number, number, number)
          Returned values are expressed in "G's", where one G is equivalent
          to one earth-gravity, or 9.81 m/s/s.
        '''
        return _linkbot.Linkbot.getAccelerometer(self)[1:]

    def getAccelerometerData(self):
        return self.getAccelerometer()

    def getBatteryVoltage(self):
        return _linkbot.Linkbot.getBatteryVoltage(self)

    def getJointAngle(self, jointNo):
        '''
        Get the current angle for a particular joint

        
        :type jointNo: int 
        :param jointNo: The joint number of robot.

        Example::

            # Get the joint angle for joint 1
            angle = robot.getJointAngle(1)
        '''
        assert(jointNo >= 1 and jointNo <= 3)
        return self.getJointAngles()[jointNo-1]

    def getJointAngles(self):
        '''
        Get the current joint angles of the robot.

        :rtype: (number, number, number)
           Returned values are in degrees. The three values indicate the
           joint angles for joints 1, 2, and 3 respectively. Values
           for joints which are not movable (i.e. joint 2 on a Linkbot-I)
           are always zero.

        Example::

            j1, j2, j3 = robot.getJointAngles()

        '''
        values = _linkbot.Linkbot.getJointAngles(self)
        return tuple(values[1:])

    def getJointSafetyThresholds(self):
        return _linkbot.Linkbot.getJointSafetyThresholds(self)

    def getJointSafetyAngles(self):
        return _linkbot.Linkbot.getJointSafetyAngles(self)

    def getJointSpeed(self, jointNo):
        """Get the current speed for a joint

        :param jointNo: A joint number.
        :type jointNo: int
        :rtype: float (degrees/second)

        Example::
            # Get the joint speed for joint 1
            speed = robot.getJointSpeed(1)
        """
        return self.getJointSpeeds()[jointNo-1]

    def getHwVersion(self):
        mybytes = self.readEeprom(0x420, 3)
        return (mybytes[0], mybytes[1], mybytes[2])

    def getSerialId(self):
        bytestream = self.readEeprom(0x412, 4)
        return bytearray(bytestream).decode()
# Setters
    def reset(self):
        _linkbot.Linkbot.resetEncoderRevs(self)

    def resetToZero(self):
        _linkbot.Linkbot.resetEncoderRevs(self)
        self.moveTo(0, 0, 0)

    def resetToZeroNB(self):
        _linkbot.Linkbot.resetEncoderRevs(self)
        self.moveToNB(0, 0, 0)

    def setBuzzerFrequency(self, freq):
        '''
        Set the Linkbot's buzzer frequency. Setting the frequency to zero turns
        off the buzzer.

        :type freq: int
        :param freq: The frequency to set the buzzer, in Hertz.
        '''
        _linkbot.Linkbot.setBuzzerFrequency(self, float(freq))

    def setJointSafetyThresholds(self, t1 = 100, t2 = 100, t3 = 100, mask=0x07):
        _linkbot.Linkbot.setJointSafetyThresholds(self, mask, t1, t2, t3)

    def setJointSafetyAngles(self, t1 = 10.0, t2 = 10.0, t3 = 10.0, mask=0x07):
        _linkbot.Linkbot.setJointSafetyThresholds(self, mask, t1, t2, t3)

    def setJointSpeed(self, jointNo, speed):
        '''
        Set the speed for a single joint on the robot.

        :type jointNo: int
        :param JointNo: The joint to set the speed. Should be 1, 2, or 3.
        :type speed: float
        :param speed: The new speed of the joint, in degrees/second.

        Example::
            # Set the joint speed for joint 3 to 100 degrees per second
            robot.setJointSpeed(3, 100)
        '''
        self.setJointSpeeds(speed, speed, speed, mask=(1<<(jointNo-1)) )

    def setJointSpeeds(self, s1, s2, s3, mask=0x07):
        """Set the joint speeds for all of the joints on a robot.

        :type s1: float
        :param s1: The speed, in degrees/sec, to set the first joint. Parameters
            s2 and s3 are similar for joints 2 and 3.
        :type mask: int 
        :param mask: (optional) A bitmask to specify which joints to modify the
           speed. The speed on the robot's joint is only changed if
           (mask&(1<<(jointNo-1))).
        """
        _linkbot.Linkbot.setJointSpeeds(self, mask, s1, s2, s3)
   
    def setMotorPower(self, jointNo, power):
        """Apply a direct power setting to a motor
        
        :type jointNo: int (1,3)
        :param jointNo: The joint to apply the power to
        :type power: int (-255,255)
        :param power: The power to apply to the motor. 0 indicates no power
        (full stop), negative number apply power to turn the motor in the
        negative direction.
        """
        assert (jointNo >= 1 and jointNo <= 3)
        mask = 1<<(jointNo-1)
        _linkbot.Linkbot.motorPower(self, mask, power, power, power)

    def setMotorPowers(self, power1, power2, power3):
        """Apply a direct power setting to all motors
        
        :type power: int (-255,255)
        :param power: The power to apply to the motor. 0 indicates no power
        (full stop), negative number apply power to turn the motor in the
        negative direction.
        """
        _linkbot.Linkbot.motorPower(self, 0x07, power1, power2, power3)

# Movement
    def drive(self, j1, j2, j3, mask=0x07):
        """Move a robot's motors using the on-board PID controller. 

        This is the fastest way to get a Linkbot's motor to a particular angle
        position. The "speed" setting of the joint is ignored during this
        motion.

        :type j1: float
        :param j1: Relative angle in degrees to move the joint. If a joint is
              currently at a position of 30 degrees and a 90 degree drive is
              issued, the final position of the joint will be at 120 degrees.
              Parameters j2 and j3 are similar for joints 2 and 3.
        :type mask: int
        :param mask: (optional) A bitmask to specify which joints to move. 
              The robot will only move joints where (mask&(1<<(jointNo-1))) is
              true.
        """
          
        self.driveNB(j1, j2, j3, mask)
        self.moveWait(mask)

    def driveNB(self, j1, j2, j3, mask=0x07):
        """Non blocking version of :func:`Linkbot.drive`."""
        _linkbot.Linkbot.drive(self, mask, j1, j2, j3)

    def driveJoint(self, jointNo, angle):
        """Move a single motor using the on-board PID controller.

        This is the fastest way to drive a single joint to a desired position.
        The "speed" setting of the joint is ignored during the motion. See also:
        :func:`Linkbot.drive`

        :type jointNo: int
        :param jointNo: The joint to move.
        :type angle: float
        :param angle: A relative angle in degrees to move the joint.
        """
        self.driveJointNB(jointNo, angle)
        self.moveWait(1<<(jointNo-1))

    def driveJointNB(self, jointNo, angle):
        """Non-blocking version of :func:`Linkbot.driveJoint`"""
        self.driveNB(angle, angle, angle, 1<<(jointNo-1))

    def driveJointTo(self, jointNo, angle):
        """Move a single motor using the on-board PID controller.

        This is the fastest way to drive a single joint to a desired position.
        The "speed" setting of the joint is ignored during the motion. See also:
        :func:`Linkbot.drive`

        :type jointNo: int
        :param jointNo: The joint to move.
        :type angle: float
        :param angle: An absolute angle in degrees to move the joint. 

        Example::
            robot.driveJointTo(1, 20)
            # Joint 1 is now at the 20 degree position.
            # The next line of code will move joint 1 10 degrees in the negative
            # direction.
            robot.driveJointTo(1, 10)
        """
        self.driveJointToNB(jointNo, angle)
        self.moveWait(1<<(jointNo))

    def driveJointToNB(self, jointNo, angle):
        """Non-blocking version of :func:`Linkbot.driveJointTo`"""
        self.driveToNB(angle, angle, angle, 1<<(jointNo-1))

    def driveTo(self, j1, j2, j3, mask=0x07):
        """Move a robot's motors using the on-board PID controller. 

        This is the fastest way to get a Linkbot's motor to a particular angle
        position. The "speed" setting of the joint is ignored during this
        motion.

        :type j1: float
        :param j1: Absolute angle in degrees to move the joint. If a joint is
              currently at a position of 30 degrees and a 90 degree drive is
              issued, the joint will move in the positive direction by 60 
              degrees.
              Parameters j2 and j3 are similar for joints 2 and 3.
        :type mask: int
        :param mask: (optional) A bitmask to specify which joints to move. 
              The robot will only move joints where (mask&(1<<(jointNo-1))) is
              true.
        """
        self.driveToNB(j1, j2, j3, mask)
        self.moveWait(mask)
        
    def driveToNB(self, j1, j2, j3, mask=0x07):
        """Non-blocking version of :func:`Linkbot.driveTo`"""
        _linkbot.Linkbot.driveTo(self, mask, j1, j2, j3)
    
    def move(self, j1, j2, j3, mask=0x07):
        '''Move the joints on a robot and wait until all movements are finished.

        Move a robot's joints at the constant velocity previously set by a call
        to :func:`Linkbot.setJointSpeed` or similar functions.

        :type j1: float
        :param j1: An angle in degrees. The joint moves this amount from
            wherever the joints are currently positioned.

        Example::
            robot.move(90, 0, -90) # Drives Linkbot-I forward by turning wheels
                                   # 90 degrees
        '''
        self.moveNB(j1, j2, j3, mask)
        self.moveWait(mask)

    def moveNB(self, j1, j2, j3, mask=0x07):
        '''Non-blocking version of :func:`Linkbot.move`

        Example::
            # The following code makes a Linkbot-I change its LED color to red 
            # and then blue while it is rolling forward.
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

        :type dir1: :class:`Linkbot.JointStates`
        :param dir1: These parameters should be members of the
            Linkbot.JointStates class. They should be one of

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
        """Move a single motor using the on-board constant velocity controller.

        Move a single joint at the velocity last set by
        :func:`Linkbot.setJointSpeed` or other speed setting functions.
        See also: :func:`Linkbot.move`

        :type jointNo: int
        :param jointNo: The joint to move.
        :type angle: float
        :param angle: A relative angle in degrees to move the joint.

        Example::

            # The following code moves joint 1 90 degrees, and then moves joint
            # 3 90 degrees after joint 1 has stopped moving.
            robot.moveJoint(1, 90)
            robot.moveJoint(3, 90)
        """
        assert (jointNo >= 1 and jointNo <= 3)
        self.moveJointNB(jointNo, angle)
        self.moveWait(1<<(jointNo-1))

    def moveJointNB(self, jointNo, angle):
        '''Non-blocking version of :func:`Linkbot.moveJoint`
        '''
        assert (jointNo >= 1 and jointNo <= 3)
        mask = 1<<(jointNo-1)
        self.moveNB(angle, angle, angle, mask)

    def moveJointTo(self, jointNo, angle):
        """Move a single motor using the on-board constant velocity controller.

        Move a single joint at the velocity last set by
        :func:`Linkbot.setJointSpeed` or other speed setting functions. The 
        'angle' parameter is the absolute position you want the motor to move
        to.
        See also: :func:`Linkbot.move`

        :type jointNo: int
        :param jointNo: The joint to move.
        :type angle: float
        :param angle: A relative angle in degrees to move the joint.

        Example::

            # The following code moves joint 1 to the 90 degree position, and 
            # then moves joint3 to the 90 degree position after joint 1 has 
            # stopped moving.
            robot.moveJointTo(1, 90)
            robot.moveJointTo(3, 90)
        """
        assert (jointNo >= 1 and jointNo <= 3)
        self.moveJointToNB(jointNo, angle)
        self.moveWait(1<<(jointNo-1))

    def moveJointToNB(self, jointNo, angle):
        '''Non-blocking version of :func:`Linkbot.moveJointTo`
        '''
        assert (jointNo >= 1 and jointNo <= 3)
        mask = 1<<(jointNo-1)
        self.moveToNB(angle, angle, angle, mask)

    def moveJointWait(self, jointNo):
        ''' Wait for a single joint to stop moving.

        This function blocks until the joint specified by the parameter
        ``jointNo`` stops moving.

        :type jointNo: int
        :param jointNo: The joint to wait for.

        '''
        assert(jointNo >= 1 and jointNo <=3)
        self.moveWait(1<<(jointNo-1))

    def moveTo(self, j1, j2, j3, mask=0x07):
        self.moveToNB(j1, j2, j3, mask)
        self.moveWait(mask)

    def moveToNB(self, j1, j2, j3, mask=0x07):
        _linkbot.Linkbot.moveTo(self, mask, j1, j2, j3)

    def moveWait(self, mask=0x07):
        ''' Wait for all masked joints (all joints by default) to stop moving.
        '''
        _linkbot.Linkbot.moveWait(self, mask)

    def stopJoint(self, jointNo):
        '''
        Stop a single joint on the robot, immediately making the joint coast.
        '''
        self.stop(1<<(jointNo-1))

    def stop(self, mask=0x07):
        '''Immediately stop and relax all joints on the Linkbot.'''
        _linkbot.Linkbot.stop(self, mask)

    # MISC

    def _recordAnglesCb(self, jointNo, angle, timestamp):
        self._recordTimes[jointNo-1].append(timestamp)
        self._recordAngles[jointNo-1].append(angle)
    
    def recordAnglesBegin(self):
        # Get the initial angles
        (timestamp, a1, a2, a3) = _linkbot.Linkbot.getJointAngles(self)
        self._recordTimes = ([timestamp], [timestamp], [timestamp])
        self._recordAngles = ([a1], [a2], [a3])
        self.enableEncoderEvents(1.0, self._recordAnglesCb)

    def recordAnglesEnd(self):
        self.disableEncoderEvents()
        # Get last angles
        (timestamp, a1, a2, a3) = _linkbot.Linkbot.getJointAngles(self)
        for i, _ in enumerate(self._recordTimes):
            self._recordTimes[i].append(timestamp)
        self._recordAngles[0].append(a1)
        self._recordAngles[1].append(a2)
        self._recordAngles[2].append(a3)

        minTimes = []
        for t in self._recordTimes:
            if len(t) > 0:
                minTimes.append(t[0])
        initTime = min(minTimes)
        fixedTimes = ()
        for times in self._recordTimes:
            fixedTimes += (list(map(lambda x: (x - initTime)/1000.0, times)), )

        return (fixedTimes, self._recordAngles)

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

        :type cb: function(x, y, z, timestamp)
        :param cb: (optional) A callback function that will be called when
            accelerometer events are received. The callback function prototype
            should be cb(x, y, z, timestamp)
        '''
        self.__accelCb = cb
        self.setAccelerometerEventCallback(self.accelerometerEventCB)

    def enableEncoderEvents(self, granularity=20.0, cb=None):
        '''Make the robot begin reporting encoder events.

        Make the robot begin reporting joint encoder events. To handle these
        events, a callback function may be specified by the "cb" parameter, or
        the member function "encoderEventCB()" may be overridden.

        :type granularity: float
        :param granularity: (optional) The granularity of the reported encoder
            events, in degrees. For example, setting the granularity to "10.0" means
            the robot will report an encoder event for every 10 degrees that a joint
            is rotated.
        :type cb: function(jointNo, angle, timestamp)
        :param cb: (optional) The callback function to handle the event. The
            function prototype should be cb(jointNo, angle, timestamp)
        '''
        self.__encoderCb = cb
        self.setEncoderEventCallback(self.encoderEventCB, granularity)

    def enableButtonEvents(self, cb=None):
        ''' Make the robot begin button events.

        Make the robot begin reporting button events. To handle the events, a
        callback function may be specified by the "cb" parameter, or the member
        function "buttonEventCB()" may be overridden.
        
        :type cb: function(buttonNo, buttonState, timestamp)
        :param cb: (optional) A callback function with the prototype
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
        _linkbot.Linkbot.writeEeprom(self, 0x412, serialId.encode())

    def _setHwVersion(self, major, minor, micro):
        self.writeEeprom(0x420, bytearray([major, minor, micro]))

class ArduinoLinkbot(Linkbot):
    TWI_ADDR = 0x03

    class PinMode:
        input = 0
        output = 1
        input_pullup = 2

    class Command:
        read_register = 0x00
        write_register = 0x01
        pin_mode = 0x02
        digital_write = 0x03
        digital_read = 0x04
        analog_ref = 0x05
        analog_read = 0x06
        analog_write = 0x07

    def analogWrite(self, pin, value):
        buf = bytearray([self.Command.analog_write, pin, value])
        self.writeTwi(self.TWI_ADDR, buf)

    def analogRead(self, pin):
        buf = bytearray([self.Command.analog_read, pin])
        data = self.writeReadTwi(self.TWI_ADDR, buf, 2)
        value = (data[0]<<8) + data[1]
        return value

    def digitalWrite(self, pin, value):
        buf = bytearray([self.Command.digital_write, pin, value])
        self.writeTwi(self.TWI_ADDR, buf)
    
    def digitalRead(self, pin):
        buf = bytearray([self.Command.digital_read, pin])
        return self.writeReadTwi(self.TWI_ADDR, buf, 1)[0]

    def pinMode(self, pin, mode):
        buf = bytearray([self.Command.pin_mode, pin, mode])
        self.writeTwi(self.TWI_ADDR, buf)

