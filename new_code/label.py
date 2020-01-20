import numpy as np
from scipy import signal
from scipy.fftpack import fft, dct
from scipy import stats
import csv
import os
import time
import pickle
import wave
import struct
import matplotlib.pyplot as plt
import h5py

###################################################################
path = os.getcwd()
print(path)
sampling_rate = 4000
n_sample = 128*sampling_rate//1000
#load model
model = pickle.load(open(path + "/model/model1/MFCC_model_SVM_linear.w", 'rb'))
###################################################################

def create_filter_banks(n_filters, spr, l):
    #create filter banks
    filter_banks = np.zeros([n_filters, l//2])
    lower_f = 50
    upper_f = spr//2
    band = np.linspace(2595*np.log(1 + lower_f/700), 2595*np.log(1 + upper_f/700), n_filters + 2)
    band = 700*(np.exp(band/2595) - 1)
    band = np.round(band*1000/(2*spr))
    for i in range(1, n_filters + 1):
        start = int(band[i - 1])
        end = int(band[i + 1])
        mid = int(band[i])
        filter_banks[i - 1][start:mid] = (1.0*np.arange(start, mid) - start)/(mid - start)
        filter_banks[i - 1][mid:end] = (end - 1.0*np.arange(mid, end))/(end - mid)
    return filter_banks

def MFCC(data, filter_banks):
    #fft
    sig = data
    l = sig.shape[0]
    yf = fft(sig)
    yf = yf[:l//2]
    energy = (1/l)*np.abs(yf)
    n_filters = filter_banks.shape[0]
    #filter
    coeff = []
    for i in range(0, n_filters):
        coeff.append(np.log(np.sum(filter_banks[i] * energy)))
    dct_coeff = dct(np.array(coeff))
    return dct_coeff[:n_filters//2]

filter_banks = create_filter_banks(26, sampling_rate, 512)


def run_test(sig, spr, n_sample):
    feature_vector = []
    hw = np.hamming(n_sample)
    for i in np.arange(1/2, sig.shape[0], 1/2):
        s = int(n_sample*(i - 1/2))
        e = int(n_sample*(i + 1/2))
        if(e > sig.shape[0]):
            break
        data = sig[s:e]
        fea = MFCC(data, filter_banks)
        feature_vector.append(fea)
        
       
    predicted = model.predict(np.array(feature_vector))
    longest_len = 0
    i = 0
    while(i < len(predicted)):
        if(predicted[i] == 0):
            len_ = 1
            j = i + 1
            while(j < len(predicted) and predicted[j] == 0):
                len_ = len_ + 1
                j = j + 1
            if(len_ > longest_len):
                longest_len = len_
            i = j + 1
        else:
            i = i + 1

    if(longest_len > 8):
        return 1
    return 0

def count_snoring(sig, spr, n_sample):
    feature_vector = []
    hw = np.hamming(n_sample)
    for i in np.arange(1/2, sig.shape[0], 1/2):
        s = int(n_sample*(i - 1/2))
        e = int(n_sample*(i + 1/2))
        if(e > sig.shape[0]):
            break
        data = sig[s:e]
        fea = MFCC(data, filter_banks)
        feature_vector.append(fea)
         
    predicted = model.predict(np.array(feature_vector))
    if(np.sum(predicted) < 3 * predicted.shape[0] / 4):
        return 1
    else:
        return 0

############################################################
def process(waveFile, max_t):
    snoring = []
    framming_t = 1
    n_frames = int(4000*framming_t)
    for i in range(0, max_t):
        #read stream
        waveData = waveFile.readframes(n_frames)
        data = struct.unpack("<4000h", waveData)
        sig = np.array(data)
        
        predict_snoring = run_test(sig, sampling_rate, n_sample)
        #print("snoring at ", i + 1,"-th second: ", predict_snoring)
        snoring.append([i + 1, predict_snoring])
    waveFile.close() 
    return np.array(snoring)

def create_spectogram_withlabel(waveFile, max_t, frame = 1, labels=None):
    fs = 4000
    n_frames = int(fs*frame)
    hm = np.hamming(fs*frame)
    spectograms = []
    targets = []
    for i in range(0, max_t, frame):
        #read stream
        waveData = waveFile.readframes(n_frames)
        data = struct.unpack('<' + str(fs*frame) + 'h', waveData)
        #normalized data
        sig = np.array(data)

        if(labels == None):
            targets.append(count_snoring(sig, fs, n_sample))
        else:
            targets.append(np.sum(labels[i:i+5, 1]))

        sig = sig - np.mean(sig)

        plot = plt.specgram(sig, NFFT = 256, Fs=fs)[0]

        # scale = (255.0 * np.std(sig)) / 100
        # plot = (plot - np.min(plot))/(np.max(plot) - np.min(plot))
        # plot = np.uint8(scale * plot)
        #f, t, plot = signal.spectrogram(sig, fs=fs)
        spectograms.append(plot)

    waveFile.close()

    return np.array(spectograms), targets
 
def sig2spec(sig):
    sig = sig - np.mean(sig)
    fs = 4000
    plot = plt.specgram(sig, NFFT = 256, Fs=fs)[0]

    scale = (255.0 * np.std(sig)) / 200
    plot = (plot - np.min(plot))/(np.max(plot) - np.min(plot))
    plot = np.uint8(scale * plot)
    #f, t, plot = signal.spectrogram(sig, fs=fs)
    return plot

def create_spectrogram():
    for f in [1, 4, 5, 7, 8, 9]:
        no_snoring = np.load(path + "/1s/non_snoring_" + str(f) + ".wav.npy")
        n_snoring_sample = no_snoring.shape[0]
        print(n_snoring_sample)
        spectrograms = []
        targets = []
        cl = []

        for i in range(0, n_snoring_sample, 3):
            sig = no_snoring[i]
            spec = sig2spec(sig)
            spectrograms.append(spec)
            targets.append(0)
            cl.append(f)


        snoring = np.load(path + "/1s/snoring_" + str(f) + ".wav.npy")
        n_snoring_sample = snoring.shape[0]
        print(n_snoring_sample)
      
        for i in range(0, n_snoring_sample):
            sig = snoring[i]
            spec = sig2spec(sig)
            spectrograms.append(spec)
            targets.append(1)
            cl.append(f)

        hf = h5py.File(path + "/spectrograms/" + str(f) + ".h5", 'w')
        hf.create_dataset('spectrograms', data=np.array(spectrograms))
        hf.create_dataset('targets', data=np.array(targets))
        hf.create_dataset('class', data=np.array(cl))
        hf.close()

if __name__ == "__main__":
    # index = "1"
    # for f in os.listdir(path + "/sound/" + index + "/"):
        
    #     max_t = 15 * 60
    #     name = index + "-" + f[:-4]
    #     print(name)

    #     # waveFile = wave.open(path + "/sound/" + index + "/" + f, 'r')
    #     # snoring = process(waveFile, max_t)
    #     # np.savetxt(path + "/sound/label/" + name + ".txt", snoring.astype(int), fmt='%i')

    #     waveFile = wave.open(path + "/sound/" + index + "/" + f, 'r')
    #     #labels = np.loadtxt(path + "/sound/label/" + name + ".txt")
    #     spectograms, targets = create_spectogram_withlabel(waveFile, max_t=max_t, frame = 5)
    #     hf = h5py.File(path + "/sound/spectogram_5s_scale/" + name + ".h5", 'w')
    #     hf.create_dataset('spectograms', data=spectograms)
    #     hf.create_dataset('targets', data=targets)
    #     hf.close()
    create_spectrogram()




        
        