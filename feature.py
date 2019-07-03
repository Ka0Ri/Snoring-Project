import numpy as np
from scipy import signal
from scipy.fftpack import fft, dct
from scipy import stats
import csv
import os
import time
# import matplotlib.pyplot as plt

#############################################################
path = os.path.dirname(os.getcwd())
print(path)
sampling_rate = 4000
#############################################################

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

def stas_feature1(data, spr):
    l = data.shape[0]
    #fft
    yf = fft(data)
    yf = yf[:l//2]
    energy = (1/l)*np.abs(yf)
    r0 = 50*l//spr
    r1 = 150*l//spr
    r2 = 250*l//spr
    r3 = 450*l//spr
    r4 = 600*l//spr
    r5 = 900*l//spr
    r6 = 1200*l//spr

    mean = np.mean(energy) + 0.1
    sd = np.std(energy) + 0.1
    mean1 = np.mean(energy[r0:r1])/mean
    sd1 = np.std(energy[r0:r1])
    mean2 = np.mean(energy[r1:r2])/mean
    sd2 = np.std(energy[r1:r2])
    mean3 = np.mean(energy[r2:r3])/mean
    sd3 = np.std(energy[r2:r3])
    mean4 = np.mean(energy[r3:r4])/mean
    sd4 = np.std(energy[r3:r4])
    mean5 = np.mean(energy[r4:r5])/mean
    sd5 = np.std(energy[r5:r6])
    mean6 = np.mean(energy[r5:r6])/mean
    sd6 = np.std(energy[r5:r6])

    return [mean1, mean2, mean3, mean4, mean5, mean6]

def stas_feature2(data, spr):
    l = data.shape[0]
    #fft
    yf = fft(data)
    yf = yf[:l//2]
    energy = (1/l)*np.abs(yf)
    r0 = 50*l//spr
    r1 = 150*l//spr
    r2 = 250*l//spr
    r3 = 450*l//spr
    r4 = 600*l//spr
    r5 = 900*l//spr
    r6 = 1200*l//spr

    mean = np.mean(energy) + 0.1
    sd = np.std(energy) + 0.1
    mean1 = np.mean(energy[r0:r1])
    sd1 = np.std(energy[r0:r1])
    mean2 = np.mean(energy[r1:r2])
    sd2 = np.std(energy[r1:r2])
    mean3 = np.mean(energy[r2:r3])
    sd3 = np.std(energy[r2:r3])
    mean4 = np.mean(energy[r3:r4])
    sd4 = np.std(energy[r3:r4])
    mean5 = np.mean(energy[r4:r5])
    sd5 = np.std(energy[r5:r6])
    mean6 = np.mean(energy[r5:r6])
    sd6 = np.std(energy[r5:r6])

    return [mean1, mean2, mean3, mean4, mean5, mean6]

def stas_feature3(data, spr):
    l = data.shape[0]
    #fft
    yf = fft(data)
    yf = yf[:l//2]
    energy = (1/l)*np.abs(yf)
    r0 = 50*l//spr
    r1 = 150*l//spr
    r2 = 250*l//spr
    r3 = 350*l//spr
    r4 = 500*l//spr

    mean = np.mean(energy) + 0.1
    sd = np.std(energy) + 0.1
    mean1 = np.mean(energy[r0:r1])
    mean2 = np.mean(energy[r1:r2])
    mean3 = np.mean(energy[r2:r3])
    mean4 = np.mean(energy[r3:r4])
   
    return [mean1, mean2, mean3, mean4]

def stas_feature4(data, spr):
    l = data.shape[0]
    #fft
    yf = fft(data)
    yf = yf[:l//2]
    energy = 1/(l)*np.abs(yf)
    #feature
    r0 = 50*l//spr
    r1 = 300*l//spr
    r3 = 800*l//spr
     
    mean = np.mean(energy)
    sd = np.std(energy)
    mean1 = np.mean(energy[r0:r1])/mean
    sd1 = np.std(energy[r0:r1])/sd
    mean2 = np.mean(energy[r1:r3])/mean
    sd2 = np.std(energy[r1:r3])/sd
    skew = stats.skew(energy[r0:r3])
    return [mean1, mean2, sd1, sd2, skew]

def create_filter_banks(n_filters, spr, l):
    #create filter banks
    filter_banks = np.zeros([n_filters, l//2])
    lower_f = 50
    upper_f = spr//2
    band = np.linspace(1125*np.log(1 + lower_f/700), 1125*np.log(1 + upper_f/700), n_filters + 2)
    band = 700*(np.exp(band/1125) - 1)
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
        #normalize
        # sig = sig - np.mean(sig)
        # mi = 1.0*np.min(sig)
        # ma = 1.0*np.max(sig)
        # sig = (2*sig - (ma + mi))/(ma - mi)
        sig = sig * hw
        fea = stas_feature2(sig, spr)
        feature_vectors.append(fea)
    return feature_vectors   

#############################################################
#load data
snoring = np.load(path + '/numerical_data/snoring_new.wav.npy')
n_snoring_sample = snoring.shape[0]
print(n_snoring_sample)
t1 = time.time()
snoring_fea_vecs = feature_extract(snoring, sampling_rate)
np.save(path + '/feature/snoring_new_6mean', np.array(snoring_fea_vecs))
t2 = time.time()
print("feature extraction", (t2 -t1)/(n_snoring_sample))

snoring = np.load(path + '/numerical_data/none_snoring_new.wav.npy')
n_snoring_sample = snoring.shape[0]
print(n_snoring_sample)
t1 = time.time()
snoring_fea_vecs = feature_extract(snoring, sampling_rate)
np.save(path + '/feature/none_snoring_new_6mean', np.array(snoring_fea_vecs))
t2 = time.time()
print("feature extraction", (t2 -t1)/(n_snoring_sample))

# snoring = np.load(path + '/numerical_data/snoring101.wav.npy')
# n_snoring_sample = snoring.shape[0]
# print(n_snoring_sample)
# t1 = time.time()
# snoring_fea_vecs = feature_extract(snoring, sampling_rate)
# np.save(path + '/feature/snoring_101_4mean', np.array(snoring_fea_vecs))
# t2 = time.time()
# print("feature extraction", (t2 -t1)/(n_snoring_sample))

# snoring = np.load(path + '/numerical_data/none_snoring101.wav.npy')
# n_snoring_sample = snoring.shape[0]
# print(n_snoring_sample)
# t1 = time.time()
# snoring_fea_vecs = feature_extract(snoring, sampling_rate)
# np.save(path + '/feature/none_snoring_101_4mean', np.array(snoring_fea_vecs))
# t2 = time.time()
# print("feature extraction", (t2 -t1)/(n_snoring_sample))




