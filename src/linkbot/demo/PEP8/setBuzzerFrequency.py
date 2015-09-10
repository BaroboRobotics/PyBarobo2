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

    for f in range(100, 600, 5):
        myLinkbot.set_buzzer_frequency(f)
    myLinkbot.set_buzzer_frequency(0)

