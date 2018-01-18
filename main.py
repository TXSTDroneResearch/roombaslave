import pyudev
import serial
import socket
import struct
import sys
import time
import zeroconf

from twisted.internet import reactor
from twisted.internet.protocol import Protocol, ClientFactory
from twisted.internet.endpoints import TCP4ClientEndpoint, connectProtocol


def FindDevice(vendor, model):
    """ Finds the first USB TTY device by vendor and model IDs.

    Returns None if the device wasn't found.
    """
    context = pyudev.Context()
    usb_dev = None
    for device in context.list_devices(subsystem='tty', ID_BUS='usb'):
      if device['ID_VENDOR_ID'] == vendor and device['ID_MODEL_ID'] == model:
        usb_dev = device

    if usb_dev is None:
        return None

    return usb_dev['DEVNAME']


class Roomba(object):
  def __init__(self, ser):
    self._ser = ser
    self._init_roomba('safe')

  def _init_roomba(self, mode):
    self._ser.write(struct.pack('>B', 128))  # start
    time.sleep(0.4)
    if mode == 'safe':
      self._ser.write(struct.pack('>B', 131))  # safe mode
    elif mode == 'full':
      self._ser.write(struct.pack('>B', 132))  # full mode

    time.sleep(0.4)

  def SendRaw(self, data):
    self._ser.write(data)


class RoombaProto(Protocol):
  def __init__(self, device_path):
    ser = serial.Serial(device_path, baudrate=57600, timeout=0.5)
    self._roomba = Roomba(ser)

  def dataReceived(self, data):
    """ Called when data was received from the remote host.
    """
    # Pass this data into the roomba.
    # David: protobuf magic here!
    self._roomba.SendRaw(data)

  def connectionLost(self, reason):
    self._roomba.SendRaw(bytearray(b'\x89\x00\x00\x00\x00'))  # Stop driving


class Listener(object):
    def __init__(self):
        self._enabled = True

    def OnSuccessfulConnection(self, proto):
        self._proto = proto

    def OnConnectionFailure(self, err):
        self._enabled = True

    def remove_service(self, zc, service_type, name):
        pass

    def add_service(self, zc, service_type, name):
        info = zc.get_service_info(service_type, name)
        if info:
            print("- Found new service @ %s:%d" %
                  (socket.inet_ntoa(info.address), info.port))
            print("  Weight: %d, priority: %d" % (info.weight, info.priority))
            print("  Server: %s" % (info.server))

            def InitiateConnection(listener, reactor, info):
                point = TCP4ClientEndpoint(
                    reactor, socket.inet_ntoa(info.address), info.port)

                d = connectProtocol(point, RoombaProto())
                d.addCallback(listener.OnSuccessfulConnection)
                d.addErrback(listener.OnConnectionFailure)

            reactor.callFromThread(InitiateConnection, self, reactor, info)


def main(args):
    device_path = FindDevice('0403', '6001')
    if device_path is None:
        print("!! CRITICAL: Failed to find device.")
        return 1

    print("Device @ %s" % device_path)

    zc = zeroconf.Zeroconf()
    listener = Listener(RoombaProtoFac(device_path))
    browser = zeroconf.ServiceBrowser(
        zc, "_roomba._tcp.local.", listener=listener)

    print("Waiting for the master server to come online...")
    reactor.run()
    print("Exiting.")

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
