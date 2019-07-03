import sys
import os
from PyQt5.QtWidgets import QWidget, QPushButton, QLabel, QLineEdit, QRadioButton, QApplication, QGridLayout, QFileDialog, QSlider, QButtonGroup, QGroupBox, QComboBox, QVBoxLayout, QCheckBox
from PyQt5.QtCore import Qt
import numpy as np

from scipy.io import wavfile
from scipy.signal import resample_poly, firwin, freqz, lfilter, cheby1, butter
from scipy.fftpack import fft
 
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
 
class App(QWidget):
 
    def __init__(self):
        super().__init__()
        self.title = 'signal display'
        self.initUI()
 
    def initUI(self):
        self.data = None
        self.filter = None
        self.filter_a = 1.0
        self.filter_IIR = None
        self.spr = 0
        self.setWindowTitle(self.title)
        self.setGeometry(100, 100, 800, 600)

        grid = QGridLayout()
        self.setLayout(grid)
       
        #signal
        self.figure = plt.figure(figsize=(5,5))
        self.canvas = FigureCanvas(self.figure)
        grid.addWidget(self.canvas, 7, 0, 2, 2)
        self.toolbar = NavigationToolbar(self.canvas, self)
        grid.addWidget(self.toolbar, 6, 0, 1, 2)
        
        #sampling rate
        self.label_spr = QLabel("sampling rate")
        grid.addWidget(self.label_spr, 0, 0, 1, 1)
        self.txt_spr = QLineEdit(self)
        grid.addWidget(self.txt_spr, 0, 1, 1, 1)
        self.txt_spr.editingFinished.connect(self.recalculate)

        #load button
        self.btn_load = QPushButton("load signal", self)
        grid.addWidget(self.btn_load, 5, 0, 1, 1)
        self.btn_load.clicked.connect(self.load)

        #radio button
        self.ft_group = QButtonGroup(grid)
        # grid.addWidget(self.ft_group, 8, 0, 1, 2)
        self.b1 = QRadioButton("Time Domain")
        self.b1.setChecked(True)
        self.b1.toggled.connect(self.toogle)
        self.ft_group.addButton(self.b1)
        grid.addWidget(self.b1, 9, 0, 1, 1)
        self.b2 = QRadioButton("Frequency Domain")
        self.b2.toggled.connect(self.toogle)
        self.ft_group.addButton(self.b2)
        grid.addWidget(self.b2, 9, 1, 1, 1)

        #slider
        self.label_start = QLabel("Start time")
        grid.addWidget(self.label_start, 1, 0, 1, 1)
        self.label_end = QLabel("end time")
        grid.addWidget(self.label_end, 3, 0, 1, 1)
        self.sl_start = QSlider(Qt.Horizontal)
        self.sl_start.setMinimum(0)
        self.sl_start.setMaximum(0)
        self.sl_start.setValue(0)
        grid.addWidget(self.sl_start, 1, 1, 1, 1)
        self.sl_start.valueChanged.connect(self.valuechange_start)
        # self.sl_start.sliderReleased.connect(self.valuechange_start)
        self.sl_end = QSlider(Qt.Horizontal)
        self.sl_end.setMinimum(0)
        self.sl_end.setMaximum(0)
        self.sl_end.setValue(0)
        grid.addWidget(self.sl_end, 3, 1, 1, 1)
        self.sl_end.valueChanged.connect(self.valuechange_end)
        # self.sl_end.sliderReleased.connect(self.valuechange_end)

        self.txt_start = QLineEdit(self)
        grid.addWidget(self.txt_start, 2, 1, 1, 1)
        self.txt_start.editingFinished.connect(self.start_change)
        self.txt_end = QLineEdit(self)
        grid.addWidget(self.txt_end, 4, 1, 1, 1)
        self.txt_end.editingFinished.connect(self.end_change)
        

        #filter
        self.figure_fil = plt.figure(figsize=(1,1))
        self.canvas_fil = FigureCanvas(self.figure_fil)
        grid.addWidget(self.canvas_fil, 7, 2, 2, 6)
        # self.toolbar1 = NavigationToolbar(self.canvas_fil, self)
        # grid.addWidget(self.toolbar1, 6, 2, 1, 2)
        
        self.filtered = QCheckBox("Filtering")
        grid.addWidget(self.filtered, 9, 3, 1, 1)

        ###########################################################################
        self.filter_gr = QGroupBox("filter")
        vbox = QGridLayout()
        self.filter_type = QComboBox()
        self.filter_type.addItems(["hamming", "blackman", "hann", "bartlett", "boxcar", "kaiser", "Chebyshev"])
        self.filter_type.activated.connect(self.filter_choice)
        vbox.addWidget(self.filter_type,0, 0, 1, 1)
        self.band_type = QComboBox()
        self.band_type.addItems(["bandpass", "bandstop", "lowpass", "highpass"])
        self.band_type.activated.connect(self.filter_choice)
        vbox.addWidget(self.band_type, 0, 1, 1, 1)

        self.cut_off1 = QLabel("Cut off 1")
        vbox.addWidget(self.cut_off1,1, 0, 1, 1)
        self.sl_cut_off1 = QSlider(Qt.Horizontal)
        self.sl_cut_off1.setMinimum(1)
        self.sl_cut_off1.setMaximum(99)
        self.sl_cut_off1.setValue(0)
        vbox.addWidget(self.sl_cut_off1,1 ,1 ,1 ,1)
        self.sl_cut_off1.valueChanged.connect(self.filter_choice)
        self.cut_off2 = QLabel("Cut off 2")
        vbox.addWidget(self.cut_off2, 2, 0, 1, 1)
        self.sl_cut_off2 = QSlider(Qt.Horizontal)
        self.sl_cut_off2.setMinimum(1)
        self.sl_cut_off2.setMaximum(99)
        self.sl_cut_off2.setValue(0)
        vbox.addWidget(self.sl_cut_off2, 2, 1, 1, 1)
        self.sl_cut_off2.valueChanged.connect(self.filter_choice)
        self.sl_length = QLabel("Length")
        vbox.addWidget(self.sl_length,3, 0, 1, 1)
        self.sl_length = QSlider(Qt.Horizontal)
        self.sl_length.setMinimum(3)
        self.sl_length.setMaximum(100)
        self.sl_length.setValue(0)
        vbox.addWidget(self.sl_length,3, 1, 1, 1)
        self.sl_length.valueChanged.connect(self.filter_choice)
        self.sl_order = QLabel("order")
        vbox.addWidget(self.sl_order,4, 0, 1, 1)
        self.sl_order = QSlider(Qt.Horizontal)
        self.sl_order.setMinimum(1)
        self.sl_order.setMaximum(10)
        self.sl_order.setValue(0)
        vbox.addWidget(self.sl_order,4, 1, 1, 1)
        self.sl_order.valueChanged.connect(self.filter_choice)

        self.filter_gr.setLayout(vbox)
        grid.addWidget(self.filter_gr, 0, 3, 5, 3)

        #############################################################
        
        self.show()


    def filter_choice(self):
        win = self.filter_type.currentText()
        band = self.band_type.currentText()
        cut1 = int(self.sl_cut_off1.value())/100
        cut2 = int(self.sl_cut_off2.value())/100
        length = int(self.sl_length.value())
        order = int(self.sl_order.value())
        if(length % 2 == 0):
            length = length - 1
        if(cut1 >= cut2 ):
            return
        if(win == "Chebyshev"):
            b, a = cheby1(order, 0.001, [cut1, cut2], band)
            self.filter = b
            self.filter_a = a
            return
        if(win == "kaiser"):
            win = ('kaiser', 4.0)
        if(band == "bandpass"):
            self.filter = firwin(length, [cut1, cut2], window=win, pass_zero=False)
        if(band == "lowpass"):
            self.filter = firwin(length, [cut1], window=win)
        if(band == "highpass"):
            self.filter = firwin(length, [cut1], window=win, pass_zero=False)
        if(band == "bandstop"):
            self.filter = firwin(length, [cut1, cut2], window=win)
        
        self.plot2()
        self.plot()

    def toogle(self):
        self.plot()
        self.plot2()

    def plot2(self):
        ax = self.figure_fil.add_subplot(111)
        ax.clear()
        # ax.set_title('Filter')
        if(self.filter is None):
            return
        n = self.filter.shape[0]
        x = np.arange(0, n, 1)
        y = self.filter
        if(self.b1.isChecked() == True):
            pen = 'b-'
        else:
            w, h = freqz(y, worN=1024)
            y = np.abs(h)
            x = np.linspace(0, 0.5, 1024)
            pen = 'r-'
        ax.plot(x, y, pen)
        self.canvas_fil.draw()


    def start_change(self):
        if(self.txt_start.text() == ''):
            return
        start_time = int(self.txt_start.text())
        self.sl_start.setValue(start_time)
        self.valuechange_start()
    
    def end_change(self):
        if(self.txt_end.text() == ''):
            return
        end_time = int(self.txt_end.text())
        self.sl_end.setValue(end_time)
        self.valuechange_end()

    def valuechange_end(self):
        end_time = int(self.sl_end.value())
        t = (end_time * 1000) // self.spr
        self.label_end.setText("end time: " + str(t) + " ms ")
        self.txt_end.setText(str(end_time))
        self.plot()

    def valuechange_start(self):
        start_time = int(self.sl_start.value())
        t = (start_time * 1000) // self.spr
        self.label_start.setText("start time: " + str(t) + " ms")
        self.txt_start.setText(str(start_time))
        self.plot()

    def plot(self):
        ax = self.figure.add_subplot(111)
        ax.clear()
        ax.set_title('Snoring signal')
        if(self.data is None):
            return
        start_time = int(self.sl_start.value())
        end_time = int(self.sl_end.value())
        if(start_time < end_time):
            x = range(start_time, end_time)
            y = self.data[start_time:end_time]
            n_sample = y.shape[0]
            if(self.filtered.isChecked() == True and self.filter is not None):
                y = lfilter(self.filter, self.filter_a, y)
            # mi = 1.0*np.min(y)
            # ma = 1.0*np.max(y)
            # y = (2*y - (ma + mi))/(ma - mi)
            if(self.b1.isChecked() == True):
                pen = 'b-'
            else:
                # hw = np.hamming(n_sample)
                # y = y * hw
                yf = (1/n_sample)*fft(y)
                x = np.linspace(0, self.spr//2, n_sample//2)
                y = np.abs(yf[:n_sample//2])
                pen = 'r-'

            ax.plot(x, y, pen)
            self.canvas.draw()
    
    def load(self):
        dlg = QFileDialog(self)
        dlg.setFileMode(QFileDialog.AnyFile)
        dlg.setNameFilters(["Wave files (*.wav)"])
        if dlg.exec_():
            filenames = dlg.selectedFiles()
            fs, data = wavfile.read(filenames[0])
            data = data - np.mean(data)
            self.data = data
            n = data.shape[0]
            self.spr = fs
            self.sl_start.setMaximum(n)
            self.sl_end.setMaximum(n)
            self.label_spr.setText("sampling rate (Hz) " + str(n) + " samples")
            self.txt_spr.setText(str(fs))
            self.plot()

    def recalculate(self):
        if(self.txt_spr.text() == ''):
            return
        if(self.data is None):
            return
        resampling_rate = int(self.txt_spr.text())
        y = resample_poly(self.data, resampling_rate, self.spr)
        n = y.shape[0]
        self.sl_start.setMaximum(n)
        self.sl_end.setMaximum(n)
        self.label_spr.setText("sampling rate (Hz) " + str(n) + " samples")
        self.spr = resampling_rate
        self.data = y
        self.plot()
 
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())