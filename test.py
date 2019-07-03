import numpy as np
# from sklearn import svm
# from sklearn.naive_bayes import GaussianNB
# from sklearn.linear_model import LogisticRegression
# from sklearn.mixture import GaussianMixture
# from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
# from scipy.io import wavfile
from scipy.signal import resample_poly, spectrogram
import os
import time
import pickle
from feature import stas_feature1, stas_feature
import matplotlib.pyplot as plt
#############################################################
path = os.path.dirname(os.getcwd())
print(path)
sampling_rate = 4000
n_sample = 128*sampling_rate//1000
#load model
model = pickle.load(open(path + "/model/model_LR2.w", 'rb'))

#############################################################
def run_test(sig, spr, n_sample):
    sum_pre = 0
    l = 2*sig.shape[0]/n_sample
    for i in np.arange(1/2, sig.shape[0], 1/2):
        s = int(n_sample*(i - 1/2))
        e = int(n_sample*(i + 1/2))
        if(e > sig.shape[0]):
            break
        data = sig[s:e]
        fea_vec = stas_feature1(data, spr)
        print(fea_vec)
        # pre = model.predict([fea_vec])
        if(fea_vec[0] > 15 and fea_vec[1] > 10):
            pre = 0
        else:
            pre = 1
        sum_pre = sum_pre + pre
    
    if(sum_pre/l > 0.7):
        return False
    return True

def run_sound(sig, spr):
    mi = 1.0*np.min(sig)
    ma = 1.0*np.max(sig)
    sound = (2*sig - (ma + mi))/(ma - mi)
    sd.play(sound, sampling_rate, blocking=True)

def draw_spectogram(sig, spr):
    f, t, Sxx = spectrogram(sig, spr)
    plt.pcolormesh(t, f, Sxx)
    plt.ylabel('Frequency [Hz]')
    plt.xlabel('Time [sec]')
    plt.show()

############################################################
import wave, struct
import sounddevice as sd
waveFile = wave.open(path + "/new_data/100/test.wav", 'r')
# waveFile = wave.open(path + "/new_data/100/snoring.wav", 'r')
# waveFile = wave.open(path + "/using_data/normal.wav", 'r')
length = waveFile.getnframes()
framming_t = 1
n_frames = 8000*framming_t

for i in range(0,length):
    print(i)
    #read stream
    waveData = waveFile.readframes(n_frames)
    data = struct.unpack("<8000h", waveData)
    #resampling
    # sig = resample_poly(data, sampling_rate, 8000)    
    # sig = np.array(data)

    run_sound(sig, sampling_rate)
    predict_snoring = run_test(sig, sampling_rate, n_sample)
    print(predict_snoring)

waveFile.close()   




