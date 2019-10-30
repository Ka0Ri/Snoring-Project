import wave
import pyaudio
import numpy as np
from utls import run_test2, find_longest_len, run_test
import time


f = open("2.txt","w+")

class AudioFile:
    chunk = 1024
    def __init__(self, file):
        """ Init audio stream """ 
        self.wf = wave.open(file, 'rb')
        self.p = pyaudio.PyAudio()
        self.start = time.time()
        self.counter = 0
        self.data = []
        self.stream = self.p.open(
            format = self.p.get_format_from_width(self.wf.getsampwidth()),
            channels = self.wf.getnchannels(),
            rate = self.wf.getframerate(),
            output = True
        )
    
    def detect_1s(self, data):
        data = np.fromstring(np.array(data).flatten(), 'int16')
        sum_pre = run_test2(data, 4000, 512, 15)
        snoring = find_longest_len(sum_pre)
        if(snoring > 8):
            return True
        else:
            return False


    def play(self):
        """ Play entire file """
        data = self.wf.readframes(self.chunk)
        while data != '':
            self.stream.write(data)
            data = self.wf.readframes(self.chunk)
            self.data.append(data)

            #check 1 second
            if(time.time() - self.start > 1):
                self.start = time.time()
                self.counter += 1

                snore = self.detect_1s(self.data)
                print("snoring at %d second is %d "%(self.counter, snore))
                f.write("at %d is %d \n"%(self.counter, snore))
                
                self.data = []

    def close(self):
        """ Graceful shutdown """ 
        self.stream.close()
        self.p.terminate()

# Usage example for pyaudio
a = AudioFile("2.wav")
a.play()
a.close()
f.close()
