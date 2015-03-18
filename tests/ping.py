#!/usr/bin/env python3

import sys
import linkbot

def main():
    if len(sys.argv) != 2:
        print('Usage: {0} <Serial ID>')
        quit()

    l = linkbot.Linkbot(sys.argv[1])

    for i in range(100):
        print(l.getJointAngles())

if __name__ == '__main__':
    main()
