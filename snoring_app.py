import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5 import QtTest
import numpy as np

from scipy.io import wavfile
from scipy.signal import resample_poly
from scipy.fftpack import fft
import sounddevice as sd

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

    mean1 = np.mean(energy[r0:r1])
    mean2 = np.mean(energy[r1:r2])
    mean3 = np.mean(energy[r2:r3])
    mean4 = np.mean(energy[r3:r4])
    mean5 = np.mean(energy[r4:r5])
    mean6 = np.mean(energy[r5:r6])

    return [mean1, mean2, mean3, mean4, mean5, mean6]

def run_test(sig, spr, n_sample, threshold):
    sum_pre = 0
    l = 2*sig.shape[0]/n_sample
    for i in np.arange(1/2, sig.shape[0], 1/2):
        s = int(n_sample*(i - 1/2))
        e = int(n_sample*(i + 1/2))
        if(e > sig.shape[0]):
            break
        data = sig[s:e]
        fea_vec = stas_feature2(data, spr)
        if(fea_vec[0] > threshold and fea_vec[1] > 3*threshold/4):
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
    sd.play(sound, spr, blocking=True)

class App(QMainWindow):
 
    def __init__(self):
        super().__init__()
        self.title = 'Snoring Project'
        self.initUI()
 
    def initUI(self):
        self.data = None
        self.current = 0
        self.step = 1
        self.length = 0
        self.spr = 4000
        self.n_sample = 512
        self.hm = np.hamming(self.n_sample)
        self.isplay = False
        self.threshold = 1
        self.setWindowTitle(self.title)
        self.setGeometry(100, 100,500, 100)

        wid = QWidget(self)
        self.setCentralWidget(wid)
        grid = QGridLayout()
        wid.setLayout(grid)
       
        #threshold
        self.label_threshold = QLabel("Threshold")
        grid.addWidget(self.label_threshold, 1, 0, 1, 1)
        self.txt_threshold = QLineEdit("1")
        grid.addWidget(self.txt_threshold, 1, 1, 1, 1)
        self.txt_threshold.editingFinished.connect(self.update_threshold)

        #Button
        self.btn_play = QPushButton("Play", self)
        grid.addWidget(self.btn_play, 1, 2, 1, 1)
        self.btn_play.clicked.connect(self.push)
      
        #slider
        self.sl_sound = QSlider(Qt.Horizontal)
        self.sl_sound.setMinimum(0)
        self.sl_sound.setMaximum(0)
        self.sl_sound.setValue(0)
        grid.addWidget(self.sl_sound, 2, 0, 1, 3)
        self.sl_sound.valueChanged.connect(self.update_time)

        #Prediction
        self.label_s = QLabel("The 0th second: ")
        grid.addWidget(self.label_s, 3, 0, 1, 1)
        self.label_result = QLabel("")
        grid.addWidget(self.label_result, 3, 1, 1, 1)

        self.openfile = QAction("Open", self)
        self.openfile.setShortcut("Ctrl+O")
        self.openfile.triggered.connect(self.load)
        self.mainMenu = self.menuBar()
        self.fileMenu = self.mainMenu.addMenu('&File')
        self.fileMenu.addAction(self.openfile)

        self.show()
    
    def load(self):
        dlg = QFileDialog(self)
        dlg.setFileMode(QFileDialog.AnyFile)
        dlg.setNameFilters(["Wave files (*.wav)"])
        if dlg.exec_():
            filenames = dlg.selectedFiles()
            fs, data = wavfile.read(filenames[0])
            if(fs != self.spr):
                data = resample_poly(data, self.spr, fs)
            data = data - np.mean(data)
            self.data = data
            n = data.shape[0]
            self.btn_play.setText("Stop")
            self.isplay = True
            self.length = n//4000
            self.sl_sound.setMinimum(0)
            self.sl_sound.setMaximum(self.length)
            self.sl_sound.setValue(0)
            self.current = 0
            self.play_predict()

    def push(self):
        if(self.isplay == False):
            self.isplay = True
            self.btn_play.setText("Stop")
        else:
            self.isplay = False
            self.btn_play.setText("play")
        self.play_predict()

    def update_time(self):
        if(self.isplay == False):
            self.current = int(self.sl_sound.value())
    
    def update_threshold(self):
        if(self.isplay == False):
            self.threshold = int(self.txt_threshold.text())

    def play_predict(self):
        if(self.isplay == True):
            while(self.current < self.length):
                self.current = self.current + 1
                self.label_s.setText("The " + str(self.current) + " th second")
                self.sl_sound.setValue(self.current)
                sig = self.data[self.current*self.spr:(self.current + 1)*self.spr]
                run_sound(sig, self.spr)
                r = run_test(sig, self.spr, self.n_sample, self.threshold)
                self.label_result.setText(str(r))
                QtTest.QTest.qWait(1)
                QApplication.processEvents()
                if(self.isplay == False):
                    break

 
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())