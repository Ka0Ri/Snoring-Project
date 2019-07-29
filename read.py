
import numpy as np
from scipy.io import wavfile
from scipy.signal import resample_poly
from scipy.signal import resample_poly, firwin, freqz, lfilter, cheby1, butter
# import matplotlib.pyplot as plt
from scipy import fftpack
import os

def cut(frames, n_sample):
    samples = []
    for frame in frames:
        for i in np.arange(1/2, frame.shape[0], 1/2):
            s = int(n_sample*(i - 1/2))
            e = int(n_sample*(i + 1/2))
            if(e > frame.shape[0]):
                break
            samples.append(frame[s:e])
    return np.array(samples)

def framing(f, spr, t):
    fs, data = wavfile.read(path + "/using_data/" + f)
    print(fs)
    if(fs == 8000):
        data = resample_poly(data, spr, 8000)
    n_sample = t*spr//1000
    
    sound = cut(np.array([data]), n_sample)
    np.save(path + "/numerical_data/" + f, np.array(sound))
    return sound.shape[0]
    
def cut_newdata(path, f):
    #read wave file, under wav extension
    fs, data = wavfile.read(path + f + ".wav")
    y = resample_poly(data, 4000, fs).astype(np.int16)
    fs = 4000
    print("sampling rate ", fs, "length ", 1./3600*y.shape[0]/fs)
    start_time = (5*60)*fs
    end_time = (300*60)*fs
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

def simple_filter(path, f):
    #read wave file, under wav extension
    fs, data = wavfile.read(path + f + ".wav")
    y = resample_poly(data, sampling_rate, fs)
    print("sampling rate ", fs, "length ", 1./3600*data.shape[0]/fs)
    cut1 = 50
    cut2 = 1000
    length = 15
    win = "hamming"
    filter_ = firwin(length, [cut1, cut2], window=win, pass_zero=False, fs=4000)
    temp = lfilter(filter_, 1, y).astype(np.int16)
    
    wavfile.write(path + f + "/" + f + "_filter.wav", sampling_rate, temp)
    
def concatdata(path):
    snoring = np.zeros(1)
    for f in os.listdir(path + "snoring/"):
        print(f)
        fs, data = wavfile.read(path + "snoring/" + f)
        # data = data - np.mean(data)
        snoring = np.concatenate([snoring, data])
    snoring = snoring.flatten()
    wavfile.write(path + "none_snoring_new.wav", fs, snoring.astype(np.int16))

##################################################################

path = os.path.dirname(os.getcwd())
sampling_rate = 4000
s = framing("noise_snoring.wav", sampling_rate, 128)
print(s)
# concatdata(path + "/using_data/")
##################################################################
# fs, data = wavfile.read(path + "/old_data/snoring_3.wav")
# data = resample_poly(data, sampling_rate, 8000)
# snore3 = cut([data], 512)
# fs, data = wavfile.read(path + "/old_data/snoring_4.wav")
# data = resample_poly(data, sampling_rate, 8000)
# snore4 = cut([data], 512)
# fs, data = wavfile.read(path + "/old_data/snoring_5.wav")
# data = resample_poly(data, sampling_rate, 8000)
# snore5 = cut([data], 512)
# fs, data = wavfile.read(path + "/old_data/snoring_7.wav")
# data = resample_poly(data, sampling_rate, 8000)
# snore7 = cut([data], 512)
# fs, data = wavfile.read(path + "/old_data/snoring_17.wav")
# data = resample_poly(data, sampling_rate, 8000)
# snore17 = cut([data], 512)
# fs, data = wavfile.read(path + "/old_data/snoring_18.wav")
# data = resample_poly(data, sampling_rate, 8000)
# snore18 = cut([data], 512)
# fs, data = wavfile.read(path + "/old_data/snoring_19.wav")
# data = resample_poly(data, sampling_rate, 8000)
# snore19 = cut([data], 512)

# snore = np.concatenate([snore3, snore4, snore5, snore7, snore18, snore19], axis=0)
# np.save(path + "/numerical_data/snoring_old1.wav", np.array(snore))
# print(snore.shape)

# fs, data = wavfile.read(path + "/old_data/normal.wav")
# data = resample_poly(data, sampling_rate, 8000)
# no_snore = cut([data], 512)
# np.save(path + "/numerical_data/none_snoring_old1.wav", np.array(no_snore))
# print(no_snore.shape)




