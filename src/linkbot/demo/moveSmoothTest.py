#!/usr/bin/env python3

import linkbot
import time
import sys

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print ("Usage: {0} <Linkbot Serial ID>".format(sys.argv[0]))
        quit()
    serialID = sys.argv[1]
    myLinkbot = linkbot.Linkbot(serialID)
    myLinkbot.connect()
    myLinkbot.setJointSpeeds(90, 90, 90)
    myLinkbot.setJointAccelerations(45, 45, 45)
    myLinkbot.setJointDecelerations(45, 45, 45)
    angle = 360
    for i in range(20):
        print(i)
        for _ in range(7):
            print(angle)
            myLinkbot.moveSmooth(angle, angle, angle)
            myLinkbot.moveSmooth(-angle, -angle, -angle)
            angle *= 0.5

        for _ in range(7):
            print(angle)
            angle *= 2
            myLinkbot.moveSmooth(angle, angle, angle)
            myLinkbot.moveSmooth(-angle, -angle, -angle)

