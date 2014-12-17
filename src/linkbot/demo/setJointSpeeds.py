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

    speed = -90
    myLinkbot.setJointSpeed(1, speed)
    myLinkbot.moveContinuous(
        linkbot.Linkbot.JointStates.MOVING,
        0,
        0,
        1
        )

    while speed < 90:
        speed += 1
        myLinkbot.setJointSpeed(1, speed)
        #time.sleep(0.2)

    myLinkbot.stop()

