
# from sklearn import svm
# from sklearn.naive_bayes import GaussianNB
# from sklearn.linear_model import LogisticRegression
# from sklearn.mixture import GaussianMixture
# from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
import numpy as np
import os
import pickle
# import sounddevice as sd
from scipy.fftpack import fft
#############################################################
sampling_rate = 4000
n_sample = 256*sampling_rate//1000
#load model
model = pickle.load(open("/home/pi/RP/model/x-4-scale/model_GMM.w", 'rb'))
#############################################################
def find_longest_len(arr):
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

def stas_feature4(data, spr):
    l = data.shape[0]
    #fft
    yf = fft(data)
    yf = yf[:l//2]
    energy = 1/(l)*np.abs(yf)
    energy_scale = energy/13
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

def run_test(sig, spr, n_sample):
    sum_pre = []
    for i in np.arange(1/2, sig.shape[0], 1/2):
        s = int(n_sample*(i - 1/2))
        e = int(n_sample*(i + 1/2))
        if(e > sig.shape[0]):
            break
        data = sig[s:e]
        fea_vec = stas_feature4(data, spr)
        pre = 1 - model.predict([fea_vec])[0]
        sum_pre.append(pre)
    
    longest_len = find_longest_len(pre)
    
    if(longest_len > 3):
        return True
    return False

def scaling(data):
    l = data.shape[0]
    yf = fft(data)
    yf = yf[:l//2]
    energy = 1/(l)*np.abs(yf)
    return np.mean(energy)

def check_and_turn_on_BT(MAC_address):
    isignal = 0
    while(isignal != 1):
    #connect mic
        subprocess.call('/home/pi/snoring/autodis', shell=True)
        time.sleep(3)
        subprocess.call('sudo killall bluealsa', shell=True)
        subprocess.call('pulseaudio --start', shell=True)
        time.sleep(1)
        subprocess.call('/home/pi/snoring/autopair', shell=True)
        time.sleep(3)
        string = "set-card-profile bluez_card." + MAC_address
        check = subprocess.check_output(["pacmd", string, "headset_head_unit"])
        if(check != b''):
            flash_LED(1)
        else:
            isignal += 1
            string = "pacmd set-card-profile bluez_card." + MAC_address + " headset_head_unit"
            subprocess.call(string, shell=True)
            string = "pacmd set-default-sink bluez_sink." + MAC_address + ".headset_head_unit"
            subprocess.call(string, shell=True)
            string = "pacmd set-default-source bluez_source." + MAC_address + ".headset_head_unit"
            subprocess.call(string, shell=True)
            for i in range(5):
                flash_LED(0.2)
                time.sleep(0.2)

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
            
    longest_len = find_longest_len(pre)
    
    if(longest_len > 3):
        return True
    return False

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
    return np.mean(np.array(log)

