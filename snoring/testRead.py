import time
import serial
port = "/dev/serial0"
#port = "/dev/ttyUSB0"
baud = 115200

#ser = serial.Serial(port, baud, parity = serial.PARITY_NONE, stopbits = serial.STOPBITS_ONE, bytesize = serial.EIGHTBITS, timeout = 3.0)
ser = serial.Serial(port, baud, timeout = 3)
ser.close()
print ('Start reading data ...')
while True:
    
    try:
        print('Data found!!!')
        ser.open()
        x = ser.write('1'.encode('UTF-8'))
        time.sleep(0.2)
        print(x)
    except (OSError, serial.serialutil.SerialException):
        print("No data")
        ser.close()
        pass
    ser.close()
ser.close()
