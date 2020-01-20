import numpy as np
from scipy import signal
from scipy.fftpack import fft, dct
from scipy import stats
import csv
import os
import time
# import matplotlib.pyplot as plt

#############################################################
path = os.getcwd()
print(path)
sampling_rate = 4000
#############################################################
def nor(data):
    mi = np.min(data)*1.0
    ma = np.max(data)*1.0
    data = (2*data - ma - mi)/(ma - mi)
    return data


def stas_feature(data, spr):
    l = data.shape[0]  
    #fft
    yf = fft(data)
    yf = yf[:l//2]
    energy = 1/(l)*np.abs(yf)
    #feature
    r0 = 50*l//spr
    r1 = 250*l//spr
    r2 = 500*l//spr
    r3 = 800*l//spr
     
    mean = np.mean(energy)
    sd = np.std(energy)
    mean1 = np.mean(energy[r0:r1])/mean
    sd1 = np.std(energy[r0:r1])/sd
    mean2 = np.mean(energy[r1:r2])/mean
    sd2 = np.std(energy[r1:r2])/sd
    mean3 = np.mean(energy[r2:r3])/mean
    sd3 = np.std(energy[r2:r3])/sd
    return [mean1, mean2, mean3, sd1, sd2, sd3]

def stas_feature4(data, spr):
    l = data.shape[0]
    #fft
    yf = fft(data)
    yf = yf[:l//2]
    energy = 1/(l)*np.abs(yf)
    energy_scale = energy/scaling_factor
    # energy_scale = np.log(energy + 1)
    energy_scale = energy_scale - np.min(energy_scale)
    #feature
    r0 = 50*l//spr
    r1 = 250*l//spr
    r2 = 500*l//spr
    r3 = 800*l//spr
    # mean = np.mean(energy_scale)
    # sd = np.std(energy_scale)
    mean1 = np.mean(energy_scale[r0:r1])
    sd1 = np.std(energy_scale[r0:r1])
    mean2 = np.mean(energy_scale[r1:r2])
    sd2 = np.std(energy_scale[r1:r2])
    mean3 = np.mean(energy_scale[r2:r3])
    sd3 = np.std(energy_scale[r2:r3])
    return [mean1, mean2, mean3]

def stas_feature6(data, spr):
    l = data.shape[0]  
    #fft
    yf = fft(data)
    yf = yf[:l//2]
    energy = 1/(l)*np.abs(yf)
    energy_scale = energy/scaling_factor
    # energy_scale = np.log(energy + 1)
    energy_scale = energy_scale - np.min(energy_scale)
    #feature

    mean = np.mean(energy_scale)
    sd = np.std(energy_scale)
    skewness = stats.skew(energy_scale)
    kutoris = stats.kurtosis(energy_scale)
    median = np.median(energy_scale)
    
    return [mean, median]

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

def feature_extract(data, spr):
    n, l = data.shape[:]
    feature_vectors = []
    hw = np.hamming(l)  
    for i in range(0, n):
        sig = data[i]
        #sig = nor(sig)
        sig = sig - np.mean(sig)
        sig = sig * hw
        #fea = MFCC(sig, filter_banks)
        fea = stas_feature4(sig, spr)
        feature_vectors.append(fea)
    return feature_vectors   

def scaling(path):
    no_snoring = np.load(path)
    data = np.concatenate([no_snoring[0], no_snoring[2], no_snoring[4], no_snoring[6], no_snoring[8], no_snoring[10]])
    l = data.shape[0]
    hw = np.hamming(l)
    data = data * hw
    yf = fft(data)
    yf = yf[:l//2]
    energy = 1/(l)*np.abs(yf)
    return np.mean(energy)


#############################################################
#load data

for i in [1, 4, 5, 7, 8, 9]:
    scaling_factor = 1
    no_snoring = np.load(path + "/numerical/non_snoring_" + str(i) + ".wav.npy")
    n_snoring_sample = no_snoring.shape[0]
    print(n_snoring_sample)
    t1 = time.time()
    no_snoring_fea_vecs = feature_extract(no_snoring, sampling_rate)
    np.save(path + "/feature/" + "non_snoring_" + str(i), np.array(no_snoring_fea_vecs))
    t2 = time.time()
    print("feature extraction", (t2 -t1)/(n_snoring_sample))

    snoring = np.load(path + "/numerical/snoring_" + str(i) + ".wav.npy")
    n_snoring_sample = snoring.shape[0]
    print(n_snoring_sample)
    t1 = time.time()
    snoring_fea_vecs = feature_extract(snoring, sampling_rate)
    np.save(path + "/feature/" + "snoring_" + str(i), np.array(snoring_fea_vecs))
    t2 = time.time()
    print("feature extraction", (t2 -t1)/(n_snoring_sample))




