#!/usr/bin/env python3
# for create.py
import os
import sys
sys.path.append(os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '..'))

import create
import pyudev
import time


def main(argv):
    context = pyudev.Context()
    usb_dev = None
    for device in context.list_devices(subsystem='tty', ID_BUS='usb'):
      if device['ID_VENDOR_ID'] == '0403' and device['ID_MODEL_ID'] == '6001':
        usb_dev = device

    if usb_dev is None:
      print("!! CRITICAL: Failed to find device")
      return 1

    device_path = usb_dev['DEVNAME']

    # Read battery, travel 1.5 meters once low enough.
    r = create.Create(device_path)

    while True:
        battery_cap = r.getSensor('BATTERY_CAPACITY')
        battery_charge = r.getSensor('BATTERY_CHARGE')

        battery_pct = (battery_charge / battery_cap) * 100.0
        if battery_charge is not None and battery_cap is not None:
            print("\rCharge: %f%%" % battery_pct, end='')

        time.sleep(0.2)
        if battery_pct < 75.0:
            break

        r.drive(1000, 0)

    print('')
    r.stop()

    print("Done wasting battery. Press any key to test.")
    input()

    r.go(500)
    r.waitDistance(150)
    r.stop()

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
