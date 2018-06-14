import sys
import socket
import serial
import serial.threaded
import time


#Used as a helper class for serial.threaded.ReaderThread
#Implements necessary classes for serial.threaded.Protocol
class SerialToNet(serial.threaded.Protocol): 
    """serial->socket"""

    def __init__(self, target):
        self.socket = None
        self.target = target

    def __call__(self):
        return self

    def data_received(self, data):
        if self.socket is not None:
            self.socket.sendto(data, self.target)


if __name__ == '__main__':
    import argparse #Useful module for argument parsing

    parser = argparse.ArgumentParser(description='Serial to UDP Sockets redirector.')

    parser.add_argument(
        'SERIALPORT',
        help="serial port name")

    parser.add_argument(
        'BAUDRATE',
        type=int,
        nargs='?',
        help='set baud rate, default: %(default)s',
        default=9600)

    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='suppress non error messages',
        default=False)

    group = parser.add_argument_group('network settings')

    exclusive_group = group.add_mutually_exclusive_group()

    exclusive_group.add_argument(
        '-P', '--localIP',
        help='local UDP IP (default localhost)',
        default='')
    
    exclusive_group.add_argument(
        '-p', '--localport',
        type=int,
        help='local UDP port (default 7777)',
        default=7777)
    
    exclusive_group.add_argument(
            '-R', '--remoteIP',
            help='remote UDP IP (default localhost)',
            default=''
            )
    
    exclusive_group.add_argument(
            '-r', '--remoteport',
            type=int,
            help='remote UDP port (default 8888)',
            default=8888
            )


    args = parser.parse_args() #Parses args and puts them in an accessable format


    #Connect to serial port
    ser = serial.serial_for_url(args.SERIALPORT, do_not_open=True)
    ser.baudrate = args.BAUDRATE

    if not args.quiet:
        sys.stderr.write('--- UDP to Serial redirect on {p.name} {p.baudrate}, listening on {a.localIP}:{a.localport}, broadcasting to {a.remoteIP}:{a.remoteport} ---\n'.format(p=ser, a=args))
        sys.stderr.write('--- type Ctrl-C / BREAK to quit ---\n')

    try:
        ser.open()
    except serial.SerialException as e:
        sys.stderr.write('Could not open serial port {}: {}\n'.format(ser.name, e))
        sys.exit(1)

    



    
