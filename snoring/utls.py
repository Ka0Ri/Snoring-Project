
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
import subprocess
import time
from bluetoothctl import *
import RPi.GPIO as GPIO
#############################################################
sampling_rate = 4000
n_sample = 128*sampling_rate//1000
#load model
#model = pickle.load(open("/home/pi/snoring/model/full/model_LDA.w", 'rb'))
#############################################################

import serial
port = "/dev/serial0"
#port = "/dev/ttyUSB0"
baud = 115200

#ser = serial.Serial(port, baud, parity = serial.PARITY_NONE, stopbits = serial.STOPBITS_ONE, bytesize = serial.EIGHTBITS, timeout = 3.0)
ser = serial.Serial(port, baud, timeout = 3)
ser.close()
#############################################################
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
chan_list = [4, 21]
GPIO.setup(chan_list,GPIO.OUT)
#############################################################
def send_signal_TX(mess):
    try:
        ser.open()
        x = ser.write(mess.encode('UTF-8'))
        #time.sleep(0.1)
        #print(mess)
    except (OSError, serial.serialutil.SerialException):
        ser.close()
        pass
    ser.close()


def flash_LED(s, pin):
    GPIO.output(pin, GPIO.HIGH)
    time.sleep(s)
    GPIO.output(pin,GPIO.LOW)

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
    hw = np.hamming(l)
    data = data * hw
    yf = fft(data)
    yf = yf[:l//2]
    energy = 1/(l)*np.abs(yf)
    energy_scale = energy/10
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
    print(mean1)
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
        pre = 1 - model.predict([fea_vec])[0]
        sum_pre.append(pre)
    
    longest_len = find_longest_len(sum_pre)
    
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
    MAC_add_bl = MAC_address.replace('_',':')
    print(MAC_add_bl)
    isignal = 0
    print("Init bluetooth...")
    bl = Bluetoothctl()
    print("Ready!")
    subprocess.call('pulseaudio --start', shell=True)
    subprocess.call('pulseaudio --kill', shell=True)
    while(isignal != 1):
    #connect mic
        try:
            send_signal_TX("00000011\n")
            bl.disconnect(MAC_add_bl)
            print("disconnect")
            time.sleep(3)
        except:
            continue
        subprocess.call('sudo killall bluealsa', shell=True)
        subprocess.call('pulseaudio --start', shell=True)
        time.sleep(1)
        try:
            bl.connect(MAC_add_bl)
            print("connect")
            time.sleep(3)
        except:
            continue
        else:
            string = "set-card-profile bluez_card." + MAC_address
            check = subprocess.check_output(["pacmd", string, "headset_head_unit"])
            if(check != b''):
                continue
            else:
                isignal += 1
                string = "pacmd set-card-profile bluez_card." + MAC_address + " headset_head_unit"
                subprocess.call(string, shell=True)
                string = "pacmd set-default-sink bluez_sink." + MAC_address + ".headset_head_unit"
                subprocess.call(string, shell=True)
                string = "pacmd set-default-source bluez_source." + MAC_address + ".headset_head_unit"
                subprocess.call(string, shell=True)
    for i in range(5):
        flash_LED(0.2, 4)
        time.sleep(0.2)
    GPIO.output(4, GPIO.HIGH)
    send_signal_TX("00000100\n")
            

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
    scaling_factor = 12
    sum_pre = []
    for i in np.arange(1/2, sig.shape[0], 1/2):
        s = int(n_sample*(i - 1/2))
        e = int(n_sample*(i + 1/2))
        if(e > sig.shape[0]):
            break
        data = sig[s:e]
        mean = fea(data, sampling_rate)
        #print(mean)
        if(mean > 4*scaling_factor):
           sum_pre.append(0)
        else:
            sum_pre.append(1)
            
    longest_len = find_longest_len(sum_pre)
    
    if(longest_len > 8):
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
    return np.mean(np.array(log))
