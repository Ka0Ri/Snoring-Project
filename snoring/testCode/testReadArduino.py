import time
import serial
import RPi.GPIO as GPIO
import string

GPIO.setmode(GPIO.BOARD)
port = "/dev/serial0"
#port = "/dev/ttyUSB0"
baud = 115200
#ser = serial.Serial(port, baud, parity = serial.PARITY_NONE, stopbits = serial.STOPBITS_ONE, bytesize = serial.EIGHTBITS, timeout = 3.0)
ser = serial.Serial(port, baud, timeout = 3)
ser.close()
#ser.open()
print ('Start reading data ...')
while True:
    
    try:
        ser.open()
        
        #ser.write(string.translate(line.rootValue))
        x = ser.write(str("True").encode('UTF-8'))
        
        #line = ser.readline()
        #rcv = ser.read(10)
        #print(line)
        #time.sleep(0.1)
        #remaining_bytes = ser.inWaiting()
        print('sent data')
    except (OSError, serial.serialutil.SerialException):
        print("No data")
        ser.close()
        pass
    ser.close()
    time.sleep(3)
    #except Exception:
        #print (str(e))
        #pass
