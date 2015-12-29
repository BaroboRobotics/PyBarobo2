#!/usr/bin/env python3

import linkbot
import math
import time
import random
import sys

if len(sys.argv) < 2:
    print ("Usage: {0} <Linkbot Serial IDs>".format(sys.argv[0]))
    quit()
linkbotIds = sys.argv[1:]

linkbots = list(map(linkbot.Linkbot, linkbotIds))

t = 0.0
while True:
    '''
    print("Loop")
    r = (math.sin(t)+1)*127.0
    g = (math.sin(t+2*math.pi/3)+1)*127.0
    b = (math.sin(t+4*math.pi/3)+1)*127.0
    '''
    r = random.randint(1, 255)
    g = random.randint(1, 255)
    b = random.randint(1, 255)

    for linkbot in linkbots:
        linkbot.set_led_color(int(r), int(g), int(b))

    t += 0.1
