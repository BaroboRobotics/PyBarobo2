#!/usr/bin/env python

from linkbot.linkbot import _Linkbot 

class Linkbot(_Linkbot):
    def __init__(self, serialId):
        _Linkbot.__init__(self, serialId)
        # Enable joint event callbacks
        pass

    def buttonEventCB(self, buttonNo, state, timestamp):
        pass

    def encoderEventCB(self, jointNo, angle, timestamp):
        pass

    def accelerometerEventCB(self, x, y, z, timestamp):
        pass

    def jointEventCB(self, jointNo, state, timestamp):
        pass
