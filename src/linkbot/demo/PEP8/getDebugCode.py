#!/usr/bin/env python3

import linkbot
import time
import sys

if __name__ == "__main__":
    l = linkbot.Linkbot()
    print(l._readEeprom(0x440, 1))
