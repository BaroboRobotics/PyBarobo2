#!/usr/bin/env python3

import linkbot
import time
import sys
import math
import matplotlib.pyplot as plt

class EncoderLinkbot (linkbot.Linkbot):
    def __init__(self, *args, **kwargs):
        linkbot.Linkbot.__init__(self, *args, **kwargs)
        self.encoderData = []
        self.encoderTimes = []

    def encoderEventCB(self, jointNo, angle, timestamp):
        if jointNo == 1:
            self.encoderData.append(angle)
            self.encoderTimes.append(timestamp)

    def plot(self):
        plt.plot(self.encoderTimes, self.encoderData)
        plt.show()

        

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print ("Usage: {0} <Linkbot Serial ID>".format(sys.argv[0]))
        quit()
    serialID = sys.argv[1]
    myLinkbot = EncoderLinkbot(serialID)
    myLinkbot.connect()
    myLinkbot.enableEncoderEvents(granularity=1.0)
    myLinkbot.drive(90, 90, 90)
    myLinkbot.drive(-90, -90, -90)
    myLinkbot.disableEncoderEvents()
    myLinkbot.plot()

