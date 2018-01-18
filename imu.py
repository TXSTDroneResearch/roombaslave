import math
import RTIMU
import threading
import time

# Useful resource:
# http://kingtidesailing.blogspot.com/2016/02/how-to-setup-mpu-9250-on-raspberry-pi_25.html
class IMU(object):
    def __init__(self):
        settings = RTIMU.Settings("RTIMULib")
        self._imu = RTIMU.RTIMU(settings)

        if not self._imu.IMUInit():
            raise IOError("Failed to initialize the IMU")
        
        self._imu_data = None
        self._imu.setAccelEnable(True)
        self._imu.setGyroEnable(True)
        self._imu.setCompassEnable(False)

        self._poll_interval = self._imu.IMUGetPollInterval()

        # Create a polling thread.
        self._thread_state = 0
        self._thread = threading.Thread(target=self._PollThread)
        self._thread.start()
    
    def _PollThread(self):
        while self._thread_state == 0:
            while True:
                res = self._imu.IMURead()
                if res == 0:
                    # Out of data.
                    break
                elif res < 0:
                    # Fatal error! IMU down.
                    print("IMURead fatal error %d. IMU down." % res)
                    self._thread_state = res
                    return

                if self._thread_state != 0:
                    # Good breaking point here.
                    break

                self._imu_data = self._imu.getIMUData()

                # If the compass magnitude is above 100nT, compass data may be unreliable!
                compass_mag = math.sqrt(self._imu_data['compass'][0] ** 2 + self._imu_data['compass'][1] ** 2 + self._imu_data['compass'][2] ** 2)
                print("\rYaw: %.3f, CMag: %.3f   " % (self._imu_data['fusionPose'][2], compass_mag), end='')

            
            # Sleep for the minimum poll interval time.
            time.sleep(self._poll_interval * 1.0 / 1000.0)
    
    def Shutdown(self):
        """
        Shuts down the IMU reader.
        """
        self._thread_state = 1
        self._thread.join()

        # Shut down the IMU.
        self._imu.IMUShutdown()
        self._imu = None

    def EnableCompass(self, enable):
        """ Enables or disables compass input into the IMU fusion algorithm.
        """
        self._imu.setCompassEnable(enable)

    def GetCompassMagnitude(self):
        """ Retrieves the magnitude of the onboard compass. If above 100nT, the
        heading may not be reliable!
        """
        return math.sqrt(self._imu_data['compass'][0] ** 2 + self._imu_data['compass'][1] ** 2 + self._imu_data['compass'][2] ** 2)

    def GetHeading(self):
        """
        Retrieves the heading of the roomba based on combined sensor data, in rad
        """
        if self._imu_data == None:
            # No data yet.
            return 0

        if self._thread_state != 0:
            # IMU down.
            return None

        return self._imu_data['fusionPose'][2]

    def GetSpeed(self):
        """
        Retrieves the detected travel speed, in m/s
        """
        pass

if __name__ == '__main__':
    print("Testing IMU...")

    imu = IMU()
    try:
        while True:
            time.sleep(0.2)
    except KeyboardInterrupt:
        imu.Shutdown()
