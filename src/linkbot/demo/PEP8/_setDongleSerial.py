#!/usr/bin/env python3

import linkbot
import time
import sys
import random

if __name__ == "__main__":
    myLinkbot = linkbot.Linkbot('LOCL')
    myLinkbot.connect()

    rand_id = bytearray( [random.randint(0, 256) for _ in range(4) ] )
    rand_id[1] = rand_id[1] | 0x80
    
    myLinkbot.writeEeprom(0x412, rand_id)
