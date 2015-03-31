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
    for _ in range(7):
        myLinkbot.move(angle, angle, angle)
        myLinkbot.move(-angle, -angle, -angle)
        angle *= 0.5

    for _ in range(7):
        angle *= 2
        myLinkbot.move(angle, angle, angle)
        myLinkbot.move(-angle, -angle, -angle)

