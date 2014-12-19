#!/usr/bin/env python3

import linkbot
import time
import sys

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print ("Usage: {0} <New Linkbot Serial ID>".format(sys.argv[0]))
        quit()
    serialID = sys.argv[1]
    if len(serialID) != 4:
        print("The new serial ID must be four characters in length")
        quit()

    myLinkbot = linkbot.Linkbot('LOCL')
    myLinkbot.connect()
    time.sleep(2)
    
    myLinkbot._setSerialId(serialID)
