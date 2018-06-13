import sys
import glob
import serial
import struct
import socket
import threading
from queue import Queue


#Checking for proper amount of arguments
#NOTE: Doesn't check that arguments are in proper format
if len(sys.argv) != 7:
    raise ValueError("Proper usage: %s serial_port baudrate udp_recieve_ip udp_recieve_port udp_send_ip udp_send_port" % sys.argv[0]) 
else:               
    curPort = sys.argv[1]
    baud = int(sys.argv[2])
    host = sys.argv[3]
    port = int(sys.argv[4])
    returnIP = sys.argv[5]
    returnPort = int(sys.argv[6])

#Common baud rates used in Arduinos
BAUDRATES = (50, 75, 110, 134, 150, 200, 300, 600, 1200, 1800, 2400, 4800, 9600, 19200, 38400, 57600, 115200)

def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    #Support for other platforms including windows and cygwin
    if sys.platform.startswith('win'): 
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'): 
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    #Goes through proposed valid ports, checking them by opening a serial connection
    result = []
    for port in ports:
        try:
            s = serial.Serial(port) #Opens serial connection
            s.close()
            result.append(port)
        except (OSError, serial.SerialException): #On fail to open, continues checking
            pass
    return result

#Check if any supported serial ports are found
ports = serial_ports()
if len(ports) == 0:
    raise ValueError("No serial ports found or all are currently used!")

#Check that entered baud rate is in predefined list of baud rates
if baud not in BAUDRATES:
    raise ValueError("Invalid baud rate! Valid baud rates: " + ", ".join(BUADRATES))

#Check that entered port name is in list of valid serial ports
if curPort not in ports:
    raise ValueError("Invalid serial port! Available serial ports: " + "\n".join(ports))

ser = serial.Serial(curPort, baud)  
ser.xonxoff = True 
ser.stopbits = 1

# Datagram (udp) socket
try:
    soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
except Exception as msg:
    raise EnvironmentError('Failed to create UDP socket. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])

# Bind socket to localhost and port
try:
    soc.bind((host, port))
except Exception as msg:
    raise EnvironmentError('UDP Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])



runThreads = True #When false, all active threads will try to exit 
UDPQueue = Queue()
SerialQueue = Queue()
serialLock = threading.Lock() #Needed because serial is not threadsafe

class UDPListener(threading.Thread):
    def __init__(self, soc, UDPQueue):
        threading.Thread.__init__(self)
        self.UDPQueue = UDPQueue #Reference to queue, used by SerialSender
        self.soc = soc           #Reference to UDP Socket, used by UDPSender
    
    def run(self):
        while runThreads:
            data, addr = self.soc.recvfrom(1024)
            print("UDPL: %s" % str(data))
            for b in data:
                UDPQueue.put(b)
    

class SerialSender(threading.Thread):
    def __init__(self, ser, UDPQueue):
        threading.Thread.__init__(self)
        self.UDPQueue = UDPQueue #Reference to queue, used by UDPListener
        self.ser = ser           #Reference to Serial Port, used by SerialListener

    def run(self):
        while runThreads:
            data = self.UDPQueue.get()
            print("SS waiting for lock")
            #serialLock.acquire()
            print("SS got lock")
            self.ser.write(data)
            print("SS: %s" % str(data))
            #serialLock.release()
            print("SS lost lock")

class SerialListener(threading.Thread):
    def __init__(self, ser, SerialQueue):
        threading.Thread.__init__(self)
        self.SerialQueue = SerialQueue
        self.ser = ser
    def run(self):
        while runThreads:
            #print("SL waiting for lock")
            #serialLock.acquire() 
            #print("SL got lock")
            data = ser.read()
            if data != b'\x00':
                print("SL: %s" % str(data))
            self.SerialQueue.put(data)
            #serialLock.release()
            #print("SL lost lock")

class UDPSender(threading.Thread):
    def __init__(self, soc, SerialQueue):
        threading.Thread.__init__(self)
        self.SerialQueue = SerialQueue
        self.soc = soc
    def run(self):
        while runThreads:
            data = self.SerialQueue.get()
            #print("UDPS: %s" % str(data))
            soc.sendto(data, (returnIP, returnPort))

threads = [UDPListener(soc, UDPQueue), SerialSender(ser, UDPQueue), None, UDPSender(soc, SerialQueue)]
for thread in threads:
    try:
        thread.start()
    except:
        pass

import time
time.sleep(1.1)
threads[2] = SerialListener(ser, SerialQueue)
threads[2].start()
