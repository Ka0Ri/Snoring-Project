import numpy as np
# from scipy.signal import resample_poly
import os
import pickle
import wave, struct
from utls import *
#############################################################
path = (os.getcwd())

sampling_rate = 4000
n_sample = 128*sampling_rate//1000
#############################################################

############################################################

waveFile = wave.open(path + "/test2.wav", 'r')
length = waveFile.getnframes()
framming_t = 1
n_frames = 4000*framming_t

if __name__ == "__main__":
    for i in range(0,length):
        print(i)
        #read stream
        waveData = waveFile.readframes(n_frames)
        data = struct.unpack("<4000h", waveData)
        #resampling
        # sig = resample_poly(data, sampling_rate, 8000)    
        sig = np.array(data)
        if(i == 0):
            scaling_factor = scaling(sig)
            print(scaling_factor)
        else:
            #run_sound(sig, sampling_rate)
            predict_snoring = run_test(sig, sampling_rate, n_sample)
            print(predict_snoring)

    waveFile.close()   




