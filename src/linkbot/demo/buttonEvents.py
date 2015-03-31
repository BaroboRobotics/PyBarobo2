#!/usr/bin/env python3

import linkbot
import time
import sys
import math
import gc

class ButtonLinkbot (linkbot.Linkbot):
    def __init__(self, *args, **kwargs):
        linkbot.Linkbot.__init__(self, *args, **kwargs)

    def buttonEventCB(self, *args, **kwargs):
        self.setLedColor(255, 0, 0)
        print(args, kwargs)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print ("Usage: {0} <Linkbot Serial ID>".format(sys.argv[0]))
        quit()
    serialID = sys.argv[1]
    myLinkbot = ButtonLinkbot(serialID)
    myLinkbot.enableButtonEvents()
    input('Press enter to quit.')

