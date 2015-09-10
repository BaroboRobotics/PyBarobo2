#!/usr/bin/env python3

# This program spams a robot with driveNB commands. The motor should move
# somewhat smoothly one full rotation.

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
    myLinkbot.reset()
    myLinkbot.move_to(0,0,0)

    # Try adjusting this stepsize; Values as high as 20 should still produce
    # _somewhat_ smooth motion.
    stepsize = 5
    for p in range(0, 360, stepsize):
        myLinkbot.drive_joint_to_nb(1, p)
        time.sleep(0.05)
