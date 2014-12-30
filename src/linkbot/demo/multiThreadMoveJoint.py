#!/usr/bin/env python3

import linkbot
import time
import sys
import threading

def jointPosThread(linkbot):
    for _ in range (90):
        print (linkbot.getJointAngles())

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print ("Usage: {0} <Linkbot Serial ID>".format(sys.argv[0]))
        quit()
    serialID = sys.argv[1]
    myLinkbot = linkbot.Linkbot(serialID)
    time.sleep(2)
    myLinkbot.connect()
    thread = threading.Thread(target=jointPosThread, args=(myLinkbot,))
    thread.start()
    for joint in range(1, 4):
        myLinkbot.moveJoint(joint, 90)
        myLinkbot.moveJoint(joint, -90)

