
# from sklearn import svm
# from sklearn.naive_bayes import GaussianNB
# from sklearn.linear_model import LogisticRegression
# from sklearn.mixture import GaussianMixture
# from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
import numpy as np
from scipy.signal import resample_poly
import os
import pickle
import wave, struct
import sounddevice as sd
from scipy.fftpack import fft
#############################################################
path = os.getcwd()
print(path)
sampling_rate = 4000
n_sample = 128*sampling_rate//1000
#load model
model = pickle.load(open(path + "/model/full/model_LDA.w", 'rb'))
scaling_factor = 1
  
#############################################################
def nor(sig):
    mi = np.min(sig)*1.0
    ma = np.max(sig)*1.0
    data = (2*sig - ma - mi)/(ma - mi)
    return data

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
     
    mean = np.mean(energy[r0:r3])
    return mean

def run_test2(sig, spr, n_sample, scaling_factor):
    sum_pre = []
    for i in np.arange(1/2, sig.shape[0], 1/2):
        s = int(n_sample*(i - 1/2))
        e = int(n_sample*(i + 1/2))
        if(e > sig.shape[0]):
            break
        data = sig[s:e]
        mean = fea(data, sampling_rate)
        if(mean > 3*scaling_factor):
           sum_pre.append(0)
        else:
            sum_pre.append(1)

    print(sum_pre)
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
    
    if(longest_len > 3):
        return True
    return False

def run_sound(sig, spr):
    sound = nor(sig)
    sd.play(sound, sampling_rate, blocking=True)

def scaling(sig):
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
############################################################

waveFile = wave.open(path + "/python_code/1003.wav", 'r')
#length = waveFile.getnframes()
framming_t = 1
n_frames = int(4000*framming_t)

def process(max_t, threshold):
    snoring = []
    for i in range(0, max_t):
        #read stream
        waveData = waveFile.readframes(n_frames)
        data = struct.unpack("<4000h", waveData)
        sig = np.array(data)
        #reference frame
        if(i == 0):
            scaling_factor = scaling(sig)
            print(scaling_factor)
        else:
            run_sound(sig, sampling_rate)
            predict_snoring = run_test2(sig, sampling_rate, n_sample, scaling_factor)
            print("snoring at ",i,"-th second: ", predict_snoring)
            snoring.append(predict_snoring)
            if(i >= 30):
                snoring.append(predict_snoring)
                total = np.sum(snoring)
                print("The number of seconds snoring occured ", total)
                if(total > threshold):
                    print("snore!!!!")
                else:
                    print("zzzzzz")
                snoring.pop(0)
    waveFile.close()  


if __name__ == "__main__":
    process(100, 20)
     




