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
    myLinkbot.set_joint_speeds(90, 90, 90)
    myLinkbot.set_joint_accelerations(45, 45, 45)
    myLinkbot.set_joint_decelerations(45, 45, 45)
    angle = 360
    for i in range(20):
        print(i)
        for _ in range(7):
            print(angle)
            myLinkbot.move_smooth(angle, angle, angle)
            myLinkbot.move_smooth(-angle, -angle, -angle)
            angle *= 0.5

        for _ in range(7):
            print(angle)
            angle *= 2
            myLinkbot.move_smooth(angle, angle, angle)
            myLinkbot.move_smooth(-angle, -angle, -angle)

