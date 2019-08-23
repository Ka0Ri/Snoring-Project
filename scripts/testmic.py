import pyaudio
import wave, struct
from utls import *
from scipy.signal import resample_poly

form_1 = pyaudio.paInt16 # 16-bit resolution
chans = 1 # 1 channel
samp_rate = 44100 # 44.1kHz sampling rate
chunk = 44100 # 2^12 samples for buffer
record_secs = 30 # seconds to record
dev_index = 3 # device index found by p.get_device_info_by_index(ii)
wav_output_filename = 'test1.wav' # name of .wav file

audio = pyaudio.PyAudio() # create pyaudio instantiation

# create pyaudio stream
stream = audio.open(format = form_1,rate = samp_rate,channels = chans, \
                    input_device_index = dev_index,input = True, \
                    frames_per_buffer=chunk)
print("recording")
frames = []
sampling_rate = 4000
# loop through stream and append audio chunks to frame array
for ii in range(0,int((samp_rate/chunk)*record_secs)):
    data = stream.read(chunk, exception_on_overflow=False)
    signal = struct.unpack("<44100h", data)
    sig = resample_poly(signal, sampling_rate, chunk)
    if(ii == 0):
        scaling_factor = scaling(sig)
        print(scaling_factor)
    else:
        #run_sound(sig, sampling_rate)
        predict_snoring = run_test(sig, sampling_rate, n_sample)
        print(predict_snoring)
    print(ii)
    frames.append(data)

print("finished recording")

# stop the stream, close it, and terminate the pyaudio instantiation
stream.stop_stream()
stream.close()
audio.terminate()

# save the audio frames as .wav file
wavefile = wave.open(wav_output_filename,'wb')
wavefile.setnchannels(chans)
wavefile.setsampwidth(audio.get_sample_size(form_1))
wavefile.setframerate(samp_rate)
wavefile.writeframes(b''.join(frames))
wavefile.close()
