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

    The previous snippet of code creates a new variable called "myLinkbot" which
    is connected to a physical robot with the serial ID "ABCD". Once a Linkbot
    is connected, you may use member functions to control the robot. For
    instance, to move motors 1 and 3 90 and -90 degrees, respectively::

        myLinkbot.move(90, 0, -90)

    Note: As of version 2.3.6, all of the method names in the Linkbot class have
    been modified from the old camelHump style names to PEP8 compliant names.
    For instance, the function::

        myLinkbot.moveJointToNB(1, 90)

    is now::

        myLinkbot.move_joint_to_nb(1, 90)

    The old function names still work for backwards compatibility, but are not
    included in the documentation.

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

        def states(self):
            return self._state

        def set_moving(self, mask):
            self.lock()
            for i in range(3):
                if mask & (1<<i):
                    self._state[i] = self.MOVING
            self.unlock()

        def set_state(self, index, state):
            self._state[index] = state
            self._lock.notify_all()

        def wait(self, timeout=None):
            return self._lock.wait(timeout)

    def __init__(self, serialId = 'LOCL'):
        """Create a new Linkbot object

        :param serialId: A robot's Serial ID.  If ommitted, will
              attempt to connect to a Linkbot connected locally via USB. The
              serial ID may be specified here, in the connect() function, or not
              at all.
        :type serialId: str
        """
        self.__attributes = self.__dict__.keys()
        serialId = serialId.upper()
        _linkbot.Linkbot.__init__(self, serialId)
        self.__serialId = serialId
        self._jointStates = Linkbot.JointStates()
        self.__accelCb = None
        self.__encoderCb = None
        self.__jointCb = None
        self.__buttonCb = None
        atexit.register(self._releaseCallbacks)

        self._formFactor = _linkbot.Linkbot._getFormFactor(self)
        if self._formFactor == Linkbot.FormFactor.I:
            self._motorMask = 0x05
        elif self._formFactor == Linkbot.FormFactor.L:
            self._motorMask = 0x03
        elif self._formFactor == Linkbot.FormFactor.T:
            self._motorMask = 0x07
        else:
            self._motorMask = 0x01

        # Set up joint event callback for moveWait
        self.enable_joint_events()

    # This method allows us to programatically support both mixedCase and
    # lowercase_with_underscore method names. If an attribute cannot be found,
    # it is converted to the equivalent lowercase attribute name and checked
    # again. If it still cannot be found, AttributeError is raised.
    def __getattr__(self, name):
        # Strategy: First, convert the name to a PEP8 style name and see if it
        # is an attribute. If it is, return that. If not, try to see if the
        # original name is an attribute and return that. If not, raise
        # AttributeError.
        origname = name
        # Convert the name to a new PEP8 style name
        import re
        if name.endswith('NB'):
            name = name[:-2] + 'Nb'
        if name.endswith('CB'):
            name = name[:-2] + 'Cb'
        newname = re.sub(r'([A-Z])', lambda x: '_'+x.group(1).lower(), name)
        if newname == origname:
            raise AttributeError(origname)
        # return self.__dict__[newname]
        return getattr(self, newname)

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
    def get_accelerometer(self):
        '''Get the current accelerometer values for 3 primary axes

        :rtype: (number, number, number)
          Returned values are expressed in "G's", where one G is equivalent
          to one earth-gravity, or 9.81 m/s/s.
        '''
        return _linkbot.Linkbot._getAccelerometer(self)[1:]

    def get_accelerometer_data(self):
        return self.getAccelerometer()

    def get_battery_voltage(self):
        ''' Get the robot's current battery voltage '''
        return _linkbot.Linkbot._getBatteryVoltage(self)

    def get_form_factor(self):
        ''' Get the robot's form factor

        :rtype: linkbot.Linkbot.FormFactor.[I|L|T]
        '''
        return self._getFormFactor()

    def get_joint_angle(self, joint):
        '''
        Get the current angle for a particular joint

        
        :type joint: int 
        :param joint: The joint number of robot.

        Example::

            # Get the joint angle for joint 1
            angle = robot.get_joint_angle(1)
        '''
        assert(joint >= 1 and joint <= 3)
        return self.getJointAngles()[joint-1]

    def get_joint_angles(self):
        '''
        Get the current joint angles of the robot.

        :rtype: (number, number, number)
           Returned values are in degrees. The three values indicate the
           joint angles for joints 1, 2, and 3 respectively. Values
           for joints which are not movable (i.e. joint 2 on a Linkbot-I)
           are always zero.

        Example::

            j1, j2, j3 = robot.get_joint_angles()

        '''
        values = _linkbot.Linkbot._getJointAngles(self)
        return tuple(values[1:])

    def get_joint_safety_thresholds(self):
        return _linkbot.Linkbot._getJointSafetyThresholds(self)

    def get_joint_safety_angles(self):
        return _linkbot.Linkbot._getJointSafetyAngles(self)

    def get_joint_speed(self, joint):
        """Get the current speed for a joint

        :param joint: A joint number.
        :type joint: int
        :rtype: float (degrees/second)

        Example::

            # Get the joint speed for joint 1
            speed = robot.get_joint_speed(1)
        """
        return self.getJointSpeeds()[joint-1]

    def get_joint_speeds(self):
        return _linkbot.Linkbot._getJointSpeeds(self)

    def get_joint_states(self):
        return self._getJointStates()

    def get_hw_version(self):
        mybytes = self.readEeprom(0x430, 3)
        return (mybytes[0], mybytes[1], mybytes[2])

    def get_led_color(self):
        return _linkbot.Linkbot._getLedColor(self)

    def get_serial_id(self):
        bytestream = self._readEeprom(0x412, 4)
        return bytearray(bytestream).decode()
# Setters
    def reset(self):
        _linkbot.Linkbot._resetEncoderRevs(self)

    def reset_to_zero(self):
        _linkbot.Linkbot._resetEncoderRevs(self)
        self.moveTo(0, 0, 0)

    def reset_to_zero_nb(self):
        _linkbot.Linkbot._resetEncoderRevs(self)
        self.moveToNB(0, 0, 0)

    def set_buzzer_frequency(self, freq):
        '''
        Set the Linkbot's buzzer frequency. Setting the frequency to zero turns
        off the buzzer.

        :type freq: int
        :param freq: The frequency to set the buzzer, in Hertz.
        '''
        _linkbot.Linkbot._setBuzzerFrequency(self, float(freq))

    def set_joint_acceleration(self, joint, alpha):
        ''' Set a single joint's acceleration value.

        See :func:`Linkbot.set_joint_accelerations` and 
        :func:`Linkbot.move_smooth` .
        '''
        self.setJointAccelerations(alpha, alpha, alpha, 1<<(joint-1))

    def set_joint_accelerations(self, alpha1, alpha2, alpha3, mask=0x07):
        '''
        Set the rate at which joints should accelerate during "smoothed"
        motions, such as "move_smooth". Units are in deg/sec/sec.
        '''
        _linkbot.Linkbot._setJointAccelI(self, mask, alpha1, alpha2, alpha3)

    def set_joint_deceleration(self, joint, alpha):
        ''' Set a single joint's deceleration value.

        See :func:`Linkbot.set_joint_decelerations` and 
        :func:`Linkbot.move_smooth` .
        '''
        self.setJointDecelerations(alpha, alpha, alpha, 1<<(joint-1))

    def set_joint_decelerations(self, alpha1, alpha2, alpha3, mask=0x07):
        '''
        Set the rate at which joints should decelerate during "smoothed"
        motions, such as "move_smooth". Units are in deg/sec/sec.
        '''
        _linkbot.Linkbot._setJointAccelF(self, mask, alpha1, alpha2, alpha3)

    def set_joint_safety_thresholds(self, t1 = 100, t2 = 100, t3 = 100, mask=0x07):
        _linkbot.Linkbot._setJointSafetyThresholds(self, mask, t1, t2, t3)

    def set_joint_safety_angles(self, t1 = 10.0, t2 = 10.0, t3 = 10.0, mask=0x07):
        _linkbot.Linkbot._setJointSafetyThresholds(self, mask, t1, t2, t3)

    def set_joint_speed(self, joint, speed):
        '''
        Set the speed for a single joint on the robot.

        :type joint: int
        :param JointNo: The joint to set the speed. Should be 1, 2, or 3.
        :type speed: float
        :param speed: The new speed of the joint, in degrees/second.

        Example::

            # Set the joint speed for joint 3 to 100 degrees per second
            robot.set_joint_speed(3, 100)
        '''
        self.setJointSpeeds(speed, speed, speed, mask=(1<<(joint-1)) )

    def set_joint_speeds(self, s1, s2, s3, mask=0x07):
        """Set the joint speeds for all of the joints on a robot.

        :type s1: float
        :param s1: The speed, in degrees/sec, to set the first joint. Parameters
            s2 and s3 are similar for joints 2 and 3.
        :type mask: int 
        :param mask: (optional) A bitmask to specify which joints to modify the
           speed. The speed on the robot's joint is only changed if
           (mask&(1<<(joint-1))).
        """
        _linkbot.Linkbot._setJointSpeeds(self, mask, s1, s2, s3)

    def set_led_color(self, r, g, b):
        ''' Set the LED color on the robot.

        :type r: int [0,255]
        :type g: int [0,255]
        :type b: int [0,255]
        '''
        self._setLedColor(r, g, b)
   
    def set_motor_power(self, joint, power):
        """Apply a direct power setting to a motor
        
        :type joint: int (1,3)
        :param joint: The joint to apply the power to
        :type power: int (-255,255)
        :param power: The power to apply to the motor. 0 indicates no power
        (full stop), negative number apply power to turn the motor in the
        negative direction.
        """
        assert (joint >= 1 and joint <= 3)
        mask = 1<<(joint-1)
        _linkbot.Linkbot._motorPower(self, mask, power, power, power)

    def set_motor_powers(self, power1, power2, power3):
        """Apply a direct power setting to all motors
        
        :type power: int (-255,255)
        :param power: The power to apply to the motor. 0 indicates no power
        (full stop), negative number apply power to turn the motor in the
        negative direction.
        """
        _linkbot.Linkbot._motorPower(self, 0x07, power1, power2, power3)

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
              The robot will only move joints where (mask&(1<<(joint-1))) is
              true.
        """
          
        self.driveNB(j1, j2, j3, mask)
        self.moveWait(mask)

    def drive_nb(self, j1, j2, j3, mask=0x07):
        """Non blocking version of :func:`Linkbot.drive`."""
        self._jointStates.set_moving(mask)
        _linkbot.Linkbot._drive(self, mask, j1, j2, j3)

    def drive_joint(self, joint, angle):
        """Move a single motor using the on-board PID controller.

        This is the fastest way to drive a single joint to a desired position.
        The "speed" setting of the joint is ignored during the motion. See also:
        :func:`Linkbot.drive`

        :type joint: int
        :param joint: The joint to move.
        :type angle: float
        :param angle: A relative angle in degrees to move the joint.
        """
        self.driveJointNB(joint, angle)
        self.moveWait(1<<(joint-1))

    def drive_joint_nb(self, joint, angle):
        """Non-blocking version of :func:`Linkbot.drive_joint`"""
        self.driveNB(angle, angle, angle, 1<<(joint-1))

    def drive_joint_to(self, joint, angle):
        """Move a single motor using the on-board PID controller.

        This is the fastest way to drive a single joint to a desired position.
        The "speed" setting of the joint is ignored during the motion. See also:
        :func:`Linkbot.drive`

        :type joint: int
        :param joint: The joint to move.
        :type angle: float
        :param angle: An absolute angle in degrees to move the joint. 

        Example::

            robot.driveJointTo(1, 20)
            # Joint 1 is now at the 20 degree position.
            # The next line of code will move joint 1 10 degrees in the negative
            # direction.
            robot.drive_joint_to(1, 10)
        """
        self.driveJointToNB(joint, angle)
        self.moveWait(1<<(joint))

    def drive_joint_to_nb(self, joint, angle):
        """Non-blocking version of :func:`Linkbot.drive_joint_to`"""
        self.driveToNB(angle, angle, angle, 1<<(joint-1))

    def drive_to(self, j1, j2, j3, mask=0x07):
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
              The robot will only move joints where (mask&(1<<(joint-1))) is
              true.
        """
        self.driveToNB(j1, j2, j3, mask)
        self.moveWait(mask)
        
    def drive_to_nb(self, j1, j2, j3, mask=0x07):
        """Non-blocking version of :func:`Linkbot.drive_to`"""
        self._jointStates.set_moving(mask)
        _linkbot.Linkbot._driveTo(self, mask, j1, j2, j3)

    def move(self, j1, j2, j3, mask=0x07):
        '''Move the joints on a robot and wait until all movements are finished.

        Move a robot's joints at the constant velocity previously set by a call
        to :func:`Linkbot.set_joint_speed` or similar functions.

        :type j1: float
        :param j1: An angle in degrees. The joint moves this amount from wherever the joints are currently positioned.

        Example::

            robot.move(90, 0, -90) # Drives Linkbot-I forward by turning wheels
                                   # 90 degrees.
        '''
        self.moveNB(j1, j2, j3, mask)
        self.moveWait(mask)

    def move_nb(self, j1, j2, j3, mask=0x07):
        '''Non-blocking version of :func:`Linkbot.move`

        Example::

            # The following code makes a Linkbot-I change its LED color to red 
            # and then blue while it is rolling forward.
            robot.move_nb(90, 0, -90)
            robot.set_led_color(255, 0, 0)
            time.sleep(0.5)
            robot.set_led_color(0, 0, 255)

        '''
        self._jointStates.set_moving(mask)
        _linkbot.Linkbot._move(self, mask, j1, j2, j3)

    def move_continuous(self, dir1, dir2, dir3, mask=0x07):
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
        self._jointStates.set_moving(mask)
        _linkbot.Linkbot._moveContinuous(self, mask, dir1, dir2, dir3)

    def move_joint(self, joint, angle):
        """Move a single motor using the on-board constant velocity controller.

        Move a single joint at the velocity last set by
        :func:`Linkbot.set_joint_speed` or other speed setting functions.
        See also: :func:`Linkbot.move`

        :type joint: int
        :param joint: The joint to move.
        :type angle: float
        :param angle: A relative angle in degrees to move the joint.

        Example::

            # The following code moves joint 1 90 degrees, and then moves joint
            # 3 90 degrees after joint 1 has stopped moving.
            robot.move_joint(1, 90)
            robot.move_joint(3, 90)
        """
        assert (joint >= 1 and joint <= 3)
        self.moveJointNB(joint, angle)
        self.moveWait(1<<(joint-1))

    def move_joint_nb(self, joint, angle):
        '''Non-blocking version of :func:`Linkbot.move_joint`
        '''
        assert (joint >= 1 and joint <= 3)
        mask = 1<<(joint-1)
        self.moveNB(angle, angle, angle, mask)

    def move_joint_to(self, joint, angle):
        """Move a single motor using the on-board constant velocity controller.

        Move a single joint at the velocity last set by
        :func:`Linkbot.set_joint_speed` or other speed setting functions. The 
        'angle' parameter is the absolute position you want the motor to move
        to.
        See also: :func:`Linkbot.move`

        :type joint: int
        :param joint: The joint to move.
        :type angle: float
        :param angle: A relative angle in degrees to move the joint.

        Example::

            # The following code moves joint 1 to the 90 degree position, and 
            # then moves joint3 to the 90 degree position after joint 1 has 
            # stopped moving.
            robot.move_joint_to(1, 90)
            robot.move_joint_to(3, 90)
        """
        assert (joint >= 1 and joint <= 3)
        self.moveJointToNB(joint, angle)
        self.moveWait(1<<(joint-1))

    def move_joint_to_nb(self, joint, angle):
        '''Non-blocking version of :func:`Linkbot.move_joint_to`
        '''
        assert (joint >= 1 and joint <= 3)
        mask = 1<<(joint-1)
        self.moveToNB(angle, angle, angle, mask)

    def move_joint_wait(self, joint):
        ''' Wait for a single joint to stop moving.

        This function blocks until the joint specified by the parameter
        ``joint`` stops moving.

        :type joint: int
        :param joint: The joint to wait for.

        '''
        assert(joint >= 1 and joint <=3)
        self.moveWait(1<<(joint-1))

    def move_joint_smooth(self, joint, angle):
        ''' Move a single joint using the "Smooth" motor controller.

        See :func:`Linkbot.move_smooth` 
        '''
        self.moveJointSmoothNB(joint, angle)
        self.moveWait(1<<(joint-1))

    def move_joint_smooth_nb(self, joint, angle):
        ''' Non-blocking version of :func:`Linkbot.move_joint_smooth` '''
        self.moveSmoothNB(angle, angle, angle, 1<<(joint-1))

    def move_smooth(self, j1, j2, j3, mask=0x07):
        ''' Move joints with smooth acceleration and deceleration.

        The acceleration and deceleration can be set with the functions
        :func:`Linkbot.set_joint_accelerations` and 
        :func:`Linkbot.set_joint_decelerations`. The maximum velocity the 
        joint will travel at during the motion can be set with the
        :func:`Linkbot.set_joint_speeds` family of functions.

        :type j1: float
        :param j1: Number of degrees to move joint 1. Similar for j2 and j3.

        Example::

            # Move joint 1 720 degrees, accelerating at 45 deg/sec, traveling at
            # a maximum speed of 90 deg/sec, and decelerating at 120 deg/sec at
            # the end of the motion.
            robot.set_joint_accelerations(45, 45, 45)
            robot.set_joint_speeds(90, 90, 90)
            robot.set_joint_decelerations(120, 120, 120)
            robot.move_smooth(720, 0, 0)
        '''
        self.moveSmoothNB(j1, j2, j3, mask)
        self.moveWait(mask)

    def move_smooth_nb(self, j1, j2, j3, mask=0x07):
        '''Non-blocking version of :func:`Linkbot.move_smooth` '''
        self._jointStates.set_moving(mask)
        _linkbot.Linkbot._moveSmooth(self, mask, mask, j1, j2, j3)

    def move_smooth_to(self, j1, j2, j3, mask=0x07):
        ''' Move joints with smooth acceleration and deceleration.

        The acceleration and deceleration can be set with the functions
        :func:`Linkbot.set_joint_accelerations` and 
        :func:`Linkbot.set_joint_decelerations`.

        :type j1: float
        :param j1: The position to move joint 1 to (in degrees).
        '''
        self.moveSmoothToNB(j1, j2, j3, mask)
        self.moveWait(mask)
 
    def move_smooth_to_nb(self, j1, j2, j3, mask=0x07):
        ''' Non-blocking version of :func:`move_smooth_to` '''
        self._jointStates.set_moving(mask)
        _linkbot.Linkbot._moveSmooth(self, mask, 0, j1, j2, j3)

    def move_to(self, j1, j2, j3, mask=0x07):
        ''' Move a Linkbot's joints to specified degree locations. '''
        self.moveToNB(j1, j2, j3, mask)
        self.moveWait(mask)

    def move_to_nb(self, j1, j2, j3, mask=0x07):
        ''' Non-blocking version of :func:`Linkbot.move_to` '''
        self._jointStates.set_moving(mask)
        _linkbot.Linkbot._moveTo(self, mask, j1, j2, j3)

    def move_wait(self, mask=0x07):
        ''' Wait for all masked joints (all joints by default) to stop moving.
        '''
        mask &= self._motorMask
        # First, check the current joint states.
        def isMoving(states, mask):
            moving = False
            for i,s in enumerate(states):
                if not (mask & (1<<i) ):
                    continue
                if s is Linkbot.JointStates.MOVING:
                    moving = True
                    break
            return moving

        self._jointStates.lock()
        if not isMoving(self._jointStates.states(), mask):
            self._jointStates.unlock()
            return
        while isMoving(self._jointStates.states(), mask):
            notified = self._jointStates.wait(3)
            if not notified: # We timed out; refresh states
                states = self.getJointStates()[1:];
                for i, s in enumerate(states):
                    self._jointStates.set_state(i, s)
        self._jointStates.unlock()

    def stop_joint(self, joint):
        '''
        Stop a single joint on the robot, immediately making the joint coast.
        '''
        self.stop(1<<(joint-1))

    def stop(self, mask=0x07):
        '''Immediately stop and relax all joints on the Linkbot.'''
        _linkbot.Linkbot._stop(self, mask)

    # MISC

    def _recordAnglesCb(self, joint, angle, timestamp):
        self._recordTimes[joint-1].append(timestamp)
        self._recordAngles[joint-1].append(angle)
    
    def record_angles_begin(self):
        ''' Begin recording a Linkbot's joint angles. 

        This function tells the Linkbot to begin recording any changes
        to its joint angles. The recorded data can be retrieved with the
        function :func:`Linkbot.record_angles_end` . 
        '''
        # Get the initial angles
        (timestamp, a1, a2, a3) = _linkbot.Linkbot._getJointAngles(self)
        self._recordTimes = ([timestamp], [timestamp], [timestamp])
        self._recordAngles = ([a1], [a2], [a3])
        self.enableEncoderEvents(1.0, self._recordAnglesCb)

    def record_angles_end(self):
        ''' Stop recording a Linkbot's joint angles and return the results.

        :rtype: ((times,), [[j1_angles,], [j2_angles,], [j3_angles,]])
        '''
        self.disableEncoderEvents()
        # Get last angles
        (timestamp, a1, a2, a3) = _linkbot.Linkbot._getJointAngles(self)
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

    def disable_accelerometer_events(self):
        '''
        Make the robot stop reporting accelerometer change events.
        '''
        self._setAccelerometerEventCallback(None)

    def disable_button_events(self):
        '''
        Make the robot stop reporting button change events.
        '''
        self._setButtonEventCallback(None)

    def disable_encoder_events(self):
        '''
        Make the robot stop reporting encoder change events.
        '''
        self._setEncoderEventCallback(None, 20)

    def disable_joint_events(self):
        '''
        Make the robot stop reporting joint status change events.
        '''
        # Here, we don't actually want to disable the C++ level callbacks
        # because that will break moveWait(), which requires the C++ level
        # callbacks to be running. Instead, we just set our user level callback
        # object to None.
        self.__jointCb = None

    def enable_accelerometer_events(self, cb=None):
        '''
        Make the robot begin reporting accelerometer change events. To handle
        these events, a callback function may be specified by the "cb"
        parameter, or the member function "accelerometer_event_cb()" may be
        overridden.

        :type cb: function(x, y, z, timestamp)
        :param cb: (optional) A callback function that will be called when
            accelerometer events are received. The callback function prototype
            should be cb(x, y, z, timestamp)
        '''
        self.__accelCb = cb
        try:
            self._setAccelerometerEventCallback(self.accelerometerEventCB)
        except:
            self._setAccelerometerEventCallback(self.accelerometer_event_cb)

    def enable_encoder_events(self, granularity=20.0, cb=None):
        '''Make the robot begin reporting encoder events.

        Make the robot begin reporting joint encoder events. To handle these
        events, a callback function may be specified by the "cb" parameter, or
        the member function "encoder_event_cb()" may be overridden.

        :type granularity: float
        :param granularity: (optional) The granularity of the reported encoder
            events, in degrees. For example, setting the granularity to "10.0" means
            the robot will report an encoder event for every 10 degrees that a joint
            is rotated.
        :type cb: function(joint, angle, timestamp)
        :param cb: (optional) The callback function to handle the event. The
            function prototype should be cb(joint, angle, timestamp)
        '''
        self.__encoderCb = cb
        try:
            self._setEncoderEventCallback(self.encoderEventCB, granularity)
        except:
            self._setEncoderEventCallback(self.encoder_event_cb, granularity)

    def enable_button_events(self, cb=None):
        ''' Make the robot begin button events.

        Make the robot begin reporting button events. To handle the events, a
        callback function may be specified by the "cb" parameter, or the member
        function "button_event_cb()" may be overridden.
        
        :type cb: function(buttonNo, buttonState, timestamp)
        :param cb: (optional) A callback function with the prototype
            cb(ButtonNo, buttonState, timestamp)
        '''
        self.__buttonCb = cb
        try:
            self._setButtonEventCallback(self.buttonEventCB)
        except:
            self._setButtonEventCallback(self.button_event_cb)

    def enable_joint_events(self, cb=None):
        self.__jointCb = cb
        self._setJointEventCallback(self.jointEventCB)

    def button_event_cb(self, button_no, state, timestamp):
        if self.__buttonCb is not None:
            self.__buttonCb(buttonNo, state, timestamp)

    def encoder_event_cb(self, joint, angle, timestamp):
        if self.__encoderCb is not None:
            self.__encoderCb(joint, angle, timestamp)

    def accelerometer_event_cb(self, x, y, z, timestamp):
        if self.__accelCb is not None:
            self.__accelCb(x, y, z, timestamp)

    def joint_event_cb(self, joint, state, timestamp):
        ''' Joint event callback function.

        This function is called when the state of joint changes. For instance,
        if a moving joint stops, this callback function is invoked.

        This function is used internally by the move_wait() function and
        overriding this function is not recommended. '''
        self._jointStates.lock()
        self._jointStates.set_state(joint, state)
        self._jointStates.unlock()
        if self.__jointCb is not None:
            self.__jointCb(joint, state, timestamp)

    def test_cb(self):
        print('Test CB called.')

    def _set_serial_id(self, serialId):
        _linkbot.Linkbot._writeEeprom(self, 0x412, serialId.encode())

    def _set_hw_version(self, major, minor, micro):
        _linkbot.Linkbot._writeEeprom(self, 0x420, bytearray([major, minor, micro]))

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

    def analog_write(self, pin, value):
        buf = bytearray([self.Command.analog_write, pin, value])
        self.writeTwi(self.TWI_ADDR, buf)

    def analog_read(self, pin):
        buf = bytearray([self.Command.analog_read, pin])
        data = self.writeReadTwi(self.TWI_ADDR, buf, 2)
        value = (data[0]<<8) + data[1]
        return value

    def digital_write(self, pin, value):
        buf = bytearray([self.Command.digital_write, pin, value])
        self.writeTwi(self.TWI_ADDR, buf)
    
    def digital_read(self, pin):
        buf = bytearray([self.Command.digital_read, pin])
        return self.writeReadTwi(self.TWI_ADDR, buf, 1)[0]

    def pin_mode(self, pin, mode):
        buf = bytearray([self.Command.pin_mode, pin, mode])
        self.writeTwi(self.TWI_ADDR, buf)

