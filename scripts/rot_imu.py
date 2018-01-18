# Add parent directory to PATH
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import create
import imu
import math
import platform
import serial
import time

if platform.system() == 'Linux':
  import pyudev

def NormalizeAngle(a):
  if abs(a) > math.pi:
    # renormalize
    while a >= math.pi:
      a -= math.pi * 2

    while a < -math.pi:
      a += math.pi * 2
  
  return a

def CalculateCompassDifference(a, b):
  """ Calculate the difference of 2 compass points in radians
  ranging from [-pi, pi]
  """
  delta = NormalizeAngle(a - b)
  return delta

def TurnRobot(r, i, hdg_tgt, precision):
  """ Turns a Roomba to face the target heading (w.r.t. the IMU heading), within
  +/- precision degrees rad
  r is a Create
  i is an IMU

  Returns the final angle error.
  """
  # Continue refining the angle until we're under the req. precision
  while abs(CalculateCompassDifference(i.GetHeading(), hdg_tgt)) > precision:
    delta = CalculateCompassDifference(hdg_tgt, i.GetHeading())

    if delta > 0:
      # Clockwise turn
      r.driveDirect(1, -1)

      # Wait until the turn has finished.
      while abs(CalculateCompassDifference(hdg_tgt, i.GetHeading())) > precision:
        time.sleep(0.001)
    elif delta < 0:
      # Counter-clockwise turn
      r.driveDirect(-1, 1)

      # Wait until the turn has finished.
      while abs(CalculateCompassDifference(hdg_tgt, i.GetHeading())) > precision:
        time.sleep(0.001)
    
    # Stop and regauge
    r.stop()
    time.sleep(0.25)
  
  return CalculateCompassDifference(hdg_tgt, i.GetHeading())

if __name__ == '__main__':
  device_path = ''
  if platform.system() == 'Linux':
    context = pyudev.Context()
    usb_dev = None
    for device in context.list_devices(subsystem='tty', ID_BUS='usb'):
      if device['ID_VENDOR_ID'] == '0403' and device['ID_MODEL_ID'] == '6001':
        usb_dev = device

    if usb_dev is None:
      print("!! CRITICAL: Failed to find device")
      sys.exit(1)

    device_path = usb_dev['DEVNAME']
    print("Device @ %s" % device_path)
  else:
    # lol hardcocded on windoews
    device_path = 'COM4'

  i = imu.IMU()

  try:
    r = create.Create(device_path)
  except serial.SerialException:
    print("Failed to open the roomba")
    i.Shutdown()
    sys.exit(1)

  # Default turn rad
  hdg_tgt = NormalizeAngle(i.GetHeading() + math.pi / 2)
  if len(sys.argv) >= 2:
    # parse arg 1
    try:
      print("Using user angle of %s" % sys.argv[1])
      ang = float(sys.argv[1]) * (math.pi / 180.0)

      hdg_tgt = NormalizeAngle(i.GetHeading() + ang)
    except:
      print("Could not parse %s, reverting to default." % sys.argv[1])
  else:
    print("Using default angle of 90")
  
  print("Target heading: %f" % hdg_tgt)

  # Sleep & go
  time.sleep(0.2)

  # Turn the robot
  error = TurnRobot(r, i, hdg_tgt, 0.05)
  print("Final Delta: %f" % error)

  # Shutdown.
  i.Shutdown()