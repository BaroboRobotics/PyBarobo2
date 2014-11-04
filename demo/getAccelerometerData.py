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
    success = False
    while not success:
        try:
            myLinkbot.connect()
            success = True
        except Exception as e:
            print(e)

    print(myLinkbot.getAccelerometerData())

