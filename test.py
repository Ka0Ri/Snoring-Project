
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
path = os.path.dirname(os.getcwd())
print(path)
sampling_rate = 4000
n_sample = 128*sampling_rate//1000
#load model
model = pickle.load(open(path + "/model/101-5/model_DT.w", 'rb'))
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
    sum_pre = 0
    l = 2*sig.shape[0]/n_sample
    for i in np.arange(1/2, sig.shape[0], 1/2):
        s = int(n_sample*(i - 1/2))
        e = int(n_sample*(i + 1/2))
        if(e > sig.shape[0]):
            break
        data = sig[s:e]
        fea_vec = stas_feature4(data, spr)
       
        pre = model.predict([fea_vec])
        sum_pre = sum_pre + pre
    
    if(sum_pre/l > 0.3):
        return False
    return True

def run_sound(sig, spr):
    mi = 1.0*np.min(sig)
    ma = 1.0*np.max(sig)
    sound = (2*sig - (ma + mi))/(ma - mi)
    sd.play(sound, sampling_rate, blocking=True)

def scaling(data):
    l = data.shape[0]
    yf = fft(data)
    yf = yf[:l//2]
    energy = 1/(l)*np.abs(yf)
    return np.mean(energy)
############################################################

waveFile = wave.open(path + "/python_code/test.wav", 'r')
length = waveFile.getnframes()
framming_t = 1
n_frames = 4000*framming_t

if __name__ == "__main__":
    for i in range(0,length):
        print(i)
        #read stream
        waveData = waveFile.readframes(n_frames)
        data = struct.unpack("<4000h", waveData)
        #resampling
        # sig = resample_poly(data, sampling_rate, 8000)    
        sig = np.array(data)
        if(i == 0):
            scaling_factor = scaling(sig)
            print(scaling_factor)
        else:
            run_sound(sig, sampling_rate)
            predict_snoring = run_test(sig, sampling_rate, n_sample)
            print(predict_snoring)

    waveFile.close()   




