#! /usr/bin/python3
import pyaudio
import wave, struct
from utls import *
from scipy.signal import resample_poly
import sys
import time
import datetime
import RPi.GPIO as GPIO

flash_LED(1, 4)
time.sleep(1)

form_1 = pyaudio.paInt16 # 16-bit resolution
chans = 1 # 1 channel
samp_rate = 4000 # 44.1kHz sampling rate
chunk = 4000 # 2^12 samples for buffer
# seconds to record
dev_index = 3 # device index found by p.get_device_info_by_index(ii)

# create pyaudio stream
sampling_rate = 4000
# loop through stream and append audio chunks to frame array
log_file_name = datetime.datetime.now()
log_file_name = log_file_name.replace(":", "-")
f_log = open(log_file_name + ".txt", "w+")

def start_stream(params_dict):
    audio = pyaudio.PyAudio() # create pyaudio instantiation
    stream = audio.open(format=form_1, rate=samp_rate, channels=1, input=True, frames_per_buffer=chunk)
    snoring = []
    for ii in range(0, params_dict["RECORD_TIME"]):
        data = stream.read(chunk, exception_on_overflow=False)
        sig = np.frombuffer(data, 'int16')
        #sig = struct.unpack("<4000h", data)
        #sig = resample_poly(signal, sampling_rate, chunk)
        if(ii == 0):
            continue
        elif(ii == 1):
            scaling_factor = scaling(sig)
            print(scaling_factor)
        else:
            predict_snoring = snore_1_second(sig, params_dict)
            print("snoring at %d is %d\n"%(ii, predict_snoring))
            
            #write file
            f_log.writelines("at %d is %d"%(ii, predict_snoring))

            snoring.append(predict_snoring)
            # if(predict_snoring == True):
            #     send_signal_TX("11111111\n") 
            # else:
            #     send_signal_TX("00000000\n")
            if(ii >= 30):
                total = np.sum(snoring)
                print("The number of seconds snoring occured ", total)
                if(ii % params_dict["WAITTING_TIME"] == 0):
                    if(total > params_dict["SNORE_PER_30SECONDS"]):
                        GPIO.output(21, GPIO.HIGH)
                    else:                        
                        GPIO.output(21, GPIO.LOW)

                    #reset opened file
                    f_log.close()
                    f_log = open(log_file_name, "a")
                snoring.pop(0)

    # stop the stream, close it, and terminate the pyaudio instantiation
    stream.stop_stream()
    stream.close()
    audio.terminate()
   
    for i in range(5):
        flash_LED(0.2, 4)
        time.sleep(0.2)
    GPIO.output(4, GPIO.LOW)
    GPIO.output(21, GPIO.LOW)
    #send_signal_TX("00000101\n")

if __name__ == "__main__":
    params_dict = read_params()
    check_and_turn_on_BT(params_dict["MAC_ADDRESS"])
    start_stream(params_dict)


