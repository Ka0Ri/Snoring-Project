
import numpy as np
from scipy.io import wavfile
from scipy.signal import resample_poly
from scipy.signal import resample_poly, firwin, freqz, lfilter, cheby1, butter
# import matplotlib.pyplot as plt
from scipy import fftpack
import os
from random import randrange

def cut(frames, n_sample):
    samples = []
    for frame in frames:
        for i in np.arange(1/2, frame.shape[0], 1):
            s = int(n_sample*(i - 1/2))
            e = int(n_sample*(i + 1/2))
            if(e > frame.shape[0]):
                break
            samples.append(frame[s:e])
    return np.array(samples)

def framing(f, spr, t):
    n_sample = t*spr//1000
    for f in os.listdir(path + "/sound/new_data/snoring/"):
        print(f)
        if(f == "snoring_9.wav"):
            fs, data = wavfile.read(path + "/sound/new_data/snoring/" + f)
            # data = data - np.mean(data)
            sound = cut(np.array([data]), n_sample)
            np.save(path + "/numerical/xsnoring_6", np.array(sound))
            print(sound.shape[:])
    return sound.shape[:]
    
def cut_newdata(path, f):
    #read wave file, under wav extension
    fs, data = wavfile.read(path + f + ".wav")
    y = resample_poly(data, 4000, fs).astype(np.int16)
    fs = 4000
    print("sampling rate ", fs, "length ", 1./3600*y.shape[0]/fs)
    start_time = (0*60)*fs
    end_time = (427*60)*fs
    step = 30*60*fs
    while (start_time < end_time):
        s = start_time
        e = start_time + step
        if(e > end_time):
            e = end_time
        temp = y[int(s):int(e)]
        start_time = e
        name = str(int(s/(60*fs))) + "-" + str(int(e/(60*fs))) + ".wav"
        wavfile.write(path + f + "/" + name, fs, temp)

def randomly_cut_30s(path):
    fs, data = wavfile.read(path + "1-9.wav")
    y = resample_poly(data, 4000, fs).astype(np.int16)
    fs = 4000
    print("sampling rate ", fs, "length ", 1./3600*y.shape[0]/fs)
    l = data.shape[0]
    length = fs*30
    for i in range(100):
        start = randrange(l-30)
        sub = y[start:start+length]
        wavfile.write(path + "1-9/" + str(i) + ".wav", fs, sub)


##################################################################
path = os.getcwd()
# concatdata(path + "/sound/new_data/")
# framing("non_snoring_norm.wav", 4000, 128)
randomly_cut_30s(path + "/sound/")






