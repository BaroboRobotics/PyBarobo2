#!/usr/bin/env python
pass

from linkbot.linkbot import _Linkbot 
from linkbot.linkbot import _linkbot as L
import time
import threading
import functools

class Linkbot(_Linkbot):
    class FormFactor:
        I = 0
        L = 1
        T = 2

    class JointStates:
        def __init__(self):
            self._lock = threading.Condition()
            self._state = [L.JOINT_STOP]*3

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
        _Linkbot.__init__(self, serialId)
        """
        self._jointStates = Linkbot.JointStates()
        nbMoveFuncs = [ 'move',
                        'moveTo' ]
        for func in nbMoveFuncs:
            setattr(self, 
                    '_'+func+'NB', 
                    functools.partial( getattr(_Linkbot, func), self ) 
                   )
        """
        time.sleep(2)

    def connect(self):
        '''
        Connect to the robot.
        '''
        # Enable joint event callbacks
        _Linkbot.connect(self)
        self.enableJointEvent()
        '''
        self._formFactor = self.formFactor()
        if self._formFactor == Linkbot.FormFactor.I:
            self._motorMask = 0x05
        elif self._formFactor == Linkbot.FormFactor.L:
            self._motorMask = 0x03
        elif self._formFactor == Linkbot.FormFactor.T:
            self._motorMask = 0x07
        else:
            self._motorMask = 0x01
        '''

    def move(self, j1, j2, j3):
        '''
        Move the joints on a robot and wait until all movements are finished.

        robot.move(90, 0, -90) # Drives Linkbot-I forward by turning wheels
                               # 90 degrees
        '''
        self.moveNB(j1, j2, j3)
        self.moveWait()

    def moveNB(self, j1, j2, j3):
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
        _Linkbot.moveNB(self, 0x07, j1, j2, j3)

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
        self._moveNB(mask, angle, angle, angle)

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
        states = self.getJointStates()[1:]
        for s,i in zip(states, range(len(states))):
            self._jointStates.set_state(i, s)

        for i in range(3):
            if (1<<i) & mask:
                while self._jointStates.state(i) == L.JOINT_MOVING:
                    self._jointStates.wait()
        self._jointStates.unlock()

    # CALLBACKS

    def buttonEventCB(self, buttonNo, state, timestamp):
        print('Button press detected')

    def encoderEventCB(self, jointNo, angle, timestamp):
        print(jointNo, angle)

    def accelerometerEventCB(self, x, y, z, timestamp):
        pass

    def jointEventCB(self, jointNo, state, timestamp):
        self._jointStates.lock()
        self._jointStates.set_state(jointNo, state)
        self._jointStates.unlock()

    def testCB(self):
        print('Test CB called.')
