#! /usr/bin/python3
import pyaudio
import wave, struct
from utls import *
from scipy.signal import resample_poly
import RPi.GPIO as GPIO
import time
import subprocess


def flash_LED(s):
    GPIO.output(18,GPIO.HIGH)
    time.sleep(s)
    GPIO.output(18,GPIO.LOW)
    
    
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(18,GPIO.OUT)

flash_LED(1)
time.sleep(1)


form_1 = pyaudio.paInt16 # 16-bit resolution
chans = 1 # 1 channel
samp_rate = 44100 # 44.1kHz sampling rate
chunk = 44100 # 2^12 samples for buffer
record_secs = 20 # seconds to record
dev_index = 3 # device index found by p.get_device_info_by_index(ii)

# create pyaudio stream
sampling_rate = 4000
# loop through stream and append audio chunks to frame array

def start_stream(record_secs=100, threshold=20):
    audio = pyaudio.PyAudio() # create pyaudio instantiation
    stream = audio.open(format = form_1,rate = samp_rate,channels = chans, \
                    input_device_index = dev_index,input = True, \
                    frames_per_buffer=chunk)
    flash_LED(1)
    snoring = []  
    for ii in range(0, record_secs):
        data = stream.read(chunk, exception_on_overflow=False)
        signal = struct.unpack("<44100h", data)
        sig = resample_poly(signal, sampling_rate, chunk)
        if(ii == 0):
            scaling_factor = scaling(sig)
            print(scaling_factor)
        else:
            predict_snoring = run_test2(sig, sampling_rate, n_sample, scaling_factor)
            print("snoring at ",i,"-th second: ", predict_snoring)
            snoring.append(predict_snoring)
            if(i >= 30):
                snoring.append(predict_snoring)
                total = np.sum(snoring)
                print("The number of seconds snoring occured ", total)
                if(total > threshold):
                    print("snore!!!!")
                    flash_LED(0.2)
                else:
                    print("zzzzzz")
                snoring.pop(0)

    # stop the stream, close it, and terminate the pyaudio instantiation
    GPIO.output(18,GPIO.LOW)
    stream.stop_stream()
    stream.close()
    audio.terminate()
    subprocess.call('/home/pi/snoring/autodis', shell=True)
    for i in range(5):
        flash_LED(0.2)
        time.sleep(0.2)

if __name__ == "__main__":
    check_and_turn_on_BT("34_81_F4_38_F6_48")
    start_stream(50, 20)


