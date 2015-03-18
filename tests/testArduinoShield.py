#!/usr/bin/env python3

import linkbot
import time
import math

def main():
    l = linkbot.ArduinoLinkbot()

    # Test the six ADC's by giving them six slightly offset sinusoidal signals
    for pin in [3, 5, 6, 9, 10, 11]:
        l.pinMode(pin, linkbot.ArduinoLinkbot.PinMode.output)

    t = 0
    analogPins = (3, 5, 6, 9, 10, 11)
    while t < 5:
        for i in range(6):
            l.analogWrite(analogPins[i], int(127*math.sin(2*t + i*2/math.pi))+127)
        #time.sleep(0.1)
        t += 0.2

    print('AnalogWrite passed')

    print('Getting analog read values...')
    for pin in range(6):
        print(l.analogRead(pin))

    outputPins = [2, 7, 12]
    inputPins = [4, 8, 13]
    for ipin in inputPins:
        l.pinMode(ipin, linkbot.ArduinoLinkbot.PinMode.input)
    for opin in outputPins:
        l.pinMode(opin, linkbot.ArduinoLinkbot.PinMode.output)

    # Test values
    for opin,ipin in zip(outputPins, inputPins):
        l.digitalWrite(opin, 0)
        assert(l.digitalRead(ipin) == 0)
        l.digitalWrite(opin, 1)
        assert(l.digitalRead(ipin) == 1)
        l.digitalWrite(opin, 0)
        assert(l.digitalRead(ipin) == 0)

    # Swap directions
    inputPins = [2, 7]
    outputPins = [4, 8]
    for ipin in inputPins:
        l.pinMode(ipin, linkbot.ArduinoLinkbot.PinMode.input)
    for opin in outputPins:
        l.pinMode(opin, linkbot.ArduinoLinkbot.PinMode.output)

    # Test values
    for opin,ipin in zip(outputPins, inputPins):
        l.digitalWrite(opin, 0)
        assert(l.digitalRead(ipin) == 0)
        l.digitalWrite(opin, 1)
        assert(l.digitalRead(ipin) == 1)
        l.digitalWrite(opin, 0)
        assert(l.digitalRead(ipin) == 0)

    print('Digital IO passed.')

   
if __name__ == '__main__':
    main()
