import numpy as np
import os
import pickle
from scipy.fftpack import fft
import time


#############################################################
sampling_rate = 4000
n_sample = 128*sampling_rate//1000

hw = np.hamming(n_sample//2)
#load model
model = pickle.load(open(os.getcwd() + "/model/full/model_DT.w", 'rb'))
#############################################################

def find_longest_len(sum_pre):
    longest_len = 0
    i = 0
    while(i < len(sum_pre)):
        if(sum_pre[i] == 0):
            len_ = 1
            j = i + 1
            while(j < len(sum_pre) and sum_pre[j] == 0):
                len_ = len_ + 1
                j = j + 1
            if(len_ > longest_len):
                longest_len = len_
            i = j + 1
        else:
            i = i + 1
    
    return longest_len

def stas_feature4(data, spr, scaling_factor):
    l = data.shape[0]
    #fft
    data = data * hw
    yf = fft(data)
    yf = yf[:l//2]
    energy = 1/(l)*np.abs(yf)
    energy_scale = energy*scaling_factor
    #energy_scale = np.log(energy)
    energy_scale = energy_scale - np.min(energy_scale)
    #feature
    r0 = 50*l//spr
    r1 = 250*l//spr
    r2 = 500*l//spr
    r3 = 800*l//spr
    
    mean1 = np.mean(energy_scale[r0:r1])
    mean2 = np.mean(energy_scale[r1:r2])
    mean3 = np.mean(energy_scale[r2:r3])
    return [mean1, mean2, mean3]

def run_test(sig, spr, n_sample, scaling_factor):
    sum_pre = []
    for i in np.arange(1/2, sig.shape[0], 1/2):
        s = int(n_sample*(i - 1/2))
        e = int(n_sample*(i + 1/2))
        if(e > sig.shape[0]):
            break
        data = sig[s:e]
        fea_vec = stas_feature4(data, spr, scaling_factor)
        pre = model.predict([fea_vec])[0]
        sum_pre.append(pre)
    
    return sum_pre

def scaling(data):
    l = data.shape[0]
    yf = fft(data)
    yf = yf[:l//2]
    energy = 1/(l)*np.abs(yf)
    return np.mean(energy)
            
def fea(data, spr):
    l = data.shape[0]
    #fft
    hw = np.hamming(l)
    data = data * hw
    yf = fft(data)
    yf = yf[:l//2]
    energy = 1/(l)*np.abs(yf)
    energy = energy - np.min(energy)
    #feature
    r0 = 50*l//spr
    r1 = 250*l//spr
    r2 = 500*l//spr
    r3 = 800*l//spr
     
    mean = np.mean(energy[r0:r2])
    return mean

def run_test2(sig, spr, n_sample, scaling_factor):
    #scaling_factor = 1
    sum_pre = []
    for i in np.arange(1/2, sig.shape[0], 1/2):
        s = int(n_sample*(i - 1/2))
        e = int(n_sample*(i + 1/2))
        if(e > sig.shape[0]):
            break
        data = sig[s:e]
        mean = fea(data, sampling_rate)
        if(mean > 4*scaling_factor):
           sum_pre.append(0)
        else:
            sum_pre.append(1)       
    return sum_pre

def scaling2(sig):
    log = []
    for i in np.arange(1/2, sig.shape[0], 1/2):
        s = int(n_sample*(i - 1/2))
        e = int(n_sample*(i + 1/2))
        if(e > sig.shape[0]):
            break
        data = sig[s:e]
        mean = fea(data, sampling_rate)
        log.append(mean)
    return np.mean(np.array(log))

