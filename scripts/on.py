#!/usr/bin/python
import subprocess
import time

subprocess.call('sudo killall bluealsa', shell=True)
time.sleep(3)
subprocess.call('pulseaudio --start', shell=True)
time.sleep(2)
status = subprocess.call('ls /dev/input/event0 2>/dev/null', shell=True)  
while (True):
    print("Bluetooth On")
    subprocess.call('~/scripts/autopair', shell=True)
    subprocess.call('pacmd set-card-profile bluez_card.34_81_F4_38_F6_48 headset_head_unit', shell=True)
    subprocess.call('pacmd set-default-sink bluez_sink.34_81_F4_38_F6_48.headset_head_unit', shell=True)
    subprocess.call('pacmd set-default-source bluez_source.34_81_F4_38_F6_48.headset_head_unit', shell=True)
    time.sleep(5)
