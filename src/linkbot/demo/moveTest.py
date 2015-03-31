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
    time.sleep(2)
    myLinkbot.connect()
    angle = 90
    for i in range(20):
        print(i)
        for _ in range(7):
            print(angle)
            myLinkbot.move(angle, angle, angle)
            myLinkbot.move(-angle, -angle, -angle)
            angle *= 0.5

        for _ in range(7):
            print(angle)
            angle *= 2
            myLinkbot.move(angle, angle, angle)
            myLinkbot.move(-angle, -angle, -angle)

