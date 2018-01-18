import pyudev

class GPS(object):
    # 1. Spawn a thread that listens to the specified device
    #    path over serial, and updates class vars (long, lat)
    def __init__(self, device_path):
        pass

def create_gps(device_path = None):
    # 1. Find GPS via pyudev (vendor:device), use device_path if not None
    # 2. Create a GPS class with that device path (over serial)
    pass