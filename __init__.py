#!/usr/bin/env python

from linkbot.linkbot import _Linkbot 
from linkbot.linkbot import _linkbot as L
import time
import threading
import functools

class Linkbot(_Linkbot):
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
                    func+'NB', 
                    functools.partial( getattr(_Linkbot, func), self ) 
                   )
        time.sleep(2)

    def connect(self):
        # Enable joint event callbacks
        self.enableJointEvent()

    def move(self, j1, j2, j3):
        self._jointStates.lock()
        for i in range(3):
            self._jointStates.set_state(i, L.JOINT_MOVING)
        self.moveNB(0x07, j1, j2, j3)
        while (self._jointStates.state(0) == L.JOINT_MOVING) and \
              (self._jointStates.state(1) == L.JOINT_MOVING) and \
              (self._jointStates.state(2) == L.JOINT_MOVING) :
            self._jointStates.wait()

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
