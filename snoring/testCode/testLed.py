import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
chan_list = [4, 21]
GPIO.setup(chan_list,GPIO.OUT)

def flash_LED(s, pin):
    GPIO.output(pin, GPIO.HIGH)
    time.sleep(s)
    #GPIO.output(pin,GPIO.LOW)


flash_LED(1, 4)
time.sleep(1)
flash_LED(1, 21)