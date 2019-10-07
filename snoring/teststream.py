import RPi.GPIO as GPIO
import time
import pyaudio

def flash_LED(s):
    GPIO.output(18,GPIO.HIGH)
    time.sleep(s)
    GPIO.output(18,GPIO.LOW)

form_1 = pyaudio.paInt16 # 16-bit resolution
chans = 1 # 1 channel
samp_rate = 44100 # 44.1kHz sampling rate
chunk = 88200 # 2^12 samples for buffer
record_secs = 20 # seconds to record
dev_index = 3 # device index found by p.get_device_info_by_index(ii)

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(18,GPIO.OUT)

flash_LED(2)
audio = pyaudio.PyAudio()
time.sleep(2)
flash_LED(2)
stream = audio.open(format = form_1,rate = samp_rate,channels = chans,input = True, \
                    frames_per_buffer=chunk)
time.sleep(1)
flash_LED(1)
