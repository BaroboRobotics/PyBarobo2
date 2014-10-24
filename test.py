#!/usr/bin/env python3

import linkbot
import time

l = linkbot.Linkbot('1DK4')

time.sleep(2)

l.connect()

l.enableEncoderEvent()

l.move(0x07, 90, 90, 90)
