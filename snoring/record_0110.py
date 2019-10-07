#! /usr/bin/python3
import pyaudio
import wave, struct
from utls import *
from scipy.signal import resample_poly
import sys

import time
import subprocess
import RPi.GPIO as GPIO

flash_LED(1, 4)
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

def start_stream(record_secs=100, threshold=5):
    audio = pyaudio.PyAudio() # create pyaudio instantiation
    stream = audio.open(format = form_1,rate = samp_rate,channels = 1, input = True, \
                    frames_per_buffer=chunk)
    snoring = []
    log = []
    for ii in range(0, record_secs):
        data = stream.read(chunk, exception_on_overflow=False)
        signal = struct.unpack("<44100h", data)
        sig = resample_poly(signal, sampling_rate, chunk)
        if(ii == 0):
            continue
        elif(ii == 1):
            scaling_factor = scaling2(sig)
            print(scaling_factor)
        else:
            predict_snoring = run_test2(sig, sampling_rate, n_sample, scaling_factor)
            print("snoring at ",ii,"-th second: ", predict_snoring)
            snoring.append(predict_snoring)
            if(ii >= 30):
                total = np.sum(snoring)
                print("The number of seconds snoring occured ", total)
                if(ii % 5 == 0):
                    if(total > threshold):
                        log.append(1)
                        print("snore!!!!")
                        GPIO.output(21, GPIO.HIGH)
                    else:
                        log.append(0)
                        print("zzzzzz")
                        GPIO.output(21, GPIO.LOW)
                snoring.pop(0)

    # stop the stream, close it, and terminate the pyaudio instantiation
    stream.stop_stream()
    stream.close()
    audio.terminate()
    np.save("test1", np.array(log))
   
    for i in range(5):
        flash_LED(0.2, 4)
        time.sleep(0.2)
    GPIO.output(4, GPIO.LOW)
    GPIO.output(21, GPIO.LOW)

if __name__ == "__main__":
    check_and_turn_on_BT(sys.argv[1])
    start_stream(int(sys.argv[2]))


