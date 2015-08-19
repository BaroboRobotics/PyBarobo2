#!/usr/bin/env python3

import linkbot
import time
import sys
import math
import matplotlib.pyplot as plt

class AccelLinkbot (linkbot.Linkbot):
    def __init__(self, *args, **kwargs):
        linkbot.Linkbot.__init__(self, *args, **kwargs)
        self.accelData = []
        self.accelTimes = []

    def accelerometerEventCB(self, x, y, z, timestamp):
        self.accelData.append( math.sqrt(x**2 + y**2 + z**2) )
        self.accelTimes.append(timestamp)

    def plot(self):
        plt.plot(self.accelTimes, self.accelData)
        plt.show()

        

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print ("Usage: {0} <Controller Serial ID> <Car Serial Id>".format(sys.argv[0]))
        quit()
    serialID = sys.argv[1]
    carSerialId = sys.argv[2]
    controller = AccelLinkbot(serialID)
    controller.car = linkbot.Linkbot(carSerialId)
    controller.connect()
    controller.enableAccelerometerEvents()
    input("Now recording accelerometer events. Press 'enter' to finish "
          "recording and plot the data.")
    controller.disableAccelerometerEvents()
    controller.plot()

