import numpy as np
from scipy.io import wavfile
from scipy.signal import resample_poly
# import matplotlib.pyplot as plt
from scipy import fftpack
import os

path = os.path.dirname(os.getcwd())
sampling_rate = 4000
f = "101"

def cut(frame, sec):
    n_sample = sec * sampling_rate
    for i in np.arange(1/2, frame.shape[0], 1/2):
        s = int(n_sample*(i - 1/2))
        e = int(n_sample*(i + 1/2))
        if(e > frame.shape[0]):
            break
        sample = frame[s:e]
        wavfile.write(path + "/new_data/" + f + "/cut2s/" + str(2*i) + ".wav", sampling_rate, sample.astype(np.int16))
        print(2*i)


def concatdata():
    s = []
    sound_path = path + "/new_data/" + f + "/no_snoring2s/"
    for sound in os.listdir(sound_path):
        print(sound)
        fs, data = wavfile.read(sound_path + sound)
        s.append(data)
    s = np.array(s)
    print(s.shape)
    np.save(path + "/numerical_data/" + "no_snoring101_2s", np.array(s))

concatdata()