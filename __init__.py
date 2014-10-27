#!/usr/bin/env python

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
        self._jointStates = Linkbot.JointStates()
        nbMoveFuncs = [ 'move',
                        'moveTo' ]
        for func in nbMoveFuncs:
            setattr(self, 
                    '_'+func+'NB', 
                    functools.partial( getattr(_Linkbot, func), self ) 
                   )
        time.sleep(2)

    def connect(self):
        # Enable joint event callbacks
        _Linkbot.connect(self)
        self.enableJointEvent()
        self._formFactor = self.formFactor()
        if self._formFactor == Linkbot.FormFactor.I:
            self._motorMask = 0x05
        elif self._formFactor == Linkbot.FormFactor.L:
            self._motorMask = 0x03
        elif self._formFactor == Linkbot.FormFactor.T:
            self._motorMask = 0x07
        else:
            self._motorMask = 0x01

    def move(self, j1, j2, j3):
        self.moveNB(j1, j2, j3)
        self.moveWait()

    def moveNB(self, j1, j2, j3):
        self._moveNB(0x07, j1, j2, j3)

    def moveWait(self, mask = 0x07):
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
