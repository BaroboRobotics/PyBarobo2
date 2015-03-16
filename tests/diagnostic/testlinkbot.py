#!/usr/bin/env python3

from linkbot import Linkbot
import sys, time
import numpy 

class TestLinkbot(Linkbot):
  def __init__(self, *args, **kwargs):
    Linkbot.__init__(self, *args, **kwargs)

  def runSpeedTest(self):
    self.resetToZero()
    self.stop()
    self.setMotorPowers(255, 255, 255)
    self.recordAnglesBegin()
    time.sleep(5)
    recordDataForward = self.recordAnglesEnd()
    self.stop()
    time.sleep(1)
    self.resetToZero()
    self.stop()
    self.setMotorPowers(-255, -255, -255)
    time.sleep(1)
    self.recordAnglesBegin()
    time.sleep(5)
    recordDataBackward = self.recordAnglesEnd()
    self.stop()

    forward_slopes = []
    forward_rvalues = []
    backward_slopes = []
    backward_rvalues = []

    times = recordDataForward[0]
    values = recordDataForward[1]
    for (t, v) in zip(times, values):
        (slope, r2) = self.calculateLinearity(t, v)
        forward_slopes.append(slope)
        forward_rvalues.append(r2)

    times = recordDataBackward[0]
    values = recordDataBackward[1]
    for (t, v) in zip(times, values):
        (slope, r2) = self.calculateLinearity(t, v)
        backward_slopes.append(slope)
        backward_rvalues.append(r2)

    print(forward_slopes, forward_rvalues)
    print (backward_slopes, backward_rvalues)
    results = []
    for (fslope, frvalue, bslope, brvalue) in \
        zip(forward_slopes, forward_rvalues, backward_slopes, backward_rvalues):
      result = {}
      result['forward_slope'] = fslope
      result['forward_rvalue'] = frvalue
      result['backward_slope'] = bslope
      result['backward_rvalue'] = brvalue
      results.append(result)

    return results
    """
    # Calculate forward slopes and r_values
    forward_slopes = []
    forward_rvalues = []
    for angles in recordDataForward[1:]:
      coeffs, residuals, _, _, _ = numpy.polyfit(recordDataForward[0], angles, 1, full=True)
      p = numpy.poly1d(coeffs)
      yhat = p(recordDataForward[0])
      ybar = numpy.sum(angles)/len(angles)
      ssreg = numpy.sum((yhat-ybar)**2)
      sstot = numpy.sum((angles - ybar)**2) 
      forward_slopes.append(coeffs[0])
      forward_rvalues.append(ssreg/sstot)
    # Calculate backward slopes and r_values
    print(forward_slopes)
    backward_slopes = []
    backward_rvalues = []
    for angles in recordDataBackward[1:]:
      coeffs = numpy.polyfit(recordDataBackward[0], angles, 1)
      p = numpy.poly1d(coeffs)
      yhat = p(recordDataBackward[0])
      ybar = numpy.sum(angles)/len(angles)
      ssreg = numpy.sum((yhat-ybar)**2)
      sstot = numpy.sum((angles - ybar)**2) 
      backward_slopes.append(coeffs[0])
      backward_rvalues.append(ssreg/sstot)
   
    print (backward_slopes)
    results = []
    for (fslope, frvalue, bslope, brvalue) in \
        zip(forward_slopes, forward_rvalues, backward_slopes, backward_rvalues):
      result = {}
      result['forward_slope'] = fslope
      result['forward_rvalue'] = frvalue
      result['backward_slope'] = bslope
      result['backward_rvalue'] = brvalue
      results.append(result)

    return results
    """

  # Returns (slope, R^2)
  def calculateLinearity(self, times, values):
    if len(times) == 0:
        return (0, 0)
    coeffs, residuals, _, _, _ = numpy.polyfit(times, values, 1, full=True)
    p = numpy.poly1d(coeffs)
    yhat = p(times)
    ybar = numpy.sum(values)/len(values)
    ssreg = numpy.sum((yhat-ybar)**2)
    sstot = numpy.sum((values - ybar)**2) 
    return (coeffs[0], ssreg/sstot)

  def runFrictionTest(self, motor, direction, startangle):
    threshold = 1.5 # degrees

    if (direction < 0) or (direction == 2):
      inc = -1
    else:
      inc = 1
    
    self.moveJointTo(motor, startangle)
    time.sleep(0.5)
    self.stop()
    time.sleep(0.3)
    curAngle = self.getJointAngle(motor)
    for motorpower in range (0, inc*255, inc):
      self.setMotorPower(motor, motorpower)
      time.sleep(0.1)
      if abs(self.getJointAngle(motor) - curAngle) > threshold:
        self.stop()
        return motorpower

if __name__ == '__main__':
  if len(sys.argv) == 3:
    serialID = sys.argv[2]
  else:
    serialID = 'LOCL'

  linkbot = TestLinkbot(serialID)
  #print(linkbot.runSpeedTest())
  print(linkbot.runFrictionTest(1, -1, 45))

