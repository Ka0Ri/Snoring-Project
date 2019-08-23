
# from sklearn import svm
# from sklearn.naive_bayes import GaussianNB
# from sklearn.linear_model import LogisticRegression
# from sklearn.mixture import GaussianMixture
# from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
import numpy as np
import os
import pickle
import sounddevice as sd
from scipy.fftpack import fft
#############################################################
path = (os.getcwd())

sampling_rate = 4000
n_sample = 128*sampling_rate//1000
#load model
model = pickle.load(open(path + "/model/101-5/model_NB.w", 'rb'))
scaling_factor = 1
#############################################################
def stas_feature4(data, spr):
    l = data.shape[0]
    #fft
    yf = fft(data)
    yf = yf[:l//2]
    energy = 1/(l)*np.abs(yf)
    energy_scale = energy/scaling_factor
    # energy_scale = np.log(energy)
    energy_scale = energy_scale - np.min(energy_scale)
    #feature
    r0 = 50*l//spr
    r1 = 200*l//spr
    r2 = 400*l//spr
    r3 = 800*l//spr
    
    mean1 = np.mean(energy_scale[r0:r1])
    mean2 = np.mean(energy_scale[r1:r2])
    mean3 = np.mean(energy_scale[r2:r3])
    return [mean1, mean2, mean3]

def run_test(sig, spr, n_sample):
    sum_pre = []
    for i in np.arange(1/2, sig.shape[0], 1/2):
        s = int(n_sample*(i - 1/2))
        e = int(n_sample*(i + 1/2))
        if(e > sig.shape[0]):
            break
        data = sig[s:e]
        fea_vec = stas_feature4(data, spr)
        pre = model.predict([fea_vec])[0]
        sum_pre.append(pre)
    
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
    
    if(longest_len > 7):
        return True
    return False

def run_sound(sig, spr):
    mi = 1.0*np.min(sig)
    ma = 1.0*np.max(sig)
    sound = (2*sig - (ma + mi))/(ma - mi)
    sd.play(sound, spr, blocking=True)

def scaling(data):
    l = data.shape[0]
    yf = fft(data)
    yf = yf[:l//2]
    energy = 1/(l)*np.abs(yf)
    return np.mean(energy)

