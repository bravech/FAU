import sys
import socket
import serial
import serial.threaded
import time


# Used as a helper class for serial.threaded.ReaderThread
# Implements necessary classes for serial.threaded.Protocol
class SerialToNet(serial.threaded.Protocol):
    """serial->socket"""
    def __init__(self, target):
        self.socket = None
        self.target = target

    def __call__(self):
        return self

    def data_received(self, data):  # Called by thread when data received
        if self.socket is not None:
            self.socket.sendto(data, self.target) # Send all data to udp port, packetized automatically


if __name__ == '__main__':
    import argparse  # Useful module for argument parsing

    parser = argparse.ArgumentParser(
            description='Serial to UDP Sockets redirector.')

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


    group.add_argument(
        '-P', '--localIP',
        help='local UDP IP (default localhost)',
        default='')

    group.add_argument(
        '-p', '--localport',
        type=int,
        help='local UDP port (default 7777)',
        default=7777)

    group.add_argument(
            '-R', '--remoteIP',
            help='remote UDP IP (default localhost)',
            default=''
            )

    group.add_argument(
            '-r', '--remoteport',
            type=int,
            help='remote UDP port (default 8888)',
            default=8888
            )

    # Parses args and puts them in an accessable format
    args = parser.parse_args()

    # Connect to serial port, but do not open
    ser = serial.serial_for_url(args.SERIALPORT, do_not_open=True)
    ser.baudrate = args.BAUDRATE

    # Print info when starting
    if not args.quiet:
        sys.stderr.write('--- UDP to Serial redirect on '
                         '{p.name} at {p.baudrate}, '
                         'listening on {a.localIP}:{a.localport}, '
                         'broadcasting to {a.remoteIP}:{a.remoteport} ---\n'.format(p=ser, a=args))
        sys.stderr.write('--- type Ctrl-C / BREAK to quit ---\n')

    # Open serial port
    try:
        ser.open()
    except serial.SerialException as e:
        sys.stderr.write('Could not open serial port {}: {}\n'.format(ser.name, e))
        sys.exit(1)

    # Create helper class for serial.threaded, start threaded serial worker
    ser_to_net = SerialToNet((args.remoteIP, args.remoteport))
    serial_worker = serial.threaded.ReaderThread(ser, ser_to_net)
    serial_worker.start()

    # Start configuring socket
    soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    soc.bind((args.localIP, args.localport))
    
    # network <-> serial loop
    intentional_exit = False
    ser_to_net.socket = soc
    while True:
        try: 
            data = soc.recv(1024)  # Recieve data from socket in chunks of 1024 bytes
            ser.write(data)
        except KeyboardInterrupt:
            intentional_exit = True
            if not args.quiet:
                sys.stderr.write('\n--- exit ---\n')
            serial_worker.stop()
            break
        
        except socket.error as msg:
            if args.develop:
                raise
            if not args.quiet:
                sys.stderr.write('Error: {}\n'.format(msg))
            # Disconnect if socket error occurs
            break
