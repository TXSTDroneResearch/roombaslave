# Roomba Slave

## main.py

The main entry point to the slave code. Its responsibilities are:

1) Find and initialize the connected Roomba via serial
2) Begin listening for an Avahi service advertising `_roomba._tcp.local.`
3) When the service is found, it initiates a connection to the drone master server.
4) Once the connection is established, it echoes any data received straight into the Roomba via serial.

## imu.py

This class wraps the RTIMU device, and provides a thread that continuously updates and polls the device.

## create.py

This class is an interface for the Roomba written in Python. Taken from Zach Dodds.

## Other files

There's more files here that are mainly skeleton classes with documentation written inline, which shouldn't need much explanation.