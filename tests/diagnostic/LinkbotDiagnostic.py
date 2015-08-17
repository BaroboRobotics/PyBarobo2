#!/usr/bin/env python3

import sqlite3 as sql
import sys

from linkbot import Linkbot
from testlinkbot import TestLinkbot
import time

def initialize_tables(cursor):
  try:
    cur = cursor
    cur.execute("CREATE TABLE IF NOT EXISTS robot_type (Id TEXT, "
          "formfactor TEXT)")
    cur.execute('CREATE TABLE IF NOT EXISTS speed_tests (Id TEXT, '
          'Date DATE, '
          'm1forward SINGLE, '
          'm1backward SINGLE, '
          'm2forward SINGLE, '
          'm2backward SINGLE)')

    cur.execute('CREATE TABLE IF NOT EXISTS linearity_tests (Id TEXT, '
          'Date DATE, '
          'm1forward_slope SINGLE, '
          'm1forward_R SINGLE, '
          'm1backward_slope SINGLE, '
          'm1backward_R SINGLE, '
          'm2forward_slope SINGLE, '
          'm2forward_R SINGLE, '
          'm2backward_slope SINGLE, '
          'm2backward_R SINGLE)')

    cur.execute('CREATE TABLE IF NOT EXISTS static_friction_tests(Id TEXT, '
          'Date DATE, '
          'Motor INT, '
          'Direction INT, '
          'Angle INT, '
          'Value INT)')

    """
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    rows = cur.fetchall()
    for row in rows:
      print row[0]
    """
    
  except sql.Error as e:
    print ("Error %s:" % e.args[0])
    sys.exit(1)

class LinkbotDiagnostic():
  def __init__(self, linkbot):
    self.linkbot = linkbot
    # Check to see if this linkbot is in our database already. Add it if not
    formFactor = None
    if linkbot.getFormFactor() == Linkbot.FormFactor.I:
      formFactor = "Linkbot-I"
      self.motor2index = 2
    elif linkbot.getFormFactor() == Linkbot.FormFactor.L:
      formFactor = "Linkbot-L"
      self.motor2index = 1
    else:
      formFactor = "UNKNOWN"
    print ("Testing LinkBot {}".format(linkbot.getSerialId()))

  def run(self):
    self.runLinearityTest()
    self.runFrictionTest()

  def runLinearityTest(self):
    results = self.linkbot.runSpeedTest()
    return results

  def runFrictionTest(self):
    now = time.strftime('%Y-%m-%d %H:%M:%S')
    if self.linkbot.getFormFactor() == barobo.ROBOTFORM_I:
      motors = [1, 3]
    else:
      motors = [1, 2]

    for motor in motors:
      for dir in [1, -1]:
        self.linkbot.reset()
        for angle in range(0, 360*dir, 90*dir):
          value = self.linkbot.runFrictionTest(motor, dir, angle)
          self.cur.execute("INSERT INTO static_friction_tests "
              "VALUES ('{}', '{}', '{}', '{}', '{}', '{}')".format(
                self.linkbot.getSerialId(),
                now,
                motor,
                dir,
                angle,
                value))

buttons = 0x07
def main():
  if len(sys.argv) == 2:
    serialID = sys.argv[1]
  else:
    serialID = 'LOCL'

  linkbot = TestLinkbot(serialID)

  print('Testing robot:', linkbot.getSerialId())
  # Get firmware checksum
  print('Firmware checksum:', linkbot.readEeprom(0x423, 2))

  # Test LED
  print('Testing LED...')
  linkbot.setLedColor(255, 0, 0)
  time.sleep(1)
  linkbot.setLedColor(0, 255, 0)
  time.sleep(1)
  linkbot.setLedColor(0, 0, 255)

  # Test buzzer
  print('Testing buzzer...')
  for i in range(440, 550, 5):
      linkbot.setBuzzerFrequency(i)
  linkbot.setBuzzerFrequency(0)

  print('Current accel readings: ' + str(linkbot.getAccelerometer()))

  print('Press all three buttons on the Linkbot...')
  def buttonCB(button, state, timestamp):
    global buttons
    buttons = buttons & ~(1<<button)
  linkbot.enableButtonEvents(buttonCB)
  while buttons:
      time.sleep(1)

  con = sql.connect('testlog.db')
  initialize_tables(con.cursor())
  cur = con.cursor()
# Check to see if this linkbot is in our database already. Add it if not
  cur.execute('SELECT * FROM robot_type WHERE Id=\'{}\''.format(linkbot.getSerialId()))
  rows = cur.fetchall()
  formFactor = None
  if linkbot.getFormFactor() == Linkbot.FormFactor.I:
    formFactor = "Linkbot-I"
    motor2index = 2
  elif linkbot.getFormFactor() == Linkbot.FormFactor.L:
    formFactor = "Linkbot-L"
    motor2index = 1
  else:
    formFactor = "UNKNOWN"
  print ("Testing LinkBot {}".format(linkbot.getSerialId()))
  d = LinkbotDiagnostic(linkbot)
  results = d.runLinearityTest()
  now = time.strftime('%Y-%m-%d %H:%M:%S')
  if len(rows) == 0:
    cur.execute('INSERT INTO robot_type VALUES(\'{}\', \'{}\')'.format(
        linkbot.getSerialId(), formFactor))
  cur.execute("INSERT INTO linearity_tests "
    "VALUES('{}', '{}', {}, {}, {}, {}, {}, {}, {}, {})".format(
      linkbot.getSerialId(),
      now,
      results[0]['forward_slope'],
      results[0]['forward_rvalue'],
      results[0]['backward_slope'],
      results[0]['backward_rvalue'],
      results[motor2index]['forward_slope'],
      results[motor2index]['forward_rvalue'],
      results[motor2index]['backward_slope'],
      results[motor2index]['backward_rvalue']))

  con.commit()
  con.close()
  linkbot.setBuzzerFrequency(440)
  time.sleep(0.5)
  linkbot.setBuzzerFrequency(0)


if __name__ == '__main__':
  main()
