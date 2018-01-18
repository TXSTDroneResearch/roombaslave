import imu
from vectors import Vector

class Robot(object):
  """Robot class representing a Roomba.
  """
  def __init__(self):
    self._imu = imu.IMU()

    # XYZ position on the board
    self._position = Vector(0.0, 0.0, 0.0)
    self._rotation = Vector(0.0, 0.0, 0.0)

  def Move(distance):
    """Moves the robot the specified distance (in meters).
    Does not return until the operation is completed.
    """
    pass
  
  def Rotate(angle):
    """Rotates the robot the specified angle (in radians).
    Does not return until the operation is completed.
    """
    pass