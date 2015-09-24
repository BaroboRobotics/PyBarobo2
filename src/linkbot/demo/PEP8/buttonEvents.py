#!/usr/bin/env python3

import linkbot
import time
import sys
import math
import gc

class ButtonLinkbot (linkbot.Linkbot):
    def __init__(self, *args, **kwargs):
        linkbot.Linkbot.__init__(self, *args, **kwargs)

    def button_event_cb(self, *args, **kwargs):
        self.set_led_color(255, 0, 0)
        print(args, kwargs)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print ("Usage: {0} <Linkbot Serial ID>".format(sys.argv[0]))
        quit()
    serialID = sys.argv[1]
    myLinkbot = ButtonLinkbot(serialID)
    myLinkbot.enable_button_events()
    input('Press enter to quit.')

