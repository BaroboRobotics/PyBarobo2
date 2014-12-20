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

    print('Moving all motors to zero...')
    myLinkbot.driveTo(0, 0, 0)


    print('Moving all motors 90 degrees...')
    myLinkbot.driveNB(90, 90, 90)
    print('Waiting for movement to finish...')
    myLinkbot.moveWait()
    print('Done.')

    print('Moving all motors -90 degrees...')
    myLinkbot.drive(-90, -90, -90)
    print('Done')

    print('Moving motor 1 90 degrees...')
    myLinkbot.driveJoint(1, 90)
    print('Moving motor 1 -90 degrees...')
    myLinkbot.driveJoint(1, -90)

