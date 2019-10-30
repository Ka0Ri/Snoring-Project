# class taken from the SciPy 2015 Vispy talk opening example 
# see https://github.com/vispy/vispy/pull/928
import pyaudio
import threading
import atexit
import numpy as np

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt


from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QLabel, QSlider, QCheckBox, QVBoxLayout, QWidget, QPlainTextEdit
from PyQt5.QtCore import QTimer
import wave

from utls import run_test2, find_longest_len, run_test


class AudioPlaying(object):
    def __init__(self, path, rate=4000, chunksize=1024):
        self.wf = wave.open(path, 'rb')
        self.rate = rate
        self.chunksize = chunksize
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=pyaudio.paInt16,
                                  channels=1,
                                  rate=self.rate,
                                  input=True,
                                  frames_per_buffer=self.chunksize,
                                  stream_callback=self.new_frame)
        self.lock = threading.Lock()
        self.stop = False
        self.frames = []
        atexit.register(self.close)

    def new_frame(self, data, frame_count, time_info, status):
        data = self.wf.readframes(frame_count)
        data = np.fromstring(data, 'int16')
        with self.lock:
            self.frames.append(data)
            if self.stop:
                return None, pyaudio.paComplete
        return None, pyaudio.paContinue
    
    def get_frames(self):
        with self.lock:
            frames = self.frames
            self.frames = []
            return frames
    
    def start(self):
        self.stream.start_stream()

    def close(self):
        with self.lock:
            self.stop = True
        self.stream.close()


class MicrophoneRecorder(object):
    def __init__(self, rate=4000, chunksize=1024):
        self.rate = rate
        self.chunksize = chunksize
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=pyaudio.paInt16,
                                  channels=1,
                                  rate=self.rate,
                                  input=True,
                                  frames_per_buffer=self.chunksize,
                                  stream_callback=self.new_frame)
        self.lock = threading.Lock()
        self.stop = False
        self.frames = []
        atexit.register(self.close)

    def new_frame(self, data, frame_count, time_info, status):
        data = np.fromstring(data, 'int16')
        with self.lock:
            self.frames.append(data)
            if self.stop:
                return None, pyaudio.paComplete
        return None, pyaudio.paContinue
    
    def get_frames(self):
        with self.lock:
            frames = self.frames
            self.frames = []
            return frames
    
    def start(self):
        self.stream.start_stream()

    def close(self):
        with self.lock:
            self.stop = True
        self.stream.close()
        

class LiveFFTWidget(QWidget):
    def __init__(self):
        super().__init__()
        
        # customize the UI
        self.initUI()
        
        # init class data
        self.initData()       
        
        # connect slots
        self.connectSlots()
        
        # init MPL widget
        self.initMplWidget()
        
    def initUI(self):

        hbox_gain = QHBoxLayout()
        autoGain = QLabel('Auto gain for frequency spectrum')
        autoGainCheckBox = QCheckBox(checked=True)
        hbox_gain.addWidget(autoGain)
        hbox_gain.addWidget(autoGainCheckBox)
        
        # reference to checkbox
        self.autoGainCheckBox = autoGainCheckBox
        
        vbox = QVBoxLayout()

        vbox.addLayout(hbox_gain)

        # mpl figure
        self.main_figure = Figure(facecolor='white')
        self.canvas = FigureCanvas(self.main_figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        
        vbox.addWidget(self.toolbar)
        vbox.addWidget(self.canvas)

        # log pannel
        self.log_pannel = QPlainTextEdit(self)
        self.log_pannel.setReadOnly(True)

        vbox.addWidget(self.log_pannel)


        self.setLayout(vbox)
        
        self.setGeometry(300, 300, 500, 700)
        self.setWindowTitle('Snoring Detection Application')    
        self.show()

        #time parameters
        self.time_count = 0
        self.snoring_1_second = []
        self.snoring_30_second = []
        # timer for callbacks, taken from:
        # http://ralsina.me/weblog/posts/BB974.html
        timer = QTimer()
        timer.timeout.connect(self.handleNewData)
        timer.start(10)
        # keep reference to timer        
        self.timer = timer
             
    def initData(self):
        #mic = AudioPlaying(path="test.wav")
        mic = MicrophoneRecorder()
        mic.start()  

        # keeps reference to mic        
        self.mic = mic
        
        # computes the parameters that will be used during plotting
        self.freq_vect = np.fft.rfftfreq(mic.chunksize, 1./mic.rate)
        self.time_vect = np.arange(mic.chunksize, dtype=np.float32) / mic.rate * 1000
                
    def connectSlots(self):
        pass
    
    def initMplWidget(self):
        """creates initial matplotlib plots in the main window and keeps 
        references for further use"""
        # top plot
        self.ax_top = self.main_figure.add_subplot(211)
        self.ax_top.set_ylim(-2000, 2000)
        self.ax_top.set_xlim(0, self.time_vect.max())
        self.ax_top.set_xlabel(u'time (ms)', fontsize=6)

        # bottom plot
        self.ax_bottom = self.main_figure.add_subplot(212)
        self.ax_bottom.set_ylim(0, 1)
        self.ax_bottom.set_xlim(0, self.freq_vect.max())
        self.ax_bottom.set_xlabel(u'frequency (Hz)', fontsize=6)
        # line objects: a list of Line2D objects representing the plotted data.       
        self.line_top, = self.ax_top.plot(self.time_vect, np.ones_like(self.time_vect), 'r-')
        
        self.line_bottom, = self.ax_bottom.plot(self.freq_vect, np.ones_like(self.freq_vect), 'b-')
                                               
                                      
    def handleNewData(self):
        """ handles the asynchroneously collected sound chunks """        
        # gets the latest frames        
        frames = self.mic.get_frames()
        self.time_count = self.time_count + 10
        if len(frames) > 0:
            # keeps only the last frame
            current_frame = frames[-1]
            # plots the time signal: set the x and y data for the subplot
            self.line_top.set_data(self.time_vect, current_frame)
            # computes and plots the fft signal            
            fft_frame = np.fft.rfft(current_frame)
            if self.autoGainCheckBox.checkState() == QtCore.Qt.Checked:
                fft_frame /= np.abs(fft_frame).max()
                self.line_bottom.set_data(self.freq_vect, np.abs(fft_frame)) 
            #predicted           
            sum_pred = run_test2(current_frame, self.mic.rate, 512, 15)
            self.snoring_1_second.append(sum_pred)
            # refreshes the plots
    
        if(self.time_count % 1000 == 0):
            second = self.time_count // 1000
            print(self.snoring_1_second)
            #decision over 1 second
            no_snoring_1s = find_longest_len(np.array(self.snoring_1_second).flatten())
            if(no_snoring_1s > 8):
                mes = "Snoring at %d second: True"%(second)
                self.snoring_30_second.append(1)
            else:
                mes = "Snoring at %d second: False"%(second)
                self.snoring_30_second.append(0)
            self.log_pannel.appendPlainText(mes)
            self.snoring_1_second = []
        
            #decision over 30 second
            if(second >= 30 and second % 5 == 0):
                no_snoring_30s = sum(self.snoring_30_second)
                self.snoring_30_second.pop(0)
                if(no_snoring_30s > 10):
                    mes = "Snoring over 30 seconds: %d => snore"%(no_snoring_30s)
                else:
                    mes = "Snoring over 30 seconds: %d => no snore"%(no_snoring_30s)
                self.log_pannel.appendPlainText(mes)
        self.main_figure.canvas.draw()


import sys 
if __name__ == "__main__":
    app = QApplication(sys.argv) 
    window = LiveFFTWidget() 
    sys.exit(app.exec_())